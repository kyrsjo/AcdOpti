"""
The purpose of this module is to wrap acdtool in an stand-alone,
user-friendly matter - exposing acdtools major functions in a nice way
and returning "pre-processed" output.
"""

from AcdOptiSettings import AcdOptiSettings

import subprocess

acdtoolpath = AcdOptiSettings().getSetting("acdtoolpath") #"/opt/acdtool/acdtool" 

def convertGenNcdf(genFileName, ncdfFileName):
    """
    Converts a Genesis mesh (as provided by CUBIT)
    into a netCDF mesh (as used by ACE3P).
    
    Input:
    - Name of the genesis file
    - Name of the netCDF file
    
    Output:
    - The output text from acdtool
    """
    cmdline = acdtoolpath + " meshconvert cubitq netcdf %s %s" % (genFileName, ncdfFileName)
    print "AcdOptiAcdtoolWrapper.convertGenNcdf(): Running command \"%s\" - please wait for result..." % cmdline
    acdoutput = subprocess.check_output(cmdline, bufsize=-1, shell=True) #Warning: Insecure mechanism (shell=True)

    return acdoutput

def meshCheck(meshFileName):
    """
    Runs acdtool mesh check on a .netcdf file,
    reads output for ISOTE problems.
    Returns True if everything is good, False if there was a problem,
    and prints output
    """
    
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
    
    