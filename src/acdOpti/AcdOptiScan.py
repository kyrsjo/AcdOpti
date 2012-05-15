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
from AcdOptiExceptions import AcdOptiException_scan_createFail,\
                              AcdOptiException_scan_loadFail,\
                              AcdOptiException_scan_scanFail,\
                              AcdOptiException_scan_stageFail,\
                              AcdOptiException_scan_generateRangeFail,\
                              AcdOptiException_scan_runFail,\
                              AcdOptiException_scan_refreshDownloadFail,\
                              AcdOptiException_scan_analysisFail,\
                              AcdOptiException_scan_predictFail,\
                              AcdOptiException_runConfig_stageError,\
                              AcdOptiException_analysis_runAnalysis,\
                              AcdOptiException_dataDict_getValsSingle

import os
import numpy as np
import re

class AcdOptiScan:
    """
    Class representing a geometry parameter scan.
    This class can "own" geometryInstances, just like a geometryCollection
    """
    
    folder = None
    scanCollection = None

    __paramfile = None
    
    instName = None
    lockdown = None #irreversible lockdown on parameters, happens after createScan()
    staged   = None #2'nd "lockdown", indicates that geoms has been staged.
    run      = None #3'rd, indicates that geoms has been uploaded&ran.

    baseGeomInstance = None
    
    slaveGeoms = None
    slaveGeomsDict = None
    
    scanParameter_name = None      #Name of the parameter that should be scanned.
    scanParameter_range_max = None #   If this is set, so should the range stuff.
    scanParameter_range_min = None
    scanParameter_range_step = None #Step length

    scanParameter_range = None #List with wanted values of the scan
    
    predict_anaVariable = None
    predict_targetValue = None
    
    predict_a = None #y=ax+b
    predict_b = None
    predict_x = None #predicted x s.t. y=target
    predict_r = None #sqrt(R^2)
    predict_ndof = None
    
    def __init__(self, folder, scanCollection):
        self.folder = folder
        self.scanCollection = scanCollection
    
        #Construct the instance name from folder
        instName = folder
        if instName[-1] == "/":
            instName = instName[0:-1]
        self.instName = instName = os.path.split(instName)[1]
    
        #Load paramFile
        self.__paramfile = AcdOptiFileParser_simple(os.path.join(folder, "paramFile.set"), 'rw')
        if self.__paramfile.dataDict["fileID"] != "AcdOptiScan":
            raise AcdOptiException_scan_loadFail("Got wrong fileID='" + self.__paramfile.dataDict["fileID"] + "'")            
        
        if self.__paramfile.dataDict.getValSingle("instName") != self.instName:
            raise AcdOptiException_scan_loadFail("instName doesn't match folder name")
        
        self.lockdown = DataDict.boolconv(self.__paramfile.dataDict.getValSingle("lockdown"))
        self.staged  = DataDict.boolconv(self.__paramfile.dataDict.getValSingle("staged"))
        self.run  = DataDict.boolconv(self.__paramfile.dataDict.getValSingle("run"))


        self.slaveGeomsDict = self.__paramfile.dataDict["slaveGeoms"]
        self.slaveGeoms = []
        baseGeomInstance_name = self.__paramfile.dataDict["baseGeomInstance_name"]
        if baseGeomInstance_name == "":
            self.baseGeomInstance = None
            assert len(self.slaveGeoms) == 0
        else:
            self.baseGeomInstance = self.scanCollection.project.geomCollection.geomInstances[baseGeomInstance_name]
        
        if self.__paramfile.dataDict["scanParameter_name"] != "":
            #assert self.baseGeomInstance != None #Why?
            self.scanParameter_name       =  self.__paramfile.dataDict["scanParameter_name"]
            assert self.scanParameter_name in self.getValidParamNames()
            self.scanParameter_range_max  =  float(self.__paramfile.dataDict["scanParameter_max"])
            self.scanParameter_range_min  =  float(self.__paramfile.dataDict["scanParameter_min"])
            self.scanParameter_range_step =  float(self.__paramfile.dataDict["scanParameter_step"])
            
            self.generateRange()
        
        try:
            self.predict_anaVariable = self.__paramfile.dataDict["predict_anaVariable"]
            self.predict_targetValue = self.__paramfile.dataDict["predict_targetValue"]
        except AcdOptiException_dataDict_getValsSingle:
            self.predict_anaVariable = ""
            self.predict_targetValue = ""
            self.__paramfile.dataDict.pushBack("predict_anaVariable", "")
            self.__paramfile.dataDict.pushBack("predict_targetValue", "")
            self.__paramfile.write()
        
        try:
            self.predict_a = self.__paramfile.dataDict["predict_a"]
            self.predict_b = self.__paramfile.dataDict["predict_b"]
            self.predict_x = self.__paramfile.dataDict["predict_x"]
            self.predict_r = self.__paramfile.dataDict["predict_r"]
        except AcdOptiException_dataDict_getValsSingle:
            self.predict_a = ""
            self.predict_b = ""
            self.predict_x = ""
            self.predict_r = ""
            self.__paramfile.dataDict.pushBack("predict_a", "")
            self.__paramfile.dataDict.pushBack("predict_b", "")
            self.__paramfile.dataDict.pushBack("predict_x", "")
            self.__paramfile.dataDict.pushBack("predict_r", "")
            self.__paramfile.write()
        try:
            self.predict_ndof=self.__paramfile.dataDict["predict_ndof"]
        except AcdOptiException_dataDict_getValsSingle:
            self.predict_ndof = ""
            self.__paramfile.dataDict.pushBack("predict_ndof","")
            self.__paramfile.write()
             
        for (geomName, nothingOfInterest) in self.slaveGeomsDict:
            #Mutal referencing
            self.slaveGeoms.append(self.scanCollection.project.geomCollection.geomInstances[geomName])
            self.slaveGeoms[-1].scanInstances.append(self)
    
    def generateRange(self):
        "Generate the scan range"
        if self.scanParameter_range_max == None or self.scanParameter_range_min == None or self.scanParameter_range_step == None:
            raise AcdOptiException_scan_generateRangeFail("Range parameters not set, max='" + str(self.scanParameter_range_max) +\
                                                          "', min='" + str(self.scanParameter_range_min) + "', step='" + str(self.scanParameter_range_step) + "'")
