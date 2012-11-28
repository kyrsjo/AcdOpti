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

import os
import numpy as np

class Scan2D(ParameterScanInterface):
    """
    Simple 2D scan: Just vary two parameters over a grid
    """    
    
    scanParameter1_name = None #Name of first parameter that should be scanned. Locked by lockdown
    scanParameter1_min  = None #linspace parameters. Locked by lockdown
    scanParameter1_max  = None
    scanParameter1_num  = None
    
    scanParameter2_name = None #Name of second parameter that should be scanned. Locked by lockdown
    scanParameter2_min  = None #linspace parameters. Locked by lockdown
    scanParameter2_max  = None
    scanParameter2_num  = None
    
    def __init__(self, folder, collection):
        print "TuneFreq::__init__()"
        super(Scan2D,self).__init__(folder,collection,"ParameterScan::Scan2D")
        
        self.scanParameter1_name = self._paramFile.dataDict["scanParameter1_name"]
        self.scanParameter1_min  = float(self._paramFile.dataDict["scanParameter1_min"])
        self.scanParameter1_max  = float(self._paramFile.dataDict["scanParameter1_max"])
        self.scanParameter1_num  = int(self._paramFile.dataDict["scanParameter1_num"])
        
        self.scanParameter2_name = self._paramFile.dataDict["scanParameter2_name"]
        self.scanParameter2_min  = float(self._paramFile.dataDict["scanParameter2_min"])
        self.scanParameter2_max  = float(self._paramFile.dataDict["scanParameter2_max"])
        self.scanParameter2_num  = int(self._paramFile.dataDict["scanParameter2_num"])    
    
    def getScanRanges(self):
        if self.scanParameter1_min == self.scanParameter1_max:
            raise Scan2DException("ScanParameter1: min == max")
        if self.scanParameter1_num <= 0:
            raise Scan2DException("ScanParameter1: num <= 0")
        range1 = np.linspace(self.scanParameter1_min,self.scanParameter1_max, self.scanParameter1_num)
        
        if self.scanParameter2_min == self.scanParameter2_max:
            raise Scan2DException("ScanParameter2: min == max")
        if self.scanParameter2_num <= 0:
            raise Scan2DException("ScanParameter2: num <= 0")
        range2 = np.linspace(self.scanParameter2_min,self.scanParameter2_max, self.scanParameter2_num)
        
        return (range1, range2)
    
    def createScan(self):
        self.write()
        
        (range1,range2) = self.getScanRanges()
        X = [] #parameter 1
        Y = [] #parameter 2
        for i in xrange(len(range2)):
            X += list(range1)
            Y += [range2[i]]*len(range1)
        assert len(X) == len(Y)
        for i in xrange(len(X)):
            try:
                self.addPoint(X[i], Y[i])
            except Scan2DException:
                print "Skipping point"
                
    
    def addPoint(self, parameterValue1, parameterValue2):
        """
        Add a point to the scan with the given parameter value
        """
        assert self.scanParameter1_name != ""
        assert self.scanParameter2_name != ""
        
        oldName = self.baseGeomInstance.instName
        newName = oldName + "--NS--" + self.instName + "--" + self.scanParameter1_name + str(parameterValue1) + "-" + self.scanParameter2_name + str(parameterValue2) 
        #Check if this name already exists:
        if newName in self.getProject().geomCollection.geomInstances:
            print "Error in Scan2D::addPoint: newName '" + newName + "' in use, parameter point already exists?"
            raise Scan2DException("newName '" + newName + "' in use, parameter point already exists?")
        
        newGeom = self.getProject().geomCollection.cloneGeomInstance(oldName,newName)
        newGeom.templateOverrides_insert(self.scanParameter1_name, str(parameterValue1))
        newGeom.templateOverrides_insert(self.scanParameter2_name, str(parameterValue2))
        newGeom.scanInstances.append(self)
        newGeom.write()
        
        self.slaveGeoms[newName] = newGeom
        
        self.lockdown = True
        self.write()
        
    def write(self):
        "Update the paramFile with the class variables"
        print "Scan2D::write()"
        super(Scan2D,self).write()
        
        if self.lockdown:
            assert self.scanParameter1_name      == self._paramFile.dataDict["scanParameter1_name"]
            assert str(self.scanParameter1_min)  == self._paramFile.dataDict["scanParameter1_min"] 
            assert str(self.scanParameter1_max)  == self._paramFile.dataDict["scanParameter1_max"]
            assert str(self.scanParameter1_num)  == self._paramFile.dataDict["scanParameter1_num"]
            
            assert self.scanParameter2_name      == self._paramFile.dataDict["scanParameter2_name"]
            assert str(self.scanParameter2_min)  == self._paramFile.dataDict["scanParameter2_min"] 
            assert str(self.scanParameter2_max)  == self._paramFile.dataDict["scanParameter2_max"]
            assert str(self.scanParameter2_num)  == self._paramFile.dataDict["scanParameter2_num"]
        if self.scanParameter1_name != "":
            assert self.scanParameter1_name in self.getProject().geomCollection.paramDefaults_getKeys()
            assert self.scanParameter1_name != self.scanParameter2_name
        if self.scanParameter2_name != "":
            assert self.scanParameter2_name in self.getProject().geomCollection.paramDefaults_getKeys()
            
        self._paramFile.dataDict["scanParameter1_name"] = self.scanParameter1_name
        self._paramFile.dataDict["scanParameter1_min"]  = str(self.scanParameter1_min) 
        self._paramFile.dataDict["scanParameter1_max"]  = str(self.scanParameter1_max)
        self._paramFile.dataDict["scanParameter1_num"]  = str(self.scanParameter1_num)
            
        self._paramFile.dataDict["scanParameter2_name"] = self.scanParameter2_name
        self._paramFile.dataDict["scanParameter2_min"]  = str(self.scanParameter2_min) 
        self._paramFile.dataDict["scanParameter2_max"]  = str(self.scanParameter2_max)
        self._paramFile.dataDict["scanParameter2_num"]  = str(self.scanParameter2_num)
                
        self._paramFile.write()
        
    @staticmethod
    def createNew(folder):
        if os.path.exists(folder):
            raise Scan2DException("Folder \"" + folder + "\" already exists")
        os.mkdir(folder)
        
        paramFile = AcdOptiFileParser_simple(os.path.join(folder,"paramFile_scan.set"), "w")
        paramFile.dataDict.pushBack("fileID", "ParameterScan::Scan2D")
        
        #Construct the instance name from folder
        instName = folder
        if instName[-1] == "/":
            instName = instName[0:-1]
        instName = instName = os.path.split(instName)[1]
        paramFile.dataDict.pushBack("instName", instName)
        
        paramFile.dataDict.pushBack("baseGeomInstance_name", "")
        paramFile.dataDict.pushBack("slaveGeoms", DataDict())

        paramFile.dataDict.pushBack("scanParameter1_name", "")
        paramFile.dataDict.pushBack("scanParameter1_max", "0")
        paramFile.dataDict.pushBack("scanParameter1_min", "0")
        paramFile.dataDict.pushBack("scanParameter1_num", "0")
        
        paramFile.dataDict.pushBack("scanParameter2_name", "")
        paramFile.dataDict.pushBack("scanParameter2_max", "0")
        paramFile.dataDict.pushBack("scanParameter2_min", "0")
        paramFile.dataDict.pushBack("scanParameter2_num", "0")
                
        paramFile.dataDict.pushBack("lockdown", "False")

        paramFile.write()
    
    
class Scan2DException(AcdOptiException_parameterScan):
    pass