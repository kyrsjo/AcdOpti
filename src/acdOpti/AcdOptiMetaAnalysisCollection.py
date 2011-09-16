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
        