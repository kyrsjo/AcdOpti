from acdOpti.AcdOptiScan import AcdOptiScan
from AcdOptiFileParser import AcdOptiFileParser_simple
from AcdOptiExceptions import AcdOptiException_scanCollection_loadFail,\
                              AcdOptiException_scanCollection_createFail
import os

class AcdOptiScanCollection:
    """
    Collection class organizing the contents of the geomScans folder.
    """

    folder  = None
    project = None
    
    __paramfile = None
    
    scans = None
    
    def __init__(self, folder, project):
        self.folder = folder
        self.project = project
        
        #Load paramFile
        self.__paramfile = AcdOptiFileParser_simple(os.path.join(folder, "paramFile.set"), 'rw')
        if self.__paramfile.dataDict["fileID"] != "AcdOptiScanCollection":
            raise AcdOptiException_scanCollection_loadFail("Got wrong fileID='" + self.paramFile.dataDict["fileID"] + "'")            
        
        #Look for scans
        self.scans = {}
        dirlist = os.listdir(folder)
        for d in dirlist:
            dAbs = os.path.join(folder, d)
            if os.path.isdir(dAbs):
                self.scans[d] = AcdOptiScan(dAbs, self)
    
    def add(self, name):
        """
        Try to add a new scan with the given name.
        AcdOptiException_scan_createFail
        is raised if there is a problem (name already taken).
        """
        scanFolder = os.path.join(self.folder, name)
        AcdOptiScan.createNew(scanFolder)
        self.scans[name] = AcdOptiScan(scanFolder, self) 
    
    @staticmethod
    def createNew(folder):
        os.mkdir(folder)
        
        paramFile = AcdOptiFileParser_simple(os.path.join(folder,"paramFile.set"), 'w')
        paramFile.dataDict.pushBack("fileID", "AcdOptiScanCollection")
        paramFile.write()
    