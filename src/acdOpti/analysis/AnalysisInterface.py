from acdOpti.AcdOptiFileParser import DataDict
from acdOpti.AcdOptiExceptions import AcdOptiException

import os

#from Dummy import Dummy

class AnalysisInterface:
    lockdown = None
    
    type     = None #Type of analysis
    folder   = None #Base folder for all analysis - they create a file or folder here named <name>
    instName = None #Name of this instance, as specified by AnalysisInterface.getName()
    runConfig = None
    
    exportResults = None #DataDict with numerical results that can be used for meta-analysis (plotting etc.)
    
    def runAnalysis(self):
        """
        Call this method to actually run the analysis on the data.
        Will set lockdown=True.
        """
        raise NotImplementedError
    def clearLockDown(self):
        """
        Call this method to clear a lockdown.
        """
        raise NotImplementedError
    
    def generateRunConfigDict(self):
        """
        Return a DataDict saved by the RunConfig
        specifiying the information neccessary to load the analysis
        using loadAnalysisByDict()
        for loading the analysis . 
        """
        assert self.type in AnalysisInterface.getTypes()
        
        d = DataDict()
        d.pushBack("type", self.type)
        d.pushBack("name", self.instName)
        return d
        
        #Contents of dict:
        # - type: Type of analysis
        # - name: Name of the analysis
    
    @staticmethod
    def getName(type,name=None):
        """
        Gets the name of an analysis without cosntructing it
        """
        if not type in AnalysisInterface.getTypes():
            raise ValueError("Invalid type '" + type + "'")
        if name == None:
            return type
        else:
            return name
    
    @staticmethod
    def loadAnalysisByDict(dataDict, folder, runConfig):
        """
        Use the information in a dataDict
        of the format written by generateRunConfigDict
        to load and return a specific analysis.
        """
        if not dataDict["type"] in AnalysisInterface.getTypes():
            raise AnalysisException_loadFail("Type '" + type + "' is not valid")
        
        name = dataDict["name"]
        
        if not os.path.exists(os.path.join(folder, name)):
            raise AnalysisException_loadFail("No analysis file found?!")
        
        import acdOpti.AcdOptiRunConfig
        assert isinstance(runConfig, acdOpti.AcdOptiRunConfig.AcdOptiRunConfig)
        
        if dataDict["type"] == "Dummy":
            from Dummy import Dummy
            return Dummy(folder, name, runConfig)
        elif dataDict["type"] == "FileList":
            from FileList import FileList
            return FileList(folder,name,runConfig)
        else:
            raise NotImplementedError("This shoudn't happen?!?")
    
    @staticmethod
    def getTypes():
        """
        Returns a list of the currently valid analysis types
        """
        return ["Dummy", "FileList"]
    
    @staticmethod
    def createAndLoadAnalysis(type, runConfig, folder, name=None):
        """
        Creates a new analysis of the specified type,
        with common analysis folder given.
        If name is specified, use this name,
        else use the default for this analysis type.
        
        The created analysis is then loaded and returned.
        
        raises AnalysisException_createFail if something goes wrong.  
        """
        
        if not type in AnalysisInterface.getTypes():
            raise AnalysisException_createFail("Type '" + type + "' is not valid")
        
        name = AnalysisInterface.getName(type, name)
        if os.path.exists(os.path.join(folder, name)):
            raise AnalysisException_loadFail("Analysis file already created?!?")
        
        import acdOpti.AcdOptiRunConfig
        assert isinstance(runConfig, acdOpti.AcdOptiRunConfig.AcdOptiRunConfig)
        
        if type == "Dummy":
            from Dummy import Dummy
            Dummy.createNew(folder, name)
            return Dummy(folder, name, runConfig)
        elif type == "FileList":
            from FileList import FileList
            FileList.createNew(folder,name)
            return FileList(folder,name,runConfig)
        
    @staticmethod
    def createNew(folder, name):
        """
        Create a new analysis of the implementing type
        """
        raise NotImplementedError
        
#Exceptions
def AnalysisException_createFail(AcdOptiException):
    pass
def AnalysisException_loadFail(AcdOptiException):
    pass