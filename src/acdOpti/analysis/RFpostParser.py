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

from acdOpti.AcdOptiExceptions import AcdOptiException_analysis,\
                                      AcdOptiException_analysis_runAnalysis,\
                                      AcdOptiException_dataDict_getValsSingle

import re
redigits = r'-?\d+.\d+e[+-]\d+'

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
        retDict.pushBack("maxFieldsOnSurface", self.ParseMaxFieldsOnSurface(sectionNamesList, sectionList,retDict)) #This depends on RoverQ's results, accessed through retDict
        retDict.pushBack("powerThroughSurface", self.ParsePowerThorughSurface(sectionNamesList, sectionList))
        retDict.pushBack("fieldSurfPlaneIntersect", self.ParseFieldSurfPlaneIntersect(sectionNamesList, sectionList, retDict)) #Depends on RoverQ
        
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
            raise RFpostException_runAna("More than one RoverQ section encountered in input file '" + self.fname + "'")
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
            ldic.pushBack("Frequency", ls.group(2)) #Hz
            ldic.pushBack("Vr", ls.group(3))
            ldic.pushBack("Vi", ls.group(4))
            ldic.pushBack("Vabs", ls.group(5)) #V
            if L != -1.0:
                ldic.pushBack("Ez_ave", str(float(ldic["Vabs"])/(L/1000.0)))  #V/m
            ldic.pushBack("RoQ", ls.group(6))
            if L != -1.0:
                ldic.pushBack("RoQ_norm", str(float(ls.group(6))/L)) #Ohm/mm (weird unit, but changing would mean data containing two versions :/)
            retDict.pushBack("mode",ldic)
        
        return retDict
    
    def ParseMaxFieldsOnSurface(self,sectionNamesList,sectionList,retDataROQ=None):
        """
        Parses 'maxFieldsOnSurface' sections, returns a DataDict with one entry (another dataDict) for each section found.
        Dependent on output from RoverQ analysis for normalization, which it searches for through "retData". Skipped if not found.
        """
        mfosSec =  self.__findMySections(sectionNamesList, sectionList, "maxFieldsOnSurface")
        
        retDict = DataDict()
        
        #print mfosSec
        
        for sec in mfosSec:
            secDict = DataDict()
            surfID_match = re.match("surfaceID :[ ]*([0-9]*)", sec[1].strip())
            #print  sec[1].strip(), surfID_match.groups()
            surfID = surfID_match.group(1)
            secDict.pushBack("surfaceID", surfID)
            print "sec=", sec
            for i in xrange(2,len(sec)-1,4):
                #print "*****", i, sec[i], sec[i+1], sec[i+2]
                modDict = DataDict()
    
                print "sec[" + str(i) + "] = '" + sec[i] + "'"
                modID_match = re.match("ModeID :[ ]*([0-9]*)", sec[i].strip())
                modID = modID_match.group(1)
                modDict.pushBack("modeID", modID)
                
                Emax_match = re.match(r"Emax :[ ]*([0-9]*\.[0-9]*e\+[0-9]*)",sec[i+1].strip())
                Emax = Emax_match.group(1)
                modDict.pushBack("Emax", Emax)
                
                Hmax_match = re.match(r"Hmax :[ ]*([0-9]*\.[0-9]*e\+[0-9]*)",sec[i+2].strip())
                Hmax = Hmax_match.group(1)
                modDict.pushBack("Hmax", Hmax)
                
                SCmax_match = re.match(r"SCmax :[ ]*([0-9]*\.[0-9]*e\+[0-9]*)",sec[i+3].strip())
                SCmax = SCmax_match.group(1)
                modDict.pushBack("SCmax", SCmax)
                
                if retDataROQ != None:
                    try:
                        RoQ = retDataROQ["RoverQ"]
                        Ez_ave = None
                        for mode in RoQ.getVals("mode"):
                            if int(mode["ModeID"]) == int(modID):
                                assert Ez_ave == None
                                Ez_ave = float(mode["Ez_ave"])
                        if Ez_ave != None:
                            modDict.pushBack("Ez_ave", str(Ez_ave))
                            modDict.pushBack("Emax_norm", str(float(Emax)/Ez_ave))
                            modDict.pushBack("Hmax_norm", str(float(Hmax)/Ez_ave))
                            modDict.pushBack("SCmax_norm", str(float(SCmax)/Ez_ave/Ez_ave))
                        else:
                            print "Didn't find Ez_ave"
                    
                    except AcdOptiException_dataDict_getValsSingle:
                        print "No normalization found, skipping"
                
                secDict.pushBack("mode", modDict)
                
            retDict.pushBack("surf", secDict)
        
        return retDict

    def ParsePowerThorughSurface(self,sectionNamesList,sectionList):
        """
        Parses 'powerThroughSurface' sections, returns a DataDict with one entry (another dataDict) for each section found.
        """
        ptsSects =  self.__findMySections(sectionNamesList, sectionList, "powerThroughSurface")
        
        retDict = DataDict()
                
        for sec in ptsSects:
            secDict = DataDict()
            secDict.pushBack("surfaceID", re.match(r"surfaceID\s*:\s*(\d+)",sec[1].strip()).group(1))
            secDict.pushBack("ModeID", re.match(r"ModeID\s*:\s*(\d+)",sec[2].strip()).group(1))
            
            pow = re.match(r"Power\s*:\s*\(\s*("+redigits+r"),\s*("+redigits+r")\s*\)\s*\(W\)", sec[3].strip())
            secDict.pushBack("Power_real", pow.group(1))
            secDict.pushBack("Power_imag", pow.group(2))
            
            retDict.pushBack("surf", secDict)
        
        return retDict
    
    def ParseFieldSurfPlaneIntersect(self,sectionNamesList,sectionList, retDataROQ=None):
        """
        Parses 'fieldSurfPlaneIntersect' sections, returns a DataDict with one entry (another dataDict) for each section found.
        Dependent on output from RoverQ analysis for normalization, which it searches for through "retData". Skipped if not found.
        """
        
        ptsSects =  self.__findMySections(sectionNamesList, sectionList, "fieldSurfPlaneIntersect")

        retDict = DataDict()
        
        for sec in ptsSects:
            secDict = DataDict()
            
            #secDict.pushBack("filename", re.match(r"filename\s*:\s*("))
            secDict.pushBack("surfaceID", re.match(r"surfaceID\s*:\s*(\d+)",sec[2].strip()).group(1))
            modID = re.match(r"ModeID\s*:\s*(\d+)",sec[3].strip()).group(1); secDict.pushBack("ModeID", modID)
            secDict.pushBack("z0", re.match(r"z0\s*:\s*("+redigits+")",sec[4].strip()).group(1))
            
            Ematch = re.match(r"Emax\s*:\s*(" + redigits + r")\s*\[V/m\]\s*at\s*\(\s*(" + redigits + ")\s*,\s*(" + redigits + r")\s*,\s*(" + redigits + ")\s*\)",sec[5].strip())
            Emax = Ematch.group(1); secDict.pushBack("Emax", Emax)
            Bmatch = re.match(r"Bmax\s*:\s*(" + redigits + r")\s*\[T\]\s*=\s*(" + redigits + r")\s*\[A/m\]\s*at\s*\(\s*(" + redigits + ")\s*,\s*(" + redigits + r")\s*,\s*(" + redigits + ")\s*\)",sec[6].strip())
            Bmax = Bmatch.group(1); secDict.pushBack("Bmax", Bmax)
            Hmax = Bmatch.group(2); secDict.pushBack("Hmax", Hmax)
            
            if retDataROQ != None:
                try:
                    RoQ = retDataROQ["RoverQ"]
                    Ez_ave = None
                    for mode in RoQ.getVals("mode"):
                        if int(mode["ModeID"]) == int(modID):
                            assert Ez_ave == None
                            Ez_ave = float(mode["Ez_ave"])
                    if Ez_ave != None:
                        secDict.pushBack("Ez_ave", str(Ez_ave))
                        secDict.pushBack("Emax_norm", str(float(Emax)/Ez_ave))
                        secDict.pushBack("Bmax_norm", str(float(Bmax)/Ez_ave))
                        secDict.pushBack("Hmax_norm", str(float(Hmax)/Ez_ave))
                    else:
                        print "Didn't find Ez_ave"
                    
                except AcdOptiException_dataDict_getValsSingle:
                    print "No normalization found, skipping"
                
            
            retDict.pushBack("surf", secDict)
            
        return retDict
        
class RFpostException(AcdOptiException_analysis):
    pass
class RFpostException_runAna(AcdOptiException_analysis_runAnalysis):
    pass