#        if self.lockdown:
#            raise AcdOptiException_scan_generateRangeFail("Can't generate range: In lockdown!")
#        
        self.scanParameter_range = np.arange(self.scanParameter_range_min,\
                                             self.scanParameter_range_max,\
                                             self.scanParameter_range_step)
       
    def write(self):
        if self.baseGeomInstance != None:
            self.__paramfile.dataDict.setValSingle("baseGeomInstance_name", self.baseGeomInstance.instName)
        else:
            self.__paramfile.dataDict.setValSingle("baseGeomInstance_name", "")
        
        if self.scanParameter_name != None:
            self.__paramfile.dataDict.setValSingle("scanParameter_name", self.scanParameter_name)
            assert self.scanParameter_range_max != None and self.scanParameter_range_min != None and self.scanParameter_range_step != None
            self.__paramfile.dataDict.setValSingle("scanParameter_max", str(self.scanParameter_range_max))
            self.__paramfile.dataDict.setValSingle("scanParameter_min", str(self.scanParameter_range_min))
            self.__paramfile.dataDict.setValSingle("scanParameter_step", str(self.scanParameter_range_step))
        else:
            self.__paramfile.dataDict.setValSingle("scanParameter_name", "")
            assert self.scanParameter_range_max == None and self.scanParameter_range_min == None and self.scanParameter_range_step == None
            self.__paramfile.dataDict.setValSingle("scanParameter_max", "")
            self.__paramfile.dataDict.setValSingle("scanParameter_min", "")
            self.__paramfile.dataDict.setValSingle("scanParameter_step", "")
        
        self.slaveGeomsDict.clear()
        if len(self.slaveGeoms) != 0:
            assert self.baseGeomInstance != None
        for geom in self.slaveGeoms:
            self.slaveGeomsDict.pushBack(geom.instName, "")
        
        self.__paramfile.dataDict.setValSingle("lockdown", str(self.lockdown))
        self.__paramfile.dataDict.setValSingle("staged"  , str(self.staged))
        self.__paramfile.dataDict.setValSingle("run"     , str(self.run))
        
        self.__paramfile.dataDict.setValSingle("predict_anaVariable", self.predict_anaVariable)
        self.__paramfile.dataDict.setValSingle("predict_targetValue", self.predict_targetValue)
        
        self.__paramfile.dataDict.setValSingle("predict_a", self.predict_a)
        self.__paramfile.dataDict.setValSingle("predict_b", self.predict_b)
        self.__paramfile.dataDict.setValSingle("predict_x", self.predict_x)
        self.__paramfile.dataDict.setValSingle("predict_r", self.predict_r)
        self.__paramfile.dataDict.setValSingle("predict_ndof", self.predict_ndof)
        
        
        self.__paramfile.write()
    
    def getValidParamNames(self):
        "Selects the name of the scan parameter among the parameters in the geometry"
        return self.scanCollection.project.geomCollection.paramDefaults_getKeys()
    
    
    def createScan(self):
        """
        Using the data in baseGeomInstance_name and the range,
        create the scan. A function that will be called on each iteration may be provided.
        
        If a common error occurs, a AcdOptiException_scan_scanFail with the error message of interest is raised.
        """
        #Check that we are ready to scan
        if self.lockdown:
            raise AcdOptiException_scan_scanFail("Scan already created.")
        
        if not self.scanParameter_name in self.getValidParamNames():
            raise AcdOptiException_scan_scanFail("No (valid) scan parameter selected.")
        
        if self.scanParameter_range_min == None or self.scanParameter_range_max == None or self.scanParameter_range_step == None:
            raise AcdOptiException_scan_scanFail("Scan range not ready.")
        self.generateRange()
        
        if len(self.scanParameter_range) == 0:
            raise AcdOptiException_scan_scanFail("Scan range empty.")
        
        if not self.baseGeomInstance in self.scanCollection.project.geomCollection.geomInstances.values():
            raise AcdOptiException_scan_scanFail("No (valid) geomInstance selected")
        
        for val in self.scanParameter_range:
            self.addPoint(val)
