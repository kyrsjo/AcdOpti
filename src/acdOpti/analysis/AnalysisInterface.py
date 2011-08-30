from acdOpti.AcdOptiFileParser import DataDict
from acdOpti.AcdOptiExceptions import AcdOptiException

#from Dummy import Dummy

class AnalysisInterface:
    lockdown = None
    
    type     = None #Type of analysis
    folder   = None #Base folder for all analysis - they create a file or folder here named <name>
    instName = None #Name of this instance, as specified by AnalysisInterface.getName()
    
    exportResults = None #DataDict with numerical results that can be used for meta-analysis
    
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
    def loadAnalysisByDict(dataDict, folder):
        """
        Use the information in a dataDict
        of the format written by generateRunConfigDict
        to load and return a specific analysis.
        """
        if not dataDict["type"] in AnalysisInterface.getTypes():
            raise AnalysisException_createFail("Type '" + type + "' is not valid")
        
        if dataDict["type"] == "Dummy":
            from Dummy import Dummy
            return Dummy(folder, dataDict["name"])
    
    @staticmethod
    def getTypes():
        """
        Returns a list of the currently valid analysis types
        """
        return ["Dummy"]
    
    @staticmethod
    def createAndLoadAnalysis(type, folder, name=None):
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
        
        if type == "Dummy":
            from Dummy import Dummy
            Dummy.createNew(folder, name)
            return Dummy(folder, name)
        
    @staticmethod
    def createNew(folder, name):
        """
        Create a new analysis of the implementing type
        """
        raise NotImplementedError
        
#Exceptions
def AnalysisException_createFail(AcdOptiException):
    pass