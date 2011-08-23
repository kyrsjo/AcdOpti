import AcdOptiFileParser
import AcdOptiMeshTemplate, AcdOptiMeshInstance
import AcdOptiExceptions, exceptions
import os

class AcdOptiMeshTemplateCollection:
    """
    Collection class doing little else
    than organizing the contents of the
    meshTemplates folder.
    """
    def __init__(self,folder):
        """
        Initialize (load) a MeshTemplateCollection
        stored in some folder
        """
        self.folder = folder

        #Load the param file
        try:
            self.paramFile = AcdOptiFileParser.AcdOptiFileParser_simple(\
                os.path.join(folder, "paramFile.set"), 'rw')
        except IOError:
            raise AcdOptiExceptions.\
                AcdOptiException_meshTemplateCollection_loadFail(\
                "File paramFile.set not found")

        if self.paramFile.dataDict.getValSingle("fileID")\
                != "meshTemplateCollectionParamFile":
            raise AcdOptiExceptions.\
                AcdOptiException_meshTemplateCollection_loadFail
        
        #Find subfolders and check if they are geometry instances
        self.meshTemplates = {}
        for d in os.listdir(folder):
            dAbs = os.path.abspath(os.path.join(folder,d))
            if not os.path.isdir(dAbs):
                #Skip files etc.
                continue
            try:
                self.meshTemplates[d] = \
                    AcdOptiMeshTemplate.AcdOptiMeshTemplate(dAbs)
            except AcdOptiExceptions.\
                    AcdOptiException_meshTemplate_loadFail:
                raise AcdOptiExceptions.\
                    AcdOptiException_meshTemplateCollection_loadFail(\
                    "Problem loading mesh template instance \"" + d + "\"")

    @staticmethod
    def createNew(folder):
        """
        Sets up the basic structure inside
        a given folder, which is created.
        """
        #Create the directory
        os.mkdir(folder)
        
        #File that holds the parameters and their default values
        paramFile = AcdOptiFileParser.AcdOptiFileParser_simple(\
            os.path.join(folder,"paramFile.set"), 'w')
        paramFile.dataDict.pushBack("fileID", "meshTemplateCollectionParamFile")
        paramFile.write()

    #Object variables
    paramFile = None
    meshTemplates = None
    folder = None