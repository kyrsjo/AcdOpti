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

import os

class Dummy(AnalysisInterface):
    """
    Dummy analysis that doesn't actually do anything,
    used for testing the abstract machinery
    """
    __paramFile = None
    
    def __init__(self, folder, name, runConfig):
        print "Dummy::__init__()"
        self.type     = "Dummy"
        self.folder   = folder
        self.instName = name
        self.runConfig = runConfig
        
        
        self.__paramFile = AcdOptiFileParser_simple(os.path.join(folder, name), 'rw')
        if self.__paramFile.dataDict["fileID"] != "Analysis::Dummy":
            raise DummyException("Got fileID='" + self.__paramFile.dataDict["fileID"] + "'")
        self.lockdown = DataDict.boolconv(self.__paramFile.dataDict["lockdown"])

        self.exportResults = self.__paramFile.dataDict["export"]
    
    def runAnalysis(self):
        self.exportResults.setValSingle("result", "3.14")
        self.lockdown = True
        self.write()
        
    def clearLockdown(self):
        print "Dummy::clearLockdown()"
        self.exportResults.setValSingle("result", "")
        self.lockdown = False
        self.write()
    
    def write(self):
        self.__paramFile.dataDict.setValSingle("lockdown", str(self.lockdown))
        self.__paramFile.write()
    
    @staticmethod
    def createNew(folder,name=None):
        paramFile = AcdOptiFileParser_simple(os.path.join(folder,name), "w")
        paramFile.dataDict.pushBack("fileID", "Analysis::Dummy")
        paramFile.dataDict.pushBack("lockdown", "False")
        paramFile.dataDict.pushBack("export", DataDict())
        paramFile.dataDict["export"].pushBack("result", "")
        paramFile.write()
    
#    @staticmethod
#    def createNew_clone(folder,cloneFrom,newRunConfig):
#        newDummy = Dummy.createNew(folder, cloneFrom.name)
#        return Dummy(folder,cloneFrom.name,newRunConfig)

class DummyException(AcdOptiException):
        pass