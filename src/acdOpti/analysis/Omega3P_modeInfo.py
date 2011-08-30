from AnalysisInterface import AnalysisInterface
from acdOpti.AcdOptiFileParser import DataDict, AcdOptiFileParser_simple, AcdOptiFileParser_KVC
from acdOpti.AcdOptiExceptions import AcdOptiException

import os

class Omega3P_modeInfo(AnalysisInterface):
    """
    Analysis that presents the information
    being output directly from Omega3P per mode 
    """
    __paramFile = None
    
    def __init__(self, folder, name, runConfig):
        print "Omega3P_modeInfo::__init__()"
        self.type      = "Omega3P_modeInfo"
        self.folder    = folder
        self.instName  = name
        self.runConfig = runConfig
        
        self.__paramFile = AcdOptiFileParser_simple(os.path.join(folder, name), 'rw')
        if self.__paramFile.dataDict["fileID"] != "Analysis::Omega3P_modeInfo":
            raise Omega3P_modeInfo_exception("Got fileID='" + self.__paramFile.dataDict["fileID"] + "'")
        self.lockdown = DataDict.boolconv(self.__paramFile.dataDict["lockdown"])

        self.exportResults = self.__paramFile.dataDict["export"]
    
    def runAnalysis(self):
        finishedFolder = self.runConfig.finishedFolder
        if finishedFolder == None:
            raise Omega3P_modeInfo_exception("No data to analyse")
        
        outputFilePath = os.path.join(finishedFolder, "output")
        outputFile = open(outputFilePath, "r")
        #Find the lines with KVC syntax
#        data = ""
#        lastLineWasComment = True
#        for line in outputFile.readlines():
#            ls = line.strip()
#            if ls.startswith("/*") and ls.endswith("*/"):
#                if lastLineWasComment:
#                    continue #comments at beginning
#                else:
#                    break #comments at end
#            #Not a comment line
#            data += line
#            lastLineWasComment = False
#        
        
        #Find the lines relating to mode (else the timestamps will crash the parser due to extra ":")
        thereYet=False
        data = ""
        for line in outputFile.readlines():
            ls = line.strip()
            if ls.startswith("Mode :"):
                thereYet = True
            elif not thereYet:
                continue
            elif ls.startswith("Mesh :"):
                break
            data += line
        print data
        
        dataParser = AcdOptiFileParser_KVC(data,"s")
        self.exportResults.setValSingle("modes", dataParser.dataDict.copy())
        
        self.lockdown = True
        self.write()
    def clearLockdown(self):
        self.exportResults["modes"].clear()
        self.lockdown = False
        self.write()
    
    def write(self):
        self.__paramFile.dataDict.setValSingle("lockdown", str(self.lockdown))
        self.__paramFile.write()
    
    @staticmethod
    def createNew(folder,name=None):
        paramFile = AcdOptiFileParser_simple(os.path.join(folder,name), "w")
        paramFile.dataDict.pushBack("fileID", "Analysis::Omega3P_modeInfo")
        paramFile.dataDict.pushBack("lockdown", "False")
        paramFile.dataDict.pushBack("export", DataDict())
        paramFile.dataDict["export"].pushBack("modes", DataDict())
        paramFile.write()

class Omega3P_modeInfo_exception(AcdOptiException):
        pass