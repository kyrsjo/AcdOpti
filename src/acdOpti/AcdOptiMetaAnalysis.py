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


from AcdOptiFileParser import AcdOptiFileParser_simple, DataDict
from AcdOptiExceptions import AcdOptiException_metaAnalysis_createFail,\
                              AcdOptiException_metaAnalysis_loadFail,\
                              AcdOptiException_metaAnalysis_anaFail

import os
import re

import numpy as np


class AcdOptiMetaAnalysis:
    """
    A meta-analysis is an analysis of several other anlysis;
    i.e. "plotting" the exported output from analysis
    or geometry/mesh variables against each other.
    """
    
    instName    = None
    
    folder      = None
    collection  = None
    
    __paramfile = None
    
    #Encodings describing where to get the x- or y variables.
    # Meta-language syntax: {GEOM|MESH|ANA}.key.key([idx]) .... For ANA, field[1] is analysis name, field[2] is a name in exportResults
    xVariable = None 
    yVariable = None
    
    fVariable = None
    fEquals   = None
    fLT       = None
    fGT       = None
    
    xArray = None 
    yArray = None
    
    targetValue = None
    
    lockdown = None
    
    def __init__(self,folder,collection):
        self.folder = folder
        self.collection = collection
    
        #Construct the instance name from folder
        instName = folder
        if instName[-1] == "/":
            instName = instName[0:-1]
        self.instName = instName = os.path.split(instName)[1]
    
        #Load paramFile
        self.__paramfile = AcdOptiFileParser_simple(os.path.join(folder, "paramFile.set"), 'rw')
        if self.__paramfile.dataDict["fileID"] != "AcdOptiMetaAnalysis":
            raise AcdOptiException_metaAnalysis_loadFail("Got wrong fileID='" + self.__paramfile.dataDict["fileID"] + "'")            
        
        if self.__paramfile.dataDict.getValSingle("instName") != self.instName:
            raise AcdOptiException_metaAnalysis_loadFail("instName doesn't match folder name")
        
        self.lockdown = DataDict.boolconv(self.__paramfile.dataDict.getValSingle("lockdown"))
        
        self.xVariable = self.__paramfile.dataDict["xVariable"]
        self.yVariable = self.__paramfile.dataDict["yVariable"]
        
        if len(self.__paramfile.dataDict.getVals("fVariable")) == 0:
            self.__paramfile.dataDict.pushBack("fVariable", "")
            self.__paramfile.dataDict.pushBack("fEquals", "")
            self.__paramfile.dataDict.pushBack("fLT", "")
            self.__paramfile.dataDict.pushBack("fGT", "")
            self.__paramfile.write()
        self.fVariable = self.__paramfile.dataDict["fVariable"]
        def floatOrNone(strIn):
            if strIn == "":
                return None
            else:
                return float(strIn)
        self.fEquals   = floatOrNone(self.__paramfile.dataDict["fEquals"])
        self.fGT       = floatOrNone(self.__paramfile.dataDict["fGT"])
        self.fLT       = floatOrNone(self.__paramfile.dataDict["fLT"])
        
        if len(self.__paramfile.dataDict.getVals("targetValue")) > 0:
            self.targetValue = float(self.__paramfile.dataDict["targetValue"])
        else:
            self.targetValue = None    
        
        anaData = self.__paramfile.dataDict["anaData"]
        self.xArray = []
        self.yArray = []
        for (x,y) in anaData: 
            self.xArray.append(float(x))
            self.yArray.append(float(y))
        
        #Final init & lockdown checks
        if self.lockdown == True:
            if self.yVariable == None or self.xVariable == None:
                #The x,yArray may still be empty, don't check for this
                raise AcdOptiException_metaAnalysis_loadFail("Lockdown, but xVariable='" + self.xVariable + "', yVariable='" + self.yVariable)
            self.xArray = np.asarray(self.xArray)
            self.yArray = np.asarray(self.yArray)
        
    def write(self):
        print "AcdOptiMetaAnalysis::write()"

        self.__paramfile.dataDict.setValSingle("lockdown", str(self.lockdown))
        
        self.__paramfile.dataDict.setValSingle("xVariable", self.xVariable)
        self.__paramfile.dataDict.setValSingle("yVariable", self.yVariable)
        
        self.__paramfile.dataDict.setValSingle("fVariable", self.fVariable)
        def strFromFloatOrNone(fonIn):
            if fonIn == None:
                return ""
            else:
                return str(fonIn)
        self.__paramfile.dataDict.setValSingle("fEquals",strFromFloatOrNone(self.fEquals))
        self.__paramfile.dataDict.setValSingle("fGT",strFromFloatOrNone(self.fGT))
        self.__paramfile.dataDict.setValSingle("fLT",strFromFloatOrNone(self.fLT))
        
        if self.targetValue != None:
            if len(self.__paramfile.dataDict.getVals("targetValue")) > 0:
                self.__paramfile.dataDict.setValSingle("targetValue", str(self.targetValue))
            else:
                self.__paramfile.dataDict.pushBack("targetValue", str(self.targetValue))
        else:
            if len(self.__paramfile.dataDict.getVals("targetValue")) > 0:
                self.__paramfile.dataDict.delItem("targetValue")
        
        anaData = self.__paramfile.dataDict["anaData"]
        anaData.clear()
    
        for (x,y) in zip (self.xArray, self.yArray):
            anaData.pushBack(str(x), str(y))
    
        self.__paramfile.write()
        
    def runAnalysis(self):
        print "AcdOptiMetaAnalysis::runAnalysis()"
        assert self.lockdown == False
        #Do something...
        xVar = self.xVariable.split(".")
        yVar = self.yVariable.split(".")
        if self.fEquals != None:
            fVar = self.fVariable.split(".")
        print "AcdOptiMetaAnalysis::runAnalysis() : xVar='" + str(xVar) + "', yVar='" + str(yVar) + "'"
        
