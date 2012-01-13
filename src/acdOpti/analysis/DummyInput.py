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
from acdOpti.AcdOptiExceptions import AcdOptiException,\
                                      AcdOptiException_analysis,\
                                      AcdOptiException_analysis_runAnalysis

import os

class DummyInput(AnalysisInterface):
    """
    Dummy analysis that doesn't actually do anything,
    used for testing the abstract machinery of input data
    """
    __paramFile = None
    
    def __init__(self, folder, name, runConfig):
        print "DummyInput::__init__()"
        self.type     = "DummyInput"
        self.folder   = folder
        self.instName = name
        self.runConfig = runConfig
        
        
        self.__paramFile = AcdOptiFileParser_simple(os.path.join(folder, name), 'rw')
        if self.__paramFile.dataDict["fileID"] != "Analysis::DummyInput":
            raise DummyInputException("Got fileID='" + self.__paramFile.dataDict["fileID"] + "'")
        self.lockdown = DataDict.boolconv(self.__paramFile.dataDict["lockdown"])

        self.exportResults = self.__paramFile.dataDict["export"]

        self.settings = self.__paramFile.dataDict["settings"]
    
    def runAnalysis(self):
        try:
            N = int(self.settings["N"])
        except ValueError:
            #Could raise an exception here, choose not to
            N = 0
        
        self.exportResults.setValSingle("result", "3.14")
        self.exportResults.setValSingle("Nparrot", str(N))
        self.exportResults.setValSingle("Npi", str(3.14*N))
        
        self.lockdown = True
        self.write()
        
    def clearLockdown(self):
        print "DummyInput::clearLockdown()"
        self.exportResults.setValSingle("result", "")
        self.lockdown = False
        self.write()
    
    def write(self):
        self.__paramFile.dataDict.setValSingle("lockdown", str(self.lockdown))
        self.__paramFile.write()
    
    @staticmethod
    def createNew(folder,name):
        paramFile = AcdOptiFileParser_simple(os.path.join(folder,name), "w")
        paramFile.dataDict.pushBack("fileID", "Analysis::DummyInput")
        paramFile.dataDict.pushBack("lockdown", "False")
        paramFile.dataDict.pushBack("export", DataDict())
        paramFile.dataDict["export"].pushBack("result", "")
        paramFile.dataDict["export"].pushBack("Nparrot", "")
        paramFile.dataDict["export"].pushBack("Npi", "")
        paramFile.dataDict.pushBack("settings", DataDict())
        paramFile.dataDict["settings"].pushBack("N", "")
        paramFile.write()
    
#    @staticmethod
#    def createNew_clone(folder,cloneFrom,newRunConfig):
#        newDummy = Dummy.createNew(folder, cloneFrom.name)
#        return Dummy(folder,cloneFrom.name,newRunConfig)

class DummyInputException(AcdOptiException_analysis):
    pass
class DummyInputException_runAna(AcdOptiException_analysis_runAnalysis):
    pass