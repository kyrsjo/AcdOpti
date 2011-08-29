from acdOpti.AcdOptiFileParser import DataDict

class AnalysisInterface():
    def generateRunConfigDict(self):
        """
        Return a DataDict used by the RunConfig
        for loading the analysis . 
        """
        raise NotImplementedError
        #Contents of dict:
        # -name:
        # -type:
    
    @staticmethod
    def loadAnalysisByDict(dataDict):
        """
        Use the information in a dataDict
        of the format written by generateRunConfigDict
        to load and return a specific analysis.
        """
        raise NotImplementedError