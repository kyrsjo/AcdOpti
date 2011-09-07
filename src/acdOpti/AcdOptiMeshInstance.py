from AcdOptiExceptions import AcdOptiException_meshInstance_createFail,\
                              AcdOptiException_meshInstance_loadFail,\
                              AcdOptiException_meshInstance_lockdownError,\
                              AcdOptiException_meshInstance_nameError,\
                              AcdOptiException_meshInstance_generateFail,\
                              AcdOptiException_dataDict_getValsSingle,\
                              AcdOptiException_geomCollection_loadFail,\
                              AcdOptiException_runConfig_loadFail
from AcdOptiFileParser import AcdOptiFileParser_simple, DataDict
import os, shutil
from acdOpti.AcdOptiRunConfig import AcdOptiRunConfig
from acdOpti import AcdOptiAcdtoolWrapper


class AcdOptiMeshInstance:
    """
    This class is "owned" by a GeometryInstance,
    where it represents the application of one MeshTemplate
    onto the GeometryInstance.
    
    It will handle variable overrides and call CUBIT in the same manner
    as the GeometryInstance, and it will deliver a mesh in .netcdf format.
    
    It is also the point of attachment for RunConfigs.   
    """
    
    #Object variables
    geometryInstance       = None
    meshTemplateCollection = None
    meshTemplate           = None
    
    runConfigs             = None #RunConfig used on this MeshInstance
    
    __paramFile            = None
    
    __templateOverrides    = None
    
    folder                 = None
    instName               = None

    lockdown               = False
    
    cubitMeshPreCommands  = ["reset", "open 'geom.cub'"]
    cubitMeshPostCommands = ["export genesis 'mesh.gen' block all overwrite"]
    
    
    def __init__(self, folder, geometryInstance, meshTemplateCollection):
        """
        Loads the meshInstance from the data
        from folder and connects it to its template and geometryInstance.
        
        Raises AcdOptiException_meshInstance_loadFail
        if something (such as "not a meshInstance folder")
        goes wrong.
        """
        print "AcdOptiMeshInstance::__init__()"
        
        self.folder = folder
        self.geometryInstance = geometryInstance
        self.meshTemplateCollection = meshTemplateCollection
    
        if not os.path.isdir(folder):
            raise AcdOptiException_meshInstance_loadFail(\
                "Folder \"" + folder + "\" does not exist")
        
        #Construct the instance name from folder name
        instname = folder
        if instname[-1] == "/":
            instname = instname[0:-1]
        instname = os.path.split(instname)[1]
        self.instName = instname

        #Load paramFile.set
        try:
            self.__paramFile = AcdOptiFileParser_simple(\
                os.path.join(folder, "paramFile.set"), 'rw')
        except IOError:
            raise AcdOptiException_meshInstance_loadFail(\
                "Problem loading file \"paramFile.set\" in folder \"" +\
                    folder + "\", got an IOError")
        if self.__paramFile.dataDict.getValSingle("fileID") != "meshInstance":
            raise AcdOptiException_meshInstance_loadFail(
                "Wrong fileID in meshInstance.set, got \"" +
                self.__paramFile.dataDict.getValSingle("fileID") + "\"")
        lock = self.__paramFile.dataDict.getValSingle("lockdown")
        if lock == "True":
            self.lockdown = True
        elif lock == "False":
            self.lockdown = False
        else:
            raise AcdOptiException_meshInstance_loadFail(\
                "Invalid content in field \"lockdown\" of file paramFile.set")
        
        #Check that the geometryInstance is correct
        geometryInstance_expectedName = self.__paramFile.dataDict.getValSingle("geomInstance_name")
        if geometryInstance.instName != geometryInstance_expectedName:
            raise AcdOptiException_meshInstance_loadFail(\
                "Excpected name of geometryInstance does not match the one passed")
        
        #Find the MeshTemplate
        meshTemplate_expectedName = self.__paramFile.dataDict.getValSingle("meshTemplate_name")
        try:
            self.meshTemplate = self.meshTemplateCollection.meshTemplates[meshTemplate_expectedName]
            self.meshTemplate.registerInstance(self)
        except KeyError:
            raise AcdOptiException_meshInstance_loadFail("Could not find the meshTemplate \""
                                                         + meshTemplate_expectedName + "\"")
        
        #Find and load template overrides
        self.__templateOverrides = {}
        try:
            templateOverrides_data = self.__paramFile.dataDict.getValSingle("templateOverrides")
        except AcdOptiException_dataDict_getValsSingle:
            raise AcdOptiException_meshInstance_loadFail\
                ("Couldn't load templateOverrides from paramFile.set")
        if not isinstance(templateOverrides_data,DataDict):
            raise AcdOptiException_meshInstance_loadFail\
                ("templateOverrides from paramFile.set is not a DataDict!")
        
        for (k,v) in zip(templateOverrides_data.keys, templateOverrides_data.vals):
            if k in self.__templateOverrides:
                raise AcdOptiException_geomCollection_loadFail\
                    ("Double occurrence of key \"" + k + "\" in templateOverrides on file")
            if not k in self.meshTemplate.paramDefaults_getKeys():
                    raise AcdOptiException_meshInstance_loadFail(
                        "Entry \"" + k + "\" in templateOverrides on file has no match in the template")
            self.__templateOverrides[k] = v

        #Find subfolders and check if they are runConfigs
        if not os.path.isdir(os.path.join(self.folder, "runConfigs")):
            raise AcdOptiException_meshInstance_loadFail("Could not find runConfigs folder")
        self.runConfigs = {}
        for d in os.listdir(os.path.join(self.folder,"runConfigs")):
            dAbs = os.path.abspath(os.path.join(self.folder,"runConfigs",d))
            if not os.path.isdir(dAbs):
                #Skip files etc.
                continue
            try:
                self.runConfigs[d] = \
                    AcdOptiRunConfig(dAbs,self)
            except AcdOptiException_runConfig_loadFail as e:
                raise AcdOptiException_meshInstance_loadFail(\
                    "Problem loading assumed runConfig folder \"" + d + "\"", e)
        
    def generatePattern(self):
        """
        Generate substitution dict
        """
        params =  self.meshTemplate.paramDefaults_copy()
        for k in self.__templateOverrides:
            assert k in params
            params[k] = self.__templateOverrides[k] 
        return params
    
    def generateCubitJou(self):
        """
        Uses the currently defined variables (overrides + inherited)
        to generate a cubit script. Returns a tuple with
        the generated script as a string, and a list of tag's not found in the template.
        """
        params = self.generatePattern()
        
        (runScript, notFound) = self.meshTemplate.meshTemplateFile.generateJou(params, self.cubitMeshPreCommands, self.cubitMeshPostCommands)
        ret = ""
        for line in runScript:
            ret += line + "\n"
        
        return (ret, notFound)
    
    def generateMesh(self):
        """
        Generates the CUBIT journal with self.generateCubitJou(),
        and runs this with the pre- and post-commands that are useful
        for generating a mesh.
        
        Also saves the journal as mesh.jou for later reference
        
        Side-effect: Sets lockdown, and generates a solid if necessary
        
        Returns any keys not found. 
        """ 
        print "AcdOptiMeshInstance::generateMesh()"
        
        if not self.geometryInstance.lockdown:
            self.geometryInstance.generateGeometry()

        #Preparation        
        params = self.generatePattern()
        templateFile = self.meshTemplate.meshTemplateFile
        
        #Make the journal for later reference
        refJouFileName = os.path.join(self.folder, "mesh.jou")
        if os.path.isfile(refJouFileName):
            os.remove(refJouFileName)
        templateFile.writeJouFile(params,refJouFileName,self.cubitMeshPreCommands, self.cubitMeshPostCommands)
        
        #Make the mesh
        shutil.copy(os.path.join(self.geometryInstance.folder, "geom.cub"), os.getcwd())
        notFound = templateFile.runCubit(params, preCommands=self.cubitMeshPreCommands,\
                                         postCommands=self.cubitMeshPostCommands)
        os.rename("mesh.gen", os.path.join(self.folder, "mesh.gen"))
        
        #Convert the mesh to NetCDF
        AcdOptiAcdtoolWrapper.convertGenNcdf(os.path.join(self.folder, "mesh.gen"),
                                             os.path.join(self.folder, "mesh.ncdf"))
        meshBad = AcdOptiAcdtoolWrapper.meshCheck(os.path.join(self.folder, "mesh.ncdf"))
        if meshBad:
            raise AcdOptiException_meshInstance_generateFail("Mesh had ISOTEs -- not a good mesh!")
        
        self.setLockdown()
        return notFound
    
    def addRunConfig(self,name,runnerType, solverTypes=None):
        """
        Creates and adds a new RunConfig with the specified
        name, runnerType and solverTypes to this MeshInstance 
        """
        
        #Check that name is not already in use
        if name in self.runConfigs:
            raise AcdOptiException_meshInstance_nameError("RunConfig name already in use")
        
        #Create the runConfig
        runConfigFolder =  os.path.join(self.folder, "runConfigs", name)
        AcdOptiRunConfig.createNew(runConfigFolder, runnerType, solverTypes)
        
        #Load it
        self.runConfigs[name] = AcdOptiRunConfig(runConfigFolder, self) 
        
    def write(self):
        """
        Update the contents of self.__paramFile to reflect
        current status of the object 
        """
        print "AcdOptiMeshInstance::write()"
        
        self.__paramFile.dataDict.setValSingle("lockdown", str(self.lockdown))
        templateOverrides_data = self.__paramFile.dataDict.getValSingle("templateOverrides")
        templateOverrides_data.clear()
        for k in self.__templateOverrides:
            templateOverrides_data.pushBack(k,self.__templateOverrides[k])
        
        self.__paramFile.write()
    
    def setLockdown(self):
        """
        Set lockdown = True,
        indicating that a mesh has been generated, and that
        the templateOverrides should not be touched.
        
        Also sets lockdown on the geometryInstance and meshTemplate,
        and writes itself to file.
        """
        print "AcdOptiMeshInstance::setLockdown()"
        
        self.geometryInstance.setLockdown()
        self.meshTemplate.setLockdown()
        self.lockdown = True
        self.write()
    def clearLockdown(self):
        """
        Clears lockdown of the mesh instance,
        and deletes generated cubit objects.
        Also clears the lockdown on any RunConfig(s)
        Also writes instance to file.
        """
        print "AcdOptiGeometryInstance::clearLockdown()"
        
        if not self.lockdown:
            return
        if os.path.isfile(os.path.join(self.folder, "mesh.gen")):
            os.remove(os.path.join(self.folder, "mesh.gen"))
        if os.path.isfile(os.path.join(self.folder, "mesh.ncdf")):
            os.remove(os.path.join(self.folder, "mesh.ncdf"))
        if os.path.isfile(os.path.join(self.folder, "mesh.jou")):
            os.remove(os.path.join(self.folder, "mesh.jou"))
        
        for rc in self.runConfigs.values():
            rc.clearLockdown()
        
        self.lockdown = False
        self.write()
    def templateOverrides_insert(self,key,val):
        if self.lockdown:
            raise AcdOptiException_meshInstance_lockdownError
        self.__templateOverrides[key] = val
        return val 
    def templateOverrides_get(self,key):
        return self.__templateOverrides[key]
    def templateOverrides_getKeys(self):
        return self.__templateOverrides.keys()
    def templateOverrides_del(self,key):
        if self.lockdown:
            raise AcdOptiException_meshInstance_lockdownError
        val = self.__templateOverrides[key]
        del self.__templateOverrides[key]
        return val
    def templateOverrides_clear(self):
        if self.lockdown:
            raise AcdOptiException_meshInstance_lockdownError
        self.__templateOverrides.clear()
    
    
    @staticmethod
    def createNew(folder, geomInstance_name, meshTemplate_name):
        """
        Creates a new empty meshInstance in a
        not previously existing folder.
        Folder name should be the same as meshInstance name.
        
        Raises AcdOptiException_meshInstance_createFail
        is something goes wrong (such as "Folder already exists")
        """
        #Construct the instance name from folder
        instname = folder
        if instname[-1] == "/":
            instname = instname[0:-1]
        instname = os.path.split(instname)[1]

        #Create the folder
        if os.path.isdir(folder):
            raise AcdOptiException_meshInstance_createFail ("Folder \"" + folder + "\" already exists")
        os.mkdir(folder)
        
        #Create paramFile.set file
        paramFile = AcdOptiFileParser_simple(\
            os.path.join(folder, "paramFile.set"), 'w')
        paramFile.dataDict.pushBack("fileID", "meshInstance")
        paramFile.dataDict.pushBack("lockdown", "False")
        paramFile.dataDict.pushBack("templateOverrides", DataDict())
        paramFile.dataDict.pushBack("meshTemplate_name", meshTemplate_name)
        paramFile.dataDict.pushBack("geomInstance_name", geomInstance_name)
        paramFile.write()
        
        #Create folder for the runConfigs
        os.mkdir(os.path.join(folder, "runConfigs"))
    
    @staticmethod
    def createNew_clone(folder, cloneFrom, newGeomInstance):
        """
        Creates a new meshInstance in a not previously existing folder,
        which has identical settings as an already existing meshInstance,
        but is attached to newGeomInstance
        The newly created meshInstance is then returned.
        
        This is a deep copy, runConfigs etc. are also cloned.
        """

        #Create the new meshInstance
        AcdOptiMeshInstance.createNew(folder, newGeomInstance.instName, cloneFrom.meshTemplate.instName)
        newInstance = AcdOptiMeshInstance(folder, newGeomInstance, cloneFrom.meshTemplateCollection)

        #Copy information        
        for key in cloneFrom.templateOverrides_getKeys():
            newInstance.templateOverrides_insert(key, cloneFrom.templateOverrides_get(key))
        
        for (runConfigName, runConfig) in cloneFrom.runConfigs.iteritems():
            newRC = AcdOptiRunConfig.createNew_clone(os.path.join(folder, "runConfigs", runConfig.instName), runConfig, newInstance)
            newInstance.runConfigs[runConfigName] = newRC
            
        newInstance.write()
        return newInstance
    
    