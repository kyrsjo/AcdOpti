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
from acdOpti.AcdOptiFileParser import DataDict, AcdOptiFileParser_simple
from acdOpti.AcdOptiExceptions import AcdOptiException

from acdOpti.AcdOptiSolverManager import AcdOptiSolverManager

import os

class RFpost_local(AnalysisInterface):
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
            raise RFpost_local_exception("Got fileID='" + self.__paramFile.dataDict["fileID"] + "'")
        self.lockdown = DataDict.boolconv(self.__paramFile.dataDict["lockdown"])

        self.exportResults = self.__paramFile.dataDict["export"]
    
        #Load RFpost solverManager
        self.localSolver = AcdOptiSolverManager("rfPost.in", os.path.join(folder,name))
    
    def runAnalysis(self):
        print "RFpost_local::runAnalysis()"
        #self.exportResults.setValSingle("result", "3.14")
        self.lockdown = True
        self.localSolver.lockdown = True
        self.write()
        
    def clearLockdown(self):
        print "RFpost_local::clearLockdown()"
        #self.exportResults.setValSingle("result", "")
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
        #paramFile.dataDict["export"].pushBack("result", "")
        paramFile.write()
    
class RFpost_local_exception(AcdOptiException):
        pass