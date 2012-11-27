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

import os
from acdOpti.parameterScan.ParameterScanInterface import ParameterScanInterface

class ParameterScanCollection(object):
    """
    Collection class organizing the contents of a ParameterScan folder
    """

    folder   = None
    instName = None #Name of this instance. Set to "ParameterScanCollection" iff parent is AcdOptiProject
    parent   = None #AcdOptiProject OR another ParameterScanCollection (including implementations)
    parentScan = None #If the scan collection is owned by a ParameterScan, this points to it
    
    __paramfile = None
    
    scans = None #Map of objects implementing ParameterScanInterface 
    
    parameterScanTypes = ["ParameterScan::Dummy", "ParameterScan::DummySubscan", "ParameterScan::TuneFreq"]
    
    def __init__(self, folder, parent, parentScan=None):
        self.folder = folder
        self.parent = parent
        
        #Construct the instance name from folder
        instName = folder
        if instName[-1] == "/":
            instName = instName[0:-1]
        self.instName = instName = os.path.split(instName)[1]
        
        from acdOpti.AcdOptiProject import AcdOptiProject
        if not isinstance(parent,ParameterScanCollection) and not isinstance(parent, AcdOptiProject):
            raise ParameterScanCollectionException("Error when initializing ParameterScanCollection, "+\
                                                   "type(parent) must be AcdOptiProject or ParameterScanCollection, type was '" + str(type(parent)))
        elif self.instName == "ParameterScanCollection" and not isinstance(parent, AcdOptiProject):
            raise ParameterScanCollectionException("Error when initializing ParameterScanCollection, instName='"+self.instName+"', but type(parent)="+str(type(parent)))
        
        #Load paramFile
        self.__paramfile = AcdOptiFileParser_simple(os.path.join(folder, "paramFile_scanCollection.set"), 'rw')
        if self.__paramfile.dataDict["fileID"] != "ParameterScan::ParameterScanCollection":
            raise ParameterScanCollectionException("Error loading ParameterScanCollection: Got wrong fileID='" + self.paramFile.dataDict["fileID"] + "'")            
        if self.__paramfile.dataDict["instName"] != self.instName:
            raise ParameterScanCollectionException("Error loading ParameterScanCollection: instName mismatch")
        
        #Look for scans
        self.scans = {}
        for (scanName, scanType) in self.__paramfile.dataDict["scans"]:
            childPath = os.path.join(self.folder,"scans",scanName)
            if not os.path.exists(childPath):
                raise ParameterScanCollectionException("Error loading ParameterScanCollection, path='" + childPath + "' does not exist")
            if scanType == "ParameterScan::Dummy":
                from Dummy import Dummy
                self.scans[scanName] = Dummy(childPath, self)
            elif scanType == "ParameterScan::DummySubscan":
                from DummySubscan import DummySubscan
                self.scans[scanName] = DummySubscan(childPath, self)
            elif scanType == "ParameterScan::TuneFreq":
                from TuneFreq import TuneFreq
                self.scans[scanName] = TuneFreq(childPath,self)
            else:
                if scanType in self.parameterScanTypes or "ParameterScan::"+scanType in self.parameterScanTypes:
                    raise NotImplementedError("Forgot to implement support for ParameterScan '" + scanType + "'!")
                raise ParameterScanCollectionException("Unknown scanType='"+scanType+"'")
        
        #Setup parentScan
        if parentScan != None:
            from acdOpti.parameterScan.ParameterScanInterface import ParameterScanInterface
            assert isinstance(parentScan, ParameterScanInterface)
            
            if self.__paramfile.dataDict["parentScan"] != parentScan.instName:
                raise ParameterScanCollectionException("ParentScan mismatch, got '"+self.__paramfile.dataDict["parentScan"]+"' from paramfile" )
            
            self.parentScan = parentScan
    
    def addNew(self, name, scanType):
        """
        Try to add a new scan with the given name and tnype
        ParameterScanCollectionException is raised if there is a problem (name already taken or invalid type).
        Returns a reference to the newly created scan.
        """
        
        if name in self.scans.keys():
            raise ParameterScanCollectionException("Name '" + name + "' already taken")
        
        scanFolder = os.path.join(self.folder, "scans", name)
        
        if scanType == "ParameterScan::Dummy" or scanType == "Dummy":
            from Dummy import Dummy
            Dummy.createNew(scanFolder)
            self.scans[name] = newScan = Dummy(scanFolder, self)
        elif scanType == "ParameterScan::DummySubscan" or scanType == "DummySubscan":
            from DummySubscan import DummySubscan
            DummySubscan.createNew(scanFolder)
            self.scans[name] = newScan = DummySubscan(scanFolder, self)
        elif scanType == "ParameterScan::TuneFreq" or scanType == "TuneFreq":
            from TuneFreq import TuneFreq
            TuneFreq.createNew(scanFolder)
            self.scans[name] = newScan = TuneFreq(scanFolder,self)
        else:
            if scanType in self.parameterScanTypes or "ParameterScan::"+scanType in self.parameterScanTypes:
                raise NotImplementedError("Forgot to implement support for ParameterScan '" + scanType + "'!")
            raise ParameterScanCollectionException("Unknown ParameterScan type '" + scanType + "'")
        
        self.__paramfile.dataDict["scans"].pushBack(name,newScan.type)
        self.__paramfile.write()
        
        return self.scans[name]
    
    
    @staticmethod
    def createNew(folder, parentScanName=None):
        
        if parentScanName == None:
            #If parentScan, they are created in the same folder
            os.mkdir(folder)
            
        paramFile = AcdOptiFileParser_simple(os.path.join(folder,"paramFile_scanCollection.set"), 'w')
        
        paramFile.dataDict.pushBack("fileID", "ParameterScan::ParameterScanCollection")
        
        instName = folder
        if instName[-1] == "/":
            instName = instName[0:-1]
        instName = os.path.split(instName)[1]
        paramFile.dataDict.pushBack("instName", instName)
        
        paramFile.dataDict.pushBack("scans", DataDict())
        os.mkdir(os.path.join(folder,"scans"))
        
        if parentScanName != None:
            paramFile.dataDict.pushBack("parentScan", parentScanName)
        else:
            paramFile.dataDict.pushBack("parentScan", "")
        
        paramFile.write()

class ParameterScanCollectionException(AcdOptiException_parameterScan):
    pass
