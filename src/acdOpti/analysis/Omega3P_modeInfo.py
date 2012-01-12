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
from acdOpti.AcdOptiExceptions import AcdOptiException

import os

class Omega3P_modeInfo(AnalysisInterface):
    """
    Analysis that presents the information
    being output directly from Omega3P per mode 
    """
    __paramFile = None
    
    def __init__(self, folder, name, runConfig):
        print "Omega3P_modeInfo::__init__()"
        self.type      = "Omega3P_modeInfo"
        self.folder    = folder
        self.instName  = name
        self.runConfig = runConfig
        
        self.__paramFile = AcdOptiFileParser_simple(os.path.join(folder, name), 'rw')
        if self.__paramFile.dataDict["fileID"] != "Analysis::Omega3P_modeInfo":
            raise Omega3P_modeInfo_exception("Got fileID='" + self.__paramFile.dataDict["fileID"] + "'")
        self.lockdown = DataDict.boolconv(self.__paramFile.dataDict["lockdown"])

        self.exportResults = self.__paramFile.dataDict["export"]
    
        if "modes" in self.exportResults:
            #Convert to new format
            print "Converting to new format..."
            modes = self.exportResults["modes"].copy()
            self.exportResults.clear()
            for (k,v) in modes:
                self.exportResults.pushBack(k,v)
            self.write()
    
    def runAnalysis(self):
        finishedFolder = self.runConfig.finishedFolder
        if finishedFolder == None:
            raise Omega3P_modeInfo_exception("No data to analyze")
        
        if os.path.isdir(os.path.join(finishedFolder, "omega3p_results")):
            outputFilePath = os.path.join(finishedFolder, "omega3p_results", "omega3p.out")
        elif os.path.isfile(os.path.join(finishedFolder,"output")):
            outputFilePath = os.path.join(finishedFolder, "output")
        else:
            #self.exportResults.setValSingle("modes", "!!FILE_NOT_FOUND!!")
            raise Omega3P_modeInfo_exception("File '" + os.path.join(finishedFolder, "omega3p_results") + "' not found")
            
        outputFile = open(outputFilePath, "r")
        #Find the lines with KVC syntax
#        data = ""
#        lastLineWasComment = True
#        for line in outputFile.readlines():
#            ls = line.strip()
#            if ls.startswith("/*") and ls.endswith("*/"):
#                if lastLineWasComment:
#                    continue #comments at beginning
#                else:
#                    break #comments at end
#            #Not a comment line
#            data += line
#            lastLineWasComment = False
#        
        
        #Find the lines relating to mode (else the timestamps will crash the parser due to extra ":")
        thereYet=False
        data = ""
        for line in outputFile.readlines():
            ls = line.strip()
            if ls.startswith("Mode :"):
                thereYet = True
            elif not thereYet:
                continue
            elif ls.startswith("Mesh :") or ls.startswith("AMRLevel"):
                break
            data += line
        print data
        
        #Parse the data
        dataParser = AcdOptiFileParser_KVC(data,"s")
        
        for (modeName, mode) in dataParser.dataDict:
            #print mode
            if "," in mode["TotalEnergy"]:
                te = mode["TotalEnergy"]
                teSplit = te.split(",")
                mode.delItem("TotalEnergy")
                mode.pushBack("TotalEnergyReal", teSplit[0].strip())
                mode.pushBack("TotalEnergyImag", teSplit[1].strip())
            if "," in mode["Frequency"]:
                freq = mode["Frequency"]
                freqSplit = freq.split(",")
                mode.delItem("Frequency")
                mode.pushBack("FrequencyReal", freqSplit[0].strip())
                mode.pushBack("FrequencyImag", freqSplit[1].strip())
            self.exportResults.pushBack(modeName,mode.copy())
        
        self.lockdown = True
        self.write()
    def clearLockdown(self):
        self.exportResults.clear()
        self.lockdown = False
        self.write()
    
    def write(self):
        self.__paramFile.dataDict.setValSingle("lockdown", str(self.lockdown))
        self.__paramFile.write()
    
    @staticmethod
    def createNew(folder,name):
        paramFile = AcdOptiFileParser_simple(os.path.join(folder,name), "w")
        paramFile.dataDict.pushBack("fileID", "Analysis::Omega3P_modeInfo")
        paramFile.dataDict.pushBack("lockdown", "False")
        paramFile.dataDict.pushBack("export", DataDict())
        #paramFile.dataDict["export"].pushBack("modes", DataDict())
        paramFile.write()

class Omega3P_modeInfo_exception(AcdOptiException):
        pass