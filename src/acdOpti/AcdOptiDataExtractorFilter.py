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

from AcdOptiFileParser import DataDict

class AcdOptiDataExtractorFilter(object):
    "Base class for all filters"

    settingsDict = None
    dataExtractor = None
    
    filterType = None
    
    numFiltered = None #How many was filtered?
    
    def __init__(self,settingsDict):
        "Init and/or load  a filter"
        assert isinstance(settingsDict,DataDict)
        self.settingsDict = settingsDict
        self.numFiltered = int(settingsDict["numFiltered"])
        
    @staticmethod
    def getFilterClass(filterType, settingsDict):
        for f in AcdOptiDataExtractorFilter.__subclasses__():
            if f.is_filter_correct(filterType):
                return f(settingsDict)
    @staticmethod
    def is_filter_correct(filterType):
        "Return True if filterType is the right string"
        raise NotImplementedError
    
    def filterRow(self, row):
        "Return True if this this row should be kept, else False"
        raise NotImplementedError
    
    
class EqualsFilter(AcdOptiDataExtractorFilter):
    "Only let pass if the filtered variable 'key'exists and is equal to 'val'"
    
    filterType = "EqualsFilter"
    
    def __init__(self,settingsDict=None):
        if settingsDict == None:
            settingsDict = DataDict()
            settingsDict.pushBack("key", "")
            settingsDict.pushBack("val", "")
            settingsDict.pushBack("numFiltered", "0")
        AcdOptiDataExtractorFilter.__init__(self, settingsDict)

    @staticmethod
    def is_filter_correct(filterType):
        return filterType == "EqualsFilter"
    
    def filterRow(self,row):
        key = self.settingsDict["key"]
        val = self.settingsDict["val"]
        try:
            if row[key] == val:
                return True
            else:
                self.numFiltered += 1
                return False
        except KeyError:
            return True

class RangeFilter(AcdOptiDataExtractorFilter):
    "Let pass if the filtered variable 'key' is in (a,b)"
    
    filterType = "RangeFilter"
    
    key = None
    a = b = None
    
    def __init__(self,settingsDict=None):
        if settingsDict == None:
            settingsDict = DataDict()
            settingsDict.pushBack("key", "")
            settingsDict.pushBack("a", "")
            settingsDict.pushBack("b", "")
            settingsDict.pushBack("numFiltered", "0")
        AcdOptiDataExtractorFilter.__init__(self, settingsDict)
    
    @staticmethod
    def is_filter_correct(filterType):
        return filterType == "RangeFilter"
    
    def filterRow(self,row):
        key = self.settingsDict["key"]
        a = float(self.settingsDict["a"])
        b = float(self.settingsDict["b"])
        
        try:
            val = float(row[key])
            if val > a and val < b:
                return True
            else:
                self.numFiltered += 1
                return False
        except KeyError:
            return True
        