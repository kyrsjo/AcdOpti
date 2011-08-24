from AcdOptiFileParser import AcdOptiFileParser_simple
from AcdOptiExceptions import AcdOptiException_runConfig_createFail,\
                              AcdOptiException_runConfig_loadFail,\
                              AcdOptiException_runConfig_stageError,\
                              AcdOptiException_runConfig_updateStateError

from AcdOptiSolverSetup import AcdOptiSolverSetup
from AcdOptiRunner import AcdOptiRunner

import os, shutil
from datetime import datetime

class AcdOptiRunConfig:
    """
    Class representing a run configuration,
    holding solvers and job setup, setups and allows starting/stopping runs
    and querying their status. 
    """
    
    folder   = None
    instName = None
    lockdown = None
    
    solverSetups = None
    runner       = None
    meshInstance = None
    
    __paramFile = None
    
    status = "not_initialized"
    
    stageName = None   #status > staged, name of tar.gz file with staged data (else None)
    stageFolder = None #Path to the staging directory (if status>staged, else None)
    
    statuses= ["not_initialized", # Before object is fully created
               "initialized",     # Has one or more runners and a meshInstance
               "staged",          # Object is staged, all files are in place
               "remote::uploaded",# Files uploaded to HPC, but has not yet appeared in queue system
               "remote::queued",  # Job is submitted to HPC, but has not started yet
               "remote::running", # Job is running
               "remote::finished",# Job has finished, but is not downloaded
               "local::running",  # Local job is running
               "finished"]        # Job is completely finished, ready for analysis
    
    def __init__(self, folder, meshInstance):
        print "AcdOptiRunConfig::__init__()"
        self.folder = folder
        self.meshInstance = meshInstance
        self.status = "not_initialized"
        
        #Construct the instance name from folder
        instname = folder
        if instname[-1] == "/":
            instname = instname[0:-1]
        self.instName = instname = os.path.split(instname)[1]
        
        #Load the param file
        try:
            print os.path.join(self.folder, "paramFile.set")
            self.__paramFile = AcdOptiFileParser_simple(\
                os.path.join(self.folder, "paramFile.set"), 'rw')
        except IOError:
            raise AcdOptiException_runConfig_loadFail("File paramFile.set not found")

        if self.__paramFile.dataDict.getValSingle("fileID") != "runConfigParamFile":
            raise AcdOptiException_runConfig_loadFail\
                ("Wrong fileID, got \""+ self.__paramFile.dataDict.getValSingle("fileID")+"\" while loading paramFile")                
        if self.instName != self.__paramFile.dataDict.getValSingle("instName"):
            raise AcdOptiException_runConfig_loadFail("instName doesn't match folder name, expected='"+self.instName+"', got '"+self.__paramFile.dataDict.getValSingle("instName")+"'")
        
        self.status = self.__paramFile.dataDict.getValSingle("status")
        if not self.status in self.statuses:
            raise AcdOptiException_runConfig_loadFail("Status '" + self.status + "' not valid")
        self.stageName = self.__paramFile.dataDict.getValSingle("stageName")
        if self.stageName == "":
            self.stageName = None
        if self.stageName and self.status == "initialized":
            raise AcdOptiException_runConfig_loadFail("StageName != None while status='" + self.status + "'")
        self.stageFolder = self.__paramFile.dataDict.getValSingle("stageFolder")
        if self.stageFolder == "":
            self.stageFolder = None
        #TODO: Sanity check on stageFolder
        
        #Load the solverSetups
        solverSetupNames = self.__paramFile.dataDict.getVals("solverSetup")
        self.solverSetups = []
        for ssName in solverSetupNames:
            self.solverSetups.append(AcdOptiSolverSetup(ssName, self))
        
        #Load the runner
        runnerType  = self.__paramFile.dataDict["runnerType"]
        self.runner = AcdOptiRunner.getRunner(runnerType, self)

    
    def refreshStatus_running(self):
        """
        Refresh async statuses "remote::*" and "local::*"
        by calling the runner
        """
        print "AcdOptiRunConfig::refreshStatus_remote()"
        if not self.status.beginswith("remote::") or not self.status.beginswith("local::"):
            raise AcdOptiException_runConfig_updateStateError("Not an async status, current status='" + self.status + "'")
        
        status = self.runner.queryStatus()
        
        if not status in self.statuses:
            raise AcdOptiException_runConfig_updateStateError("Got an invalid status, current status='" + self.status + "'")
        
        self.status = status
        
        for solver in self.solverSetups:
            solver.refreshLockdown()
        
    def stage(self):
        """
        Stages all the files needed for running the job
        """
        if self.status != "initialized":
            raise AcdOptiException_runConfig_stageError("Not in status 'initialized', status='" + self.status + "'")
        if self.status == "staged":
            return
        
        #Find the correct name to use for the staging and create the folder
        meshInstance = self.meshInstance
        geomInstance = meshInstance.geometryInstance
        project = geomInstance.template.project
        meshTemplate = meshInstance.meshTemplate
        solverString = ""
        for solver in self.solverSetups:
            solverString += solver.name + "::+::"
        solverString = solverString[:-5]
        self.stageName = "AcdOpti-stage::" + project.projectName_name + "::"\
                 + geomInstance.instName + "::+::" + meshTemplate.instName + "::"\
                 + meshInstance.instName + "::"\
                 + self.instName + "::+::" + self.runner.type + "::+::" + solverString + "::"\
                 +  datetime.now().isoformat()
        self.stageFolder = os.path.join(self.folder,"stage",self.stageName)
        os.mkdir(self.stageFolder)
        
        #Get the mesh file, generate if necessary
        if not self.meshInstance.lockdown:
            self.meshInstance.generateMesh()
        shutil.copy(os.path.join(self.meshInstance.folder, "mesh.ncdf"),\
                    self.stageFolder)
        
        #Prepare SolverSetups
        for solv in self.solverSetups:
            solv.stage()
        
        #Prepare runner
        self.runner.stage()
        
        #Zip the folder to make it ready for upload       
        shutil.make_archive(os.path.join(self.folder, "stage", self.stageName), "gztar",\
                            root_dir=os.path.join(self.folder, "stage"), base_dir=self.stageFolder)
        
        #Set status flag
        self.status = "staged"
        for solver in self.solverSetups:
            solver.refreshLockdown()
    
    def clearLockdown(self):
        """
        Clears the staged data and any solutions/analysis
        results that might exist, bringing status back to 'initialized'"
        """
        print "AcdOptiRunConfig::clearLockdown()"
        if self.status == "initialized":
            return
        
        #Clear staged data folder and tarball
        for d in os.listdir(self.stageFolder):
            dAbs = os.path.abspath(os.path.join(self.stageFolder,d))
            os.remove(dAbs)
        os.rmdir(self.stageFolder)
        os.remove(os.path.join(self.folder, "stage" ,self.stageName)+".tar.gz")
        
        #Clear finished data
        # TODO:
        
        self.stageName = None
        self.stageFolder = None
        self.status = "initialized"
        self.write()
        for solver in self.solverSetups:
            solver.refreshLockdown()
    
    def write(self):
        """
        Updates the __paramFile and writes it to disk.
        """
        print "AcdOptiRunConfig::write()"
        self.__paramFile.dataDict.setValSingle("status",self.status)
        
        if self.stageName:
            self.__paramFile.dataDict.setValSingle("stageName", self.stageName)
            self.__paramFile.dataDict.setValSingle("stageFolder", self.stageFolder)
        else:
            self.__paramFile.dataDict.setValSingle("stageName", "")
            self.__paramFile.dataDict.setValSingle("stageFolder", "")
        
        #Solver setups
        self.__paramFile.dataDict.delItem("solverSetup")
        for ss in self.solverSetups:
            self.__paramFile.dataDict.pushBack("solverSetup", ss.name)
        
        #Runner
        self.__paramFile.dataDict.setValSingle("runnerType", self.runner.type)
        
        self.__paramFile.write()
    
    def __del__(self):
        self.write()
    
    @staticmethod
    def createNew(folder, runnerType, solverTypes=None):
        """
        Create a new RunConfig, if wanted with ready-made
        SolverSetups and Runners created and attached.
        
        Input:
        - Folder      : In which folder to store the setup files etc.
        - runnerType  : String with the runner type wanted (example: Hopper)
        - solverTypes : String or list of strings with the types of SolverSetups wanted
                        (as accepted by AcdOptiSolverSetup.createNew()).
                        If None, don't attach any solvers
        """
        print "AcdOptiRunConfig::createNew(), folder=" + folder
        
        #Construct the instance name from folder
        instname = folder
        if instname[-1] == "/":
            instname = instname[0:-1]
        instname = os.path.split(instname)[1]
        if os.path.isdir(folder):
            raise AcdOptiException_runConfig_createFail ("Folder \"" + folder + "\" already exists")
        os.mkdir(folder)

        #Create the SolverSetups:
        solverSetups = []
        if solverTypes == None:
            pass #To simplify the "else" at the end...
        elif type(solverTypes) == str:
            solverSetups.append(AcdOptiSolverSetup.createNew(solverTypes, folder))
        elif type(solverTypes) == list:
            for st in solverTypes:
                solverSetups.append(AcdOptiSolverSetup.createNew(st, folder))
        else:
            raise AcdOptiException_runConfig_createFail ("Expected solverTypes to be a string or list of strings, got " + str(solverTypes))

        #Create the runner
        AcdOptiRunner.createNew(runnerType, folder)

        #Create the paramFile
        paramFile = AcdOptiFileParser_simple(\
            os.path.join(folder, "paramFile.set"), 'w')
        paramFile.dataDict.pushBack("fileID", "runConfigParamFile")
        paramFile.dataDict.pushBack("instName", instname)
        if len(solverSetups):
            paramFile.dataDict.pushBack("status", "initialized")
        else:
            paramFile.dataDict.pushBack("status", "not_initialized")
        paramFile.dataDict.pushBack("stageName", "")
        paramFile.dataDict.pushBack("stageFolder", "")
        #Pushback all solverSetups under the same key
        for ssName in solverSetups:
            paramFile.dataDict.pushBack("solverSetup", ssName)
        #Runner type
        paramFile.dataDict.pushBack("runnerType", runnerType) 
        paramFile.write()
        
        #Create the staging folder
        os.mkdir(os.path.join(folder, "stage"))