#        if not xVar[0] in ["GEOM","MESH","ANA"]:
#            raise AcdOptiException_metaAnalysis_anaFail("xVar[0] invalid")
#        if not yVar[0] in ["GEOM","MESH","ANA"]:
#            raise AcdOptiException_metaAnalysis_anaFail("yVar[0] invalid")
#        
        for geom in self.collection.project.geomCollection.geomInstances.values():
            xData = self.__getData(geom, xVar)
            yData = self.__getData(geom, yVar)
            if len(xData) > 1 and len(yData) > 1:
                raise AcdOptiException_metaAnalysis_anaFail("Multiple hits for both xData and yData")
            
            if self.fEquals != None:
                fData = self.__getData(geom, fVar)
                if len(xData) > 1 or len(yData) > 1 or len(fData) > 1:
                    raise AcdOptiException_metaAnalysis_anaFail("Multiple hits when filtering")
                if fData[0] != self.fEquals:
                    continue

            print xData, yData
            
            if len(xData) > 1:
                for x in xData:
                    self.xArray.append(x)
                    self.yArray.append(yData[0])
            elif len(yData) > 1:
                for y in yData:
                    self.xArray.append(xData[0])
                    self.yArray.append(y)
            elif len(xData) == 1 and len(yData) == 1:
                self.xArray.append(xData[0])
                self.yArray.append(yData[0])
            elif len(xData) == 0 or len(yData) == 0:
                continue
            else:
                raise AcdOptiException_metaAnalysis_anaFail("This shouldn't happen?!")
            
        #Icing on the top..
        assert len(self.xArray) == len(self.yArray)
        self.xArray = np.asarray(self.xArray)
        self.yArray = np.asarray(self.yArray)
        print self.xArray, self.yArray
        self.lockdown = True
        #self.write()
    
    def __getData(self,geom,descriptor):
        ret = []
        if descriptor[0] == "GEOM":
            if len(descriptor) > 2:
                raise AcdOptiException_metaAnalysis_anaFail("Descriptor '" + str(descriptor) + "' starting with 'GEOM' too long")
            if descriptor[1] in geom.templateOverrides_getKeys():
                ret.append(float(geom.templateOverrides_get(descriptor[1])))
            elif descriptor[1] in geom.template.paramDefaults_getKeys():
                ret.append(float(geom.template.paramDefaults_get(descriptor[1])))
            else:
                raise AcdOptiException_metaAnalysis_anaFail("Geometry field ID '" + str(descriptor[1]) + "' not found")
            
        elif descriptor[0] == "MESH":
            if len(descriptor) > 2:
                raise AcdOptiException_metaAnalysis_anaFail("Descriptor '" + str(descriptor) + "' starting with 'MESH' too long")
            
            for mesh in geom.meshInsts.values():
                if descriptor[1] in mesh.templateOverrides_getKeys():
                    ret.append(float(mesh.templateOverrides_get(descriptor[1])))
                elif descriptor[1] in mesh.meshTemplate.paramDefaults_getKeys():
                    ret.append(float(mesh.meshTemplate.paramDefaults_get(descriptor[1])))
                else:
                    raise AcdOptiException_metaAnalysis_anaFail("Mesh field ID '" + str(descriptor[1]) + "' not found")
        elif descriptor[0] == "ANA":
            for mesh in geom.meshInsts.values():
                for rc in mesh.runConfigs.values():
                    #Get the ana
                    try:
                        ana = rc.analysis[descriptor[1]]
                    except KeyError:
                        continue
                    #Dig down into the exportResults
                    results = ana.exportResults
                    if len(descriptor) < 3:
                        raise AcdOptiException_metaAnalysis_anaFail("ANA descriptor '" + str(descriptor) + "' too short, doesn't specify field")
                    ret += self.__anaExportDigger(results, descriptor[2:])                    
        else:
            raise AcdOptiException_metaAnalysis_anaFail("Unknown descriptor[0]: '" + str(descriptor[0]) + "'")

        return ret
    
    def __anaExportDigger(self, exported, descriptor):
        print "AcdOptiMetaAnalysis::__anaExportDigger() : descriptor='" + str(descriptor) + "', exported='" + str(exported) + "'"
        ret = []
        
        numberMatch = re.match("\w*\[([0-9]+)\]\Z",descriptor[0])
        data = None
        if numberMatch:
            #next descriptor has an index
            idx = int(numberMatch.group(1))
            fetch = exported.getVals(descriptor[0].split("[")[0])
            try:
                data = [fetch[idx], ] #Put in a list to make loop work
            except IndexError:
                print "AcdOptiMetaAnalysis::__anaExportDigger() : WARNING - index not found!"
                data = [] #If the 
        else:
            data = exported.getVals(descriptor[0])

        for val in data:
            if type(val) == str:
                if len(descriptor) > 1:
                    raise AcdOptiException_metaAnalysis_anaFail("Got deeper descriptors than data")
                ret.append(val)
            else: #DataDict
                if len(descriptor) == 1:
                    raise AcdOptiException_metaAnalysis_anaFail("Got deeper data than descriptors")
                ret += self.__anaExportDigger(val, descriptor[1:])
