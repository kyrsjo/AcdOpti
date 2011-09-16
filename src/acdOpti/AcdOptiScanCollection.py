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
    