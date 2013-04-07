# -*- coding: utf8 -*-
#
# Copyright 2011 Kyrre Ness Sjøbæk
# This file is part of AcdOpti.
#
#    AcdOpti is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    AcdOpti is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with AcdOpti.  If not, see <http://www.gnu.org/licenses/>.


"""
The purpose of this module is to wrap acdtool in an stand-alone,
user-friendly matter - exposing acdtools major functions in a nice way
and returning "pre-processed" output.
"""

from AcdOptiSettings import AcdOptiSettings
from AcdOptiExceptions import AcdOptiException_settings_notFound

import os

import subprocess
## Ducktape subprocess.check_output for old Python (SLC 6 / python 2.6)
if "check_output" not in dir( subprocess ): # duck punch it in!
    for i in xrange(20):
        print "WARNING WARNING WARNING EXECUTING DUCK PUNCH INSERTION OF SUBPROCESS.CHECK_OUTPUT() WARNING WARNING WARNING"
        class CalledProcessError(Exception):
            """This exception is raised when a process run by check_call() or
            check_output() returns a non-zero exit status.
            The exit status will be stored in the returncode attribute;
            check_output() will also store the output in the output attribute.
            """
            def __init__(self, returncode, cmd, output=None):
                self.returncode = returncode
                self.cmd = cmd
                self.output = output
            def __str__(self):
                return "Command '%s' returned non-zero exit status %d" % (self.cmd, self.returncode)
    def f(*popenargs, **kwargs):
        if 'stdout' in kwargs:
            raise ValueError('stdout argument not allowed, it will be overridden.')
        process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
        output, unused_err = process.communicate()
        retcode = process.poll()
        if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
                cmd = popenargs[0]
            print unused_err
            raise CalledProcessError(retcode, cmd)
        return output
    subprocess.check_output = f

acdtoolpath = AcdOptiSettings().getSetting("acdtoolpath") #"/opt/acdtool/acdtool" 

acdtool_initDone = False
def initAcdTool():
    "Helper function, runs the neccessary initialization commands"
    if not acdtool_initDone:
        #subprocess.check_call("module load openmpi-x86_64", shell=True)
        pass #Not needed on pcbe15690
        

def convertGenNcdf(genFileName, ncdfFileName):
    """
    Converts a Genesis mesh (as provided by CUBIT)
    into a netCDF mesh (as used by ACE3P).
    
    Input:
    - Name of the genesis file
    - Name of the netCDF file
    
    Output:
    - The output text from acdtool
    - Number of bad elements (ISOTE)
    """
    initAcdTool()
    
    #cmdline = acdtoolpath + " meshconvert cubitq netcdf %s %s" % (genFileName, ncdfFileName)
    cmdline = acdtoolpath + " meshconvert %s %s" % (genFileName, ncdfFileName)
    
    print "AcdOptiAcdtoolWrapper.convertGenNcdf(): Running command \"%s\" - please wait for result..." % cmdline
    acdoutput = subprocess.check_output(cmdline, bufsize=-1, shell=True) #Warning: Insecure mechanism (shell=True)
    print acdoutput
    
    badelems = 0
    print "Grepp'ing output for ISOTEs..."
    for line in acdoutput.split("\n"):
        if line.startswith("Total Number of invalid second order tetrahedral elements (ISOTE) is:"):
            badelems = int(line.strip().split()[-1])
    print "Done. Found %u bad elements" % badelems
    
    return (acdoutput, badelems)

def meshCheck(meshFileName):
    """
    Runs acdtool mesh check on a .netcdf file,
    reads output for ISOTE problems.
    Returns True if everything is good, False if there was a problem,
    and prints output
    """
    
    initAcdTool()
    
    cmdline = acdtoolpath + " mesh check %s" % meshFileName
    print "AcdOptiAcdtoolWrapper.meshCheck(): Running command '%s' -- please wait for result..." % cmdline
    acdoutput = subprocess.check_output(cmdline, bufsize=-1, shell=True) #Warning: Insecure mechanism (shell=True)
    print acdoutput
    print "Done."
    
    badelems = 0
    print "Grepp'ing output..."
    for line in acdoutput.split("\n"):
        if line.startswith("Total Number of invalid second order tetrahedral elements (ISOTE) is:"):
            badelems = int(line.strip().split()[-1])
    print "Done. Found %u bad elements" % badelems
    
    if badelems > 0:
        return True
    else:
        return False

def rfPost(inputFileName, folder):
    """
    Runs acdtool postprocess rf <inputfilename>.
    Output is printed
    """
    
    initAcdTool()
    
    cmdline = acdtoolpath + " postprocess rf " + inputFileName
    print "AcdOptiToolWrapper.rfPost(): Running command '%s' -- please wait for result..." % cmdline
    cwd = os.getcwd()
    os.chdir(folder)
    try:
        acdoutput = subprocess.check_output(cmdline, bufsize=-1, shell=True) #Warning: Insecure mechanism (shell=True)
    finally:
        os.chdir(cwd)
    
    print acdoutput
    print "Done."

def eigentomode(jobname, folder):
    """
    Runs acdtool postprocess eigentomode <jobname>
    """
    
    initAcdTool()
    
    cmdline = acdtoolpath + " postprocess eigentomode " + jobname
    print "AcdOptiToolWrapper.rfPost(): Running command '%s' -- please wait for result..." % cmdline
    cwd = os.getcwd()
    os.chdir(folder)
    try:
        acdoutput = subprocess.check_output(cmdline, bufsize=-1, shell=True) #Warning: Insecure mechanism (shell=True)
    finally:
        os.chdir(cwd)
    
    print acdoutput
    print "Done."
