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

#from AcdOptiSolverSetup import AcdOptiSolverSetup

from AcdOptiFileParser import DataDict,\
                              AcdOptiFileParser_simple,\
                              AcdOptiFileParser_Lua,\
                              AcdOptiFileParser_KVC

#Same exceptions used for several classes
from acdOpti.AcdOptiExceptions import AcdOptiException_solverSetup_loadFail,\
                                      AcdOptiException_solverSetup_createFail,\
                                      AcdOptiException_solverSetup_createFail_nameTaken                              

import os

#Where to find the .set files describing solver setup types
solverSetupResourcesPath = os.path.join(os.path.split(__file__)[0],"resources","solverSetup")


class AcdOptiSolverManager:
    """
    This class does the dirtywork of AcdOptiSolverSetup,
    such as creating the actual solver setup files.
    
    It generates a solver setup from the specified type.
    If the solution name exists, it will be loaded, 
    else it will be created from default values.
    
    AcdOptiSolverSetup remains as an alternative interface to this class,
    with simpler initialization given by an AcdOptiRunConfig
    """
    
    #Constants

    #Data types
    fileTypes = ["simple", "Lua", "KVC"]
    dataTypes = ["dict", "fnameNoEx", "fnameEx", "string", "bool", "int", "intList", "float"] 
    # dict: Dictionary. Have key/DataDict "children" with sub-keys
    # fnameNoEx : relative path of file that does not exist
    # fnameEx   : relative path of file that does exist
    # string    : a string without trailing/leading whitespace
    # bool      : a bool, coded as "True"/"False" or "true"/"false". If key "int" is True, coded as "1"/"0"
    # int       : an integer
    # intList   : a list of integers "a,b,c"
    # float     : a float

    #Object fields
    type              = None  # Type of the setup file
                              #  (omega3P etc.; name of one of the .set files found in solverSetupResourcesPath)
    name              = None  # Name of the generated setup file
    folder            = None  # Folder where this file is located
    fileName          = None  # Full path of the setup file
    __metaSetupFile   = None  # AcdOptiFileParser_simple object with metadata and current settings
    metaSetupFilePath = None  # Full path to the MetaSetupFile
    metaSetup         = None  # DataDict object pointing to metaSetupFile.dataDict["options"] (shortcut pointer)   
    setupFileFormat   = None  # Pointer to correct AcdOptiFileParser_* class 
    lockdown          = None  # Is the solverSetup currently not writable? (not enforced)
     
    
    def __init__(self, name, folder):
        """
        Initialize a solverManager.
        - Name: Name of this instance (used to find the metaFile and name of the created setup file)
        - folder: Where the metaFile lives, and where the setup file is created.
        """
        print "AcdOptiSolverManager::__init__(), name='" + name + "', folder='" + folder + "'"
        self.folder = folder
        self.name   = name 

        if not os.path.isdir(self.folder):
            raise AcdOptiException_solverSetup_loadFail("Subfolder 'stage' is missing")

        #Load the metaFile
        self.metaSetupFilePath = metaFileName = os.path.join(self.folder, name + ".meta")
        self.__metaSetupFile = AcdOptiFileParser_simple(metaFileName, 'rw')
        if self.__metaSetupFile.dataDict["fileID"] != "SolverManager":
            if self.__metaSetupFile.dataDict["fileID"] == "SolverSetup":
                print "\t WARNING: Old-style file detected, fileID='SolverSetup'"
                print "\t Will change it to new-style 'solverManager'"
                self.__metaSetupFile.dataDict.setValSingle("fileID","SolverManager")
                self.__metaSetupFile.write()
            else:
                raise AcdOptiException_solverSetup_loadFail("Wrong fileID in metaSetupFile '" + self.metaSetupFilePath + "'")
        
        if self.name != self.__metaSetupFile.dataDict["name"]:
            raise AcdOptiException_solverSetup_loadFail("name in metaSetupFile '"+self.__metaSetupFile.dataDict["name"]+"' doesn't match provided argument '"+self.name+"'")

        self.setupFileFormat = self.__metaSetupFile.dataDict.getValSingle("fileFormat")
        if self.setupFileFormat == "simple":
            self.setupFileFormat = AcdOptiFileParser_simple
        elif self.setupFileFormat == "Lua":
            self.setupFileFormat = AcdOptiFileParser_Lua
        elif self.setupFileFormat == "KVC":
            self.setupFileFormat = AcdOptiFileParser_KVC
        else:
            raise ValueError("Unknown setupFileFormat encountered, setupFileFormat='" + self.setupFileFormat + "'")
        
        self.type = self.__metaSetupFile.dataDict["type"]
        
        self.metaSetup = self.__metaSetupFile.dataDict.getValSingle("options")
        
        self.fileName = os.path.join(self.folder, self.name)
       
    def generateSetup(self):
        "Generates a setupFile from the current contents of metaSetup, which is written."
        print "AcdOptiSolverSetupManager::__generateSetup()"
        self.write()
        
        setupFile = self.setupFileFormat(self.fileName, 'w')
        metaSetupDict = AcdOptiSolverManager.__generateSetup_recursiveHelper(self.metaSetup)
        setupFile.importDataDict(metaSetupDict)
        setupFile.write()
    
    @staticmethod
    def __generateSetup_recursiveHelper(setupDict):
        print "AcdOptiSolverManager::__generateSetup_recursiveHelper()"#, setupDict=", setupDict
        ret = DataDict()
        for item in setupDict:
            if not DataDict.boolconv(item[1]["enabled"]):
                continue
            if item[1]["type"] == "dict":
                ret.pushBack(item[0], AcdOptiSolverManager.__generateSetup_recursiveHelper(item[1]["children"]))
            else:
                ret.pushBack(item[0], item[1]["value"])
        return ret

    def write(self):
        self.__metaSetupFile.write()
    
    @staticmethod
    def getTypes():
        """
        Returns a report listing all valid 'types'
        """
        fileList = os.listdir(solverSetupResourcesPath)
        typeList = []
        for file in fileList:
            if os.path.isfile(os.path.join(solverSetupResourcesPath,file)) and \
                file.endswith(".set"):
                typeList.append(file[:-4])
        return typeList   
    
    @staticmethod
    def createNew(type, folder, name=None):
        """
        Prepares a new AcdOptiSolverManager by creating the metaFile.
        
        Input:
        - type is the name of the type ("omega3P" etc.) wanted
        - folder is where this instance should be created
        - name is the name wanted for this instance.
          Set to None to use default name.
          Name is also the filename of the solver setup file generated.
          
        Returns the name used.
        """
        print "AcdOptiSolverSetupManager::createNew(), type=" + type + ", name=" + str(name)
        
        #Check that the type is valid
        if not type in AcdOptiSolverManager.getTypes():
            raise TypeError("type '" + type + "' is invalid")
        #Load the type definition
        typeFile = AcdOptiFileParser_simple(os.path.join(solverSetupResourcesPath, type + ".set"), 'r')
        if typeFile.dataDict["fileID"] != "SolverSetupTemplate":
            raise AcdOptiException_solverSetup_createFail("Got fileID ='" + str(typeFile.dataDict["fileID"]) + "'")
        
        #Check that everything is OK with the typeFile
        # TODO!
        
        #Read the typeFile
        if not name:
            name = typeFile.dataDict.getValSingle("fileNameDefault")
        
        #Generate the metaFile
        metaFileName = name + ".meta"

        #First: check that the name is not in use
        if os.path.isfile(os.path.join(folder,metaFileName)):
            raise AcdOptiException_solverSetup_createFail_nameTaken("Name already in use, couldn't create metaFile", name)
        metaFile = AcdOptiFileParser_simple(os.path.join(folder,metaFileName), 'w')
        #Setup the basic structure of the metaFile
        metaFile.dataDict.pushBack("fileID", "SolverManager")
        metaFile.dataDict.pushBack("name", name)
        metaFile.dataDict.pushBack("fileFormat", typeFile.dataDict["fileFormat"])
        metaFile.dataDict.pushBack("type", typeFile.dataDict["type"])
        
        #Generate the options (which in itself is a childDict)
        metaFile.dataDict.pushBack("options", AcdOptiSolverManager.__genMetaOptions(typeFile.dataDict.getValSingle("options")))
        metaFile.write()
        
        return name
    
    @staticmethod
    def createNew_clone(folder, cloneFrom):
        """
        Creates a new solverSetup in a not previously existing folder,
        which has identical settings as an already existing solverSetup.
        The newly created solverSetup is then returned.
        """
        AcdOptiSolverManager.createNew(cloneFrom.type, folder, cloneFrom.name)
        newSolverSetup = AcdOptiSolverManager(cloneFrom.name, folder)
        
        newSolverSetup.metaSetup.clear()
        for (k,v) in cloneFrom.metaSetup.copy():
            newSolverSetup.metaSetup.pushBack(k,v)
        
        newSolverSetup.write()
        return newSolverSetup
    
    @staticmethod
    def __genMetaOptions(childDict):
        """
        Recursive method used by createNew() for generating the "options" part of the metaFile.
        Returns a DataDict which becomes one branch/level of the metaFile
        """
        print "AcdOptiSolverSetupManager::__genMetaOptions()"
        ret = DataDict()
        for item in childDict:
            # Make a copy of the old items in the childDict and add it to the metFile
            thisItem = ret.pushBack(item[0],item[1].copy())
            
            # Add some new meta-information fields
            if thisItem.getValSingle("type") == "dict":
                #Recursively modify this dicts children also
                thisItem.setValSingle("children", AcdOptiSolverManager.__genMetaOptions(item[1].getValSingle("children")))
            else:
                #Ordinary data field, set its value to whatever is default
                thisItem.pushBack("value",thisItem.getValSingle("default"))
            
            if DataDict.boolconv(item[1].getValSingle("must")):
                thisItem.pushBack("enabled", "True")
            else:
                thisItem.pushBack("enabled", "False")        
        return ret

    @staticmethod
    def isInputInvalid(itemDict, newValue=None):
        """
        Check whether newValue is a valid value of the itemDict
        by the rules encoded in the itemDict.
        If newValue=None, check the current value instead.
        
        If it is invalid, return an error message as a string,
        else return None.
        """
        
        if not itemDict["type"] in AcdOptiSolverManager.dataTypes:
            return "Invalid type '" + itemDict["type"] + "'" 
        
        #TODO: implement some real checking for each type!
        if itemDict["type"] == "dict":
            return
        else:
            return
    