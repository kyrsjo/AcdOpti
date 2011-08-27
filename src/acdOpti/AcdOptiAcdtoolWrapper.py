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