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

from AnalysisInterface import AnalysisInterface
from acdOpti.AcdOptiFileParser import DataDict, AcdOptiFileParser_simple
from acdOpti.AcdOptiExceptions import AcdOptiException, AcdOptiException_dataDict_getValsSingle

import os

class GroupVelocity(AnalysisInterface):
    """
    Calculate the group velocity of the cell by powerFlow,
    cell length (both from RFpost_local), and stored energy (Omega3P_modeInfo)
    """
    __paramFile = None
    
    def __init__(self, folder, name, runConfig):
        print "GroupVelocity::__init__()"
        self.type     = "GroupVelocity"
        self.folder   = folder
        self.instName = name
        self.runConfig = runConfig
        
        self.__paramFile = AcdOptiFileParser_simple(os.path.join(folder, name), 'rw')
        if self.__paramFile.dataDict["fileID"] != "Analysis::GroupVelocity":
            raise GroupVelocityException("Got fileID='" + self.__paramFile.dataDict["fileID"] + "'")
        self.lockdown = DataDict.boolconv(self.__paramFile.dataDict["lockdown"])

        self.exportResults = self.__paramFile.dataDict["export"]

        self.settings = self.__paramFile.dataDict["settings"]
    
    def runAnalysis(self):
        print "GroupVelocity::RunAnalysis()"
        assert not self.lockdown
        
        try:
            surfID = int(self.settings["SurfaceID"])
        except ValueError:
            raise GroupVelocityException("SurfaceID setting not understood")
        
        try:
            RFpost = self.runConfig.analysis[self.settings["RFpostName"]]
        except KeyError:
            raise GroupVelocityException("Key for RFpostName not found")
        if not RFpost.lockdown:
            RFpost.runAnalysis() 
        
        try:
            ModeInfo = self.runConfig.analysis[self.settings["ModeInfoName"]] 
        except KeyError:
            raise GroupVelocityException("Key for ModeInfoName not found")
        if not ModeInfo.lockdown:
            ModeInfo.runAnalysis()
        
        #So far, only analyse 1st mode
        
        power = None
        try:
            powerThroughSurface = RFpost.exportResults["powerThroughSurface"]
        except AcdOptiException_dataDict_getValsSingle:
            raise GroupVelocityException("Couldn't find powerThroughSurface data")
        if len(powerThroughSurface) == 0:
            raise GroupVelocityException("powerThroughSurface data empty")
        
        for (key, val) in powerThroughSurface:
            assert key == "surf"
            if val["surfaceID"] == str(surfID):
                power = float(val["Power_real"])
        if power == None:
            raise GroupVelocityException("Surface " + str(surfID) + " not found")
        
        #length = None
        length = float(RFpost.settings["L"])/1000.0 #mm->meters
        
        energy = None
        modes = ModeInfo.exportResults.getVals("Mode")
        if len(modes) == 0:
            raise GroupVelocityException("No mode found")
        if "TotalEnergyReal" in modes[0]:
            energy = float(modes[0]["TotalEnergyReal"])
        elif "TotalEnergy" in modes[0]:
            energy = float(modes[0]["TotalEnergyReal"])
        else:
            raise GroupVelocityException("Total energy not found")
        assert energy != None
        
        #print "L =", length
        #print "P =", power
        #print "U =", energy
        
        vg = length*power/energy
        self.exportResults.pushBack("VG", str(vg))
        self.exportResults.pushBack("VG_cp", str(100.0*vg/3e8))
        
        self.lockdown = True
        self.write()
        
    def clearLockdown(self):
        print "GroupVelocity::clearLockdown()"
        self.exportResults.clear()
        self.lockdown = False
        self.write()
    
    def write(self):
        self.__paramFile.dataDict.setValSingle("lockdown", str(self.lockdown))
        self.__paramFile.write()
    
    @staticmethod
    def createNew(folder,name):
        paramFile = AcdOptiFileParser_simple(os.path.join(folder,name), "w")
        paramFile.dataDict.pushBack("fileID", "Analysis::GroupVelocity")
        paramFile.dataDict.pushBack("lockdown", "False")

        paramFile.dataDict.pushBack("export", DataDict())

        paramFile.dataDict.pushBack("settings", DataDict())
        paramFile.dataDict["settings"].pushBack("ModeInfoName", "Omega3P_modeInfo")
        paramFile.dataDict["settings"].pushBack("RFpostName", "RFpost_local")
        paramFile.dataDict["settings"].pushBack("SurfaceID", "")
        
        paramFile.write()

class GroupVelocityException(AcdOptiException):
        pass