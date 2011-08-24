from acdOpti.AcdOptiExceptions import AcdOptiException_solverSetup_loadFail,\
                                      AcdOptiException_solverSetup_createFail,\
    AcdOptiException_solverSetup_createFail_nameTaken

from AcdOptiFileParser import DataDict,\
                              AcdOptiFileParser_simple,\
                              AcdOptiFileParser_Lua,\
                              AcdOptiFileParser_KVC

import os
solverSetupResourcesPath = os.path.join(os.path.split(__file__)[0],"resources","solverSetup")


class AcdOptiSolverSetup:
    """
    Generates a solver setup from the specified type.
    If the solution name exists, it will be loaded, 
    else it will be created from default values.
    
    This class is dependent on being owned  by a AcdOptiRunConfig,
    as it does some initialization for it, for example creating the "stage" folder.
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
    runConfig       = None  # The main runConfig object owning this (and perhaps more) solverSetups
    type            = None  # Type of the setup file (omega3p etc)
    name            = None  # Name of the generated setup file
    folder          = None  # Folder where this file is located
    fileName        = None  # Full path of the setup file
    __metaSetupFile = None  # AcdOptiFileParser_simple object with metadata and current settings
    metaSetup       = None  # DataDict object pointing to metaSetupFile.dataDict["options"] (shortcut pointer)   
    setupFileFormat = None  # Pointer to correct AcdOptiFileParser_* class 
    lockdown        = None  # Is the solverSetup currently not writable? (not enforced)
     
    
    def __init__(self, name, runConfig):
        print "AcdOptiSolverSetup::__init__(), name='" + name + "', folder='" + runConfig.folder + "'"
        self.runConfig = runConfig 
        self.folder = runConfig.folder
        self.name   = name 

        if not os.path.isdir(os.path.join(self.folder, "stage")):
            raise AcdOptiException_solverSetup_loadFail("Subfolder 'stage' is missing")

        #Load the metaFile
        metaFileName = os.path.join(self.folder,name + ".meta") 
        self.__metaSetupFile = AcdOptiFileParser_simple(metaFileName, 'rw')
        assert self.__metaSetupFile.dataDict["fileID"] == "SolverSetup" #TODO: Raise a real error
        
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
        
        self.refreshLockdown()
        
        self.metaSetup = self.__metaSetupFile.dataDict.getValSingle("options")
        
        self.fileName = os.path.join(self.folder, self.name)
    
    def refreshLockdown(self):
        """
        Checks the status of the runConfig and uses that to determine the lockdown setting.
        """
        if self.runConfig.status == "not_initialized" or self.runConfig.status == "initialized":
            self.lockdown = False
        else:
            self.lockdown = True
        
    def stage(self):
        """
        Saves to disk and generates a setupFile,
        which is moved to the "stage" subfolder.
        """
        print "AcdOptiSolverSetup::stage()"
        # TODO: Sanity check on this objects status
        self.__metaSetupFile.write()
        self.__generateSetup()
        os.rename(self.fileName, os.path.join(self.runConfig.stageFolder, self.name))

    
    def __generateSetup(self):
        "Generates a setupFile from the current contents of metaSetup, which is written."
        print "AcdOptiSolverSetup::__generateSetup()"
        setupFile = self.setupFileFormat(self.fileName, 'w')
        print self.metaSetup
        metaSetupDict = AcdOptiSolverSetup.__generateSetup_recursiveHelper(self.metaSetup)
        setupFile.importDataDict(metaSetupDict)
        setupFile.write()  
    @staticmethod
    def __generateSetup_recursiveHelper(setupDict):
        print "AcdOptiSolverSetup::__generateSetup_recursiveHelper()"#, setupDict=", setupDict
        ret = DataDict()
        for item in setupDict:
            if not DataDict.boolconv(item[1]["enabled"]):
                continue
            if item[1]["type"] == "dict":
                ret.pushBack(item[0], AcdOptiSolverSetup.__generateSetup_recursiveHelper(item[1]["children"]))
            else:
                ret.pushBack(item[0], item[1]["value"])
        return ret
    

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
        Prepares a new AcdOptiSolverSetup by creating the metaFile.
        
        Input:
        - type is the name of the type ("omega3P" etc.) wanted
        - folder is where this instance should be created
        - name is the name wanted for this instance.
          Set to None to use default name
        
        Returns the name used.
        """
        print "AcdOptiSolverSetup::createNew(), type=" + type + ", name=" + str(name)
        
        #Check that the type is valid
        if not type in AcdOptiSolverSetup.getTypes():
            raise TypeError("type '" + type + "' is invalid")
        #Load the type definition
        typeFile = AcdOptiFileParser_simple(os.path.join(solverSetupResourcesPath, type + ".set"), 'r')
        assert typeFile.dataDict["fileID"] == "SolverSetupTemplate", "Got fileID ='" + str(typeFile.dataDict["fileID"]) + "'" #TODO: raise a real error
        
        #Check that everything is OK with the typeFile
        # TODO
        
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
        metaFile.dataDict.pushBack("fileID", "SolverSetup")
        metaFile.dataDict.pushBack("name", name)
        metaFile.dataDict.pushBack("fileFormat", typeFile.dataDict["fileFormat"])
        metaFile.dataDict.pushBack("type", typeFile.dataDict["type"])
        
        #Generate the options (which in itself is a childDict)
        metaFile.dataDict.pushBack("options", AcdOptiSolverSetup.__genMetaOptions(typeFile.dataDict.getValSingle("options")))
        metaFile.write()
        
        return name
    
    @staticmethod
    def __genMetaOptions(childDict):
        """
        Recursive method used by createNew() for generating the "options" part of the metaFile.
        Returns a DataDict which becomes one branch/level of the metaFile
        """
        print "AcdOptiSolverSetup::__genMetaOptions()"
        ret = DataDict()
        for item in childDict:
            # Make a copy of the old items in the childDict and add it to the metFile
            thisItem = ret.pushBack(item[0],item[1].copy())
            
            # Add some new meta-information fields
            if thisItem.getValSingle("type") == "dict":
                #Recursively modify this dicts children also
                thisItem.setValSingle("children", AcdOptiSolverSetup.__genMetaOptions(item[1].getValSingle("children")))
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
        
        if not itemDict["type"] in AcdOptiSolverSetup.dataTypes:
            return "Invalid type '" + itemDict["type"] + "'" 
        
        #TODO: implement!
        if itemDict["type"] == "dict":
            return
        else:
            return