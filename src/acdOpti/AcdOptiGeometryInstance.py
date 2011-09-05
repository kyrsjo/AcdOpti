from AcdOptiFileParser import AcdOptiFileParser_simple, DataDict
from AcdOptiExceptions import *
#import exceptions
import os
import AcdOptiCubitTemplateFile
from AcdOptiMeshInstance import AcdOptiMeshInstance

class AcdOptiGeometryInstance():
    """
    Class that organizes a specific geometry instance,
    i.e. a set of geometry parameters,
    which are merged with the template geometry to
    create a CUBIT script. This script may be exported,
    or sent to CUBIT for generating the solid.
    Pointers to mesh instances are kept.
    """
    def __init__(self, folder, template):
        """
        Loads the geomInstance from the data
        from folder.
        
        Raises AcdOptiException_geomInstance_loadFail
        if something (such as "not a geomInstance folder")
        goes wrong.
        """
        self.folder   = folder
        self.template = template
        
        #Check that folder exists
        if not os.path.isdir(folder):
            raise AcdOptiException_geomInstance_loadFail(\
                "Folder \"" + folder + "\" does not exist")
        
        #Construct the instance name from folder name
        instName = folder
        if instName[-1] == "/":
            instName = instName[0:-1]
        instName = os.path.split(instName)[1]
        self.instName = instName

        #Load paramFile.set
        try:
            self.__paramFile = AcdOptiFileParser_simple(\
                os.path.join(folder, "paramFile.set"), 'rw')
        except IOError as e:
            raise AcdOptiException_geomInstance_loadFail(\
                "Problem loading file \"paramFile.set\" in folder \"" +\
                    folder + "\", got an IOError")
        if self.__paramFile.dataDict.getValSingle("fileID") != "geomInstance":
            raise AcdOptiException_geomInstance_loadFail(
                "Wrong fileID in geomInstance.set, got \"" +
                self.__paramFile.dataDict.getValSingle("fileID") + "\"")
        lock = self.__paramFile.dataDict.getValSingle("lockdown")
        if lock == "True":
            self.lockdown = True
        elif lock == "False":
            self.lockdown = False
        else:
            raise AcdOptiException_geomInstance_loadFail(\
                "Invalid content in field \"lockdown\" of file paramFile.set")
        
        #Find and load template overrides
        self.__templateOverrides = {}
        try:
            templateOverrides_data = self.__paramFile.dataDict.getValSingle("templateOverrides")
        except AcdOptiException_dataDict_getValsSingle:
            raise AcdOptiException_geomInstance_loadFail\
                ("Couldn't load templateOverrides from paramFile.set")
        if not isinstance(templateOverrides_data,DataDict):
            raise AcdOptiException_geomInstance_loadFail\
                ("templateOverrides from paramFile.set is not a DataDict!")
        
        for (k,v) in zip(templateOverrides_data.keys, templateOverrides_data.vals):
            if k in self.__templateOverrides:
                raise AcdOptiException_geomInstance_loadFail\
                    ("Double occurrence of key \"" + k + "\" in templateOverrides on file")
            if not k in self.template.paramDefaults_getKeys():
                    raise AcdOptiException_geomInstance_loadFail(
                        "Entry \"" + k + "\" in templateOverrides on file has no match in the template")
            self.__templateOverrides[k] = v
        
        #Are there any mesh instances?
        self.meshInsts = {}
        for d in os.listdir(os.path.join(self.folder,self.meshInstanceFolderName)):
            dAbs = os.path.abspath(os.path.join(folder,self.meshInstanceFolderName,d))
            if not os.path.isdir(dAbs):
                #Skip files etc.
                continue
            try:
                self.meshInsts[d] = AcdOptiMeshInstance(dAbs, self, self.template.project.meshTemplateCollection)
            except AcdOptiException_meshInstance_loadFail as e:
                raise AcdOptiException_geomCollection_loadFail(\
                    "Problem loading mesh instance \"" + dAbs + "\", got error \"" + str(e) + "\"")
        
        #Scan instance name
        self.scanInstance_name = self.__paramFile.dataDict["scanInstance_name"]  
        
    
    def write(self):
        """
        Update the contents of self.__paramFile to reflect
        current status of the class 
        """
        print "AcdOptiGeometryInstance::write()"
        self.__paramFile.dataDict.setValSingle("lockdown", str(self.lockdown))
        if self.scanInstance != None:
            self.__paramFile.dataDict.setValSingle("scanInstance_name", self.scanInstance.instName)
        else:
            self.__paramFile.dataDict.setValSingle("scanInstance_name", "")
            
        
        templateOverrides_data = self.__paramFile.dataDict.getValSingle("templateOverrides")
        templateOverrides_data.clear()
        for k in self.__templateOverrides:
            templateOverrides_data.pushBack(k,self.__templateOverrides[k])
        
        self.__paramFile.write()
    
    def generatePattern(self):
        """
        Generate substitution dict
        """
        params = self.template.paramDefaults_copy()
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
        
        #Get the CUBIT template file object
        templateFile = self.template.geomTemplateFile
        
        return templateFile.subsString(params)
    
    def generateGeometry(self):
        """
        Generates the CUBIT journal with self.generateCubitJou(),
        and runs this with the pre- and post-commands that are useful
        for generating a solid.

        Also saves the journal as geom.jou for later reference.

        Side-effect: Sets lockdown
        
        Returns any keys not found. 
        """ 
        #Preparation
        params = self.generatePattern()
        templateFile = self.template.geomTemplateFile
        
        #Make the journal for later reference
        refJouFileName = os.path.join(self.folder, "geom.jou")
        if os.path.isfile(refJouFileName):
            os.remove(refJouFileName)
        templateFile.writeJouFile(params,refJouFileName,self.cubitGeomPreCommands, self.cubitGeomPostCommands)

        #Generate the geometry
        templateFile.runCubit(params, preCommands=self.cubitGeomPreCommands,\
                              postCommands=self.cubitGeomPostCommands)
        os.rename("geom.cub", os.path.join(self.folder, "geom.cub"))
        
        self.setLockdown()
    
    
    def addMeshInstance(self, meshTemplateName, meshInstanceName):
        """
        Creates and adds a new meshInstance to this geometryInstance.
        Raises an AcdOptiException_geomInstance_nameError
        if the meshInstanceName is already in use or the meshTemplate does not exist.
        """

        print "AcdOptiGeometryInstance::addMeshInstance(meshTemplateName=\""\
             + meshTemplateName + "\" , meshInstanceName=\"" + meshInstanceName + "\" )"
        
        #Check that the mesh instance name is not already in use:
        if meshInstanceName in self.meshInsts:
            raise AcdOptiException_geomInstance_nameError("Mesh instance name already in use")
        
        #Find the meshTemplate
