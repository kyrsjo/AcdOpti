from AcdOptiExceptions import AcdOptiException_metaAnalysisCollection_loadFail
from AcdOptiFileParser import AcdOptiFileParser_simple
from AcdOptiMetaAnalysis import AcdOptiMetaAnalysis

import os


class AcdOptiMetaAnalysisCollection:
    """
    This class organizes the metaAnalysis,
    just like scanCollection organizes scans etc.  
    """
    
    folder = None
    project = None
    
    __paramFile = None
    
    metaAnalysis = None
    
    def __init__(self, folder, project):
        self.folder = folder
        self.project = project
        
        #Load paramFile (check that the folder is of the wanted type)
        self.__paramfile = AcdOptiFileParser_simple(os.path.join(folder, "paramFile.set"), 'rw')
        if self.__paramfile.dataDict["fileID"] != "AcdOptiMetaAnalysisCollection":
            raise AcdOptiException_metaAnalysisCollection_loadFail("Got wrong fileID='" + self.paramFile.dataDict["fileID"] + "'")            
        
        #Look for children metaAnalysis
        self.metaAnalysis = {}
        dirlist = os.listdir(folder)
        for d in dirlist:
            dAbs = os.path.join(folder, d)
            if os.path.isdir(dAbs):
                self.metaAnalysis[d] = AcdOptiMetaAnalysis(dAbs, self)
    
    def add(self, name):
        """
        Try to add a new metaAnalysis with the given name.
        AcdOptiException_metaAnalysis_createFail
        is raised if there is a problem (name already taken).
        """
        
        anaFolder = os.path.join(self.folder, name)
        AcdOptiMetaAnalysis.createNew(anaFolder)
        self.metaAnalysis[name] = AcdOptiMetaAnalysis(anaFolder, self) 
    
    @staticmethod
    def createNew(folder):
        os.mkdir(folder)
    
        paramFile = AcdOptiFileParser_simple(os.path.join(folder,"paramFile.set"), 'w')
        paramFile.dataDict.pushBack("fileID", "AcdOptiMetaAnalysisCollection")
        paramFile.write()
        