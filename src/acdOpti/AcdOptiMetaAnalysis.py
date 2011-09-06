

from AcdOptiFileParser import AcdOptiFileParser_simple, DataDict
from AcdOptiExceptions import AcdOptiException_metaAnalysis_createFail,\
                              AcdOptiException_metaAnalysis_loadFail

import os

class AcdOptiMetaAnalysis:
    """
    A meta-analysis is an analysis of several other anlysis;
    i.e. "plotting" the exported output from analysis
    or geometry/mesh variables against each other.
    """
    
    instName    = None
    
    folder      = None
    collection  = None
    
    __paramfile = None
    
    #Encodings describing where to get the x- or y variables.
    # Meta-language: {GEOM|MESH|ANA}.key([idx]).key([idx]) ...
    xVariable = None 
    yVariable = None
    
    xArray = None 
    yArray = None
    
    lockdown = None
    
    def __init__(self,folder,collection):
        self.folder = folder
        self.collection = collection
    
        #Construct the instance name from folder
        instName = folder
        if instName[-1] == "/":
            instName = instName[0:-1]
        self.instName = instName = os.path.split(instName)[1]
    
        #Load paramFile
        self.__paramfile = AcdOptiFileParser_simple(os.path.join(folder, "paramFile.set"), 'rw')
        if self.__paramfile.dataDict["fileID"] != "AcdOptiMetaAnalysis":
            raise AcdOptiException_metaAnalysis_loadFail("Got wrong fileID='" + self.__paramfile.dataDict["fileID"] + "'")            
        
        if self.__paramfile.dataDict.getValSingle("instName") != self.instName:
            raise AcdOptiException_metaAnalysis_loadFail("instName doesn't match folder name")
        
        self.lockdown = DataDict.boolconv(self.__paramfile.dataDict.getValSingle("lockdown"))
        
        xVariable = self.__paramfile.dataDict["xVariable"]
        if xVariable != "":
            self.xVariable = xVariable
        yVariable = self.__paramfile.dataDict["yVariable"]
        if yVariable != "":
            self.yVariable = yVariable
        
        anaData = self.__paramfile.dataDict["anaData"]
        xArray = []
        yArray = []
        for (x,y) in anaData: 
            xArray.append(x)
            yArray.append(y)
        
        
    def write(self):
        pass
    
    def runAnalysis(self):
        pass
    
    def clearLockdown(self):
        pass
    
    def exportData(self, fileName):
        pass
    
    @staticmethod
    def createNew(folder):
        #Construct the instance name from folder
        instName = folder
        if instName[-1] == "/":
            instName = instName[0:-1]
        instName = os.path.split(instName)[1]
        if os.path.isdir(folder):
            raise AcdOptiException_metaAnalysis_createFail("Folder \"" + folder + "\" already exists")
        os.mkdir(folder)
        
        #Create paramfile
        paramFile = AcdOptiFileParser_simple(os.path.join(folder, "paramFile.set"), 'w')
        paramFile.dataDict.pushBack("fileID", "AcdOptiMetaAnalysis")
        paramFile.dataDict.pushBack("instName", instName)
        
        paramFile.dataDict.pushBack("xVariable", "")
        paramFile.dataDict.pushBack("yVariable", "")
        
        paramFile.dataDict.pushBack("anaData", DataDict()) #(key, value) = (x,y)
        
        paramFile.dataDict.pushBack("lockdown", "False")
        
        paramFile.write()