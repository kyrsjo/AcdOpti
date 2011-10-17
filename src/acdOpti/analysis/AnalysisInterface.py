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


from acdOpti.AcdOptiFileParser import DataDict
from acdOpti.AcdOptiExceptions import AcdOptiException


import os
#from acdOpti import AcdOptiExceptions

class AnalysisInterface:
    lockdown = None
    
    type     = None #Type of analysis
    folder   = None #Base folder for all analysis - they create a file or folder here named <name>
    instName = None #Name of this instance, as specified by AnalysisInterface.getName()
    runConfig = None
    
    exportResults = None #DataDict with numerical results that can be used for meta-analysis (plotting etc.)
    settings      = None #Optional flat (no branches) DataDict with settings specific for this analysis instance
                         #      (file names within result folders, weight factors etc.)
    
    def runAnalysis(self):
        """
        Call this method to actually run the analysis on the data.
        Will set lockdown=True.
        """
        raise NotImplementedError
    def clearLockdown(self):
        """
        Call this method to clear a lockdown.
        """
        print "AnalysisIterface::clearLockDown()"
        #pass
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
        elif dataDict["type"] == "DummyInput":
            from DummyInput import DummyInput
            return DummyInput(folder,name,runConfig)
        elif dataDict["type"] == "FileList":
            from FileList import FileList
            return FileList(folder,name,runConfig)
        elif dataDict["type"] == "Omega3P_modeInfo":
            from Omega3P_modeInfo import Omega3P_modeInfo
            return Omega3P_modeInfo(folder,name,runConfig)
        elif dataDict["type"] == "RFpost":
            from RFpost import RFpost
            return RFpost(folder, name, runConfig)
        else:
            raise NotImplementedError("This shoudn't happen?!?")
    
    @staticmethod
    def getTypes():
        """
        Returns a list of the currently valid analysis types
        """
        return ["Dummy", "DummyInput", "FileList", "Omega3P_modeInfo", "RFpost"]
    
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
            raise AnalysisException_createFail("Analysis file already created?!?")
        
        import acdOpti.AcdOptiRunConfig
        assert isinstance(runConfig, acdOpti.AcdOptiRunConfig.AcdOptiRunConfig)
        
        if type == "Dummy":
            from Dummy import Dummy
            Dummy.createNew(folder, name)
            return Dummy(folder, name, runConfig)
        if type == "DummyInput":
            from DummyInput import DummyInput
            DummyInput.createNew(folder, name)
            return DummyInput(folder, name, runConfig)
        elif type == "FileList":
            from FileList import FileList
            FileList.createNew(folder,name)
            return FileList(folder,name,runConfig)
        elif type == "Omega3P_modeInfo":
            from Omega3P_modeInfo import Omega3P_modeInfo
            Omega3P_modeInfo.createNew(folder, name)
            return Omega3P_modeInfo(folder,name,runConfig)
        elif type == "RFpost":
            from RFpost import RFpost
            RFpost.createNew(folder, name)
            return RFpost(folder, name, runConfig)
        else:
            raise AnalysisException_createFail("Unknown analysis type '" + type + "'")
    @staticmethod
    def createNew(folder, name):
        """
        Create a new analysis of the implementing type
        """
        raise NotImplementedError

    @classmethod
    def createNew_clone(cls, folder,cloneFrom,newRunConfig):
        """
        Clone an already existing analysis
        of the implementing type.
        """
        cls.createNew(folder, cloneFrom.instName)
        newAna = cls(folder,cloneFrom.instName,newRunConfig)
        if cloneFrom.settings != None:
            newAna.settings = cloneFrom.settings.copy()
            newAna.write()
            
        return newAna
        
        
##Exceptions
class AnalysisException_createFail(AcdOptiException):
    pass
class AnalysisException_loadFail(AcdOptiException):
    pass