# -*- coding: utf8 -*-
#
# Copyright 2012 Kyrre Ness Sjøbæk
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

class Metadata(AnalysisInterface):
    """
    Dummy analysis that doesn't actually do anything,
    used for testing the abstract machinery of input data
    """
    __paramFile = None
    
    def __init__(self, folder, name, runConfig):
        print "Metadata::__init__()"
        self.type     = "Metadata"
        self.folder   = folder
        self.instName = name
        self.runConfig = runConfig
        
        
        self.__paramFile = AcdOptiFileParser_simple(os.path.join(folder, name), 'rw')
        if self.__paramFile.dataDict["fileID"] != "Analysis::Metadata":
            raise MetadataException("Got fileID='" + self.__paramFile.dataDict["fileID"] + "'")
        self.lockdown = DataDict.boolconv(self.__paramFile.dataDict["lockdown"])

        self.exportResults = self.__paramFile.dataDict["export"]

        self.settings = self.__paramFile.dataDict["settings"]
    
    def runAnalysis(self):
        converged = self.settings["Converged"]
        if not (converged == "True" or converged == "False"):
            raise MetadataException_runAna("Setting 'Converged' should be 'True' or 'False'")  
        self.exportResults.pushBack("Converged",converged)
        
        self.lockdown = True
        self.write()
        
    def clearLockdown(self):
        print "Metadata::clearLockdown()"
        self.exportResults.clear()
        self.lockdown = False
        self.write()
    
    def write(self):
        self.__paramFile.dataDict.setValSingle("lockdown", str(self.lockdown))
        self.__paramFile.write()
    
    @staticmethod
    def createNew(folder,name):
        paramFile = AcdOptiFileParser_simple(os.path.join(folder,name), "w")
        paramFile.dataDict.pushBack("fileID", "Analysis::Metadata")
        paramFile.dataDict.pushBack("lockdown", "False")
        paramFile.dataDict.pushBack("export", DataDict())
        paramFile.dataDict.pushBack("settings", DataDict())
        paramFile.dataDict["settings"].pushBack("Converged", "True")
        paramFile.write()
    
class MetadataException(AcdOptiException_analysis):
    pass
class MetadataException_runAna(AcdOptiException_analysis_runAnalysis):
    pass