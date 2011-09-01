import exceptions
import acdOpti

class AcdOptiException(Exception):
    pass

#Project exceptions
# class AcdOptiException_project_folderExists(AcdOptiException):
#     pass
#class AcdOptiException_project_folderNotFound(AcdOptiException):
#    pass
# class AcdOptiException_project_folderNameMismatch(AcdOptiException):
#     pass
class AcdOptiException_project_loadFail(AcdOptiException):
    pass

#Settings exception
class AcdOptiException_settings_notFound(AcdOptiException):
    pass

#GeomCollection
class AcdOptiException_geomCollection_loadFail(AcdOptiException):
    pass
class AcdOptiException_geomCollection_lockdownError(AcdOptiException):
    pass
#GeomInstance
class AcdOptiException_geomInstance_loadFail(AcdOptiException):
    pass
class AcdOptiException_geomInstance_createFail(AcdOptiException):
    pass
class AcdOptiException_geomInstance_nameError(AcdOptiException):
    pass # This mesh instance name for this geometry is already taken
class AcdOptiException_geomInstance_lockdownError(AcdOptiException):
    pass

#MeshTemplateCollection
class AcdOptiException_meshTemplateCollection_loadFail(AcdOptiException):
    pass

#MeshTemplate
class AcdOptiException_meshTemplate_loadFail(AcdOptiException):
    pass
class AcdOptiException_meshTemplate_createFail(AcdOptiException):
    pass
class AcdOptiException_meshTemplate_lockdownError(AcdOptiException):
    pass

#MeshInstance
class AcdOptiException_meshInstance_createFail(AcdOptiException):
    pass
class AcdOptiException_meshInstance_loadFail(AcdOptiException):
    pass
class AcdOptiException_meshInstance_lockdownError(AcdOptiException):
    pass
class AcdOptiException_meshInstance_nameError(AcdOptiException):
    pass

#DataDict exceptions
class AcdOptiException_dataDict_stringWithSpace(AcdOptiException):
    pass
class AcdOptiException_dataDict_notAString(AcdOptiException):
    pass
class AcdOptiException_dataDict_getValsSingle(AcdOptiException):
    pass
class AcdOptiException_dataDict_setValSingle(AcdOptiException):
    pass

#File parser exceptions
class AcdOptiException_fileParser_invalidSyntax(AcdOptiException):
    pass
class AcdOptiException_fileParser_invalidMode(AcdOptiException):
    pass

#AcdOptiCubitTemplateFile
class AcdOptiException_cubitTemplateFile_fileAlreadyExists(AcdOptiException):
    pass
class AcdOptiException_cubitTemplateFile_CUBITerror(AcdOptiException):
    pass
class AcdOptiException_cubitTemplateFile_initError(AcdOptiException):
    pass

#AcdOptiRunConfig
class AcdOptiException_runConfig_createFail(AcdOptiException):
    pass
class AcdOptiException_runConfig_loadFail(AcdOptiException):
    pass
class AcdOptiException_runConfig_stageError(AcdOptiException):
    pass
class AcdOptiException_runConfig_updateStateError(AcdOptiException):
    pass
#AcdOptiRunner
class AcdOptiException_optiRunner_createFail(AcdOptiException):
    pass
class AcdOptiException_optiRunner_loadFail(AcdOptiException):
    pass
class AcdOptiException_optiRunner_remoteProblem(AcdOptiException):
    pass
class AcdOptiException_optiRunner_stageError(AcdOptiException):
    pass
class AcdOptiException_optiRunner_runError(AcdOptiException):
    pass
#AcdOptiSolverSetup
class AcdOptiException_solverSetup_createFail(AcdOptiException):
    pass
class AcdOptiException_solverSetup_createFail_nameTaken(AcdOptiException):
    pass
class AcdOptiException_solverSetup_loadFail(AcdOptiException):
    pass

#AcdOptiScanCollection
class AcdOptiException_scanCollection_createFail(AcdOptiException):
    pass
class AcdOptiException_scanCollection_loadFail(AcdOptiException):
    pass

#AcdOptiScan
class AcdOptiException_scan_createFail(AcdOptiException):
    pass
class AcdOptiException_scan_loadFail(AcdOptiException):
    pass