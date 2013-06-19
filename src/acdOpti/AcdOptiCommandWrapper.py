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
This module wraps starting and stopping of ParaView
with common options.
"""

import os, subprocess

## For old Python (SLC 6 / python 2.6)
if "check_output" not in dir( subprocess ):
    useAlternateCheckOutput = True;
def alternateCheckOutput(cmdline):
    "Call a given commandline, return the output data. Used for compatability if subprocess.check_output() doesn't exist"
    import tempfile
    (tmpf, tmpfn) = tempfile.mkstemp()
    print "Created temp file '" + tmpfn + "'"
    subprocess.call(cmdline, shell=True, stdout=tmpf)
    os.close(tmpf)
    tmpf = open(tmpfn, 'r')
    ret = tmpf.read()
    tmpf.close()
    os.remove(tmpfn)
    return ret

def runProgramInFolder(command, folder):
    "Runs a given command, starting in a given folder"
    
    print "Running '%s' in folder '%s" % (command, folder) 
    cwd = os.getcwd()
    os.chdir(folder)
    try:
        if useAlternateCheckOutput:
            output = alternateCheckOutput(command)
        else:
            #Warning: Insecure mechanism (shell=True)
            output = subprocess.check_output(command, bufsize=-1, shell=True)
    finally:
        os.chdir(cwd)
    
    print output
    print "Done."
