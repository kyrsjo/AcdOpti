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

from AcdOptiFileParser import DataDict
from AcdOptiExceptions import AcdOptiException_dataDict_getValsSingle

import numpy as np

class AcdOptiDataExtractorPlot(object):
    "Base class for plot data/settings objects"

    settingsDict = None
    dataExtractor = None
    
    plotType = None
    
    instName = None
    
    numFiltered = None #How many was filtered?
    
    def __init__(self,dataExtractor,settingsDict):
        "Init and/or load a plotter. Init by inheriting class only."
        
        assert isinstance(settingsDict,DataDict)
        
        from AcdOptiDataExtractor import AcdOptiDataExtractor
        assert isinstance(dataExtractor, AcdOptiDataExtractor)
        self.dataExtractor = dataExtractor
        
        self.settingsDict = settingsDict
    
        assert self.plotType == settingsDict["plotType"]
        self.instName = settingsDict["instName"]
#    def doPlot(self):
#        "Ask the plot object to get the data from the dataExtractor and plot itself"
#        raise NotImplementedError
    def doExport(self, fname):
        "Ask the plot object to get the data from the dataExtractor and export itself to file"
        raise NotImplementedError
    def getData(self):
        "Ask the plot object to get the data from the dataExtractor and return it as a (X,Y,...) tuple."
        raise NotImplementedError
    
    @staticmethod
    def getPlotClass(plotType, dataExtractor, instName):
        for f in AcdOptiDataExtractorPlot.__subclasses__():
            if f.is_plot_correct(plotType):
                return f(dataExtractor, instName)    
    @classmethod
    def is_plot_correct(cls, plotType):
        "Return True if plotType is the right string"
        #raise NotImplementedError
        return plotType == cls.plotType

class DataExtractorPlot2D(AcdOptiDataExtractorPlot):
    
    plotType = "DataExtractorPlot2D"

    varX = None
    varY = None
    
    def __init__(self, dataExtractor, settingsDictOrInstName):
        assert settingsDictOrInstName != None
        settingsDict = None
        print settingsDictOrInstName
        if type(settingsDictOrInstName) == str:
            settingsDict = DataDict()
            settingsDict.pushBack("plotType", self.plotType)
            settingsDict.pushBack("instName", settingsDictOrInstName)
            settingsDict.pushBack("varX", "")
            settingsDict.pushBack("varY", "")
        else:
            settingsDict = settingsDictOrInstName
        print settingsDict
        
        super(DataExtractorPlot2D,self).__init__(dataExtractor,settingsDict)
        self.varX = settingsDict["varX"]
        self.varY = settingsDict["varY"]
        

        
    def doExport(self,fname):
        (X, Y) = self.getData()
        raise NotImplementedError
        
    def getData(self):
        assert self.dataExtractor.lockdown
        assert self.varX in self.dataExtractor.keyNames
        assert self.varY in self.dataExtractor.keyNames
        
        X = []
        Y = []
        
        for (row, rcount) in zip(self.dataExtractor.dataExtracted, xrange(len(self.dataExtractor.dataExtracted))):
            try:
                x = float(row[self.varX])
                y = float(row[self.varY])
                
                X.append(x)
                Y.append(y)
            except KeyError:
                pass
            except ValueError:
                print "Warning in DataExtractorPlot2D::getData(): Could not convert value in row", rcount, "to float, skipping!"
        
        return (X,Y)
    
    def updateSettingsDict(self):
        self.settingsDict["varX"] = self.varX
        self.settingsDict["varY"] = self.varY


