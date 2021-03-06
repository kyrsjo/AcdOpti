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


from AcdOptiGeometryCollection      import AcdOptiGeometryCollection
from AcdOptiMeshTemplateCollection  import AcdOptiMeshTemplateCollection
from AcdOptiScanCollection          import AcdOptiScanCollection
from AcdOptiMetaAnalysisCollection  import AcdOptiMetaAnalysisCollection
from AcdOptiDataExtractorCollection import AcdOptiDataExtractorCollection
#import AcdOptiGeometryInstance
from parameterScan.ParameterScanCollection import ParameterScanCollection

import AcdOptiFileParser
from AcdOptiExceptions import AcdOptiException_project_loadFail

import os

class AcdOptiProject():
    """
    Top-level class controlling one project
    which contains one template geometry,
    geometry instances, meshes etc.
    """
    
    #Class variables
    projectFolder_name      = None #Full path to projectFolder
    projectName_name        = None #Name of project
    
    projectDescription_file = None
    
    geomCollection          = None
    meshTemplateCollection  = None    
    
    scanCollection          = None #Old style
    parameterScanCollection = None #New style
    
    metaAnalysisCollection  = None
    dataExtractorCollection = None
    
    def __init__(self, projectFolder_name):
        """
        Loads a project
        """
        print "AcdOptiProject::__init__()"
        
        self.projectFolder_name = os.path.abspath(projectFolder_name)
        if self.projectFolder_name[-1] == "/":
            #Format the name in the most useful way
            self.projectFolder_name = self.projectFolder_name[0:-1]

        #Check whether projectFolder_name is a valid path,
        # and if necessary setup a new project
        if not os.path.isdir(self.projectFolder_name):
            raise AcdOptiException_project_loadFail(\
                "Folder " + self.projectFolder_name + " not found")        

        #Get main project parameters
        self.projectDescription_file = AcdOptiFileParser.AcdOptiFileParser_simple(\
            os.path.join(self.projectFolder_name, "project.set"), "rw")
        if self.projectDescription_file.dataDict.getValSingle("fileID") != "projectDescription":
            raise AcdOptiException_project_loadFail
        self.projectName_name = self.projectDescription_file.dataDict.getValSingle("projectName")
        if self.projectName_name != os.path.split(self.projectFolder_name)[1]:
            raise AcdOptiException_project_loadFail("Project name in in file \"project.set\" doesn't match folder name ")

        #Load the meshTemplateCollection        
        self.meshTemplateCollection = AcdOptiMeshTemplateCollection(os.path.join(self.projectFolder_name, "meshTemplates"))

        #Load the geomCollection
        self.geomCollection = AcdOptiGeometryCollection(os.path.join(self.projectFolder_name, "geomInstances"), self)

        #Load the scanCollection
        self.scanCollection = AcdOptiScanCollection(os.path.join(self.projectFolder_name, "scans"), self)
        
        #Load the metaAnalysisCollection
        self.metaAnalysisCollection = AcdOptiMetaAnalysisCollection(os.path.join(self.projectFolder_name, "metaAnalysis"), self)
        
        #Load the dataExtractorCollection (create if missing)
        if not os.path.isdir(os.path.join(self.projectFolder_name, "dataExtractor")):
            AcdOptiDataExtractorCollection.createNew(os.path.join(self.projectFolder_name, "dataExtractor"))
        self.dataExtractorCollection = AcdOptiDataExtractorCollection(os.path.join(self.projectFolder_name, "dataExtractor"), self)
        
        #Load the new-style parameterScanCollection
        if not os.path.isdir(os.path.join(self.projectFolder_name, "ParameterScanCollection")):
            ParameterScanCollection.createNew(os.path.join(self.projectFolder_name, "ParameterScanCollection"))
        self.parameterScanCollection = ParameterScanCollection(os.path.join(self.projectFolder_name, "ParameterScanCollection"),self)
            
        
    #END __init__()
        
    @staticmethod
    def createNew(folder):
        """
        Setting up a new project, creating the basic structures.
        Delegates work to similar createNew() methods.
        """
        #Folder
        try:
            os.mkdir(folder)
        except:
            print "Couldn't create the project folder!"
            raise

        #File project.set
        projectDescription_file = AcdOptiFileParser.AcdOptiFileParser_simple(\
            os.path.join(folder, "project.set"), "w")
        projectName = os.path.split(folder)[1]
        projectDescription_file.dataDict.pushBack("fileID", "projectDescription")
        projectDescription_file.dataDict.pushBack("projectName", projectName)
        projectDescription_file.write()
        
        #Mesh template folder
        AcdOptiMeshTemplateCollection.createNew(os.path.join(folder, "meshTemplates"))
        
        #Geometry instance folder
        AcdOptiGeometryCollection.createNew(os.path.join(folder, "geomInstances"))
        
        #Scan collection (old-style)
        AcdOptiScanCollection.createNew(os.path.join(folder, "scans"))
        
        #Meta-analysis collection
        AcdOptiMetaAnalysisCollection.createNew(os.path.join(folder, "metaAnalysis"))

        #DataExtractor collection
        AcdOptiDataExtractorCollection.createNew(os.path.join(folder, "dataExtractor"))
    
        #Parameter scan collection (new style)
        ParameterScanCollection.createNew(os.path.join(folder, "ParameterScanCollection"))
