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

from AnalysisInterface import AnalysisInterface
from acdOpti.AcdOptiFileParser import DataDict, AcdOptiFileParser_simple
from acdOpti.AcdOptiExceptions import AcdOptiException,\
                                      AcdOptiException_analysis,\
                                      AcdOptiException_analysis_runAnalysis

import os

class FileList(AnalysisInterface):
    """
    Simple analysis that lists the files in the finished folder
    """
    
    __paramFile = None
    
    def __init__(self, folder, name, runConfig):
        print "FileList::__init__()"
        self.type      = "FileList"
        self.folder    = folder
        self.instName  = name
        self.runConfig = runConfig
        
        self.__paramFile = AcdOptiFileParser_simple(os.path.join(folder, name), 'rw')
        if self.__paramFile.dataDict["fileID"] != "Analysis::FileList":
            raise FileListException("Got fileID='" + self.__paramFile.dataDict["fileID"] + "'")
        self.lockdown = DataDict.boolconv(self.__paramFile.dataDict["lockdown"])

        self.exportResults = self.__paramFile.dataDict["export"]
    
    def runAnalysis(self):
        finishedFolder = self.runConfig.finishedFolder
        if finishedFolder == None:
            raise FileListException_runAna("No data to analyse")
        self.__recursiveDirList(self.exportResults["files"], finishedFolder)
        self.lockdown = True
        self.write()
    def __recursiveDirList(self,storeDict,path):
        dirlist = os.listdir(path)
        for entry in dirlist:
            path2 = os.path.join(path, entry)
            if os.path.isdir(path2):
                folderDict = storeDict.pushBack(entry, DataDict())
                self.__recursiveDirList(folderDict, path2)
            else:
                storeDict.pushBack(entry, "")
        
        
    def clearLockdown(self):
        print "FileList::clearLockdown()"
        self.exportResults["files"].clear()
        self.lockdown = False
        self.write()
    
    def write(self):
        self.__paramFile.dataDict.setValSingle("lockdown", str(self.lockdown))
        self.__paramFile.write()
    
    @staticmethod
    def createNew(folder,name):
        paramFile = AcdOptiFileParser_simple(os.path.join(folder,name), "w")
        paramFile.dataDict.pushBack("fileID", "Analysis::FileList")
        paramFile.dataDict.pushBack("lockdown", "False")
        paramFile.dataDict.pushBack("export", DataDict())
        paramFile.dataDict["export"].pushBack("files", DataDict())
        paramFile.write()
    
#    @staticmethod
#    def createNew_clone(folder,cloneFrom,newRunConfig):
#        newFileList = FileList.createNew(folder, cloneFrom.name)
#        return FileList(folder,cloneFrom.name,newRunConfig)
    
class FileListException(AcdOptiException_analysis):
    pass
class FileListException_runAna(AcdOptiException_analysis_runAnalysis):
    pass    