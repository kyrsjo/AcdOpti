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
from RFpostParser import RFpostParser, RFpostException
from acdOpti.AcdOptiFileParser import DataDict, AcdOptiFileParser_simple
from acdOpti.AcdOptiExceptions import AcdOptiException_dataDict_getValsSingle,\
                                      AcdOptiException_analysis_runAnalysis

import os
from acdOpti.analysis.RFpostParser import RFpostException_runAna

class RFpost(AnalysisInterface, RFpostParser):
    """
    Parses rfpost output files
    """
    __paramFile = None
    fname = None
    
    def __init__(self, folder, name, runConfig):
        print "RFpost::__init__()"
        self.type     = "RFpost"
        self.folder   = folder
        self.instName = name
        self.runConfig = runConfig
        
        
        self.__paramFile = AcdOptiFileParser_simple(os.path.join(folder, name), 'rw')
        if self.__paramFile.dataDict["fileID"] != "Analysis::RFpost":
            raise RFpostException("Got fileID='" + self.__paramFile.dataDict["fileID"] + "'")
        self.lockdown = DataDict.boolconv(self.__paramFile.dataDict["lockdown"])

        self.exportResults = self.__paramFile.dataDict["export"]

        self.settings = self.__paramFile.dataDict["settings"]
    
    def runAnalysis(self):
        if self.settings["RFpost_LogFileName"] == "":
            raise RFpostException_runAna("Input file not set")
        self.fname = fname = os.path.join(self.runConfig.finishedFolder, self.settings["RFpost_LogFileName"])
        if not os.path.isfile(fname):
            raise RFpostException_runAna("Could not find input file '" + fname + "'")
        
        ifile = open(fname, 'r')
        fileData = ifile.read()
        ifile.close()
        
        addDic = self.parseData(fileData)
        for (k,v) in addDic:
            self.exportResults.pushBack(k,v)

        self.lockdown = True
        self.write()
    
    def clearLockdown(self):
        print "RFpost::clearLockdown()"
        self.exportResults.clear()
        self.lockdown = False
        self.fname = None
        self.write()
    
    def write(self):
        self.__paramFile.dataDict.setValSingle("lockdown", str(self.lockdown))
        self.__paramFile.write()
    
    @staticmethod
    def createNew(folder,name):
        paramFile = AcdOptiFileParser_simple(os.path.join(folder,name), "w")
        paramFile.dataDict.pushBack("fileID", "Analysis::RFpost")
        paramFile.dataDict.pushBack("lockdown", "False")
        paramFile.dataDict.pushBack("export", DataDict())
        paramFile.dataDict.pushBack("settings", DataDict())
        paramFile.dataDict["settings"].pushBack("RFpost_LogFileName", "acdtool.log")
        paramFile.write()
    