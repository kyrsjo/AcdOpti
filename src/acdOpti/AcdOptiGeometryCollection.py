from AcdOptiFileParser import AcdOptiFileParser_simple,\
                              DataDict
from AcdOptiCubitTemplateFile import AcdOptiCubitTemplateFile

from AcdOptiGeometryInstance import AcdOptiGeometryInstance

from AcdOptiExceptions import AcdOptiException_geomCollection_loadFail,\
                              AcdOptiException_geomCollection_lockdownError,\
                              AcdOptiException_geomInstance_loadFail,\
                              AcdOptiException_dataDict_getValsSingle

import os

class AcdOptiGeometryCollection:
    """
    Class that knows what the geometry parameters are,
    and organizes the content of the geomInstances folder.
    """
    
    #Object variables
    geomInstances = None
    folder = None
    
    __paramDefaults = None #Default value of the parameters
    __paramFile     = None #File holding these

    geomTemplateFile        = None
    geomTemplateFile_name   = "geomTemplateFile.jou.template"

    lockdown = False

    project = None #Pointer to the top-level AcdOptiProject

    #TODO: Need link to geometry cubit template file

    def __init__(self,folder, project):
        """
        Initialize (load) a GeometryCollection
        stored in some folder
        """
        self.folder = folder
        self.project = project

        #Load the param file
        try:
            self.__paramFile = AcdOptiFileParser_simple(\
                os.path.join(self.folder, "paramFile.set"), 'rw')
        except IOError:
            raise AcdOptiException_geomCollection_loadFail\
                    ("File paramFile.set not found")

        if self.__paramFile.dataDict.getValSingle("fileID")\
                != "geomCollectionParamFile":
            raise AcdOptiException_geomCollection_loadFail\
                ("Wrong fileID, got\""\
                     + self.__paramFile.dataDict.getValSingle("fileID")\
                     + "\" while loading __paramFile")
        lock = self.__paramFile.dataDict.getValSingle("lockdown")
        if lock == "True":
            self.lockdown = True
        elif lock == "False":
            self.lockdown = False
        else:
            raise AcdOptiException_geomInstance_loadFail(\
                "Invalid content in field \"lockdown\" of file paramFile.set")

        #Load the default parameters
        self.__paramDefaults = {}
        try:
            paramDefaults_data = self.__paramFile.dataDict.getValSingle("paramDefaults")
        except AcdOptiException_dataDict_getValsSingle:
            raise AcdOptiException_geomCollection_loadFail\
                ("Couldn't load paramDefaults from file paramFile.set")
        if not isinstance(paramDefaults_data,DataDict):
            raise AcdOptiException_geomCollection_loadFail\
                ("paramDefaults from paramFile is not a DataDict!")
                
        for (k,v) in zip(paramDefaults_data.keys, paramDefaults_data.vals):
            if k in self.__paramDefaults:
                raise AcdOptiException_geomCollection_loadFail\
                    ("Double occurence of key \"" + k + "\" in paramFile")
            self.__paramDefaults[k] = v

        #Load the template file
        self.geomTemplateFile = AcdOptiCubitTemplateFile(os.path.join(folder,self.geomTemplateFile_name))

        #Find subfolders and check if they are geometry instances
        self.geomInstances = {}
        for d in os.listdir(self.folder):
            dAbs = os.path.abspath(os.path.join(self.folder,d))
            if not os.path.isdir(dAbs):
                #Skip files etc.
                continue
            try:
                self.geomInstances[d] = \
                    AcdOptiGeometryInstance(dAbs, self)
            except AcdOptiException_geomInstance_loadFail as e:
                print e
                raise AcdOptiException_geomCollection_loadFail(\
                    "Problem loading geometry instance \"" + d + "\"")
    def write(self):
        """
        Write the current contents of this class to paramFile,
        which is then written to file.
        """
        print "AcdOptiGeometryCollection::write()"
        print "Lockdown =", self.lockdown
        self.__paramFile.dataDict.setValSingle("lockdown", str(self.lockdown))
        
        paramDefaults_data = self.__paramFile.dataDict.getValSingle("paramDefaults")
        paramDefaults_data.clear()
        for (k,v) in self.__paramDefaults.iteritems():
            paramDefaults_data.pushBack(k,v)
        
        print self.__paramFile   
        self.__paramFile.write()

    def mayDelete(self,key):
        """
        Check if key can be deleted -
        if it has it been overridden in a GeometryInstance
        or (TODO) is used in the cubit template script,
        return the problematic AcdOptiGeometryInstance or AcdOptiCubitTemplateFile.
        Normally return None, meaning that the key may be deleted.
        """
        for gi in self.geomInstances:
            if key in self.geomInstances[gi].templateOverrides_getKeys():
                return self.geomInstances[gi]
        return None

    def setLockdown(self):
        """
        Set lockdown = True,
        indicating that a geometry instance has been generated, and that
        the template should not be touched.
        
        Also writes data to file
        """
        print "AcdOptiGeometryCollection::setLockdown()"        
        self.lockdown = True
        self.write()
    def clearLockdown(self):
        """
        Clears lockdown of the geometry collection and
        any geometry/mesh instances, deleting generated cubit objects
        
        Also writes instance to file.
        """
        print "AcdOptiGeometryCollection::clearLockdown()"
        
        for geomInstance in self.geomInstances.values():
            geomInstance.clearLockdown()
        
        self.lockdown = False
        self.write()
    def paramDefaults_insert(self,key,val):
        if self.lockdown:
            raise AcdOptiException_geomCollection_lockdownError
        self.__paramDefaults[key] = val
        return val
    def paramDefaults_get(self,key):
        return self.__paramDefaults[key]
    def paramDefaults_getKeys(self):
        return self.__paramDefaults.keys()
    def paramDefaults_copy(self):
        return self.__paramDefaults.copy()
    def paramDefaults_len(self):
        return len(self.__paramDefaults)
    def paramDefaults_del(self,key):
        if self.lockdown:
            raise AcdOptiException_geomCollection_lockdownError
        val = self.__paramDefaults[key]
        del self.__paramDefaults[key]
        return val
    def paramDefaults_clear(self):
        if self.lockdown:
            raise AcdOptiException_geomCollection_lockdownError
        self.__paramDefaults.clear()

    @staticmethod
    def createNew(folder):
        """
        Sets up the basic structure inside
        a given folder, which is created.
        """
        #Create the directory
        os.mkdir(folder)
        
        #File that holds the parameters and their default values
        paramFile = AcdOptiFileParser_simple(\
            os.path.join(folder,"paramFile.set"), 'w')
        paramFile.dataDict.pushBack("fileID", "geomCollectionParamFile")
        paramFile.dataDict.pushBack("lockdown", "False")
        paramFile.dataDict.pushBack("paramDefaults",DataDict())
        paramFile.write()

        #Default empty template file
        AcdOptiCubitTemplateFile.createEmpty(os.path.join(folder,AcdOptiGeometryCollection.geomTemplateFile_name))
    
