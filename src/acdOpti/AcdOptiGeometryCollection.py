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


from AcdOptiFileParser import AcdOptiFileParser_simple, DataDict
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
                self.geomInstances[d] = AcdOptiGeometryInstance(dAbs, self)
            except AcdOptiException_geomInstance_loadFail as e:
                raise AcdOptiException_geomCollection_loadFail("Problem loading geometry instance \"" + d + "\", got error='" + str(e.args) + "'")
                
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

    def addGeomInstance(self,name):
        """
        Creates and adds a GeometryInstance to the geomCollection.
        Raises an AcdOptiException_geomInstance_createFail if the name already exists.
        The created geomInstance is returned.
        """
        #Create the AcdOptiGeometryInstance
        folder = os.path.join(self.folder, name)
        AcdOptiGeometryInstance.createNew(folder)

        #Add it to the project/geomCollection
        assert not name in self.geomInstances, "Folder did not exist but there was an entry in self.geomInstances?!? name='" + name + "'"
        self.geomInstances[name] = AcdOptiGeometryInstance(folder,self)
        
        return self.geomInstances[name]
    
    def cloneGeomInstance(self,oldName, newName):
        """
        Create a new geomInstance called <newName>, having
        identical same settings, meshInstance etc. as the one called <oldName>.
        The new geom instance is returned.
        """
        assert oldName in self.geomInstances
        newGeom = AcdOptiGeometryInstance.createNew_clone(os.path.join(self.folder, newName), self.geomInstances[oldName]) 
        self.geomInstances[newName] = newGeom
        return newGeom

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
    