#        try: #TODO: reomove this block?!?
#            meshTemplate = self.template.project.meshTemplateCollection.meshTemplates[meshTemplateName]
#        except KeyError:
#            raise AcdOptiException_geomInstance_nameError("meshTemplateName not found")
        
        folder = os.path.join(self.folder,self.meshInstanceFolderName,meshInstanceName)
    
        try:
            AcdOptiMeshInstance.createNew(folder, self.instName, meshTemplateName)
        except AcdOptiException_meshInstance_createFail:
            raise AcdOptiException_geomInstance_nameError("Mesh instance name \"" + meshInstanceName + "\" already in use")
        
        meshInstance = AcdOptiMeshInstance(folder, self, self.template.project.meshTemplateCollection)
        
        self.meshInsts[meshInstanceName] = meshInstance

        print "AcdOptiGeometryInstance::addMeshInstance():Mesh instances currently loaded:" + str(self.meshInsts)
        
    def setLockdown(self):
        """
        Set lockdown = True,
        indicating that a geometry has been generated, and that
        the templateOverrides should not be touched.
        
        Also writes instance to file.
        """
        print "AcdOptiGeometryInstance::setLockdown()"
        self.template.setLockdown()
        self.lockdown = True
        self.write()
        
    
    def clearLockdown(self):
        """
        Clears lockdown of the geometry instance and any mesh instances,
        and deletes generated cubit objects.
        
        Also writes instance to file.
        """
        print "AcdOptiGeometryInstance::clearLockdown()"
        
        if not self.lockdown:
            return
        
        for mesh in self.meshInsts.values():
            mesh.clearLockdown()
        if os.path.isfile(os.path.join(self.folder, "geom.cub")):
            os.remove(os.path.join(self.folder, "geom.cub"))
        if os.path.isfile(os.path.join(self.folder, "geom.jou")):
            os.remove(os.path.join(self.folder, "geom.jou"))
        self.lockdown = False
        self.write()
    def templateOverrides_insert(self,key,val):
        if self.lockdown:
            raise AcdOptiException_geomInstance_lockdownError
        self.__templateOverrides[key] = val
        return val
    def templateOverrides_get(self,key):
        return self.__templateOverrides[key]
    def templateOverrides_getKeys(self):
        return self.__templateOverrides.keys()
    def templateOverrides_len(self):
        return len(self.__templateOverrides)
    def templateOverrides_del(self,key):
        if self.lockdown:
            raise AcdOptiException_geomInstance_lockdownError
        val = self.__templateOverrides[key]
        del self.__templateOverrides[key]
        return val
    def templateOverrides_clear(self):
        if self.lockdown:
            raise AcdOptiException_geomInstance_lockdownError
        self.__templateOverrides.clear()

    @staticmethod
    def createNew(folder):
        """
        Creates a new empty geomInstance in a
        not previously existing folder.
        Geometry instance name will be the same as the folder name.
        
        Raises AcdOptiException_geomInstance_createFail
        is something goes wrong (such as "Folder already exists")
        """
        #Construct the instance name from folder
        instName = folder
        if instName[-1] == "/":
            instName = instName[0:-1]
        instName = os.path.split(instName)[1]

        #Create the folder
        if os.path.isdir(folder):
            raise AcdOptiException_geomInstance_createFail("Folder \"" + folder + "\" already exists")
        os.mkdir(folder)
        
        #Create paramFile.set file
        paramFile = AcdOptiFileParser_simple(\
            os.path.join(folder, "paramFile.set"), 'w')
        paramFile.dataDict.pushBack("fileID", "geomInstance")
        paramFile.dataDict.pushBack("lockdown", "False")
        paramFile.dataDict.pushBack("templateOverrides", DataDict())
        paramFile.dataDict.pushBack("scanInstance_name", "")
        paramFile.write()
        
        #Create folder for meshInstance's
        os.mkdir(os.path.join(folder, AcdOptiGeometryInstance.meshInstanceFolderName))

    @staticmethod
    def createNew_clone(folder, cloneFrom):
        """
        Creates a new geomInstance in a not previously existing folder,
        which has identical settings as an already existing geometryInstance.
        The newly created geomInstance is then returned.
        
        This is a deep copy, meshInstances etc. are also cloned.
        """
        #Create the new geomInstance
        AcdOptiGeometryInstance.createNew(folder)
        newInstance = AcdOptiGeometryInstance(folder, cloneFrom.template)

        #Copy information        
        for key in cloneFrom.templateOverrides_getKeys():
            newInstance.templateOverrides_insert(key, cloneFrom.templateOverrides_get(key))
        
        for (meshName, mesh) in cloneFrom.meshInsts.iteritems():
            newMesh = AcdOptiMeshInstance.createNew_clone(os.path.join(folder,"meshInstances",meshName), mesh, newInstance)
            newInstance.meshInsts[meshName] = newMesh
        
        newInstance.write()
        return newInstance

    #Object variables
    lockdown    = False #Write-protected?
    
    folder      = None  #Folder where this geometryInstance is stored
    __paramFile = None  #Settings file for the geometryInstance
    instName    = None  #Name of this instance
    meshInsts   = None  #Dict of mesh instances for this geometry
    
    template    = None  #Pointer to the GeometryCollection of which
                        # this is an instance
    __templateOverrides = None #Dict describing the variables that are
                             # given a different value than the default
                             # from the collection.  

    scanInstance = None #If this geomInstance belongs to a scan, this points to it.
                        # This is set by the scanInstance's __init__()
    scanInstance_name = None # The name of said scanInstance. Used by it's init for consitency check.
    
    #Static class fields
    cubitGeomPreCommands  = ["reset"]
    cubitGeomPostCommands = ["save as 'geom.cub' overwrite"]
    
    meshInstanceFolderName = "meshInstances"