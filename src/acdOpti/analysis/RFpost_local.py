# -*- coding: utf8 -*-
#
# Copyright 2011 Kyrre Ness Sjøbæk
# This file is part of AcdOpti.
#
#    AcdOpti is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    AcdOpti is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with AcdOpti.  If not, see <http://www.gnu.org/licenses/>.

from AnalysisInterface import AnalysisInterface

from acdOpti.AcdOptiFileParser import DataDict, AcdOptiFileParser_simple, AcdOptiFileParser_KVC
from acdOpti.AcdOptiSolverManager import AcdOptiSolverManager
import acdOpti.AcdOptiAcdtoolWrapper as AcdOptiAcdtoolWrapper

from RFpostParser import RFpostParser, RFpostException, RFpostException_runAna


import os, shutil

class RFpost_local(AnalysisInterface, RFpostParser):
    """
    Analysis that runs acdtool postprocess rf locally.
    The output can then be parsed by the RFpost analysis.
    
    This analysis is detected specially by the AnalysisExportedResults
    GUI infoframecomponent, making it simple to edit its SolverSetup.
    """
    __paramFile = None
        
    def __init__(self, folder, name, runConfig):
        print "RFpost_local::__init__()"
        self.type     = "RFpost_local"
        self.folder   = folder
        self.instName = name
        self.runConfig = runConfig
        
        #Load paramFile
        self.__paramFile = AcdOptiFileParser_simple(os.path.join(folder, name, "paramFile.set"), 'rw')
        if self.__paramFile.dataDict["fileID"] != "Analysis::RFpost_local":
            raise RFpostException("Got fileID='" + self.__paramFile.dataDict["fileID"] + "'")
        self.lockdown = DataDict.boolconv(self.__paramFile.dataDict["lockdown"])

        self.exportResults = self.__paramFile.dataDict["export"]
    
        #Load RFpost solverManager
        self.localSolver = AcdOptiSolverManager("rfPost.in", os.path.join(folder,name))
        if self.lockdown:
            self.localSolver.lockdown = True
    
        #Load the settings
        if len(self.__paramFile.dataDict.getVals("settings")) == 0:
            self.__paramFile.dataDict.pushBack("settings", DataDict())
            self.__paramFile.dataDict["settings"].pushBack("L","")
            self.__paramFile.write()
        self.settings = self.__paramFile.dataDict["settings"]
    
    def runAnalysis(self):
        print "RFpost_local::runAnalysis()"        
        assert not self.lockdown
        
        #Generate the setup file
        self.lockdown = True

        origResultDir = self.localSolver.metaSetup['RFField']['children']['ResultDir']['value'] #Subdirectory whith the data
        dataPath = os.path.join(self.folder, self.instName, "data") #Path to symlink to data folder
        dataPath2 = os.path.join(dataPath, origResultDir) #Path to O3P etc. results thorough symlink
        self.localSolver.metaSetup['RFField']['children']['ResultDir'].setValSingle("value", os.path.join("data", origResultDir))
        
        self.localSolver.generateSetup()
        self.localSolver.lockdown = True
        
        #Create a symlink to avoid long folder names (ACDtool doesn't like that)
        if os.path.islink(dataPath):
            os.unlink(dataPath)
        os.symlink(self.runConfig.finishedFolder, dataPath) #UNIX only!
        
        #Modify the postprocess.in file to the right path
        shutil.copy(os.path.join(dataPath2, "VECTOR", "postprocess.in"),\
                    os.path.join(self.folder, self.instName, "postprocess.in.bak"))
        
        postFile = AcdOptiFileParser_KVC(os.path.join(dataPath2, "VECTOR", "postprocess.in"),"rw")
        #print postFile.dataDict
        postFile.dataDict["ModelInfo"].setValSingle("File", os.path.join(dataPath, "mesh.ncdf"))
        postFile.dataDict["CheckPoint"].setValSingle("Directory", os.path.join(os.path.join(dataPath2, "VECTOR")))
        postFile.write()
        
        #Run AcdTool!
        AcdOptiAcdtoolWrapper.rfPost("rfPost.in", os.path.join(self.folder, self.instName))
        
        #Restore stuff
        self.localSolver.metaSetup['RFField']['children']['ResultDir'].setValSingle("value", origResultDir)
        self.localSolver.write()
        
        shutil.copy(os.path.join(self.folder, self.instName, "postprocess.in.bak"),\
                    os.path.join(dataPath2, "VECTOR", "postprocess.in"))
        
        os.unlink(dataPath)
        
        #Parse output
        ifile = open(os.path.join(self.folder, self.instName, "rfpost.out"), 'r')
        fileData = ifile.read()
        ifile.close()
        
        #Save results
        try:
            L = float(self.settings["L"])
        except ValueError:
            print 'Couldnt parse self.settings["L"]'
            L = -1.0;
        addDic = self.parseData(fileData, L)
        for (k,v) in addDic:
            self.exportResults.pushBack(k,v)
        
        self.write()
        
    def clearLockdown(self):
        print "RFpost_local::clearLockdown()"
        if not self.lockdown:
            return
        self.exportResults.clear()
        os.remove(self.localSolver.fileName)
        self.lockdown = False
        self.localSolver.lockdown = False
        self.write()
    
    def write(self):
        self.__paramFile.dataDict.setValSingle("lockdown", str(self.lockdown))
        self.__paramFile.write()
    
    @staticmethod
    def createNew(folder,name):
        #Create a new folder to hold the stuff
        os.mkdir(os.path.join(folder,name))
        
        #Create a SolverSetup
        AcdOptiSolverManager.createNew("acdtool_rfpost", os.path.join(folder,name))
        
        #Parameter file
        paramFile = AcdOptiFileParser_simple(os.path.join(folder,name,"paramFile.set"), "w")
        paramFile.dataDict.pushBack("fileID", "Analysis::RFpost_local")
        paramFile.dataDict.pushBack("lockdown", "False")
        
        paramFile.dataDict.pushBack("export", DataDict())
        
        paramFile.dataDict.pushBack("settings", DataDict())
        paramFile.dataDict["settings"].pushBack("L","")
        
        paramFile.write()

    @classmethod
    def createNew_clone(cls, folder,cloneFrom,newRunConfig):
        print "RFpost_local::createNew_clone()"
        #Call baseclass createNew_clone(), but don't keep the object:
        #AnalysisInterface.createNew_clone(folder, cloneFrom, newRunConfig)
        super(RFpost_local,cls).createNew_clone(folder,cloneFrom,newRunConfig)
        #Replace the SolverSetup
        os.unlink(os.path.join(folder,cloneFrom.instName,"rfPost.in.meta"))
        AcdOptiSolverManager.createNew_clone(os.path.join(folder, cloneFrom.instName),cloneFrom.localSolver)
        
        return RFpost_local(folder,cloneFrom.instName,newRunConfig)
        