class DataExtractorPlot3D(AcdOptiDataExtractorPlot):
    
    plotType = "DataExtractorPlot3D"

    varX = None
    varY = None
    varZ = None
    
    limit = None
    useLimit = None

    numContours = None

    def __init__(self, dataExtractor, settingsDictOrInstName):
        assert settingsDictOrInstName != None
        settingsDict = None
        print settingsDictOrInstName
        if type(settingsDictOrInstName) == str:
            settingsDict = DataDict()
            settingsDict.pushBack("plotType", self.plotType)
            settingsDict.pushBack("instName", settingsDictOrInstName)
            settingsDict.pushBack("varX", "")
            settingsDict.pushBack("varY", "")
            settingsDict.pushBack("varZ", "")
            settingsDict.pushBack("limit", "")
            settingsDict.pushBack("useLimit", "False")
            settingsDict.pushBack("numContours", "");
        else:
            settingsDict = settingsDictOrInstName
        print settingsDict
        
        super(DataExtractorPlot3D,self).__init__(dataExtractor,settingsDict)
        self.varX = settingsDict["varX"]
        self.varY = settingsDict["varY"]
        self.varZ = settingsDict["varZ"]
        try:
            self.limit = settingsDict["limit"]
            self.useLimit = settingsDict["useLimit"]
        except AcdOptiException_dataDict_getValsSingle:
            settingsDict.pushBack("limit", "")
            self.limit = ""
            settingsDict.pushBack("useLimit", "False")
            self.useLimit = "False"

        try:
            self.numContours = settingsDict["numContours"]
        except AcdOptiException_dataDict_getValsSingle:
            settingsDict.pushBack("numContours", "");
            self.numContours = ""

    def doExport(self,fname):
        (X, Y, Z) = self.getData()
        raise NotImplementedError
        
    def getData(self):
        assert self.dataExtractor.lockdown
        assert self.varX in self.dataExtractor.keyNames
        assert self.varY in self.dataExtractor.keyNames
        assert self.varZ in self.dataExtractor.keyNames
        
        X = []
        Y = []
        Z = []
        
        for (row, rcount) in zip(self.dataExtractor.dataExtracted, xrange(len(self.dataExtractor.dataExtracted))):
            try:
                x = float(row[self.varX])
                y = float(row[self.varY])
                z = float(row[self.varZ])
                
                X.append(x)
                Y.append(y)
                Z.append(z)
            except KeyError:
                pass
            except ValueError:
                print "Warning in DataExtractorPlot2D::getData(): Could not convert value in row", rcount, "to float, skipping!"
        
        return (X,Y,Z)
    
    def deduplicate(self,X,Y,Z,mode="mean"):
        """
        Deduplicate by finding all unique pairs (x,y), for each such pair set Z = average Z over all pair occurences,
        or find min or max value
        """
        assert len(X) == len(Y) and len(Y) == len(Z)

        assert mode=="mean" or mode=="max" or mode=="min"

        #Dedup'ed variables
        x = []
        y = []
        z = []
        n = []
        
        def comparePair(x1,y1, x2,y2):
            return x1==x2 and y1==y2
        
        #Find all unique paris
        for i in xrange(len(X)):
            prevFound = False
            for j in xrange(len(x)):
                if comparePair(X[i],Y[i],x[j],y[j]):
                    prevFound = True
                    break
            if not prevFound:
                x.append(X[i])
                y.append(Y[i])
        
        #Average over z 
        for j in xrange(len(x)): #Loop over unique (x,y) -> z
            n.append(0)

            if mode == "mean":
                z.append(0.0)
            else:
                z.append(None)

            for i in xrange(len(X)): #Loop over all (X,Y,Z))
                if comparePair(X[i],Y[i],x[j],y[j]):
                    n[-1] += 1
                    if mode == "mean":
                        z[-1] += Z[i]
                    elif mode == "min" and (z[-1] == None or z[-1] > Z[i]):
                        z[-1] = Z[i]
                    elif mode == "max" and (z[-1] == None or z[-1] < Z[i]):
                        z[-1] = Z[i]
            
            if mode == "mean":
                z[-1] /= float(n[-1])
        
        return(x,y,z,n)
    
    def fitPlane(self):
        """Fit Z=a0+a1*x+a2*y"""
        
        (X,Y,Z) = self.getData()
        assert len(X) == len(Y) and len(X) == len(Z)
        ndof = len(Z)-3
        assert ndof > 0             
    
        import numpy as np
        
        A = [np.ones(len(Z))]
        A.append(np.asarray(X))
        A.append(np.asarray(Y))
        A = np.vstack(A).T
        
        model = np.linalg.lstsq(A,Z)[0]
        
        #Calculate R^2
        R2 = 0.0
        for i in xrange(len(Z)):
            R2 += ( (model[0] + model[1]*X[i] + model[2]*Y[i]) - Z[i])**2
        
        return (model, ndof, R2)
     
    def fitQuad(self):
        """Fit Z=a0 + a1*x+a2*y + a3*x^2+a4*y^2 + a5*x*y"""
        
        (X,Y,Z) = self.getData()
        assert len(X) == len(Y) and len(X) == len(Z)
        ndof = len(Z)-6
        assert ndof > 0             
    
        import numpy as np
        
        A = [np.ones(len(Z))]
        A.append(np.asarray(X))
        A.append(np.asarray(Y))
        A.append(np.asarray(X)**2)
        A.append(np.asarray(Y)**2)
        A.append(np.asarray(X)*np.asarray(Y))
        A = np.vstack(A).T
        
        model = np.linalg.lstsq(A,Z)[0]
        
        #Calculate R^2
        R2 = 0.0
        for i in xrange(len(Z)):
            R2 += ( (model[0] + model[1]*X[i] + model[2]*Y[i] + model[3]*X[i]**2 + model[4]*Y[i]**2 + model[5]*X[i]*Y[i]) - Z[i])**2
        
        return (model, ndof, R2)

    def getBelowLimit(self,limit):
        "Remove points with z-values larger than limit"
        (X,Y,Z) = self.getData()      
        x = []
        y = []
        z = []
        
        for i in xrange(len(X)):
            if (Z[i] < limit):
                x.append(X[i])
                y.append(Y[i])
                z.append(Z[i])
        return (x,y,z);

    def updateSettingsDict(self):
        self.settingsDict["varX"] = self.varX
        self.settingsDict["varY"] = self.varY
        self.settingsDict["varZ"] = self.varZ

        self.settingsDict["limit"] = self.limit
        self.settingsDict["useLimit"] = self.useLimit
        
        self.settingsDict["numContours"] = self.numContours

