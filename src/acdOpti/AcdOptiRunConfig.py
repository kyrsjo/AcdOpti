from AcdOptiFileParser import AcdOptiFileParser_simple,\
                              DataDict
from AcdOptiExceptions import AcdOptiException_runConfig_createFail,\
                              AcdOptiException_runConfig_loadFail,\
                              AcdOptiException_runConfig_stageError,\
                              AcdOptiException_runConfig_updateStateError,\
                              AcdOptiException_optiRunner_stageError

from AcdOptiSolverSetup import AcdOptiSolverSetup
from AcdOptiRunner import AcdOptiRunner
from analysis.AnalysisInterface import AnalysisInterface

import os, shutil, tarfile
from datetime import datetime

class AcdOptiRunConfig:
    """
    Class representing a run configuration,
    holding solvers and job setup, setups and allows starting/stopping runs
    and querying their status. 
    """
    
    folder   = None
    instName = None
    #lockdown = None
    
    solverSetups = None #List of solverSetups
    runner       = None #The runner in use
    meshInstance = None #Pointer back to the "owning" meshInstance 
    
    __paramFile = None  #Settings file
    
    status = "not_initialized"
    
    stageName   = None #status > staged, name of folder or tar.gz file (without ending) with staged data (else None)
    stageFolder = None #Path to the staging directory (if status>staged, else None)
    stageFile   = None #Full path to the tar.gz file with the staged data (if status>staged, else None)
    
    finishedFolder = None #Full path to the folder with the finished data
    
    analysis = None #List of the analysis loaded
    
    statuses= ["not_initialized", # Before object is fully created
               "initialized",     # Has one or more runners and a meshInstance
               "staged",          # Object is staged, all files are in place
               "remote::uploaded",# Files uploaded to HPC, but has not yet appeared in queue system
               "remote::queued",  # Job is submitted to HPC, but has not started yet
               "remote::running", # Job is running
               "remote::unclean", # Job was submitted, but crashed or was canceled
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
        
        self.stageFile = self.__paramFile.dataDict.getValSingle("stageFile")
        if self.stageFile == "":
            self.stageFile = None
        
        self.finishedFolder = self.__paramFile.dataDict.getValSingle("finishedFolder")
        if self.finishedFolder == "":
            self.finishedFolder = None
            assert self.status != "finished"
        
        #Sanity check on folders for staged- and finished data:
        if not os.path.isdir(os.path.join(self.folder, "stage")):
            raise AcdOptiException_runConfig_loadFail("stage folder not found")
        if not os.path.isdir(os.path.join(self.folder, "finished")):
            raise AcdOptiException_runConfig_loadFail("finished folder not found")
        if not os.path.isdir(os.path.join(self.folder, "analysis")):
            raise AcdOptiException_runConfig_loadFail("analysis folder not found")
        
        #Load the solverSetups
        solverSetupNames = self.__paramFile.dataDict.getVals("solverSetup")
        self.solverSetups = []
        for ssName in solverSetupNames:
            self.solverSetups.append(AcdOptiSolverSetup(ssName, self))
        
        #Load the runner
        runnerType  = self.__paramFile.dataDict["runnerType"]
        self.runner = AcdOptiRunner.getRunner(runnerType, self)
        
        #Load any analysis specified by the paramFile
        anaDict = self.__paramFile.dataDict["analysis"]
        self.analysis = {}
        for (anaName, anaOptions) in anaDict:
            print anaName, anaOptions
            if anaName in self.analysis:
                raise KeyError("Analysis name '" + anaName + "' encountered twice")
            self.analysis[anaName] = AnalysisInterface.loadAnalysisByDict(anaOptions, os.path.join(self.folder, "analysis"))
            
    
        for solver in self.solverSetups:
            solver.refreshLockdown()
        self.runner.refreshLockdown()
    
    def refreshStatus(self):
        """
        Refresh async statuses "remote::*" and "local::*"
        by calling the runner
        """
        print "AcdOptiRunConfig::refreshStatus_remote()"
        if not (self.status.startswith("remote::") or self.status.startswith("local::")):
            raise AcdOptiException_runConfig_updateStateError("Not an async status, current status='" + self.status + "'")
        
        status = self.runner.queryStatus()
        
        if not status in self.statuses:
            raise AcdOptiException_runConfig_updateStateError("Got an invalid status, current status='" + self.status + "'")
        
        self.status = status
        
        for solver in self.solverSetups:
            solver.refreshLockdown()
        self.runner.refreshLockdown()
        
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
        self.stageName = "AcdOpti-stage--" + project.projectName_name + "-"\
                 + geomInstance.instName + "-" + meshTemplate.instName + "--"\
                 + meshInstance.instName + "--"\
                 + self.instName + "-" + self.runner.type + "-" + solverString + "--"\
                 +  datetime.now().isoformat()
        #self.stageName = "test"
        self.stageFolder = os.path.join(self.folder,"stage",self.stageName)
        os.mkdir(self.stageFolder)
        
        
        #Get the mesh file, generate if necessary
        if not self.meshInstance.lockdown:
            self.meshInstance.generateMesh()
        shutil.copy(os.path.join(self.meshInstance.folder, "mesh.ncdf"), self.stageFolder)
        shutil.copy(os.path.join(self.meshInstance.folder, "mesh.jou"), self.stageFolder)
        
        #Get the geometry journal file (for reference)
        shutil.copy(os.path.join(self.meshInstance.geometryInstance.folder, "geom.jou"), self.stageFolder)
        
        #Prepare SolverSetups
        for solv in self.solverSetups:
            solv.stage()
        
        #Prepare runner
        try:
            self.runner.stage()
        except AcdOptiException_optiRunner_stageError as e:
            #Something went wrong when staging the runner
            # cleanup and raise exception
            self.clearLockdown(forced=True)
            raise AcdOptiException_runConfig_stageError("Error when staging runner", e.args[0])
            
        
        #Zip the folder to make it ready for upload
        self.stageFile = os.path.join(self.folder, "stage", self.stageName) + ".tar.gz"
        stageFileObject = tarfile.open(self.stageFile, mode="w:gz")
        stageFileObject.add(self.stageFolder, arcname=self.stageName)
        stageFileObject.close()
        
        #Set status flag
        self.status = "staged"
        for solver in self.solverSetups:
            solver.refreshLockdown()
        self.runner.refreshLockdown()
    
        self.write()
    
    def upload(self):
        """
        Given that everything is staged, and we have a "remote" runner,
        upload the data to the HPC 
        """
        assert self.status=="staged"
        assert self.runner.isRemote()
        self.runner.upload()
        self.status = "remote::uploaded"
    
    def run(self):
        """
        Given that the runConfig etc. is ready to run, starts the run.
        """
        print "AcdOptiRunConfig::run()"
        if self.runner.isRemote():
            assert self.status == "remote::uploaded"
        self.runner.run()
        self.status = "remote::queued"
    def getRemote(self):
        """
        Given that there are remote data and we are not running,
        download this data to the local machine.
        """
        print "AcdOptiRunConfig::getRemote()"
        assert self.runner.isRemote()
        assert self.status == "remote::finished" or self.status == "remote::unclean"
        self.finishedFolder = self.runner.getRemoteData()
        self.remoteCleanup()
        self.status = "finished"
    
    def cancel(self):
        """
        Given that there is a run in progress or queued, cancel it.
        """
        print "AcdOptiRunConfig::cancel()"
        if self.runner.isRemote():
            assert self.status == "remote::running" or\
                   self.status == "remote::queued"
        self.runner.cancelRun()
        self.status = "remote::unclean"
        
    def remoteCleanup(self):
        print "AcdOptiRunConfig::remoteCleanup()"
        assert self.runner.isRemote()
        assert self.status=="remote::uploaded" or self.status=="remote::finished" or self.status=="remote::unclean"
        self.runner.remoteCleanup()
        self.status = "staged"
        
    def clearLockdown(self,forced=False):
        """
        Clears the staged data and any solutions/analysis
        results that might exist, bringing status back to 'initialized'"
        
        Set forced=True if the clearLockdown() happens because of a crash in stage,
        and is intended to bring the runConfig back to a defined state
        """
        print "AcdOptiRunConfig::clearLockdown()"
        if self.status == "initialized" and not forced:
            return
        
        #Clear staged data folder and tarball
        if self.stageFolder and os.path.isdir(self.stageFolder):
            for d in os.listdir(self.stageFolder):
                dAbs = os.path.abspath(os.path.join(self.stageFolder,d))
                os.remove(dAbs)
            os.rmdir(self.stageFolder)
        if self.stageFile and os.path.isfile(self.stageFile):
            os.remove(self.stageFile)
        
        self.stageName   = None
        self.stageFolder = None
        self.stageFile   = None
        
        #Clear finished data
        shutil.rmtree(os.path.join(self.folder, "finished"))
        os.mkdir(os.path.join(self.folder, "finished"))
        
        self.finishedFolder = None
        
        self.status = "initialized"
        for solver in self.solverSetups:
            solver.refreshLockdown()
        self.runner.refreshLockdown()

        self.write()
    
    def write(self):
        """
        Updates the __paramFile and writes it to disk.
        """
        print "AcdOptiRunConfig::write()"
        self.__paramFile.dataDict.setValSingle("status",self.status)
        
        #TODO: Only store relative paths!
        if self.stageName:
            self.__paramFile.dataDict.setValSingle("stageName", self.stageName)
            self.__paramFile.dataDict.setValSingle("stageFolder", self.stageFolder)
            self.__paramFile.dataDict.setValSingle("stageFile", self.stageFile)
            
        else:
            self.__paramFile.dataDict.setValSingle("stageName", "")
            self.__paramFile.dataDict.setValSingle("stageFolder", "")
            self.__paramFile.dataDict.setValSingle("stageFile", "")

        if self.finishedFolder != None:
            assert self.status == "finished"
            self.__paramFile.dataDict.setValSingle("finishedFolder", self.finishedFolder)
        else:
            assert self.status != "finished"
            self.__paramFile.dataDict.setValSingle("finishedFolder", "")
        
        #Solver setups
        self.__paramFile.dataDict.delItem("solverSetup")
        for ss in self.solverSetups:
            self.__paramFile.dataDict.pushBack("solverSetup", ss.name)
        
        #Runner
        self.__paramFile.dataDict.setValSingle("runnerType", self.runner.type)
        
        #Analysis
        anaDict = self.__paramFile.dataDict["analysis"]
        anaDict.clear()
        for (key, val) in self.analysis.iteritems():
            anaDict.pushBack(key,val.generateRunConfigDict())
        
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
        paramFile.dataDict.pushBack("stageFile", "")
        paramFile.dataDict.pushBack("finishedFolder", "")
        #Pushback all solverSetups under the same key
        for ssName in solverSetups:
            paramFile.dataDict.pushBack("solverSetup", ssName)
        #Runner type
        paramFile.dataDict.pushBack("runnerType", runnerType) 
        
        #Analysis dictionary
        paramFile.dataDict.pushBack("analysis", DataDict())
        
        paramFile.write()
        
        #Create the staging folder
        os.mkdir(os.path.join(folder, "stage"))

        #Create the finished folder
        os.mkdir(os.path.join(folder, "finished"))
        
        #Create the analysis folder
        os.mkdir(os.path.join(folder,"analysis"))
        