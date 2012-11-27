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
from acdOpti.AcdOptiExceptions import AcdOptiException_parameterScan

from ParameterScanInterface import ParameterScanInterface
from ParameterScanCollection import ParameterScanCollection

import os

class DummySubscan(ParameterScanInterface):
    
    def __init__(self, folder, collection):
        print "DummySubscan::__init__()"
        super(DummySubscan,self).__init__(folder,collection,"ParameterScan::DummySubscan")
        self.slaveScanCollection = ParameterScanCollection(folder, collection,self) #Initialized in same folder
    
    def addSubscan(self, newName):
        "Test method, add one new DummySubscan to this scan's ParameterScanCollection"
        if newName == "" or " " in newName:
            raise DummySubscanException("Invalid name '" + newName + "'")
        self.slaveScanCollection.addNew(newName, self.type)
    
    def addGeom(self, newName):
        "Test method, add one new GeometryInstance to this scan's ParameterScanCollection"
        if newName == "" or " " in newName:
            raise DummySubscanException("Invalid name '" + newName + "'")
        
        gName = self.instName + "--" + newName
        newGeom = self.getProject().geomCollection.addGeomInstance(gName)
        if self.baseGeomInstance == None:
            self.setBaseGeom(gName)
            
        self.slaveGeoms[gName] = newGeom
        newGeom.scanInstances.append(self)
        
        self.lockdown = True
        
        self.write()
    
    @staticmethod
    def createNew(folder):
        if os.path.exists(folder):
            raise DummySubscanException("Folder \"" + folder + "\" already exists")
        os.mkdir(folder)
        
        paramFile = AcdOptiFileParser_simple(os.path.join(folder,"paramFile_scan.set"), "w")
        paramFile.dataDict.pushBack("fileID", "ParameterScan::DummySubscan")
        
        #Construct the instance name from folder
        instName = folder
        if instName[-1] == "/":
            instName = instName[0:-1]
        instName = instName = os.path.split(instName)[1]
        paramFile.dataDict.pushBack("instName", instName)
        
        paramFile.dataDict.pushBack("baseGeomInstance_name", "")
        paramFile.dataDict.pushBack("slaveGeoms", DataDict())

        paramFile.dataDict.pushBack("lockdown", "False")

        paramFile.write()
        
        #Setup the ScanCollection in the same folder
        ParameterScanCollection.createNew(folder, instName)
    
    
class DummySubscanException(AcdOptiException_parameterScan):
    pass