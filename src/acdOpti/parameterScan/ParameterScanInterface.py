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

import numpy as np
import re

import os

#Inspired by AnalysisInterface and AcdOptiScan
class ParameterScanInterface(object):
    
    type           = None 
    folder         = None #Folder where it stores it data
    scanCollection = None #Pointer to ParameterScanCollection
    instName       = None #Name of this particular ParameterScan instance
    
    _paramFile    = None
    
    baseGeomInstance = None #Geometry instance on which to base the scan
    slaveGeoms       = None #List of geometry instances "belonging" to this scan
    slaveScanCollection = None #ParameterScanCollection with slave scans
    
    lockdown = False  #Set to true once we have slaveGeoms. When true baseGeom isn't changeable
    
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
        self._paramFile = AcdOptiFileParser_simple(os.path.join(folder, "paramFile_scan.set"), 'rw')
        if self._paramFile.dataDict["fileID"] != self.type:
            raise ParameterScanInterfaceException_init("Got fileID='" + self._paramFile.dataDict["fileID"] + "'")
        
        if self._paramFile.dataDict.getValSingle("instName") != self.instName:
            raise ParameterScanInterfaceException_init("instName doesn't match folder name")
    
        self.lockdown = DataDict.boolconv(self._paramFile.dataDict["lockdown"])
        
        baseGeomInstance_name = self._paramFile.dataDict["baseGeomInstance_name"]
        if baseGeomInstance_name == "":
            self.baseGeomInstance = None
            assert len(self._paramFile.dataDict["slaveGeoms"]) == 0
            assert self.lockdown == False
        else:
            self.baseGeomInstance = self.getProject().geomCollection.geomInstances[baseGeomInstance_name]
        
        self.slaveGeoms = {}
        for (geomName, nothingOfInterest) in self._paramFile.dataDict["slaveGeoms"]:
            #Mutal referencing
            self.slaveGeoms[geomName] = self.getProject().geomCollection.geomInstances[geomName]
            self.slaveGeoms[geomName].scanInstances.append(self)
        if len(self.slaveGeoms) > 0:
            assert self.lockdown == True
             
    def write(self):
        "Update slaveGeoms and write to paramfile"
        if len(self.slaveGeoms) > 0:
            assert self.lockdown == True
            
        for geomName in self.slaveGeoms.keys():
            if not geomName in self._paramFile.dataDict["slaveGeoms"]:
                self._paramFile.dataDict["slaveGeoms"].pushBack(geomName, "")
        
        if self.lockdown == True:
            assert self.baseGeomInstance != None
            assert self._paramFile.dataDict["baseGeomInstance_name"] == self.baseGeomInstance.instName

        if self.baseGeomInstance != None:
            assert self.baseGeomInstance in self.getProject().geomCollection.geomInstances.values()
            self._paramFile.dataDict["baseGeomInstance_name"] = self.baseGeomInstance.instName
        else:
            self._paramFile.dataDict["baseGeomInstance_name"] = ""
        
        self._paramFile.dataDict["lockdown"] = str(self.lockdown) 

        self._paramFile.write() 
    
    def setBaseGeom(self,baseGeomName):
        assert self.lockdown == False, "Can't change baseGeomInstance once we have lockdown"
        assert len(self.slaveGeoms) == 0
        
        self.baseGeomInstance = self.getProject().geomCollection.geomInstances[baseGeomName]
        self.write()
    
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
 
    # # # # # # # Utility methods # # # # # # # # # # # # # # # # # # # # # # #
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
    def getAnalysisResults(geom,anaVarString):
        """
        For a geom, retrive all analysis results using the address anaVarString,
        maximum one result per analysisInstance.
        AnaVarString syntax:
         key.key[idx].key....
         If [idx] not present, assume [idx]=0
         First key is analysis instance name
        """
        anaVarSplit = anaVarString.split(".")
        retVals = []
        
        for mesh in geom.meshInsts.itervalues():
            for rc in mesh.runConfigs.itervalues():
                for ana in rc.analysis.itervalues():
                    if ana.instName == anaVarSplit[0]:
                        #Recursive function to find the analysis result
                        #Uses the usual key.key[idx].key.... syntax
                        #If not [idx] present, assume idx=0
                        #If not found, return None
                        def dictRecDig(avsRemaining, dictBranch):
                            avsParsed = re.match(r'(\w)+[(\d+)]',avsRemaining[0])
                            if avsParsed != None:
                                nextName = avsParsed.group(1)
                                nextNumber = int(avsParsed.group(2))
                            else:
                                nextName = avsRemaining[0]
                                nextNumber = 0

                            try:
                                nextBranch = dictBranch.getVals(nextName)[nextNumber]
                            except IndexError:
                                print "WARNING in dictRecDig(): Key '" + avsRemaining[0] + "' not found"
                                return None
                            
                            if isinstance(nextBranch,DataDict):
                                if len(avsRemaining) == 1:
                                    print "WARNING in dictRecDig(): More depth than keys"
                                    return None
                                return dictRecDig(avsRemaining[1:],nextBranch)
                            else:
                                if len(avsRemaining) > 1:
                                    print "WARNING in dictRecDig(): More keys than depth"
                                    return None
                                return nextBranch
                        r = dictRecDig(anaVarSplit[1:],ana.exportResults)
                        if r != None:
                            retVals.append(r)
        return retVals
    
    @staticmethod
    def fit1D(x,y, deg):
        """
        For two lists of values (x,y), return a a fitted model ŷ = a0 + a1*x + a2*x^2 + ... + adeg*x^deg.
        Also return number of degrees of freedom and R^2 = sum (ŷ(x_i)-y_i)^2.
        Return:
        ((a0,a1,...,adeg), ndof, R^2) 
        """
        
        if len(x) != len(y):
            raise FittingException("length of x (%i) should be equal to length of y (%i)" % ( len(x), len(y) ) )
        ndof = len(y) - (deg+1) 
        if ndof < 0:
            raise FittingException_NDOF("ndof =", ndof, "< 0, can't fit.")
        A = [np.ones(len(x))]
        for i in xrange(deg):
            A.append(np.asarray(x)**(i+1))
        A = np.vstack(A).T
        
        model = np.linalg.lstsq(A,y)[0]
        
        R2 = 0.0
        for i in xrange(len(x)):
            R2 += (y[i]-ParameterScanInterface.eval1D(x[i],model))**2

        return (model, ndof, R2)

    @staticmethod
    def eval1D(x,model):
        """
        Evaluate a polynomial y=model[0]+model[1]*x+model[2]*x**2 + ... model[n]*x**n.
        Works with x both float as and ndarray.
        """
        y = None
        if type(x) == float:
            y = 0.0
        elif type(x) == np.ndarray:
            y = np.zeros_like(x)
        for i in xrange(len(model)):
            y += model[i]*x**i
        return y
        
 
class ParameterScanInterfaceException(AcdOptiException_parameterScan):
    pass
class ParameterScanInterfaceException_init(ParameterScanInterfaceException):
    pass
class FittingException(AcdOptiException_parameterScan):
    pass
class FittingException_NDOF(AcdOptiException_parameterScan):
    pass
