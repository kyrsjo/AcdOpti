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


from AcdOptiExceptions import AcdOptiException_meshTemplate_createFail,\
                              AcdOptiException_meshTemplate_loadFail,\
                              AcdOptiException_meshTemplate_lockdownError,\
                              AcdOptiException_dataDict_getValsSingle
from AcdOptiFileParser import AcdOptiFileParser_simple, DataDict
from AcdOptiCubitTemplateFile import AcdOptiCubitTemplateFile
import os


class AcdOptiMeshTemplate:
    """
    Class that represents a specific
    mesh template script, which can be applied
    in different configurations to different
    geometry instances.
    
    One mesh template =
    meshing script with variables + default values for those variables.
    """
    def __init__(self, folder):
        self.folder = folder
        
        #Construct the instance name from folder
        instname = folder
        if instname[-1] == "/":
            instname = instname[0:-1]
        self.instName = instname = os.path.split(instname)[1]
        
        #Load the param file
        try:
            self.__paramFile = AcdOptiFileParser_simple(\
                os.path.join(self.folder, "paramFile.set"), 'rw')
        except IOError:
            raise AcdOptiException_meshTemplate_loadFail("File paramFile.set not found")

        if self.__paramFile.dataDict.getValSingle("fileID")\
                != "meshTemplateParamFile":
            raise AcdOptiException_meshTemplate_loadFail\
                ("Wrong fileID, got \""\
                     + self.__paramFile.dataDict.getValSingle("fileID")\
                     + "\" while loading paramFile")
        if self.__paramFile.dataDict.getValSingle("instName")\
                != instname:
            raise AcdOptiException_meshTemplate_loadFail("templateName doesn't match folder name")
        lock = self.__paramFile.dataDict.getValSingle("lockdown")
        if lock == "True":
            self.lockdown = True
        elif lock == "False":
            self.lockdown = False
        else:
            raise AcdOptiException_meshTemplate_loadFail(\
                "Invalid content in field \"lockdown\" of file paramFile.set, got'"+lock+"'")
        #Load the default parameters
        self.__paramDefaults = {}
        try:
            paramDefaults_data = self.__paramFile.dataDict.getValSingle("paramDefaults")
        except AcdOptiException_dataDict_getValsSingle:
            raise AcdOptiException_meshTemplate_loadFail\
                ("Couldn't load paramDefaults from file paramFile.set")
        if not isinstance(paramDefaults_data,DataDict):
            raise AcdOptiException_meshTemplate_loadFail\
                ("paramDefaults from paramFile is not a DataDict!")
                
        for (k,v) in zip(paramDefaults_data.keys, paramDefaults_data.vals):
            if k in self.__paramDefaults:
                raise AcdOptiException_meshTemplate_loadFail\
                    ("Double occurrence of key \"" + k + "\" in paramFile")
            self.__paramDefaults[k] = v

        #Load the template file
        self.meshTemplateFile = AcdOptiCubitTemplateFile(os.path.join(folder,self.meshTemplateFile_name))
        
        #Initialize __meshInstances
        self.__meshInstances = []
    
    def mayDelete(self,key): #TODO!!
        """
        Check if key can be deleted -
        if it has it been overridden in a MeshInstance
        or (TODO) is used in the cubit template script,
        return the problematic AcdOptiMeshInstance or AcdOptiCubitTemplateFile.
        Normally return None, meaning that the key may be deleted.
        """
        print "AcdOptiMeshTemplate::mayDelete()"
    
        for mi in self.__meshInstances:
            if key in mi.templateOverrides_getKeys():
                return mi
        return None
    
    def write(self):
        """
        Write the current contents of this class to paramFile,
        which is written to file.
        """
        print "AcdOptiMeshTemplate::write()"
        self.__paramFile.dataDict.setValSingle("lockdown", str(self.lockdown))

        paramDefaults_data = self.__paramFile.dataDict.getValSingle("paramDefaults")
        paramDefaults_data.clear()
        
        for (k,v) in self.__paramDefaults.iteritems():
            paramDefaults_data.pushBack(k,v)
            
        self.__paramFile.write()
    
    def registerInstance(self, instance):
        """
        Register a mesh instance with this mesh template.
        """
        self.__meshInstances.append(instance)
    
    def setLockdown(self):
        """
        Set lockdown = True,
        indicating that a mesh instance has been generated, and that
        the template should not be touched.
        
        Also writes data to file.
        """
        print "AcdOptMeshTemplate::setLockdown()"
        self.lockdown = True
        self.write()
        
    def clearLockdown(self):
        """
        Clears lockdown of the mesh template and
        any mesh instances, deleting generated cubit objects.
        Also writes instance to file.
        """
        print "AcdOptiMeshTemplate::clearLockdown()"
        
        for meshInstance in self.__meshInstances:
            meshInstance.clearLockdown()

        self.lockdown = False
        self.write()
    def paramDefaults_insert(self,key,val):
        if self.lockdown:
            raise AcdOptiException_meshTemplate_lockdownError
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
            raise AcdOptiException_meshTemplate_lockdownError
        val = self.__paramDefaults[key]
        del self.__paramDefaults[key]
        return val
    def paramDefaults_clear(self):
        if self.lockdown:
            raise AcdOptiException_meshTemplate_lockdownError
        self.__paramDefaults.clear()

    
    @staticmethod
    def createNew(folder):
        """
        Creates a new empty meshTemplate in a
        not previously existing folder.
        Folder name should be the same as geometry instance name.
        
        Raises AcdOptiException_meshTemplate_createFail
        is something goes wrong (such as "Folder already exists")
        """
        
        #Construct the instance name from folder
        instname = folder
        if instname[-1] == "/":
            instname = instname[0:-1]
        instname = os.path.split(instname)[1]
        if os.path.isdir(folder):
            raise AcdOptiException_meshTemplate_createFail ("Folder \"" + folder + "\" already exists")
        os.mkdir(folder)
        
        #Create the paramFile
        paramFile = AcdOptiFileParser_simple(\
            os.path.join(folder, "paramFile.set"), 'w')
        paramFile.dataDict.pushBack("fileID", "meshTemplateParamFile")
        paramFile.dataDict.pushBack("instName", instname)
        paramFile.dataDict.pushBack("lockdown", "False")
        paramFile.dataDict.pushBack("paramDefaults", DataDict())
        paramFile.write()
        
        #Default empty template file
        AcdOptiCubitTemplateFile.createEmpty(os.path.join(folder,AcdOptiMeshTemplate.meshTemplateFile_name))
         
    
    #Object variables
    folder       = None  #Folder where this template lives
    instName     = None  #Name of this template
    
    meshTemplateFile_name   = "meshTemplateFile.jou.template"
    meshTemplateFile = None
    
    __meshInstances = None #List of mesh instances implementing this template
    
    lockdown = False
    __paramFile =  None
    __paramDefaults = None
