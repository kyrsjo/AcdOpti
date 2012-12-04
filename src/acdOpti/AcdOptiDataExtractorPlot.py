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
        else:
            settingsDict = settingsDictOrInstName
        print settingsDict
        
        super(DataExtractorPlot3D,self).__init__(dataExtractor,settingsDict)
        self.varX = settingsDict["varX"]
        self.varY = settingsDict["varY"]
        self.varZ = settingsDict["varZ"]
        
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
    
    def deduplicate(self,X,Y,Z):
        """
        Deduplicate by finding all unique pairs (x,y), for each such pair set Z = average Z over all pair occurences
        """
        assert len(X) == len(Y) and len(Y) == len(Z)
        
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
        for j in xrange(len(x)):
            n.append(0)
            z.append(0.0)
            for i in xrange(len(X)):
                if comparePair(X[i],Y[i],x[j],y[j]):
                    n[-1] += 1
                    z[-1] += Z[i]
            z[-1] /= float(n[-1])
        
        return(x,y,z,n)
                
    
    def updateSettingsDict(self):
        self.settingsDict["varX"] = self.varX
        self.settingsDict["varY"] = self.varY
        self.settingsDict["varZ"] = self.varZ