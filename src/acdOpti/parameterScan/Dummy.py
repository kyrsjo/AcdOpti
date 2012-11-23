# -*- coding: utf8 -*-
#
# Copyright 2012 Kyrre Ness Sjøbæk
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

from acdOpti.AcdOptiFileParser import DataDict, AcdOptiFileParser_simple
from acdOpti.AcdOptiExceptions import AcdOptiException_parameterScan

from ParameterScanInterface import ParameterScanInterface

import os

class Dummy(ParameterScanInterface):
    
    def __init__(self, folder, collection):
        print "Dummy::__init__()"
        super(Dummy,self).__init__(folder,collection,"ParameterScan::Dummy")
        
        
    @staticmethod
    def createNew(folder):
        if os.path.exists(folder):
            raise DummyException("Folder \"" + folder + "\" already exists")
        os.mkdir(folder)
        
        paramFile = AcdOptiFileParser_simple(os.path.join(folder,"paramFile_scan.set"), "w")
        paramFile.dataDict.pushBack("fileID", "ParameterScan::Dummy")
        
        #Construct the instance name from folder
        instName = folder
        if instName[-1] == "/":
            instName = instName[0:-1]
        instName = instName = os.path.split(instName)[1]
        paramFile.dataDict.pushBack("instName", instName)
        
        paramFile.dataDict.pushBack("baseGeomInstance_name", "")
        paramFile.dataDict.pushBack("slaveGeoms", DataDict())

        paramFile.write()
    
    
class DummyException(AcdOptiException_parameterScan):
    pass