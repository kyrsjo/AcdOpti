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


from acdOpti.AcdOptiFileParser import DataDict

from acdOpti.AcdOptiExceptions import AcdOptiException_analysis_runAnalysis, AcdOptiException_dataDict_getValsSingle

import re
redigits = r'-*\d+.\d+e[+-]\d+'

class RFpostParser():
    """
    Class providing functions usefull for RFpost and RFpost_local,
    that parses the output from acdtool postprocess rf
    """
    
    def parseData(self, dataString, L=-1.0):
        #Split into sections by looking for [NAME]
        sectionNamesList = []
        sectionList = []

        sectionBuffer = []
        braceCounter = 0

        for line in dataString.splitlines():
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
        retDict = DataDict()
        retDict.pushBack("RoverQ", self.ParseRoverQ(sectionNamesList, sectionList,L))
        retDict.pushBack("maxFieldsOnSurface", self.ParseMaxFieldsOnSurface(sectionNamesList, sectionList,retDict,L)) #This depends on RoverQ's results, accessed through retDict
        
        return retDict

    def __findMySections(self,sectionNamesList,sectionList, mySectionName):
        "Helper func., returns a list of only the sections that match mySectionName"
        ret = []
        for i in xrange(len(sectionNamesList)):
            if sectionNamesList[i] == mySectionName:
                ret.append(sectionList[i])
        return ret
    
    def ParseRoverQ(self,sectionNamesList,sectionList,L=-1.0):
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
            ls = re.match(r'\s*(\d+)\s+('+redigits+")\s+\(\s*("+redigits+"),\s*(" + redigits + ")\s*\)\s*("+redigits+")\s*("+redigits+")",line)
            #ls = line.split()
            ldic.pushBack("ModeID", ls.group(1))
            ldic.pushBack("Frequency", ls.group(2))
            ldic.pushBack("Vr", ls.group(3))
            ldic.pushBack("Vi", ls.group(4))
            ldic.pushBack("Vabs", ls.group(5))
            ldic.pushBack("RoQ", ls.group(6))
            ldic.pushBack("RoQ_norm", str(float(ls.group(6))/L))
            retDict.pushBack("mode",ldic)
        
        return retDict
    
    def ParseMaxFieldsOnSurface(self,sectionNamesList,sectionList,retDataROQ=None,L=-1.0):
        """
        Parses 'maxFieldsOnSurface' sections, returns a DataDict with one entry (another dataDict) for each section found.
        Dependent on output from RoverQ analysis for normalization, which it searches for through "retData". Skipped if not found.
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
                
                if retDataROQ != None:
                    try:
                        RoQ = retDataROQ["RoverQ"]
                        Vabs = None
                        for mode in RoQ.getVals("mode"):
                            if int(mode["ModeID"]) == int(modID):
                                Vabs = float(mode["Vabs"])
                        if Vabs != None and L != -1.0:
                            Ez_ave = Vabs / (L/1000)
                            modDict.pushBack("Ez_ave", str(Ez_ave))
                            modDict.pushBack("Emax_norm", str(float(Emax)/Ez_ave))
                            modDict.pushBack("Hmax_norm", str(float(Hmax)/Ez_ave))
                        else:
                            print "Didn't find a good Vabs"
                    
                    except AcdOptiException_dataDict_getValsSingle:
                        print "No normalization found, skipping"
                
                secDict.pushBack("mode", modDict)
                
            retDict.pushBack("surf", secDict)
        
        return retDict

class RFpostException(AcdOptiException_analysis_runAnalysis):
    pass