class DataExtractorPlotsScaleOptim(AcdOptiDataExtractorPlot):
    
    plotType = "DataExtractorPlotScaleOptim"

    varX     = None
    varY     = None

    constE   = None
    constE_2 = None
    varNormE = None
    
    constSC   = None
    constSC_2 = None
    varNormSC = None
    
    constPC      = None
    constPC_2    = None
    varFrequency = None
    varRQ        = None
    varVg        = None
    varRadius    = None
        
    def __init__(self, dataExtractor, settingsDictOrInstName):
        assert settingsDictOrInstName != None
        settingsDict = None
        print settingsDictOrInstName
        if type(settingsDictOrInstName) == str:
            settingsDict = DataDict()
            settingsDict.pushBack("plotType", self.plotType)
            settingsDict.pushBack("instName", settingsDictOrInstName)
            settingsDict.pushBack("varX", "GEOM.e")
            settingsDict.pushBack("varY", "GEOM.sFrac")
            
            settingsDict.pushBack("constE",   "220") #(MV/m)**6 * 200 ns, will be taken to the power 6
            settingsDict.pushBack("constE_2", "250") #(MV/m)**6 * 200 ns, will be taken to the power 6
            settingsDict.pushBack("varNormE", DataDict())
            settingsDict["varNormE"].pushBack("var", "ANA.RFpost_local.maxFieldsOnSurface[0].surf[0].mode[0].Emax_norm[0]")
            
            settingsDict.pushBack("constSC",   "4.0") #(MW/mm**2)**3 * 200 ns, will be taken to the power 3
            settingsDict.pushBack("constSC_2", "5.0") #(MW/mm**2)**3 * 200 ns, will be taken to the power 3
            settingsDict.pushBack("varNormSC", DataDict())
            settingsDict["varNormSC"].pushBack("var", "ANA.RFpost_local.maxFieldsOnSurface[0].surf[0].mode[0].SCmax_norm[0]")
            
            settingsDict.pushBack("constPC",   "2.3") #(MW/mm)**3 * 200 ns, will be taken to the power 3
            settingsDict.pushBack("constPC_2", "2.9") #(MW/mm)**3 * 200 ns, will be taken to the power 3
            settingsDict.pushBack("varFrequency", "ANA.Omega3P_modeInfo.Mode[0].FrequencyReal[0]")
            settingsDict.pushBack("varRQ", "ANA.RFpost_local.RoverQ[0].mode[0].RoQ_norm[0]")
            settingsDict.pushBack("varVg", "ANA.GroupVelocity.VG[0]")
            settingsDict.pushBack("varRadius", "GEOM.a")
            
        else:
            settingsDict = settingsDictOrInstName
            if not "constE_2" in settingsDict.getKeys():
                print "Adding optimistic constants!"
                print settingsDict
                settingsDict.pushBack("constE_2",  "250") #(MV/m)**6 * 200 ns, will be taken to the power 6
                settingsDict.pushBack("constSC_2", "5.0") #(MW/mm**2)**3 * 200 ns, will be taken to the power 3
                settingsDict.pushBack("constPC_2", "2.9") #(MW/mm)**3 * 200 ns, will be taken to the power 3
            
            if type(settingsDict["varNormE"]) == str:
                assert type(settingsDict["varNormSC"]) == str
                print "Changing varNormE and varNormSC to a DataDict"
                print settingsDict
                
                oldVarNormE = settingsDict["varNormE"]
                newVarNormE = DataDict()
                newVarNormE.pushBack("var", oldVarNormE)
                settingsDict.delItem("varNormE")
                settingsDict.pushBack("varNormE", newVarNormE)
                
                oldVarNormSC = settingsDict["varNormSC"]
                newVarNormSC = DataDict()
                newVarNormSC.pushBack("var", oldVarNormSC)
                settingsDict.delItem("varNormSC")
                settingsDict.pushBack("varNormSC", newVarNormSC)
        
        print settingsDict
        
        super(DataExtractorPlotsScaleOptim,self).__init__(dataExtractor,settingsDict)
        
        self.varX = settingsDict["varX"]
        self.varY = settingsDict["varY"]
        
        self.constE   = settingsDict["constE"]
        self.constE_2 = settingsDict["constE_2"]
        self.varNormE = settingsDict["varNormE"].vals
        
        self.constSC     = settingsDict["constSC"]
        self.constSC_2   = settingsDict["constSC_2"]
        self.varNormSC   = settingsDict["varNormSC"].vals

        self.constPC      = settingsDict["constPC"]
        self.constPC_2    = settingsDict["constPC_2"]
        self.varFrequency = settingsDict["varFrequency"]
        self.varRQ        = settingsDict["varRQ"]
        self.varVg        = settingsDict["varVg"]
        self.varRadius    = settingsDict["varRadius"]
        
    def doExport(self,fname):
        raise NotImplementedError
        
    def getData(self,scalingFactor2=False):
        "Use scalingFactor2 to get the second set of (optimistic) scaling factors"
        assert self.dataExtractor.lockdown
        assert self.varX         in self.dataExtractor.keyNames
        assert self.varY         in self.dataExtractor.keyNames
        for var in self.varNormE:
            assert var in self.dataExtractor.keyNames
        for var in self.varNormSC:
            assert var in self.dataExtractor.keyNames
        assert self.varFrequency in self.dataExtractor.keyNames
        assert self.varRQ        in self.dataExtractor.keyNames
        assert self.varVg        in self.dataExtractor.keyNames
        assert self.varRadius    in self.dataExtractor.keyNames

        constE_scaled  = 0.0;
        constSC_scaled = 0.0;
        constPC_scaled = 0.0;

        try:
            if scalingFactor2:
                constE_scaled  = float(self.constE_2)**6  * 200  # (MV/m)^6 * ns
                constSC_scaled = float(self.constSC_2)**3 * 200  # (MW/mm^2)^3 * ns
                constPC_scaled = float(self.constPC_2)**3 * 200  # (MW/mm)^3 * ns
            else:
                constE_scaled  = float(self.constE)**6  * 200  # (MV/m)^6 * ns
                constSC_scaled = float(self.constSC)**3 * 200  # (MW/mm^2)^3 * ns
                constPC_scaled = float(self.constPC)**3 * 200  # (MW/mm)^3 * ns
        except ValueError:
            print "Warning in DataExtractorPlotsScaleOptim::getData(): Could not convert a constant"
            return ([],[], [],[],[])
        
        X = []
        Y = []
        
        #Units: (MV/m)^6 * ns
        tE = []
        tSC = []
        tPC = []
        
        for (row, rcount) in zip(self.dataExtractor.dataExtracted, xrange(len(self.dataExtractor.dataExtracted))):
            try:
                x = float(row[self.varX])
                y = float(row[self.varY])
                
                maxE = 0.0
                for var in self.varNormE:
                    maxE_this = float(row[var])
                    if maxE_this > maxE:
                        maxE = maxE_this
                t_E = constE_scaled/maxE**6
                
                maxSC = 0.0
                for var in self.varNormSC:
                    maxSC_this = float(row[var])
                    if maxSC_this > maxSC:
                        maxSC = maxSC_this
                t_SC  = constSC_scaled/maxSC**3
                
                radius = float(row[self.varRadius]) # mm
                circ = 2*np.pi*radius*1e-3          # m
                
                vg = float(row[self.varVg])         # m/s
                omega = 2*np.pi*float(row[self.varFrequency]) # s^-1
                RQnorm = float(row[self.varRQ])*1e3     # Ohm/m (its Ohm/mm in R/Q parser) 
                
                t_PC = 1e+9*constPC_scaled * (circ*omega*RQnorm/vg)**3
                
                X.append(x)
                Y.append(y)
                tE.append(t_E)
                tSC.append(t_SC)
                tPC.append(t_PC)
            except KeyError:
                pass
            except ValueError:
                print "Warning in DataExtractorPlotScaleOptim::getData(): Could not convert value in row", rcount, "to float, skipping!"
        
        return (X,Y,tE,tSC,tPC)
    
    def updateSettingsDict(self):
        self.settingsDict["varX"] = self.varX
        self.settingsDict["varY"] = self.varY
        
        self.settingsDict["constE"]    = self.constE
        self.settingsDict["constE_2"]  = self.constE_2
        self.settingsDict["varNormE"].clear()
        for var in self.varNormE:
            self.settingsDict["varNormE"].pushBack("var",var)
        
        self.settingsDict["constSC"]   = self.constSC
        self.settingsDict["constSC_2"] = self.constSC_2
        self.settingsDict["varNormSC"].clear()
        for var in self.varNormSC:
            self.settingsDict["varNormSC"].pushBack("var",var)

        self.settingsDict["constPC"]      = self.constPC
        self.settingsDict["constPC_2"]    = self.constPC_2
        self.settingsDict["varFrequency"] = self.varFrequency
        self.settingsDict["varRQ"]        = self.varRQ
        self.settingsDict["varVg"]        = self.varVg
        self.settingsDict["varRadius"]    = self.varRadius

