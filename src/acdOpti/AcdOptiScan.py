from AcdOptiFileParser import AcdOptiFileParser_simple, DataDict
from AcdOptiExceptions import AcdOptiException_scan_createFail,\
                              AcdOptiException_scan_loadFail
import os

class AcdOptiScan:
    """
    Class representing a geometry parameter scan.
    This class can "own" geometryInstances, just like a geometryCollection
    """
    
    folder = None
    scanCollection = None

    __paramfile = None
    
    instName = None
    lockdown = None
    
    baseGeomInstance = None
    
    scanParameter_name = None  #Name of the parameter that should be scanned
    scanParameter_range = None #List with wanted values of the scan
    scanParameter_range_max = None
    scanParameter_range_min = None
    scanParameter_range_step = None
    
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
    
        baseGeomInstance_name = self.__paramfile.dataDict["baseGeomInstance_name"]
        if baseGeomInstance_name == "":
            self.baseGeomInstance = None
        else:
            self.baseGeomInstance = self.scanCollection.project.geomCollection.geomInstances["baseGeomInstance_name"]
        
        if self.__paramfile.dataDict["scanParameter_name"] != "":
            assert self.baseGeomInstance != None
            self.scanParameter_name       =  self.__paramfile.dataDict["scanParameter_name"]
            assert self.scanParameter_name in self.getValidParamNames()
            self.scanParameter_range_max  =  self.__paramfile.dataDict["scanParameter_max"]
            self.scanParameter_range_min  =  self.__paramfile.dataDict["scanParameter_min"]
            self.scanParameter_range_step =  self.__paramfile.dataDict["scanParameter_step"]
        
    
    def getValidParamNames(self):
        "Selects the name of the scan parameter among the parameters in the geometry"
        return self.scanCollection.project.geomCollection.paramDefaults_getKeys()
        
        
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
        
        paramFile.dataDict.pushBack("scanParameter_name", "")
        paramFile.dataDict.pushBack("scanParameter_max", "")
        paramFile.dataDict.pushBack("scanParameter_min","")
        paramFile.dataDict.pushBack("scanParameter_step","")
        
        paramFile.write()