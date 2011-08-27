from AcdOptiFileParser import DataDict,\
                              AcdOptiFileParser_simple
from AcdOptiSettings   import AcdOptiSettings
from AcdOptiExceptions import AcdOptiException_optiRunner_createFail,\
                              AcdOptiException_optiRunner_loadFail,\
                              AcdOptiException_optiRunner_remoteProblem,\
                              AcdOptiException_optiRunner_stageError

import paramiko

import os, math

class AcdOptiRunner:
    """
    Baseclass for runners, which handle uploading the job to HPC etc.
    Dependent on being "owned" by an AcdOptiRunConfig.
    """
    folder    = None
    runConfig = None
    type      = None
    
    lockdown  = None  # Is the runner currently not writable? (not enforced)

    
    def __init__(self):
        raise NotImplementedError("Don't initialize the interface AcdOptiRunner")
    
    def stage(self):
        "Prepare all files etc. for running the job"
        raise NotImplementedError
    
    def isRemote(self):
        "Returns True if this runner is using a remote resource"
        raise NotImplementedError
    def upload(self):
        """
        If the job is remote, upload the staged data.
        Raises an AcdOptiException_optiRunner_remoteProblem
        if there is a problem, error message as argument.  
        """
        raise NotImplementedError
    def run(self):
        "Start a job with this configuration"
        raise NotImplementedError
    def remoteCleanup(self):
        "Delete files belonging to this job on remote server"
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
    def refreshLockdown(self):
        """
        Checks the status of the runConfig and uses that to determine the lockdown setting.
        """
        if self.runConfig.status == "not_initialized" or self.runConfig.status == "initialized":
            self.lockdown = False
        else:
            self.lockdown = True
    
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
    type = "Hopper"
    CPUsPerNode = 24
    hostname = "hopper.nersc.gov"
    commonExecs = {"Omega3P::2011May23":"~candel/.community/hopper2/omega3p-2011May23"}
    
    __paramFile = None    
    #PBSjobName = None
    
    
    def __init__(self,runConfig):
        
        self.runConfig = runConfig
        self.folder = self.runConfig.folder
        
        self.__paramFile = AcdOptiFileParser_simple(os.path.join(self.folder,"paramFile_acdOptiRunner_Hopper.set"), 'rw')
        if not self.__paramFile.dataDict["fileID"] == "AcdOptiRunner_Hopper":
            raise AcdOptiException_optiRunner_loadFail("Wrong fileID, got'"+self.__paramFile.dataDict["fileID"] + "'")
    
    def isRemote(self):
        return True
    def __connectSSH(self):
        """
        Method that setups a ssh connection, returning a paramiko.SSHClient object.
        Remember to close() it!
        """
        print "Connecting..."
        username = AcdOptiSettings().getSetting("hopperUser")
        client = paramiko.SSHClient()
        client.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
        client.connect(self.hostname, username=username)
        #client.load_system_host_keys()
        print "Connected."
        return client
    
    def upload(self):
        stageFile = self.runConfig.stageFile
        
        #Check for programming errors
        assert stageFile != None
        assert os.path.isfile(stageFile)
        
        #Setup the ssh connection
        username = AcdOptiSettings().getSetting("hopperUser")
        client = self.__connectSSH()

        #Look for the acdopti scratch directory        
        sftp = client.open_sftp()
        remoteDir = "/scratch/scratchdirs/" + username + "/"
        remoteScratch = remoteDir + "acdopti_scratch/"
        remoteDirList = sftp.listdir(remoteDir)
        if not "acdopti_scratch" in remoteDirList:
            print "Making directory..."
            print remoteDirList
            sftp.mkdir(remoteScratch)
        scratchDirList =  sftp.listdir(remoteScratch)
        
        #Put the file
        if os.path.split(stageFile)[1] in scratchDirList:
            print "File already on HPC?!?"
            client.close()
            return
        print "Uploading file..."
        remoteFile = remoteScratch + os.path.split(stageFile)[1]
        sftp.put(stageFile, remoteScratch + os.path.split(stageFile)[1])
        print "Uploading finished."
        
        #Unzip
        print "Unzipping..."
        print "COMMAND:", "tar xzvf " + remoteFile + " --directory " + remoteScratch
        (ssh_stdin, ssh_stdout, ssh_stderr) = client.exec_command("tar xzvf " + remoteFile + " --directory " + remoteScratch)
        print "STDOUT:", ssh_stdout.read()
        print "STDERR:", ssh_stderr.read()
        print "Unzipped."
        
        #Delete the remote tar.gz
        print "Deleting tar.gz..."
        dirList = sftp.listdir(remoteScratch)
        if os.path.split(self.runConfig.stageFile)[1] in dirList:
            sftp.remove(remoteFile)
            print "Deleted."
        else:
            print "Already gone."
        
        client.close()
    def remoteCleanup(self):
        #Make connection...
        username = AcdOptiSettings().getSetting("hopperUser")
        client = self.__connectSSH()
        sftp = client.open_sftp()
        
        remoteDir = "/scratch/scratchdirs/" + username + "/"
        remoteScratch = remoteDir + "acdopti_scratch/"
        remoteFile = remoteScratch + os.path.split(self.runConfig.stageFile)[1]

        #Delete the remote tar.gz
        print "Deleting tar.gz..."
        dirList = sftp.listdir(remoteScratch)
        if os.path.split(self.runConfig.stageFile)[1] in dirList:
            sftp.remove(remoteFile)
            print "Deleted."
        else:
            print "Already gone."
        
        #Delete the remote folder
        print "Deleting remote folder..."
        if self.runConfig.stageName in dirList:
            #Emptying the folder...
            inDirList = sftp.listdir(remoteScratch + "/" + self.runConfig.stageName)
            for file in inDirList:
                sftp.remove(remoteScratch + "/" + self.runConfig.stageName + "/" + file)
            sftp.rmdir(remoteScratch + self.runConfig.stageName)
            print "Deleted."
        else:
            print "Already gone."
        
    def run(self):
        #Make connection...
        username = AcdOptiSettings().getSetting("hopperUser")
        client = self.__connectSSH()
        remoteDir = "/scratch/scratchdirs/" + username + "/"
        remoteScratch = remoteDir + "acdopti_scratch/"
        
        #Submit job
        print "Submitting..."
        (ssh_stdin, ssh_stdout, ssh_stderr) = client.exec_command("qsub " + remoteScratch + self.runConfig.stageName + "/run.pbs")
        print "STDOUT:", ssh_stdout.read()
        print "STDERR:", ssh_stderr.read()
        print "Submitted."
    

    def stage(self):
        self.__makePBS()
    def __makePBS(self):
        """
        Creates the run.pbs file used by Hopper's batch system
        """
        
        #Calculate number of mpi nodes needed, and build the commands
        jobs = self.__paramFile.dataDict["jobs"]
        commands = []
        numNodes = 0
        for job in jobs:
            nodesThis = int(math.ceil(int(job["tasks"])/float(self.CPUsPerNode)))
            if nodesThis > numNodes:
                numNodes = nodesThis
            def makeOption(optionName, key):
                get = job.getVals[key]
                if len(get) == 1:
                    return "-" + optionName + " " + get[0]
                elif len(get) > 0:
                    raise KeyError("Got more than one hit on key='" + key + "'")
                else:
                    return ""
            command = "aprun -n" + job["tasks"] + " " +\
                        makeOption("-N", "tasksNode") + " " +\
                        makeOption("-S", "tasksNuma")
                        #TODO: More keys in job...
            command.append(command)  
        
        if len(commands) == 0:
            raise AcdOptiException_optiRunner_stageError("No commands built")
        
        if not numNodes > 0:
            raise AcdOptiException_optiRunner_stageError("Got numNodes="+str(numNodes))
        
        #Write PBS file header
        runpbs = open(os.path.join(self.runConfig.stageFolder, "run.pbs"), 'w')
        runpbs.write("#!/bin/bash\n")
        
        torqueMeta = self.__paramFile.dataDict["TorqueMeta"]
        runpbs.write("#PBS -q " + torqueMeta["queue"])
        runpbs.write("#PBS -l mppwidth=" + str(numNodes*self.CPUsPerNode) + "\n")
        runpbs.write("#PBS -l walltime=" + torqueMeta["walltime"] + "\n")
        runpbs.write("#PBS -N " + self.runConfig.stageName + "\n")
        runpbs.write("#PBS -A " + torqueMeta["repo"] + "\n")
        if DataDict.boolconv(torqueMeta["importVars"]):
            runpbs.write("#PBS -V\n")
        
        runpbs.write("\n\n")
        #Write PBS script
        runpbs.write("## Commands:\n")
        for command in commands:
            runpbs.write(command + "\n")
        
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

        #Set default torque meta stuff
        torqueMeta = paramFile.dataDict.pushBack("TorqueMeta", DataDict())
        torqueMeta.pushBack("queue", "regular")
        torqueMeta.pushBack("walltime", "00:30:00")
        torqueMeta.pushBack("repo", "m349")
        torqueMeta.pushBack("importVars", "True")

        #Create a datastructure for storing aprun jobs
        paramFile.dataDict.pushBack("jobs", DataDict())
        # Each aprun job has the following fields:
        #  - tasks:       Number of MPI tasks, -n.               Essential!
        #  - tasksNode:   Number of MPI tasks pr. node, -N.      Optional.
        #  - tasksNuma:   Number of MPI tasks pr. NUMA node, -S. Optional.
        #  - commandID:   Executable ID (corresponding to the self.commonExecs flags
        #  - commandArgs: Arguments to pass to the executable (such as name of input file)
        
        paramFile.write()
        
        