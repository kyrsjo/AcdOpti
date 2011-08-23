from AcdOptiFileParser import DataDict,\
                              AcdOptiFileParser_simple
from AcdOptiExceptions import AcdOptiException_optiRunner_createFail,\
                              AcdOptiException_optiRunner_loadFail

import os, math

class AcdOptiRunner:
    """
    Baseclass for runners, which handle uploading the job to HPC etc.
    Dependent on being "owned" by an AcdOptiRunConfig.
    """
    folder = None
    runConfig = None
    type = None
    
    def __init__(self):
        raise NotImplementedError("Don't initialize the interface AcdOptiRunner")
    
    def stage(self):
        "Prepare all files etc. for running the job"
        raise NotImplementedError
    
    def isRemote(self):
        "Returns True if this runner is using a remote resource"
        raise NotImplementedError
    def run(self):
        "Start a job with this configuration"
        raise NotImplementedError
    def cancelRun(self):
        "Stop a running job with this configuration"
        raise NotImplementedError
    def queryStatus(self):
        "Query the status of this job, returning one of AcdOptiRunConfig.statuses"
        raise NotImplementedError
    def getRemoteData(self):
        "If the job is remote, download the data"
        raise NotImplementedError
    
    @staticmethod
    def getRunner(type, runConfig):
        """"
        Get a runner instance of the specified type.
        Acts like a constructor constructing the correct type of runner
        """
        folder = runConfig.folder
        
        if not os.path.isdir(os.path.join(folder, "stage")):
            raise AcdOptiException_optiRunner_loadFail("Missing subfolder 'stage'")
        
        if type.split("::")[0] == "Hopper":
            return AcdOptiRunner_Hopper(runConfig)
        else:
            raise AcdOptiException_optiRunner_loadFail("Unknown type '" + type +"'")
    
    @staticmethod
    def createNew(type, folder):
        """
        Create a new runner instance of the specified type in folder.
        Allows sending options to the subclass createNew()s by the syntax
        Name::Options 
        """
        if type.split("::")[0] == "Hopper":
            AcdOptiRunner_Hopper.createNew(folder, type)
        else:
            raise AcdOptiException_optiRunner_createFail("Unkown type '" + type + "'")

class AcdOptiRunner_Hopper(AcdOptiRunner):
    
    __paramFile = None
    
    CPUsPerNode = 24
    
    def __init__(self,runConfig):
        self.type = "Hopper"
        
        self.runConfig = runConfig
        self.folder = self.runConfig.folder
        
        self.__paramFile = AcdOptiFileParser_simple(os.path.join(self.folder,"paramFile_acdOptiRunner_Hopper.set"), 'rw')
        if not self.__paramFile.dataDict["fileID"] == "AcdOptiRunner_Hopper":
            raise AcdOptiException_optiRunner_loadFail("Wrong fileID, got'"+self.__paramFile.dataDict["fileID"] + "'")
    def stage(self):
        self.__makePBS()
    
    def __makePBS(self):
        """
        Creates the run.pbs file used by Hopper's batch system
        """
        
        #Calculate the number of mpijobs to ask for
        jobs = self.__paramFile.dataDict.getVals("job")
        nodes = 0
        for job in jobs:
            nodesThis = math.ceil(int(job["tasks"])/float(self.CPUsPerNode))
            if nodesThis:
                nodes = nodesThis
        assert nodes > 0
            
        #Write the PBS file
        torqueMeta = self.__paramFile.dataDict["TorqueMeta"]
        runpbs = open(os.path.join(self.runConfig.stageFolder, "run.pbs"), 'w')
        runpbs.write("#!/bin/bash" + "\n")
        
        runpbs.write("#PBS -q " + torqueMeta["q"] + "\n")
        runpbs.write("#PBS -l mppwidth=" + str(nodes*self.CPUsPerNode) + "\n")
        runpbs.write("#PBS -l walltime=" + torqueMeta["walltime"] + "\n")
        runpbs.write("#PBS -N " + torqueMeta["N"] + "\n")
        runpbs.write("#PBS -j " + torqueMeta["j"] + "\n")
        runpbs.write("#PBS -A " + torqueMeta["A"] + "\n")
        runpbs.write("#PBS -V" + "\n")
        
        runpbs.write("\n\n")
        
        for job in jobs:
            runpbs.write("aprun -n " + job["tasks"] + "  " + job["executable"] + " " + "\n")
        
        runpbs.close()
        
        #Move it to stage folder
        #os.rename(os.path.join(self.folder, "run.pbs"), os.path.join(self.folder, "stage", "run.pbs"))
        
    def __del__(self):
        self.paramFile.write()
    
    @staticmethod
    def createNew(folder, type):
        #Create the settings file
        paramFile = AcdOptiFileParser_simple(os.path.join(folder,"paramFile_acdOptiRunner_Hopper.set"),"w")
        paramFile.dataDict.pushBack("fileID", "AcdOptiRunner_Hopper")
        TorqueMeta = paramFile.dataDict.pushBack("TorqueMeta", DataDict())
        TorqueMeta.pushBack("q", "debug") #pbsMeta.pushBack("q", "regular")
        TorqueMeta.pushBack("walltime", "01:00:00")
        TorqueMeta.pushBack("N", "AcdOpti_test")
        TorqueMeta.pushBack("j", "eo")
        TorqueMeta.pushBack("A", "m349")
        
        job1 = paramFile.dataDict.pushBack("job", DataDict())
        #Single-CPU Omega3P
        job1.pushBack("tasks","1")
        #job1.pushBack("tasksNode", "1")
        job1.pushBack("executable", "~candel/.community/hopper2/omega3p-2011May23")
        job1.pushBack("execInput","")
        paramFile.write()
        
        