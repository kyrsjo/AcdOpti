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

from acdOpti.AcdOptiExceptions import AcdOptiException_analysis, AcdOptiException_analysis_runAnalysis

#from RFpostParser import RFpostParser, RFpostException, RFpostException_runAna


import os, shutil

class ModeFileRecalc(AnalysisInterface):
    """
    Analysis that runs acdtool postprocess eigentomode locally,
    recreating the buggy modefiles you get from paralell O3P. 
    """
    __paramFile = None
        
    def __init__(self, folder, name, runConfig):
        print "ModeFileRecalc::__init__()"
        self.type     = "ModeFileRecalc"
        self.folder   = folder
        self.instName = name
        self.runConfig = runConfig
        
        #Load paramFile
        self.__paramFile = AcdOptiFileParser_simple(os.path.join(folder, name, "paramFile.set"), 'rw')
        if self.__paramFile.dataDict["fileID"] != "Analysis::ModeFileRecalc":
            raise ModeFileRecalcException("Got fileID='" + self.__paramFile.dataDict["fileID"] + "'")
        self.lockdown = DataDict.boolconv(self.__paramFile.dataDict["lockdown"])

        self.exportResults = self.__paramFile.dataDict["export"]
    
        #Load the settings
        self.settings = self.__paramFile.dataDict["settings"]
    
    def runAnalysis(self):
        print "ModeFileRecalc::runAnalysis()"        
        assert not self.lockdown
        
        #Generate the setup file
        self.lockdown = True

        origResultDir = self.settings["ResultDir"] #Subdirectory whith the data
        dataPath = os.path.join(self.folder, self.instName, "data") #Path to symlink to data folder
        dataPath2 = os.path.join(dataPath, origResultDir) #Path to O3P etc. results thorough symlink
        
        #Create a symlink to avoid long folder names (ACDtool doesn't like that)
        if os.path.islink(dataPath):
            os.unlink(dataPath)
        os.symlink(self.runConfig.finishedFolder, dataPath) #UNIX only!
        
        #Modify the postprocess.in file to the right path
        shutil.copy(os.path.join(dataPath2, "VECTOR", "postprocess.in"),\
                    os.path.join(self.folder, self.instName, "postprocess.in.bak"))
        
        postFile = AcdOptiFileParser_KVC(os.path.join(dataPath2, "VECTOR", "postprocess.in"),"rw")
        postFile.dataDict["ModelInfo"].setValSingle("File", os.path.join(dataPath, "mesh.ncdf"))
        postFile.dataDict["CheckPoint"].setValSingle("Directory", os.path.join(os.path.join(dataPath2, "VECTOR")))
        postFile.write()
        
        #Check that we don't destroy any data...
        if os.path.isfile(os.path.join(dataPath, "acdtool.log")) or os.path.isfile(os.path.join(dataPath, "acdtool.warn")):
            #Restore stuff
            shutil.copy(os.path.join(self.folder, self.instName, "postprocess.in.bak"),\
                        os.path.join(dataPath2, "VECTOR", "postprocess.in"))
            os.unlink(dataPath)
            raise ModeFileRecalcException_runAna("acdtool log files already exists")
        
        #Move the old modefile out of the way...
        oldFilesFolder = os.path.join(self.folder,self.instName, "oldModes")
        if os.path.isdir(oldFilesFolder):
            offls = os.listdir(oldFilesFolder)
            if len(offls) > 0:
                shutil.copy(os.path.join(self.folder, self.instName, "postprocess.in.bak"),\
                            os.path.join(dataPath2, "VECTOR", "postprocess.in"))   
                raise ModeFileRecalcException_runAna
        else:
            os.mkdir(oldFilesFolder)
        files = os.listdir(dataPath2)
        movedFiles = []
        for f in files:
            if f.startswith("mode.") and f.endswith(".mod"):
                shutil.move( os.path.join(dataPath2,f), os.path.join(oldFilesFolder,f) )
                movedFiles.append(f)
        
        #Run AcdTool!
        try:
            AcdOptiAcdtoolWrapper.eigentomode(origResultDir, dataPath)
        except:
            shutil.move( os.path.join(dataPath,"acdtool.log"), os.path.join(self.folder,self.instName,"acdtool.log"))
            raise
        
        #Move newly created files to results dir
        files = os.listdir(dataPath2)
        for f in files:
            if f.startswith("mode.") and f.endswith(".mod"):
                shutil.move( os.path.join(dataPath2,f), os.path.join(self.folder,self.instName,f)) 
        shutil.move( os.path.join(dataPath,"acdtool.log"), os.path.join(self.folder,self.instName,"acdtool.log"))
        shutil.move( os.path.join(dataPath,"acdtool.warn"), os.path.join(self.folder,self.instName,"acdtool.warn"))
        
        #Restore stuff
        shutil.copy(os.path.join(self.folder, self.instName, "postprocess.in.bak"),\
                    os.path.join(dataPath2, "VECTOR", "postprocess.in"))
        
        for f in movedFiles:
            shutil.move(os.path.join(oldFilesFolder,f), os.path.join(dataPath2,f))
        os.rmdir(oldFilesFolder)
        
        os.unlink(dataPath)
        
        #Save results
        self.exportResults.pushBack("Job", "complete")
        
        self.write()
        
    def clearLockdown(self):
        print "ModeFileRecalc::clearLockdown()"
        if not self.lockdown:
            return
        self.exportResults.clear()
        self.lockdown = False
        self.write()
    
    def write(self):
        self.__paramFile.dataDict.setValSingle("lockdown", str(self.lockdown))
        self.__paramFile.write()
    
    @staticmethod
    def createNew(folder,name):
        #Create a new folder to hold the stuff
        os.mkdir(os.path.join(folder,name))
        
        #Parameter file
        paramFile = AcdOptiFileParser_simple(os.path.join(folder,name,"paramFile.set"), "w")
        paramFile.dataDict.pushBack("fileID", "Analysis::ModeFileRecalc")
        paramFile.dataDict.pushBack("lockdown", "False")
        
        paramFile.dataDict.pushBack("export", DataDict())
        
        paramFile.dataDict.pushBack("settings", DataDict())
        paramFile.dataDict["settings"].pushBack("ResultDir","omega3p_results")
        
        paramFile.write()

class ModeFileRecalcException(AcdOptiException_analysis):
    pass
class ModeFileRecalcException_runAna(AcdOptiException_analysis_runAnalysis):
    pass