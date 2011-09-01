from AcdOptiFileParser import DataDict,\
                              AcdOptiFileParser_simple
from AcdOptiSettings   import AcdOptiSettings
from AcdOptiExceptions import AcdOptiException_optiRunner_createFail,\
                              AcdOptiException_optiRunner_loadFail,\
                              AcdOptiException_optiRunner_remoteProblem,\
                              AcdOptiException_optiRunner_stageError,\
                              AcdOptiException_optiRunner_runError

import paramiko
import os, math, re, tarfile

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
        """
        If the job is remote, download the data.
        Returns the path to the folder with the finished data.
        """
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
    
    def cloneInto(self,cloneFrom):
        """
        Empty this runner and copy the data from cloneFrom.
        """
        raise NotImplementedError
    
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
    #commonExecs = {"Omega3P::2011May23":"~candel/.community/hopper2/omega3p-2011May23"}
    
    __paramFile = None    
    #PBSjobName = None
    remoteJobID = None
    
    def __init__(self,runConfig):
        
        self.runConfig = runConfig
        self.folder = self.runConfig.folder
        
        self.__paramFile = AcdOptiFileParser_simple(os.path.join(self.folder,"paramFile_acdOptiRunner_Hopper.set"), 'rw')
        if not self.__paramFile.dataDict["fileID"] == "AcdOptiRunner_Hopper":
            raise AcdOptiException_optiRunner_loadFail("Wrong fileID, got'"+self.__paramFile.dataDict["fileID"] + "'")
        self.remoteJobID = self.__paramFile.dataDict["remoteJobID"]
        if self.remoteJobID == "":
            self.remoteJobID = None
        if self.remoteJobID != None and not (self.runConfig.status == "remote::queued" or self.runConfig.status != "remote::running"):
            raise AcdOptiException_optiRunner_loadFail("Found remoteJobID, but status='" + self.runConfig.status + "'")
        elif self.remoteJobID == None and (self.runConfig.status == "remote::queued" or self.runConfig.status == "remote::running"):
            raise AcdOptiException_optiRunner_loadFail("Did not find remoteJobID, but status='" + self.runConfig.status + "'")
         
    
    def getTorqueMeta(self):
        "Returns a pointer to the TorqueMeta data structure"
        return self.__paramFile.dataDict["TorqueMeta"]
    def getJobs(self):
        "Return a pointer to the jobs data structure"
        return self.__paramFile.dataDict["jobs"]
    
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
    def __SSHkillDir(self, dir, sftp):
        """
        Recursively delete directory dir and its contents using a sftp connection
        """
        #Emptying the folder...
        iDir = ""
        if dir[-1] == "/":
            iDir = dir[:-1]
        else:
            iDir = dir
        fileList = sftp.listdir(iDir)
        for file in fileList:
            try:
                sftp.remove(iDir + "/" + file)
            except IOError:
                #Directory
                self.__SSHkillDir(iDir + "/" + file, sftp)
        sftp.rmdir(iDir)
    
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
        print "COMMAND:", "cd " + remoteScratch +"; tar xzvf " + remoteFile # + " --directory " + remoteScratch
        (ssh_stdin, ssh_stdout, ssh_stderr) = client.exec_command("cd " + remoteScratch +"; tar xzvf " + remoteFile) #+ " --directory " + remoteScratch)
        (ssh_stdout_str, ssh_stderr_str) = (ssh_stdout.read(), ssh_stderr.read()) 
        print "STDOUT:", ssh_stdout_str
        print "STDERR:", ssh_stderr_str
        print "Unzipped."
        
        if len(ssh_stderr_str):
            client.close()
            raise AcdOptiException_optiRunner_remoteProblem("Problem while unzipping, see output")
        
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
        remoteFinishedFile = remoteScratch + self.runConfig.stageName + "--finished.tar.gz"

        #Delete the remote tar.gz's
        print "Deleting remote stage tar.gz..."
        dirList = sftp.listdir(remoteScratch)
        if os.path.split(self.runConfig.stageFile)[1] in dirList:
            sftp.remove(remoteFile)
            print "Deleted."
        else:
            print "Already gone."
        print "Deleting remote finished tar.gz..."
        if os.path.split(remoteFinishedFile)[1] in dirList:
            sftp.remove(remoteFinishedFile)
            print "Deleted."
        else:
            print "Already gone."
        
        #Delete the remote folder
        print "Deleting remote folder..."
        if self.runConfig.stageName in dirList:
            self.__SSHkillDir(remoteScratch + "/" + self.runConfig.stageName, sftp)
        else:
            print "Already gone."
        
        client.close()
        
    def run(self):
        #Make connection...
        username = AcdOptiSettings().getSetting("hopperUser")
        client = self.__connectSSH()
        remoteDir = "/scratch/scratchdirs/" + username + "/"
        remoteScratch = remoteDir + "acdopti_scratch/"
        
        #Submit job
        print "Submitting..."
        (ssh_stdin, ssh_stdout, ssh_stderr) = client.exec_command("cd " + remoteScratch + self.runConfig.stageName + "; qsub " + remoteScratch + self.runConfig.stageName + "/run.pbs")
        (ssh_stdout_str, ssh_stderr_str) = (ssh_stdout.read(), ssh_stderr.read()) 
        print "STDOUT:", ssh_stdout_str
        print "STDERR:", ssh_stderr_str
        print "Submitted."
    
        client.close()
        
        if len(ssh_stderr_str):
            raise AcdOptiException_optiRunner_remoteProblem("Problem during submission, see output")
        
        #Check if the stdout matches XXXXX.YYY, where XXXXX is a number, and YYY is letters.
        # This is then the job ID.
        if re.match("[0-9]+\.[a-zA-Z]+$", ssh_stdout_str):
            self.remoteJobID = ssh_stdout_str.strip()
            self.__paramFile.dataDict.setValSingle("remoteJobID", self.remoteJobID)
            print "Submission successful, JobID='" + self.remoteJobID + "'"
        else:
            raise AcdOptiException_optiRunner_runError("Problem with job submission, see standard output")
        self.write()
        
    def cancelRun(self):
        assert self.remoteJobID != "None" 
        #Make connection...
        client =  self.__connectSSH()
        
        #Cancel the current job
        print "Issuing cancel command..."
        (ssh_stdin, ssh_stdout, ssh_stderr) = client.exec_command("qdel " + self.remoteJobID)
        (ssh_stdout_str, ssh_stderr_str) = (ssh_stdout.read(), ssh_stderr.read()) 
        print "STDOUT:", ssh_stdout_str
        print "STDERR:", ssh_stderr_str
        print "Cancel command issued."
        
        client.close()
        
        if len(ssh_stderr_str):
            if "Unknown Job Id " + self.remoteJobID in ssh_stderr_str:
                return
            raise AcdOptiException_optiRunner_remoteProblem("Problem during cancel, see output")

    def queryStatus(self):
        assert self.runConfig.status == "remote::queued" or self.runConfig.status == "remote::running", "status = '" + self.runConfig.status + "'"
        
        #Make connection
        client = self.__connectSSH()
        
        print "Getting status..."
        (ssh_stdin, ssh_stdout, ssh_stderr) = client.exec_command("qstat " + self.remoteJobID)
        (ssh_stdout_str, ssh_stderr_str) = (ssh_stdout.read(), ssh_stderr.read()) 
        print "STDOUT:", ssh_stdout_str
        print "STDERR:", ssh_stderr_str
        print "Got status."
        
        client.close()
        
        #Parse the status output:
        if len(ssh_stderr_str):
            if "Unknown Job Id " + self.remoteJobID in ssh_stderr_str:
                return "remote::finished"
            raise AcdOptiException_optiRunner_remoteProblem("Problem while getting status, see output")
                
        statusline = ""
        for line in ssh_stdout_str.splitlines():
            if line.startswith(self.remoteJobID):
                statusline = line
                break
        statusChar = statusline.split()[-2]
        print "statusLine='" + statusline + "', statusChar='" + statusChar + "'"
        if statusChar == "Q":
            return "remote::queued"
        elif statusChar == "R":
            return "remote::running"
        elif statusChar == "C":
            return "remote::finished"
        else:
            raise ValueError("Unknown status char '" + statusChar + "'")
        
        
    def getRemoteData(self):
        assert self.runConfig.status=="remote::finished" or self.runConfig.status=="remote::unclean"
        
        finishedLocalPath=os.path.join(self.folder, "finished")
        
        username = AcdOptiSettings().getSetting("hopperUser")
        remoteDir = "/scratch/scratchdirs/" + username + "/"
        remoteScratch = remoteDir + "acdopti_scratch/"
        #remoteJobDir = remoteScratch + self.runConfig.stageName + "/"
        remoteFile = self.runConfig.stageName + "--finished.tar.gz"

        #Make connection
        client = self.__connectSSH()
        sftp = client.open_sftp()
        
        #Tar the data
        print "Zipping..."
        command = "cd " + remoteScratch +"; tar czvf " + remoteFile + " --force-local " + self.runConfig.stageName
        print "COMMAND:", command
        (ssh_stdin, ssh_stdout, ssh_stderr) = client.exec_command(command)
        (ssh_stdout_str, ssh_stderr_str) = (ssh_stdout.read(), ssh_stderr.read())
        print "STDOUT:", ssh_stdout_str
        print "STDERR:", ssh_stderr_str
        print "Zipped."
        if len(ssh_stderr_str):
            client.close()
            raise AcdOptiException_optiRunner_remoteProblem("Problem during zipping, see output")
        
        #Download the tarball
        sftp.get(remoteScratch + remoteFile, os.path.join(finishedLocalPath, remoteFile))
        
        client.close()
        
        #Unzip the downloaded solution tar.gz
        archive = tarfile.open(os.path.join(finishedLocalPath, remoteFile), "r:gz")
        archive.extractall(path=finishedLocalPath)
        
        return os.path.join(finishedLocalPath, self.runConfig.stageName)
        
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
        for jobName, job in jobs:
            command = None
            if DataDict.boolconv(job["aprun"]):
                nodesThis = int(math.ceil(int(job["tasks"])/float(self.CPUsPerNode)))
                if nodesThis > numNodes:
                    numNodes = nodesThis
                def makeOption(optionName, key, optional):
                    get = job[key]
                    if get == "-1" and optional:
                        return "" 
                    return optionName + " " + get[0] + " "
                command = "aprun "  + makeOption("-n", "tasks", False)\
                                    + makeOption("-N", "tasksNode", True)\
                                    + makeOption("-S", "tasksNuma", True)\
                                    + job["command"] + " " + job["commandArgs"]
            else:
                command = job["command"]
            commands.append(command)
        
        if len(commands) == 0:
            raise AcdOptiException_optiRunner_stageError("No commands built")
        
        if not numNodes > 0:
            raise AcdOptiException_optiRunner_stageError("Got numNodes="+str(numNodes))
        
        #Write PBS file header
        runpbs = open(os.path.join(self.runConfig.stageFolder, "run.pbs"), 'w')
        runpbs.write("#!/bin/bash\n")
        
        torqueMeta = self.getTorqueMeta()
        runpbs.write("#PBS -q " + torqueMeta["queue"] + "\n")
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
    
    def write(self):
        self.__paramFile.write()
    
    def cloneInto(self,cloneFrom):
        """
        Empty this runner and copy the data from cloneFrom.
        """
        
        #Copy the torque stuff
        torqueOriginal = cloneFrom.getTorqueMeta()
        torqueThis = self.getTorqueMeta()
        torqueThis.clear()
        for (k,v) in torqueOriginal.copy():
            torqueThis.pushBack(k,v) 
        
        #Copy the jobs stuff
        jobsOriginal = cloneFrom.getJobs()
        jobsThis = self.getJobs()
        jobsThis.clear()
        for (k,v) in jobsOriginal.copy():
            jobsThis.pushBack(k,v)
        
        self.write()
        
    @staticmethod
    def createNew(folder, type):
        #Create the settings file
        paramFile = AcdOptiFileParser_simple(os.path.join(folder,"paramFile_acdOptiRunner_Hopper.set"),"w")
        paramFile.dataDict.pushBack("fileID", "AcdOptiRunner_Hopper")

        paramFile.dataDict.pushBack("remoteJobID", "")

        #Set default torque meta stuff
        torqueMeta = paramFile.dataDict.pushBack("TorqueMeta", DataDict())
        torqueMeta.pushBack("queue", "regular")
        torqueMeta.pushBack("walltime", "00:30:00")
        torqueMeta.pushBack("repo", "m349")
        torqueMeta.pushBack("importVars", "True")

        #Create a datastructure for storing aprun jobs
        jobs = paramFile.dataDict.pushBack("jobs", DataDict())
        # Each aprun job has the following fields:
        #  - aprun:       Boolean, true in the case of aprun jobs
        #  - command:     Command to run
        #  - commandArgs: Arguments to pass to the executable (such as name of input file)
        #  - tasks:       Number of MPI tasks, -n.               Essential!
        #  - tasksNode:   Number of MPI tasks pr. node, -N.      Optional.
        #  - tasksNuma:   Number of MPI tasks pr. NUMA node, -S. Optional.
        # If the aprun flag is False, then only command is used (but all keys should be present!)
        # Optional args should also be present. Set to "-1" to disable.
        
        #This command is always needed.
        cdpbs = jobs.pushBack("cdPBS", DataDict())
        cdpbs.pushBack("aprun", "False")
        cdpbs.pushBack("command", "cd $PBS_O_WORKDIR")
        cdpbs.pushBack("commandArgs", "")
        cdpbs.pushBack("tasks", "-1")
        cdpbs.pushBack("tasksNode", "-1")
        cdpbs.pushBack("tasksNuma", "-1")
        
        paramFile.write()
        
        