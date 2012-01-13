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
from acdOpti.AcdOptiExceptions import AcdOptiException,\
                                      AcdOptiException_dataDict_getValsSingle,\
                                      AcdOptiException_analysis,\
                                      AcdOptiException_analysis_runAnalysis

import os
import numpy as np
import math

class ScMax(AnalysisInterface):
    """
    Calculate the peak Sc value using a fieldOnSurface file
    """
    __paramFile = None
    
    def __init__(self, folder, name, runConfig):
        print "ScMax::__init__()"
        self.type     = "ScMax"
        self.folder   = folder
        self.instName = name
        self.runConfig = runConfig
        
        self.__paramFile = AcdOptiFileParser_simple(os.path.join(folder, name), 'rw')
        if self.__paramFile.dataDict["fileID"] != "Analysis::ScMax":
            raise ScMaxException("Got fileID='" + self.__paramFile.dataDict["fileID"] + "'")
        self.lockdown = DataDict.boolconv(self.__paramFile.dataDict["lockdown"])

        self.exportResults = self.__paramFile.dataDict["export"]

        self.settings = self.__paramFile.dataDict["settings"]
    
    @staticmethod
    def crossProd(a,b):
        r = np.array((a[1]*b[2]-a[2]*b[1], -a[0]*b[2]+a[2]*b[0], a[0]*b[1]-a[1]*b[0]))
        return r
    @staticmethod
    def complexConjVec(a):
        r = np.empty_like(a);
        for i in xrange(len(a)):
            r[i] = complex(a[i].real, -a[i].imag)
        return r
    @staticmethod
    def makeComplxVec(ampl, phas):
        r = np.array(map(lambda (a,p): complex(a*math.cos(p),a*math.sin(p)),zip(ampl,phas)))
        return r
    mu0 = (4e-7*np.pi)
    
    def runAnalysis(self):
        print "ScMax::RunAnalysis()"
        assert not self.lockdown
        
        try:
            RFpost = self.runConfig.analysis[self.settings["RFpostName"]]
        except KeyError:
            raise ScMaxException_runAna("Key for RFpostName not found")
        if not RFpost.lockdown:
            RFpost.runAnalysis() 
        
        #Load the files
        print "Loading files..."
        basefname = os.path.join(RFpost.folder, RFpost.instName, self.settings["fieldOnSurface_basename"])
        try:
            file_eField = open(basefname + ".e", 'r');
            file_bField = open(basefname + ".b", 'r');
        except IOError:
            raise ScMaxException_runAna("Could not open file(s)")
        (Epos,Eampl,Ephas) = self.__readfile(file_eField)
        (Bpos,Bampl,Bphas) = self.__readfile(file_bField)
        file_eField.close()
        file_bField.close()
        
        #Calculate Sc in every point, find the maximum
        print "Calculating..."
        maxPos = None
        maxSc = -1.0
        
        for i in xrange(len(Epos)):
            #Complex S-vectorfield, frequency domain definition
            S = 0.5 * self.crossProd( self.makeComplxVec(Eampl[i],Ephas[i]), self.complexConjVec(self.makeComplxVec(Bampl[i]/self.mu0,Bphas[i])) )
            Sc = np.sqrt(np.sum((np.abs(np.real(S))+np.abs(np.imag(S))/6.0)**2))
            if Sc > maxSc:
                maxSc = Sc
                maxPos = Epos[i]
                #assert Epos[i] == Bpos[i]

        #Try to find Ez_ave for the right surface
        Ez_ave = None
        if "RoverQ" in RFpost.exportResults:
            RoQ = RFpost.exportResults["RoverQ"]
            try:
                Ez_ave = float(RoQ["mode"]["Ez_ave"])
            except AcdOptiException_dataDict_getValsSingle:
                print "Couldn't find normalization"
        
        
        self.exportResults.pushBack("maxSc", str(maxSc))
        if Ez_ave != None:
            self.exportResults.pushBack("maxSc_norm", str(maxSc/Ez_ave**2))
        self.exportResults.pushBack("maxPos", str(maxPos))
        
        self.lockdown = True
        self.write()
    
    def __readfile(self, fileObject):
        print "ScMax::__readfile(), fileObject = " + str(fileObject)
        
        #Create storage
        pos  = []
        #real = []
        #imag = []
        ampl = []
        phas = []
        
        #Read files
        for line in fileObject.readlines():
            if line[0] == "!":
                continue #Skip comment line at the beginning
            ls = line.split()
    
            #Get position
            pos.append(map(float,ls[0:3]))
    
            #E-field
            #real.append(map(float,ls[3:6]))
            real = map(float,ls[3:6])
            #imag.append(map(float,ls[6:9]))
            imag = map(float,ls[6:9])
            
            ampl.append(map(lambda r,i: np.sqrt(r**2 + i**2), real, imag))
            phas.append(np.arctan2(imag,real))
        
        #Convert to numpy arrays
        pos  = np.asarray(pos)
        #real = np.asarray(real)
        #imag = np.asarray(imag)
        ampl = np.asarray(ampl)
        phas = np.asarray(phas)
    
        #return (pos,real,imag,ampl,phas)
        return (pos,ampl,phas)
        
    def clearLockdown(self):
        print "ScMax::clearLockdown()"
        self.exportResults.clear()
        self.lockdown = False
        self.write()
    
    def write(self):
        self.__paramFile.dataDict.setValSingle("lockdown", str(self.lockdown))
        self.__paramFile.write()
    
    @staticmethod
    def createNew(folder,name):
        paramFile = AcdOptiFileParser_simple(os.path.join(folder,name), "w")
        paramFile.dataDict.pushBack("fileID", "Analysis::ScMax")
        paramFile.dataDict.pushBack("lockdown", "False")

        paramFile.dataDict.pushBack("export", DataDict())

        paramFile.dataDict.pushBack("settings", DataDict())
        paramFile.dataDict["settings"].pushBack("RFpostName", "RFpost_local")
        paramFile.dataDict["settings"].pushBack("fieldOnSurface_basename", "fieldOnSurface_metal")
        
        paramFile.write()

class ScMaxException(AcdOptiException_analysis):
    pass
class ScMaxException_runAna(AcdOptiException_analysis_runAnalysis):
    pass