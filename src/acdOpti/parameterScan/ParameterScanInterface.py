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

from acdOpti.AcdOptiFileParser import DataDict, AcdOptiFileParser_simple
from acdOpti.AcdOptiExceptions import AcdOptiException, AcdOptiException_parameterScan

import os

#Inspired by AnalysisInterface and AcdOptiScan
class ParameterScanInterface(object):
    
    type           = None 
    folder         = None #Folder where it stores it data
    scanCollection = None #Pointer to ParameterScanCollection
    instName       = None #Name of this particular ParameterScan instance
    
    __paramFile    = None
    
    baseGeomInstance = None #Geometry instance on which to base the scan
    slaveGeoms       = None #List of geometry instances "belonging" to this scan
    slaveScanCollection = None #ParameterScanCollection with slave scans
    
    def __init__(self,folder,collection, typ):
        from ParameterScanCollection import ParameterScanCollection
        assert typ in ParameterScanCollection.parameterScanTypes or "ParameterScan::"+ typ in ParameterScanCollection.parameterScanTypes
        self.type      = typ
        self.folder    = folder
        self.scanCollection = collection
        
        #Construct the instance name from folder
        instName = folder
        if instName[-1] == "/":
            instName = instName[0:-1]
        self.instName = instName = os.path.split(instName)[1]
        
        #Load paramFile.set
        self.__paramFile = AcdOptiFileParser_simple(os.path.join(folder, "paramFile_scan.set"), 'rw')
        if self.__paramFile.dataDict["fileID"] != self.type:
            raise ParameterScanInterfaceException_init("Got fileID='" + self.__paramFile.dataDict["fileID"] + "'")
        
        if self.__paramFile.dataDict.getValSingle("instName") != self.instName:
            raise ParameterScanInterfaceException_init("instName doesn't match folder name")
        
        baseGeomInstance_name = self.__paramFile.dataDict["baseGeomInstance_name"]
        if baseGeomInstance_name == "":
            self.baseGeomInstance = None
            assert len(self.__paramFile.dataDict["slaveGeoms"]) == 0
        else:
            self.baseGeomInstance = self.getProject().geomCollection.geomInstances[baseGeomInstance_name]
        
        self.slaveGeoms = {}
        for (geomName, nothingOfInterest) in self.__paramFile.dataDict["slaveGeoms"]:
            #Mutal referencing
            self.slaveGeoms[geomName] = self.getProject().geomCollection.geomInstances[geomName]
            self.slaveGeoms[geomName].scanInstances.append(self)
    
    def write(self):
        "Update slaveGeoms and write to paramfile"
        for geomName in self.slaveGeoms.keys():
            if not geomName in self.__paramFile.dataDict["slaveGeoms"]:
                self.__paramFile.dataDict["slaveGeoms"].pushBack(geomName, "")
        
        self.__paramFile.dataDict["baseGeomInstance_name"] = self.baseGeomInstance.instName 
        
        self.__paramFile.write() 
    
    def getProject(self):
        #Find the project's GeometryCollection:
        from acdOpti.AcdOptiProject import AcdOptiProject
        scanCollectionParent = self.scanCollection.parent
        while True:
            if isinstance(scanCollectionParent,AcdOptiProject):
                return scanCollectionParent
            else:
                scanCollectionParent = scanCollectionParent.parent
    
    @staticmethod
    def createNew(folder):
        """
        Create a new ParameterScan of the implementing type
        """
        raise NotImplementedError("Please implement a createNew method in your class!")

    @classmethod
    def createNew_clone(cls, folder, collection, cloneFrom):
        """
        Clone an already existing ParameterScan
        of the implementing type.
        """
        print "ParameterScan::createNew_clone()"
        raise NotImplementedError
#        cls.createNew(folder)
#        newScan = cls(folder, collection)
#        if cloneFrom.settings != None:
#            newScan.settings.clear()
#            for (k,v) in cloneFrom.settings:
#                if isinstance(v,DataDict):
#                    newScan.settings.pushBack(k,v.copy())
#                else:
#                    newScan.settings.pushBack(k,v)
#            newScan.write()
#            
#        return newScan
 
class ParameterScanInterfaceException(AcdOptiException_parameterScan):
    pass
class ParameterScanInterfaceException_init(ParameterScanInterfaceException):
    pass
    