#            if isinstance(val, DataDict):
#                if not isMore:
#                    raise AcdOptiException_metaAnalysis_anaFail("Got deeper data than descriptors")
#                ret += self.__anaExportDigger(val, descriptor[1:])
#            else:
#                if isMore:
#                    raise AcdOptiException_metaAnalysis_anaFail("Got deeper descriptors than data")
#                ret.append(val)
        return ret
    
    def clearLockdown(self):
        print "AcdOptiMetaAnalysis::clearLockdown()"
        assert self.lockdown == True
        
        self.xArray = []
        self.yArray = []
        self.lockdown = False
    
    def exportData(self, fileName):
        print "AcdOptiMetaAnalysis::exportData()"
        assert self.lockdown == True

    
    @staticmethod
    def createNew(folder):
        #Construct the instance name from folder
        instName = folder
        if instName[-1] == "/":
            instName = instName[0:-1]
        instName = os.path.split(instName)[1]
        if os.path.isdir(folder):
            raise AcdOptiException_metaAnalysis_createFail("Folder \"" + folder + "\" already exists")
        os.mkdir(folder)
        
        #Create paramfile
        paramFile = AcdOptiFileParser_simple(os.path.join(folder, "paramFile.set"), 'w')
        paramFile.dataDict.pushBack("fileID", "AcdOptiMetaAnalysis")
        paramFile.dataDict.pushBack("instName", instName)
        
        paramFile.dataDict.pushBack("xVariable", "")
        paramFile.dataDict.pushBack("yVariable", "")
        
        paramFile.dataDict.pushBack("fVariable", "")
        paramFile.dataDict.pushBack("fEquals", "")
        paramFile.dataDict.pushBack("fLT", "")
        paramFile.dataDict.pushBack("fGT", "")
        
        paramFile.dataDict.pushBack("anaData", DataDict()) #(key, value) = (x,y)
        
        paramFile.dataDict.pushBack("lockdown", "False")
        
        paramFile.write()