import exceptions

class AcdOptiGuiException(Exception):
    pass

#OptiGuiMain
class AcdOptiGuiException_guiMain_nameTaken(AcdOptiGuiException):
    pass # This geom/mesh name is already taken
