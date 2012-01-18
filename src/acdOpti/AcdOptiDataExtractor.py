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
from acdOpti.AcdOptiExceptions import AcdOptiException_dataExtractor_createFail,\
                                      AcdOptiException_dataExtractor_loadFail

import os

class AcdOptiDataExtractor:
    """
    This class extracts data from analysis, geoms etc.
    This is presented in a FLAT table.
    """
    
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
            pb = {}
            for (k,v) in v:
                pb[k] = v
                if not k in self.keyNames:
                    raise AcdOptiException_dataExtractor_loadFail("Key name '" + k + "' not found in self.keyNames")
            self.dataExtracted.append(pb)
        
        #Find, load, and attach filters 
    
    def runExtractor(self, folder, collection):
        assert self.lockdown == False
        
        #Run Loop over all runconfigs and for each extract one row in the table
        #geomCollection = self.collection.project.... 
        for geom in geomCollection.geomInstances.iterValues():
            for mesh in geom.meshInsts.iterValues():
                meshTemplateName = mesh.meshTemplate.instName
                #for rc in runconfigs...:
                    #Extract toward root
                    #Extract from RC
                    #Extract from analysis
        
        #Fill keyNames
        
        #Run filters
        
        self.lockdown = True
        
    
    def clearLockdown(self):
        self.dataExtracted = []
        self.keyNames = []
        self.lockdown = False
        self.write()
    
    def write(self):
        self.__paramfile.dataDict.setValSingle("lockdown", str(self.lockdown))
        
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
        paramFile.dataDict.pushBack("extractedData", DataDict()) #(key, value) = (x,y)
        
        paramFile.dataDict.pushBack("lockdown", "False")
        
        paramFile.write()