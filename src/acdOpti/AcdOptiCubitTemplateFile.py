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

import exceptions
from AcdOptiExceptions  import *
import os
import atexit
import re
import string
from datetime import datetime

#Initialize
print "Module AcdOptiCubitTemplateFile.py is loading CUBIT..."
#if not os.path.lexists("/tmp/AcdOpti"):
#    os.mkdir("/tmp/AcdOpti")
#elif not os.path.isdir("/tmp/AcdOpti"):
#    raise AcdOptiException_cubitTemplateFile_initError("/tmp/AcdOpti already exists but is not a folder")
#CUBIT_basepath = "/tmp/AcdOpti"
#CUBIT_journalPath = os.path.join(CUBIT_basepath, "debugJournal.jou")

#Make sure that "." is the decimal separator
os.environ['LC_NUMERIC'] = 'en_US.utf8'

import cubit
cubit.init([""])

def cleanupCubit():
    files = os.listdir(os.getcwd())
    for f in files:
        if re.match("cubit[0-9]+\.jou", f):
            print "Deleting \"" + f + "\""
            os.remove(f)
atexit.register(cleanupCubit)

#if not os.path.isfile(CUBIT_journalPath):
#    f = open(CUBIT_journalPath,'w')
#    f.write("")
#    f.close()
#cubit.init(["-journalfile " + CUBIT_journalPath,])
#cubit.print_cmd_options()

class AcdOptiCubitTemplateFile():
    """
    Class managing a cubit template file, including
    - Parsing the template file syntax
    - Creating normal cubit .jou scripts using template and parameters
    
    Cubit template syntax is the same as normal .jou's,
    except that all occurences of "${TAG}" is replaced
    with the value of TAG. TAG's cannot contain spaces
    or special characters.
    """
    
    fname = None
    ifile = None
    
    template = None

    tags = None

    def __init__(self, fname):
        """
        Loads an already existing file
        (IOError if it doesn't exist)
        """    
        self.fname = fname
        self.reload()
        
    def reload(self):
        """
        Re-reads the file from disk
        """
        self.ifile = open(self.fname, 'r')
        self.template = string.Template(self.ifile.read())
        self.ifile.close()
    
    def update(self,newData):
        """
        Updates the file on disk and self
        with newData
        """
        self.ifile = open(self.fname, 'w')
        self.ifile.write(newData)
        self.ifile.close()
        self.reload()

    def subsString(self,pattern):
        """
        Tries to substitute all occurrences of the ${TAG}'s using
        the contents of the hashmap "pattern".
        
        Returns the constructed journal as a string,
        and a list of not-found keywords in the input file. 
        
        If the template file contains a single $, a ValueError is raised.
        
        Extra keys in pattern not found in the template are ignored. 
        """
        notFound = []
        while True:
            try:
                return (self.template.substitute(pattern), notFound)
            except KeyError as e:
                k = e.args[0]
                notFound.append(k)
                pattern[k] = "${" + k + "}"
                
    def generateJou(self, pattern, preCommands=None, postCommands=None):
        """
        Creates a cubit journal.
        
        Accepts lists of commands (strings, no tag replacement done)
        to be run before and after the script itself.
        
        Returns: (script, notFound) where
        - script   : Finished script as a list of single-line strings
        - notfound : list of keys in pattern not found in the template file.
        """
        #Build the list of commands
        (script,notFound) = self.subsString(pattern)
        scriptLines = script.splitlines()
        runScript = []
        if preCommands:
            runScript += preCommands
        runScript += scriptLines
        if postCommands:
            runScript += postCommands
        
        return (runScript, notFound)
    
    def writeJouFile(self,pattern,ofname, preCommands=None, postCommands=None):
        """
        Writes a normal journal to the file ofname.
        Raises AcdOptiException_cubitTemplateFile_fileAlreadyExists
        if the file already exists.
        
        Accepts lists of commands (strings, no tag replacement done)
        to be run before and after the script itself.
        
        Returns:
        - notfound : list of keys in pattern not found in the template file.
        """
        (runScript, notFound) = self.generateJou(pattern, preCommands, postCommands)
        
        if os.path.lexists(ofname):
            raise AcdOptiException_cubitTemplateFile_fileAlreadyExists\
                ("File " + ofname + " already exists")
        
        ofile = open(ofname, 'w')
        for line in runScript:
            ofile.write(line + "\n")
        ofile.close()

    def runCubit(self, pattern, preCommands=None, postCommands=None):
        """
        Creates a cubit journal and runs it in CUBIT.
        
        If a CUBIT error occurs, a AcdOptiException_cubitTemplateFile_CUBITerror
        is raised, with the full runScript array, index, and offending line as an argument.
        """
        #Generate the pattern
        (runScript, notFound) = self.generateJou(pattern, preCommands, postCommands)

        #Run the script
        errCount = cubit.get_error_count()
        for (line, i) in zip(runScript, xrange(len(runScript))):
            cubit.cmd(line)
            #Detect errors
            if cubit.get_error_count() > errCount:
                raise AcdOptiException_cubitTemplateFile_CUBITerror(runScript,i,line)
        return notFound
    
    @classmethod
    def createEmpty(cls,fname):
        """
        Creates an empty file,
        and returns a AcdOptiCubitTemplateFile
        with this file attached.
        """
        ofile = open(fname, 'w')
        ofile.write("# Cubit script template created by ACD optimizer\n")
        ofile.write("# Syntax: Write ${TAG} for fields that should be replaced before executing.\n")
        ofile.write("# To get a single dollar sign in the output, write a double dollar sign \"$$\" in this file.\n")
        ofile.write("# If ran within AcdOpti, \"reset\" command issued before start of script,\n")
        ofile.write("# and \"save as geom.cub overwrite\" issued at the end of a geometry generation script.\n")
        ofile.write("# For a meshing script, \"reset\" then \"open 'geom.cub'\" is issued at the beginning, and\n")
        ofile.write("# \"export genesis 'mesh.gen' block all overwrite\" is issued at the end.\n")
        ofile.write("# \n")
        ofile.write("# Template created at " + str(datetime.now().ctime()) + "\n")
        ofile.write("# \n")
        ofile.close()
        
        return(cls(fname))