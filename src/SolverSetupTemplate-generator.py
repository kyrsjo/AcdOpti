#!/usr/bin/env python
# coding: utf8
"""
This is a smalish program that reads a setup file and spits out
an auto-generated SolverSetupTemplate (which needs to be edited)

Kyrre Sjøbæk, September 2011
"""

import os, sys
from acdOpti.AcdOptiFileParser import *

#Setup the application
if len(sys.argv) != 3:
    print "Usage: " + sys.argv[0] + " <file> <format>"
    sys.exit()
inFileName   = sys.argv[1]
fileFormat = sys.argv[2]

outFileName = inFileName + ".autogen.set"

fileParserClass = None
if fileFormat == "simple":
    fileParserClass = AcdOptiFileParser_simple
elif fileFormat == "KVC":
    fileParserClass = AcdOptiFileParser_KVC
elif fileFormat == "Lua":
    fileParserClass = AcdOptiFileParser_Lua
else:
    print "format must be 'simple', 'KVC', or 'Lua'"
    sys.exit()

inFile  = fileParserClass(inFileName, 'r')
outFile = AcdOptiFileParser_simple(outFileName, 'w')

#Iterate through the inFile, filling up the outFile
def digger(inDict):
    """"
    Recursive function that gets a dict, and calls itself each time it sees another dict.
    Returns a 'dict of dicts', one dict for each variable
    """
    #print
    #print "digger()", inDict
    
    retDict = DataDict()
    for (k,v) in inDict:
        if isinstance(v, DataDict):
            #print k,v, "Dict"
            r = DataDict()
            r.pushBack("type", "dict")
            r.pushBack("must", "True")
            r.pushBack("single", "False")
            r.pushBack("children", digger(v))
            retDict.pushBack(k, r)
        else:
            #print k,v,"String"
            r = DataDict()
            r.pushBack("type", "string")
            r.pushBack("must", "True")
            r.pushBack("single", "False")
            r.pushBack("default", v)
            retDict.pushBack(k, r)
    return retDict

outFile.dataDict.pushBack("fileID", "SolverSetupTemplate")
outFile.dataDict.pushBack("fileFormat", fileFormat)
outFile.dataDict.pushBack("fileNameDefault", inFileName)
outFile.dataDict.pushBack("type", "?????????????????????????????????")
outFile.dataDict.pushBack("options", digger(inFile.dataDict))

outFile.write()

            