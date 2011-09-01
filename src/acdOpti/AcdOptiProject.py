import AcdOptiGeometryCollection, AcdOptiGeometryInstance
import AcdOptiMeshTemplateCollection
import AcdOptiFileParser
from AcdOptiExceptions import *

import os
from acdOpti.AcdOptiScanCollection import AcdOptiScanCollection

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
    
    scanCollection = None
    
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
        self.meshTemplateCollection = AcdOptiMeshTemplateCollection.AcdOptiMeshTemplateCollection(\
            os.path.join(self.projectFolder_name, "meshTemplates"))

        #Load the geomCollection
        self.geomCollection = AcdOptiGeometryCollection.AcdOptiGeometryCollection(\
            os.path.join(self.projectFolder_name, "geomInstances"), self)

        #Load the scanCollection
        self.scanCollection = AcdOptiScanCollection(os.path.join(self.projectFolder_name, "scans"), self)
        
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
        AcdOptiMeshTemplateCollection.AcdOptiMeshTemplateCollection.createNew(\
            os.path.join(folder, "meshTemplates"))
        
        #Geometry instance folder
        AcdOptiGeometryCollection.AcdOptiGeometryCollection.createNew(\
            os.path.join(folder, "geomInstances"))
        
        #Scan collection
        AcdOptiScanCollection.createNew(os.path.join(folder, "scans"))


    

    
    
