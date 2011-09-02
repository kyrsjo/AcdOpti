from AcdOptiFileParser import AcdOptiFileParser_simple, DataDict
from AcdOptiExceptions import AcdOptiException_scan_createFail,\
                              AcdOptiException_scan_loadFail
import os

import numpy as np

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

    baseGeomInstance = None
    
    slaveGeoms = None
    slaveGeomsDict = None
    
    scanParameter_name = None      #Name of the parameter that should be scanned.
    scanParameter_range_max = None #   If this is set, so should the range stuff.
    scanParameter_range_min = None
    scanParameter_range_step = None #Step length

    scanParameter_range = None #List with wanted values of the scan
    
    
    
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
            
            
            self.scanParameter_range = np.arange(self.scanParameter_range_min,\
                                                 self.scanParameter_range_max,\
                                                 self.scanParameter_range_step)
        
        for (geomName, nothingOfInterest) in self.slaveGeomsDict:
            self.slaveGeoms.append(self.scanCollection.project.geomCollection.geomInstances[geomName])
            
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
        
        self.__paramfile.write()
    
    def getValidParamNames(self):
        "Selects the name of the scan parameter among the parameters in the geometry"
        return self.scanCollection.project.geomCollection.paramDefaults_getKeys()
    
    
    def createScan(self, progressCallback = None):
        """
        Using the data in baseGeomInstance_name and the range,
        create the scan. A function that will be called on each iteration may be provided.
        """
        assert self.scanParameter_range != None
        assert self.baseGeomInstance in self.scanCollection.project.geomCollection.geomInstances.values()
        assert not self.lockdown
        
        for val in self.scanParameter_range:
            oldName = self.baseGeomInstance.instName
            newName = oldName + "--scan--" + self.scanParameter_name + "#" + str(val)
            newGeom = self.scanCollection.project.geomCollection.cloneGeomInstance(oldName,newName)
            self.slaveGeoms.append(newGeom)
            if progressCallback != None:
                progressCallback()
        
        self.lockdown = True
        self.write()
        
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
        
        paramFile.dataDict.pushBack("baseGeomInstance_name", "")
        
        paramFile.dataDict.pushBack("slaveGeoms", DataDict())
        
        paramFile.dataDict.pushBack("scanParameter_name", "")
        paramFile.dataDict.pushBack("scanParameter_max", "")
        paramFile.dataDict.pushBack("scanParameter_min","")
        paramFile.dataDict.pushBack("scanParameter_step","")
        
        
        paramFile.write()