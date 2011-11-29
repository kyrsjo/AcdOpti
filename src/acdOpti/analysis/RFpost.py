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
from acdOpti.AcdOptiExceptions import AcdOptiException_dataDict_getValsSingle,\
                                      AcdOptiException_analysis_runAnalysis

import os
import re

class RFpost(AnalysisInterface):
    """
    Dummy analysis that doesn't actually do anything,
    used for testing the abstract machinery of input data
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
            raise RFpostException("Input file not set")
        self.fname = fname = os.path.join(self.runConfig.finishedFolder, self.settings["RFpost_LogFileName"])
        if not os.path.isfile(fname):
            raise RFpostException("Could not find input file '" + fname + "'")
        
        ifile = open(fname, 'r')
        fileData = ifile.read()
        ifile.close()
        
        #Split into sections by looking for [NAME]
        sectionNamesList = []
        sectionList = []

        sectionBuffer = []
        braceCounter = 0

        for line in fileData.splitlines():
            #Look for new sections
            if len(sectionNamesList) == len(sectionList):
                mobj = re.match(r"\[(\w*)\]",line)
                if mobj:
                    sectionNamesList.append(mobj.group(1))
            #Scan to the end of section
            else:
                if line.strip().startswith("{"):
                    braceCounter += 1
                elif line.strip().startswith("}"):
                    braceCounter -=1
                sectionBuffer.append(line)
                if braceCounter == 0:
                    #Reached end of a section
                    sectionList.append(sectionBuffer)
                    sectionBuffer = []
        assert len(sectionNamesList) == len(sectionList)
        
        #Filter through sections to find the interesting results
        self.exportResults.pushBack("RoverQ", self.__ParseRoverQ(sectionNamesList, sectionList))
        self.exportResults.pushBack("maxFieldsOnSurface", self.__ParseMaxFieldsOnSurface(sectionNamesList, sectionList)) #This depends on RoverQ!
#        
#        self.exportResults.setValSingle("Nparrot", str(N))
#        self.exportResults.setValSingle("Npi", str(3.14*N))
#        
        self.lockdown = True
        self.write()
    
    def __findMySections(self,sectionNamesList,sectionList, mySectionName):
        "Helper func., returns a list of only the sections that match mySectionName"
        ret = []
        for i in xrange(len(sectionNamesList)):
            if sectionNamesList[i] == mySectionName:
                ret.append(sectionList[i])
        return ret
    
    def __ParseRoverQ(self,sectionNamesList,sectionList):
        "Parses RoverQ sections, returns a DataDict. Assumes there to be only one RoverQ."
        RoQsec =  self.__findMySections(sectionNamesList, sectionList, "RoverQ")
        if len(RoQsec) == 0:
            return(DataDict())
        elif len(RoQsec) > 1:
            raise RFpostException("More than one RoverQ section encountered in input file '" + self.fname + "'")
        RoQsec = RoQsec[0]
        
        loi = [] #Lines of interest
        trigger = False
        for line in RoQsec:
            if trigger:
                #We are capturing!
                if line.strip() == "}":
                    break
                loi.append(line)
            else:
                #Ready for trigger
                if line.strip().startswith("ModeID"):
                    trigger = True
        
        #Parse line-for-line
        retDict = DataDict()
        for line in loi:
            ldic = DataDict()
            ls = line.split()
            ldic.pushBack("ModeID", ls[0])
            ldic.pushBack("Frequency", ls[1])
            ldic.pushBack("Vr", ls[2][1:])
            ldic.pushBack("Vi", ls[3][:-1])
            ldic.pushBack("Vabs", ls[4])
            ldic.pushBack("RoQ", ls[5])
            retDict.pushBack("mode",ldic)
        
        return retDict
    
    def __ParseMaxFieldsOnSurface(self,sectionNamesList,sectionList):
        """
        Parses 'maxFieldsOnSurface' sections, returns a DataDict with one entry (another dataDict) for each section found.
        Dependent on output from RoverQ analysis for normalization (if not found, this is just skipped)
        """
        mfosSec =  self.__findMySections(sectionNamesList, sectionList, "maxFieldsOnSurface")
        
        retDict = DataDict()
        
        print mfosSec
        
        for sec in mfosSec:
            secDict = DataDict()
            surfID_match = re.match("surfaceID :[ ]*([0-9]*)", sec[1].strip())
            print  sec[1].strip(), surfID_match.groups()
            surfID = surfID_match.group(1)
            secDict.pushBack("surfaceID", surfID)
            for i in xrange(2,len(sec)-1,3):
                print "*****", i, sec[i], sec[i+1], sec[i+2]
                modDict = DataDict()
    
                modID_match = re.match("ModeID :[ ]*([0-9]*)", sec[i].strip())
                modID = modID_match.group(1)
                modDict.pushBack("modeID", modID)
                
                Emax_match = re.match(r"Emax :[ ]*([0-9]*\.[0-9]*e\+[0-9]*)",sec[i+1].strip())
                Emax = Emax_match.group(1)
                modDict.pushBack("Emax", Emax)
                
                Hmax_match = re.match(r"Hmax :[ ]*([0-9]*\.[0-9]*e\+[0-9]*)",sec[i+2].strip())
                Hmax = Hmax_match.group(1)
                modDict.pushBack("Hmax", Hmax)
                
                try:
                    RoQ = self.exportResults["RoverQ"]
                    Vabs = None
                    for mode in RoQ.getVals("mode"):
                        if int(mode["ModeID"]) == int(modID):
                            Vabs = float(mode["Vabs"])
                    if Vabs != None:
                        modDict.pushBack("Emax_norm", str(float(Emax)/Vabs))
                        modDict.pushBack("Hmax_norm", str(float(Hmax)/Vabs))
                    else:
                        print "Didn't find a good Vabs"
                    
                except AcdOptiException_dataDict_getValsSingle:
                    print "No normalization found, skipping"
                
                    
                
                secDict.pushBack("mode", modDict)
                
            retDict.pushBack("surf", secDict)
        
        return retDict
             
    
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
    
class RFpostException(AcdOptiException_analysis_runAnalysis):
        pass