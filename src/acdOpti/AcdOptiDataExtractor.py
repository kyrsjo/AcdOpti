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
from AcdOptiDataExtractorFilter import AcdOptiDataExtractorFilter
from acdOpti.AcdOptiExceptions import AcdOptiException_dataExtractor_createFail,\
                                      AcdOptiException_dataExtractor_loadFail

import os

class AcdOptiDataExtractor:
    """
    This class extracts data from analysis, geoms etc.
    This is presented in a FLAT table.
    """

    instName = None    
    folder = None
    collection = None
    __paramfile = None
    
    
    dataExtracted = None
    keyNames = None
    filters = None
    
    lockdown = None
    
    def __init__(self, folder, collection):
        self.folder = folder
        self.collection = collection
    
        #Construct the instance name from folder
        instName = folder
        if instName[-1] == "/":
            instName = instName[0:-1]
        self.instName = instName = os.path.split(instName)[1]
    
        #Load paramFile
        self.__paramfile = AcdOptiFileParser_simple(os.path.join(folder, "paramFile.set"), 'rw')
        if self.__paramfile.dataDict["fileID"] != "AcdOptiDataExtractor":
            raise AcdOptiException_dataExtractor_loadFail("Got wrong fileID='" + self.__paramfile.dataDict["fileID"] + "'")            
        
        if self.__paramfile.dataDict.getValSingle("instName") != self.instName:
            raise AcdOptiException_dataExtractor_loadFail("instName doesn't match folder name")
        
        self.lockdown = DataDict.boolconv(self.__paramfile.dataDict.getValSingle("lockdown"))
    
        #Parse keyNames
        self.keyNames = []
        for (k,v) in self.__paramfile.dataDict["keyNames"]:
            assert k == "keyName"
            self.keyNames.append(v)
    
        #Parse extractedData
        self.dataExtracted = []
        for (k,v) in self.__paramfile.dataDict["extractedData"]:
            assert k == "dataPoint"
            assert isinstance(v,DataDict)
            pb = {}
            for (k,v) in v:
                pb[k] = v
                if not k in self.keyNames:
                    raise AcdOptiException_dataExtractor_loadFail("Key name '" + k + "' not found in self.keyNames")
            self.dataExtracted.append(pb)
        
        #Find, load, and attach filters 
        self.filters = []
        for (k,v) in self.__paramfile.dataDict["filters"]:
            self.filters.append(AcdOptiDataExtractorFilter.getFilterClass(k,v))
        
            
    def runExtractor(self):
        assert self.lockdown == False
        #self.dataExtracted = []
        #self.keyNames = []
        
        #Reset filter counters
        for f in self.filters:
            f.numFiltered = 0
        
        self.keyNames.append("META.GeomInstName")
        self.keyNames.append("META.ScanInstNames")
        self.keyNames.append("META.MeshInstName")
        self.keyNames.append("META.rcInstName")
        
        #Run Loop over all runconfigs and for each extract one row in the table
        geomCollection = self.collection.project.geomCollection
        for geom in geomCollection.geomInstances.itervalues():
            geomData = {}

            geomData["META.GeomInstName"] = geom.instName
            if len(geom.scanInstances) > 0:
                siString = ""
                for si in geom.scanInstances:
                    siString += si.instName + " "
                geomData["META.ScanInstNames"] = siString[:-1]
                
            geomOverrideList = geom.templateOverrides_getKeys()
            for key in geomCollection.paramDefaults_getKeys():
                geomKey = "GEOM."+key
                if key in geomOverrideList:
                    geomData[geomKey] = geom.templateOverrides_get(key)
                else:
                    geomData[geomKey] = geomCollection.paramDefaults_get(key)
                if not geomKey in self.keyNames:
                    self.keyNames.append(geomKey)
            
            for mesh in geom.meshInsts.itervalues():
                meshData = {}
                
                meshData["META.MeshInstName"] = mesh.instName

                meshOverrideList = mesh.templateOverrides_getKeys()
                for key in mesh.meshTemplate.paramDefaults_getKeys():
                    meshKey = "MESH." + mesh.meshTemplate.instName + "." + key
                    if key in meshOverrideList:
                        meshData[meshKey] = mesh.templateOverrides_get(key)
                    else:
                        meshData[meshKey] = mesh.meshTemplate.paramDefaults_get(key)
                    if not meshKey in self.keyNames:
                        self.keyNames.append(meshKey)
                    
                for rc in mesh.runConfigs.itervalues():
                    pb = {}
                    
                    pb["META.rcInstName"] = rc.instName
                                    
                    #Extract toward root: Geom and mesh data
                    pb.update(geomData)
                    pb.update(meshData)
                    
                    #Extract data in RC
                    #TODO
                    
                    #Extract from analysis
                    for (anaName,anaObj)  in rc.analysis.iteritems():
                        #Recursively dig through keys in analysis
                        def anaDigger(exportedDict,nameSoFar):
                            keys = set(exportedDict.getKeys())
                            for k in keys:
                                vals = exportedDict.getVals(k)
                                for vIdx in xrange(len(vals)):
                                    anaKey = nameSoFar + k + "["+str(vIdx)+"]"
                                    if type(vals[vIdx]) == str:
                                        pb[anaKey] = vals[vIdx]
                                        if not anaKey in self.keyNames:
                                            self.keyNames.append(anaKey)
                                    else:
                                        anaDigger(vals[vIdx],anaKey+".")
                        #END anaDigger
                        anaDigger(anaObj.exportResults,"ANA." + anaName + ".")
                    
                    #Filter and store result
                    if reduce(lambda a,b: a and b, map(lambda f: f.filterRow(pb), self.filters) + [True]):
                        self.dataExtracted.append(pb)
        
        #Sort keyName, first as as {META < GEOM < MESH < ANA}, then alphabetically after the first "." (but sort commands must be reversed)
        def sort1(s):
            if s.startswith("META."):
                return 1
            elif s.startswith("GEOM."):
                return 2
            elif s.startswith("MESH."):
                return 3
            elif s.startswith("ANA."):
                return 4
            else:
                raise KeyError
        self.keyNames.sort(key=lambda s: s.split(".",1)[1])
        self.keyNames.sort(key=sort1)
                  
        self.lockdown = True
        self.write()
    
    def export(self,fname,useKeys=None):
        """
        Export the data as a CSV file suitable for import to R, spreadsheet etc.
        The useKeys argument lets you specify which columns you want to use.
        """
        ofile = open(fname,"w")

        if useKeys==None:
            keys = self.keyNames
        else:
            keys = useKeys

        #Write header
        hline = ""
        for k in keys:
            hline += k + ", "
        ofile.write(hline[:-2] + "\n")
        
        #Data
        for row in self.dataExtracted:
            rline = ""
            for k in keys:
                try:
                    #ofile.write(row[k] + ", ")
                    rline += row[k] + ", "
                except KeyError:
                    #ofile.write(" , ")
                    rline += ", "
            #ofile.write("\n")
            ofile.write(rline[:-2] + "\n")
        
        ofile.close()
    
    def clearLockdown(self):
        self.dataExtracted = []
        self.keyNames = []
        self.lockdown = False
        self.write()
    
    def write(self):
        self.__paramfile.dataDict.setValSingle("lockdown", str(self.lockdown))
        
        knfile = self.__paramfile.dataDict["keyNames"]
        knfile.clear()
        for kn in self.keyNames:
            knfile.pushBack("keyName", kn)
        
        edfile = self.__paramfile.dataDict["extractedData"]
        edfile.clear()
        for row in self.dataExtracted:
            rowDict = DataDict()
            for (colKey,col) in row.iteritems():
                rowDict.pushBack(colKey, col)
            edfile.pushBack("dataPoint",rowDict)
        
        fifile = self.__paramfile.dataDict["filters"]
        fifile.clear()
        for f in self.filters:
            f.settingsDict["numFiltered"] = str(f.numFiltered)
            fifile.pushBack(f.filterType, f.settingsDict)
        
        self.__paramfile.write()
            
    @staticmethod
    def createNew(folder):
        #Construct the instance name from folder
        instName = folder
        if instName[-1] == "/":
            instName = instName[0:-1]
        instName = os.path.split(instName)[1]
        if os.path.isdir(folder):
            raise AcdOptiException_dataExtractor_createFail("Folder \"" + folder + "\" already exists")
        os.mkdir(folder)
        
        #Create paramfile
        paramFile = AcdOptiFileParser_simple(os.path.join(folder, "paramFile.set"), 'w')
        paramFile.dataDict.pushBack("fileID", "AcdOptiDataExtractor")
        paramFile.dataDict.pushBack("instName", instName)
        
        paramFile.dataDict.pushBack("keyNames", DataDict())
        paramFile.dataDict.pushBack("extractedData", DataDict())
        
        paramFile.dataDict.pushBack("filters", DataDict())
        
        paramFile.dataDict.pushBack("lockdown", "False")
        
        paramFile.write()