#            oldName = self.baseGeomInstance.instName
#            newName = oldName + "--scan--" + self.scanParameter_name + str(val) #Separators  messes things up..
#            #Check if this already exists:
#            newGeom = None
#            if newName in self.scanCollection.project.geomCollection.geomInstances:
#                #It's already there!
#                newGeom = self.scanCollection.project.geomCollection.geomInstances[newName]
#                newGeom.scanInstances.append(self)
#                #TODO: Now assuming that the name is an unique identifier for a configuration.
#                # This might not be safe - maybe add some kind of lockdown?
#            else:
#                newGeom = self.scanCollection.project.geomCollection.cloneGeomInstance(oldName,newName)
#                newGeom.templateOverrides_insert(self.scanParameter_name, str(val))
#                newGeom.scanInstances.append(self)
#                newGeom.write()
#            self.slaveGeoms.append(newGeom)
        
        self.lockdown = True
        self.write()
    
    def stageAll(self, progressCallback=None):
        """
        Stage all geoms/meshes/runConfigs in self.slaveGeoms
        """
        print "AcdOptiScan::stageAll()"
        if not self.lockdown:
            raise AcdOptiException_scan_stageFail("Lockdown not set, not ready to stage!")
        for geom in self.slaveGeoms:
            for mesh in geom.meshInsts.values():
                for rc in mesh.runConfigs.values():
                    if rc.status == "finished":
                        continue #In case of geom reuse
                    try:
                        rc.stage()
                    except AcdOptiException_runConfig_stageError:
                        print "Staging of rc failed - skipping to the next one."
                    if progressCallback != None:
                        print "AcdOptiScan::stageAll() : progressCallback()"
                        progressCallback()
        self.staged = True
    
    def runScan(self):
        """
        Upload and run all runConfigs
        """
        print "AcdOptiScan::RunScan()"
        if not self.staged:
            raise AcdOptiException_scan_runFail("Not staged yet!")
        
        for geom in self.slaveGeoms:
            for mesh in geom.meshInsts.values():
                for rc in mesh.runConfigs.values():
                    if rc.status != "staged":
                        continue #In case of geom reuse or nongenerated mesh'es
                    rc.upload()
                    rc.run()
                    
        self.run = True
    
    def refreshAndDownload(self):
        """
        Refresh the status on all the runConfigs, download results where finished
        """
        print "AcdOptiScan::refreshAndDownload()"
        if self.run != True:
            raise AcdOptiException_scan_refreshDownloadFail("Not yet ran, run != True")
        
        for geom in self.slaveGeoms:
            for mesh in geom.meshInsts.values():
                for rc in mesh.runConfigs.values():
                    if rc.status.startswith("remote::"):
                        rc.refreshStatus()
                        #TODO: Handle possible local runner?
                        if rc.status == "remote::finished":
                            rc.getRemote()
    
    def runAnalysis(self):
        """
        For all finished runConfigs, run the defined analysis.
        """
        print "AcdOptiScan::runAnalysis()"
        if self.run != True:
            raise AcdOptiException_scan_analysisFail("Not yet ran, run != True")
        
        for geom in self.slaveGeoms:
            for mesh in geom.meshInsts.values():
                for rc in mesh.runConfigs.values():
                    if rc.status.startswith("finished"):
                        for analysis in rc.analysis.values():
                            if not analysis.lockdown:
                                try:
                                    analysis.runAnalysis()
                                except AcdOptiException_analysis_runAnalysis as e:
                                    print "Error in analysis '" + analysis.instName + "': '" + str(e.args) + "', skipping!"
    
    def predictCorrectValue(self):
        """
        Fit the some analysis result versus the scanned parameter,
        and predict the value of this parameter that yields
        the analysis result equals a target value.
        
        Returns: predicted parameter value, sum of squared residuals in fit.
        """
        
        anaVariable = self.predict_anaVariable
        targetValue = float(self.predict_targetValue)
        
        #Get fit data
        x = []
        y = []
        
        anaVarSplit = anaVariable.split(".")
        
        #for geom in self.slaveGeoms:
        for geom in self.scanCollection.project.geomCollection.geomInstances.itervalues():
            #skip geometries which differs in more than one parameter
            goodGeom = True
            for param in self.scanCollection.project.geomCollection.paramDefaults_getKeys():
                if param == self.scanParameter_name:
                    continue
                
                if param in self.baseGeomInstance.templateOverrides_getKeys():
                    paramVal = self.baseGeomInstance.templateOverrides_get(param)
                else:
                    paramVal = self.scanCollection.project.geomCollection.paramDefaults_get(param)
                
                if param in geom.templateOverrides_getKeys():
                    paramVal2 = geom.templateOverrides_get(param)
                else:
                    paramVal2 = self.scanCollection.project.geomCollection.paramDefaults_get(param)
                if paramVal != paramVal2:
                    goodGeom = False
                    break
            if not goodGeom:
                continue #Skip this geometry
            
            #Baseline geom may be included; just skip'it (including it makes it neccessary to rewrite the code below)
            if not self.scanParameter_name in geom.templateOverrides_getKeys():
                continue
            
            thisX=float(geom.templateOverrides_get(self.scanParameter_name))
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
                                    return float(nextBranch)

                            thisY = dictRecDig(anaVarSplit[1:],ana.exportResults)
                            if thisY != None:
                                x.append(thisX)
                                y.append(thisY)
        print "X=", x
        print "Y=", y
        
        #Fit function y = ax+b
        obs = len(y)
        ndof = obs-2
        if ndof < 0:
            raise AcdOptiException_scan_predictFail("ndof = " + str(ndof) + " < 0")
        self.predict_ndof=str(ndof)
        
        H = np.ones([obs,2])
        for i in xrange(obs):
            H[i,1] = x[i]
        project = np.dot(np.linalg.inv(np.dot(H.transpose(),H)), H.transpose())
        
        y = np.asarray(y)
        theta = np.dot(project,y)
        print "THETA=(y0,dy/dx)=", theta
        self.predict_a=str(theta[1])
        self.predict_b=str(theta[0])
        
        
        #Find x such that y=target
        x_predicted = (targetValue-theta[0])/theta[1]
        print "X_PREDICTED=",x_predicted
        self.predict_x = str(x_predicted)
        
        #Calculate R^2
        R2 = 0.0
        for i in xrange(obs):
            yhat = theta[0] + theta[1]*x[i]
            print "Y YHAT = ", y[i], yhat, yhat-y[i] 
            R2 += (yhat-y[i])**2
        print "sqrt(R**2)=", np.sqrt(R2)
        self.predict_r = str(np.sqrt(R2))
        
        self.write()
        
    def addPoint(self,parameterValue):
        """
        Add a point to the scan with the given parameter value
        """
        oldName = self.baseGeomInstance.instName
        newName = oldName + "--scan--" + self.scanParameter_name + str(parameterValue) #Separators  messes things up..
        #Check if this already exists:
        newGeom = None
        if newName in self.scanCollection.project.geomCollection.geomInstances:
            #It's already there!
            newGeom = self.scanCollection.project.geomCollection.geomInstances[newName]
            newGeom.scanInstances.append(self)
            #TODO: Now assuming that the name is an unique identifier for a configuration.
            # This might not be safe - maybe add some kind of lockdown?
        else:
            newGeom = self.scanCollection.project.geomCollection.cloneGeomInstance(oldName,newName)
            newGeom.templateOverrides_insert(self.scanParameter_name, str(parameterValue))
            newGeom.scanInstances.append(self)
            newGeom.write()
        self.slaveGeoms.append(newGeom)
    
    @staticmethod
    def createNew(folder):
        #Construct the instance name from folder
        instName = folder
        if instName[-1] == "/":
            instName = instName[0:-1]
        instName = os.path.split(instName)[1]
        if os.path.isdir(folder):
            raise AcdOptiException_scan_createFail("Folder \"" + folder + "\" already exists")
        os.mkdir(folder)
        
        #Create paramfile
        paramFile = AcdOptiFileParser_simple(os.path.join(folder, "paramFile.set"), 'w')
        paramFile.dataDict.pushBack("fileID", "AcdOptiScan")
        paramFile.dataDict.pushBack("instName", instName)
        paramFile.dataDict.pushBack("lockdown", "False")
        paramFile.dataDict.pushBack("staged", "False")
        paramFile.dataDict.pushBack("run", "False")
        
        paramFile.dataDict.pushBack("baseGeomInstance_name", "")
        
        paramFile.dataDict.pushBack("slaveGeoms", DataDict())
        
        paramFile.dataDict.pushBack("scanParameter_name", "")
        paramFile.dataDict.pushBack("scanParameter_max", "")
        paramFile.dataDict.pushBack("scanParameter_min","")
        paramFile.dataDict.pushBack("scanParameter_step","")
        
        paramFile.dataDict.pushBack("predict_anaVariable", "")
        paramFile.dataDict.pushBack("predict_targetValue", "")
        
        paramFile.dataDict.pushBack("predict_a", "")
        paramFile.dataDict.pushBack("predict_b", "")
        paramFile.dataDict.pushBack("predict_x", "")
        paramFile.dataDict.pushBack("predict_r", "")
        paramFile.dataDict.pushBack("predict_ndof", "")
        
        paramFile.write()