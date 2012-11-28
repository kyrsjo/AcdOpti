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

from ParameterScanInterface import ParameterScanInterface, FittingException_NDOF

import os

class TuneFreq(ParameterScanInterface):
    """
    Simple scanner that tunes a cavity to the correct frequency by changing one geometry parameter.
    """
    
    scanParameter_name = None      #Name of the parameter that should be scanned. Locked by lockdown
    
    predict_anaVariable = None
    predict_targetValue = None
    
    predict_a = None #y=ax+b
    predict_b = None
    predict_x = None #predicted x s.t. y=target
    predict_R2 = None #sqrt(R^2)
    predict_ndof = None
       
    def __init__(self, folder, collection):
        print "TuneFreq::__init__()"
        super(TuneFreq,self).__init__(folder,collection,"ParameterScan::TuneFreq")
        
        self.scanParameter_name = self._paramFile.dataDict["scanParameter_name"]
                
        self.predict_anaVariable = self._paramFile.dataDict["predict_anaVariable"]
        self.predict_targetValue = float(self._paramFile.dataDict["predict_targetValue"])
        
        self.predict_a = float(self._paramFile.dataDict["predict_a"])
        self.predict_b = float(self._paramFile.dataDict["predict_b"])
        self.predict_x = float(self._paramFile.dataDict["predict_x"])
        self.predict_R2 = float(self._paramFile.dataDict["predict_R2"])
        self.predict_ndof = int(self._paramFile.dataDict["predict_ndof"])
    
        
    def iterate(self):
        "predict and add point at predicted value"
        assert self.lockdown == True
        self.doPredict()
        if self.predict_ndof >= 0:
            self.addPoint(self.predict_x)
        else:
            raise TuneFreqException("No prediction, can't add point")
        
        self.write()
    def getXY(self):
        X = []
        Y = []
        for geom in (self.slaveGeoms.values() + [self.baseGeomInstance]):
            x = None
            if self.scanParameter_name in geom.templateOverrides_getKeys():
                x = geom.templateOverrides_get(self.scanParameter_name)
            else:
                x = self.getProject().geomCollection.paramDefaults_get(self.scanParameter_name)
            y = self.getAnalysisResults(geom, self.predict_anaVariable)
            X += [x]*len(y)
            Y += y
        print "X =", X, "Y =", Y
        X = map(float,X)
        Y = map(float,Y)  
        return (X,Y)
    def doPredict(self):
        "Update the current prediction"
        assert self.baseGeomInstance != None, "You must set a baseGeomInstance before doPredict()"
        assert self.scanParameter_name in self.getProject().geomCollection.paramDefaults_getKeys()
        
        (X,Y) = self.getXY()
        
        try:
            (model, ndof, R2) = self.fit1D(X, Y, 1)
            self.predict_ndof = ndof
            #self.predict_x = self.eval1D(self.predict_targetValue, model)
            self.predict_R2 = R2
            self.predict_a = model[1]
            self.predict_b = model[0]
            self.predict_x = (self.predict_targetValue-self.predict_b)/self.predict_a
        except FittingException_NDOF:
            self.predict_ndof = len(Y)-2
            self.predict_x = 0.0
            self.predict_R2 = 0.0
            self.predict_a = 0.0
            self.predict_b = 0.0
        

        
    def addPoint(self, parameterValue):
        """
        Add a point to the scan with the given parameter value
        """
        assert self.scanParameter_name != ""
        
        oldName = self.baseGeomInstance.instName
        newName = oldName + "--NS--" + self.instName + "--" + self.scanParameter_name + str(parameterValue)
        #Check if this name already exists:
        if newName in self.getProject().geomCollection.geomInstances:
            raise TuneFreqException("newName in use, parameter point already exists?")
        
        newGeom = self.getProject().geomCollection.cloneGeomInstance(oldName,newName)
        newGeom.templateOverrides_insert(self.scanParameter_name, str(parameterValue))
        newGeom.scanInstances.append(self)
        newGeom.write()
        
        self.slaveGeoms[newName] = newGeom
        
        self.lockdown = True
        self.write()
        
    def write(self):
        "Update the paramFile with the class variables"
        super(TuneFreq,self).write()
        
        if self.lockdown:
            assert self.scanParameter_name == self._paramFile.dataDict["scanParameter_name"] 
        self._paramFile.dataDict["scanParameter_name"] = self.scanParameter_name
        
        if self.scanParameter_name != "":
            assert self.scanParameter_name in self.getProject().geomCollection.paramDefaults_getKeys()
        self._paramFile.dataDict["predict_anaVariable"] = self.predict_anaVariable
        self._paramFile.dataDict["predict_targetValue"] = str(self.predict_targetValue)
        
        self._paramFile.dataDict["predict_a"]    = str(self.predict_a)
        self._paramFile.dataDict["predict_b"]    = str(self.predict_b)
        self._paramFile.dataDict["predict_x"]    = str(self.predict_x)
        self._paramFile.dataDict["predict_R2"]   = str(self.predict_R2)
        self._paramFile.dataDict["predict_ndof"] = str(self.predict_ndof)
                
        self._paramFile.write()
        
    @staticmethod
    def createNew(folder):
        if os.path.exists(folder):
            raise TuneFreqException("Folder \"" + folder + "\" already exists")
        os.mkdir(folder)
        
        paramFile = AcdOptiFileParser_simple(os.path.join(folder,"paramFile_scan.set"), "w")
        paramFile.dataDict.pushBack("fileID", "ParameterScan::TuneFreq")
        
        #Construct the instance name from folder
        instName = folder
        if instName[-1] == "/":
            instName = instName[0:-1]
        instName = instName = os.path.split(instName)[1]
        paramFile.dataDict.pushBack("instName", instName)
        
        paramFile.dataDict.pushBack("baseGeomInstance_name", "")
        paramFile.dataDict.pushBack("slaveGeoms", DataDict())

        paramFile.dataDict.pushBack("scanParameter_name", "")
        
        paramFile.dataDict.pushBack("predict_anaVariable","Omega3P_modeInfo.Mode.FrequencyReal_GHz")
        paramFile.dataDict.pushBack("predict_targetValue", "11.9942")
        paramFile.dataDict.pushBack("predict_tolerance", "0.001")
     
        paramFile.dataDict.pushBack("predict_a", "0")
        paramFile.dataDict.pushBack("predict_b", "0")
        paramFile.dataDict.pushBack("predict_x", "0")
        paramFile.dataDict.pushBack("predict_R2", "0")
        paramFile.dataDict.pushBack("predict_ndof", "-10") #predict_ndof only positive iff have valid prediction

        paramFile.dataDict.pushBack("lockdown", "False")

        paramFile.write()
    
    
class TuneFreqException(AcdOptiException_parameterScan):
    pass