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
from acdOpti.AcdOptiExceptions import AcdOptiException_parameterScan,\
                                      AcdOptiException_dataDict_getValsSingle

from ParameterScanInterface import ParameterScanInterface
from ParameterScanCollection import ParameterScanCollection

import os
import numpy as np

class Scan2D_Tune(ParameterScanInterface):
    """
    2D scan with tuning: Vary two parameters over a grid.
    For each parameter point created, also create and initialize a TuneFreq. 
    """    
    
    #Parameter scanning setup
    scanParameter1_name = None #Name of first parameter that should be scanned. Locked by lockdown
    scanParameter1_min  = None #linspace parameters. Locked by lockdown
    scanParameter1_max  = None
    scanParameter1_num  = None
    
    scanParameter2_name = None #Name of second parameter that should be scanned. Locked by lockdown
    scanParameter2_min  = None #linspace parameters. Locked by lockdown
    scanParameter2_max  = None
    scanParameter2_num  = None
    
    #TuneFreq initial parameters
    tune_parameter = None
    tune_anaVariable = None
    tune_targetValue = None
    
    tune_initialPoints = None #List of points to add to the tuneFreq
    tune_model = None #List of coefficients for plane/quad surface to use for initial points
    tune_useModelPoints = False #If True, use a model to generate initial points. If false, use initialPoints.
    #Todo: Add initial point prediction
    
    def __init__(self, folder, collection):
        print "Scan2D_Tune::__init__()"
        super(Scan2D_Tune,self).__init__(folder,collection,"ParameterScan::Scan2D_Tune")
        
        self.scanParameter1_name = self._paramFile.dataDict["scanParameter1_name"]
        self.scanParameter1_min  = float(self._paramFile.dataDict["scanParameter1_min"])
        self.scanParameter1_max  = float(self._paramFile.dataDict["scanParameter1_max"])
        self.scanParameter1_num  = int(self._paramFile.dataDict["scanParameter1_num"])
        
        self.scanParameter2_name = self._paramFile.dataDict["scanParameter2_name"]
        self.scanParameter2_min  = float(self._paramFile.dataDict["scanParameter2_min"])
        self.scanParameter2_max  = float(self._paramFile.dataDict["scanParameter2_max"])
        self.scanParameter2_num  = int(self._paramFile.dataDict["scanParameter2_num"])    
    
        self.tune_parameter   = self._paramFile.dataDict["tune_parameter"]
        self.tune_anaVariable = self._paramFile.dataDict["tune_anaVariable"]
        self.tune_targetValue = float(self._paramFile.dataDict["tune_targetValue"])
        
        self.tune_initialPoints = []
        for (k,v) in self._paramFile.dataDict["tune_initialPoints"]:
            self.tune_initialPoints.append(k)
        
        self.tune_model = []            
        try:
            tune_ipModelDict = self._paramFile.dataDict["tune_ipModelDict"]
            self.tune_useModelPoints = DataDict.boolconv(self._paramFile.dataDict["tune_useModelPoints"])
        except AcdOptiException_dataDict_getValsSingle:
            print "Scan2D_Tune::__init__(): Adding tune_ipModelDict and tune_useModelPoints to paramFile"
            self._paramFile.dataDict.pushBack("tune_ipModelDict", DataDict())
            self._paramFile.dataDict.pushBack("tune_useModelPoints", "False")
            self._paramFile.write()
            tune_ipModelDict = DataDict()
            self.tune_useModelPoints = False
        i = 0
        for (k,v) in tune_ipModelDict:
            assert k == str(i)
            self.tune_model.append(float(v))
            i += 1
        
        #Initialize slave scan collection in same folder     
        self.slaveScanCollection = ParameterScanCollection(folder, collection,self)

    
    def getScanRanges(self):
        if self.scanParameter1_min == self.scanParameter1_max:
            raise Scan2D_TuneException("ScanParameter1: min == max")
        if self.scanParameter1_num <= 0:
            raise Scan2D_TuneException("ScanParameter1: num <= 0")
        range1 = np.linspace(self.scanParameter1_min,self.scanParameter1_max, self.scanParameter1_num)
        
        if self.scanParameter2_name != "": #2D scan
            if self.scanParameter2_min == self.scanParameter2_max:
                raise Scan2D_TuneException("ScanParameter2: min == max")
            if self.scanParameter2_num <= 0:
                raise Scan2D_TuneException("ScanParameter2: num <= 0")
            range2 = np.linspace(self.scanParameter2_min,self.scanParameter2_max, self.scanParameter2_num)
        else: #1D scan
            range2 = None
        
        return (range1, range2)
    
    def createScan(self):
        self.write()
        
        (range1,range2) = self.getScanRanges()
        
        assert self.tune_parameter != ""
        assert self.tune_anaVariable != ""
        #Target cannot be empty, no assertion needed
        
        if range2 != None: #2D scan
            X = [] #parameter 1
            Y = [] #parameter 2
            for i in xrange(len(range2)):
                X += list(range1)
                Y += [range2[i]]*len(range1)
            assert len(X) == len(Y)
            for i in xrange(len(X)):
                try:
                    self.addPoint(X[i], Y[i])
                except Scan2D_TuneException:
                    print "Skipping point"
        else: #1D scan
            for i in xrange(len(range1)):
                try:
                    self.addPoint(range1[i])
                except Scan2D_TuneException:
                    print "Skipping point"
    
    def addPoint(self, parameterValue1, parameterValue2=None):
        """
        Add a point to the scan with the given parameter value
        """
        assert self.scanParameter1_name in self.getProject().geomCollection.paramDefaults_getKeys()
        if parameterValue2 != None:
            assert self.scanParameter2_name in self.getProject().geomCollection.paramDefaults_getKeys()
        
        assert self.tune_parameter in self.getProject().geomCollection.paramDefaults_getKeys()
        assert self.tune_anaVariable != ""
        
        
        oldName = self.baseGeomInstance.instName
        if parameterValue2 != None: #2D scan
            newName = oldName + "--NS--" + self.instName + "--" + self.scanParameter1_name + str(parameterValue1) + "-" + self.scanParameter2_name + str(parameterValue2)
        else: #1D scan 
            newName = oldName + "--NS--" + self.instName + "--" + self.scanParameter1_name + str(parameterValue1)
        #Check if this name already exists:
        if newName in self.getProject().geomCollection.geomInstances:
            print "Error in Scan2D_Tune::addPoint: newName '" + newName + "' in use, parameter point already exists in geomCollection!"
            raise Scan2D_TuneException("newName '" + newName + "' in use, parameter point already exists in geomCollection!")
        elif newName in self.slaveScanCollection.scans.keys():
            print "Error in Scan2D_Tune::addPoint: newName '" + newName + "' in use, parameter point already exists in slaveScanCollection!"
            raise Scan2D_TuneException("newName '" + newName + "' in use, parameter point already exists in slaveScanCollection!")
        #Create geom & set parameters
        newGeom = self.getProject().geomCollection.cloneGeomInstance(oldName,newName)
        newGeom.templateOverrides_insert(self.scanParameter1_name, str(parameterValue1))
        if parameterValue2 != None:
            newGeom.templateOverrides_insert(self.scanParameter2_name, str(parameterValue2))
        if self.tune_useModelPoints == False:
            if len(self.tune_initialPoints) > 0:
                newGeom.templateOverrides_insert(self.tune_parameter, self.tune_initialPoints[0])
        elif self.tune_useModelPoints == True:
            assert parameterValue2 != None
            newGeom.templateOverrides_insert(self.tune_parameter, str(self.getTunedModel(parameterValue1, parameterValue2)))
        newGeom.scanInstances.append(self)
        newGeom.write()
        
        self.slaveGeoms[newName] = newGeom        
        
        newTuner = self.slaveScanCollection.addNew(newName, "ParameterScan::TuneFreq")
        newTuner.setBaseGeom(newName)
        newTuner.scanParameter_name  = self.tune_parameter
        newTuner.predict_anaVariable = self.tune_anaVariable
        newTuner.predict_targetValue = self.tune_targetValue
        newTuner.write()
        if self.tune_useModelPoints == False:
            for pi in xrange(1,len(self.tune_initialPoints)):
                newTuner.addPoint(self.tune_initialPoints[pi])
        
        self.lockdown = True
        self.write()
    
    def getTunedModel(self, parameterValue1, parameterValue2):
        assert self.scanParameter2_name != "" #Can only be used for 2D scan
        if len(self.tune_model) == 3:
            return self.tune_model[0] + parameterValue1*self.tune_model[1] + parameterValue2*self.tune_model[2]
        elif len(self.tune_model) == 6:
            return self.tune_model[0] + parameterValue1*self.tune_model[1] + parameterValue2*self.tune_model[2] + \
                (parameterValue1**2)*self.tune_model[3] + (parameterValue2**2)*self.tune_model[4] + (parameterValue1*parameterValue2)*self.tune_model[5]
        else:
            raise ValueError("Something wrong with tune_model!")
        
    def write(self):
        "Update the paramFile with the class variables"
        print "Scan2D_Tune::write()"
        super(Scan2D_Tune,self).write()
        
        if self.lockdown:
            assert self.scanParameter1_name      != ""
            assert self.scanParameter1_name      == self._paramFile.dataDict["scanParameter1_name"]
            #assert str(self.scanParameter1_min)  == self._paramFile.dataDict["scanParameter1_min"] 
            #assert str(self.scanParameter1_max)  == self._paramFile.dataDict["scanParameter1_max"]
            #assert str(self.scanParameter1_num)  == self._paramFile.dataDict["scanParameter1_num"]
            
            assert self.scanParameter2_name      == self._paramFile.dataDict["scanParameter2_name"]
            #assert str(self.scanParameter2_min)  == self._paramFile.dataDict["scanParameter2_min"] 
            #assert str(self.scanParameter2_max)  == self._paramFile.dataDict["scanParameter2_max"]
            #assert str(self.scanParameter2_num)  == self._paramFile.dataDict["scanParameter2_num"]
            
            assert self.tune_parameter           == self._paramFile.dataDict["tune_parameter"]
            assert self.tune_anaVariable         == self._paramFile.dataDict["tune_anaVariable"]
            assert str(self.tune_targetValue)    == self._paramFile.dataDict["tune_targetValue"]
        else:
            if self.tune_parameter != self._paramFile.dataDict["tune_parameter"] and self.tune_parameter != "": #it changed!
                assert self.tune_parameter in self.getProject().geomCollection.paramDefaults_getKeys()
                print "resetting tune_initialPoints"
                del self.tune_initialPoints[:]
                
                if self.tune_parameter in self.baseGeomInstance.templateOverrides_getKeys():
                    self.tune_initialPoints.append(self.baseGeomInstance.templateOverrides_get(self.tune_parameter))
                else:
                    self.tune_initialPoints.append(self.getProject().geomCollection.paramDefaults_get(self.tune_parameter))
                
        if self.scanParameter1_name != "":
            assert self.scanParameter1_name in self.getProject().geomCollection.paramDefaults_getKeys()
            assert self.scanParameter1_name != self.scanParameter2_name
        if self.scanParameter2_name != "":
            assert self.scanParameter2_name in self.getProject().geomCollection.paramDefaults_getKeys()
        if self.tune_parameter != "":
            assert self.tune_parameter in self.getProject().geomCollection.paramDefaults_getKeys()
            if self.scanParameter1_name != "":
                assert self.tune_parameter != self.scanParameter1_name
            if self.scanParameter2_name != "":
                assert self.tune_parameter != self.scanParameter2_name
        
        self._paramFile.dataDict["scanParameter1_name"] = self.scanParameter1_name
        self._paramFile.dataDict["scanParameter1_min"]  = str(self.scanParameter1_min) 
        self._paramFile.dataDict["scanParameter1_max"]  = str(self.scanParameter1_max)
        self._paramFile.dataDict["scanParameter1_num"]  = str(self.scanParameter1_num)
            
        self._paramFile.dataDict["scanParameter2_name"] = self.scanParameter2_name
        self._paramFile.dataDict["scanParameter2_min"]  = str(self.scanParameter2_min) 
        self._paramFile.dataDict["scanParameter2_max"]  = str(self.scanParameter2_max)
        self._paramFile.dataDict["scanParameter2_num"]  = str(self.scanParameter2_num)
        
        self._paramFile.dataDict["tune_parameter"]   =     self.tune_parameter
        self._paramFile.dataDict["tune_anaVariable"] =     self.tune_anaVariable
        self._paramFile.dataDict["tune_targetValue"] = str(self.tune_targetValue)
        
        self._paramFile.dataDict["tune_initialPoints"].clear()
        for p in self.tune_initialPoints:
            self._paramFile.dataDict["tune_initialPoints"].pushBack(p, "") 
        
        self._paramFile.dataDict["tune_ipModelDict"].clear()
        i = 0
        for p in self.tune_model:
            self._paramFile.dataDict["tune_ipModelDict"].pushBack(str(i), str(p))
            i += 1
            
        self._paramFile.dataDict["tune_useModelPoints"] = str(self.tune_useModelPoints)
        
        self._paramFile.write()
        
    @staticmethod
    def createNew(folder):
        if os.path.exists(folder):
            raise Scan2D_TuneException("Folder \"" + folder + "\" already exists")
        os.mkdir(folder)
        
        paramFile = AcdOptiFileParser_simple(os.path.join(folder,"paramFile_scan.set"), "w")
        paramFile.dataDict.pushBack("fileID", "ParameterScan::Scan2D_Tune")
        
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
        
        paramFile.dataDict.pushBack("tune_parameter","")
        paramFile.dataDict.pushBack("tune_anaVariable","Omega3P_modeInfo.Mode.FrequencyReal_GHz")
        paramFile.dataDict.pushBack("tune_targetValue","11.9942")
        paramFile.dataDict.pushBack("tune_initialPoints", DataDict())
        
        paramFile.dataDict.pushBack("tune_ipModelDict", DataDict())
        paramFile.dataDict.pushBack("tune_useModelPoints", "False")
        
        paramFile.dataDict.pushBack("lockdown", "False")

        paramFile.write()
    
        #Setup the ScanCollection in the same folder
        ParameterScanCollection.createNew(folder, instName)
    
class Scan2D_TuneException(AcdOptiException_parameterScan):
    pass