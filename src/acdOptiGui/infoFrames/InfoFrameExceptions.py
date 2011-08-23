#import exceptions

class InfoFrameException(Exception):
    pass

#GeometryCollection
class InfoFrameException_geometryCollection_dontDelete(InfoFrameException):
    pass #Tried to delete a parameter which is in use

#MeshTemplate
class InfoFrameException_meshTemplate_dontDelete(InfoFrameException):
    pass #Tried to delete a parameter which is in use