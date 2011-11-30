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

from AcdOptiSolverManager import AcdOptiSolverManager

from acdOpti.AcdOptiExceptions import AcdOptiException_solverSetup_loadFail,\
                                      AcdOptiException_solverSetup_createFail,\
                                      AcdOptiException_solverSetup_createFail_nameTaken

from AcdOptiFileParser import DataDict,\
                              AcdOptiFileParser_simple,\
                              AcdOptiFileParser_Lua,\
                              AcdOptiFileParser_KVC

import os
solverSetupResourcesPath = os.path.join(os.path.split(__file__)[0],"resources","solverSetup")


class AcdOptiSolverSetup(AcdOptiSolverManager):
    """
    Wrapper for AcdOptiSolverManager for use by RunConfig.
    
    Generates a solver setup from the specified type.
    If the solution name exists, it will be loaded, 
    else it will be created from default values.
    
    This class is dependent on being owned  by a AcdOptiRunConfig,
    as it does some initialization for it, for example creating the "stage" folder.
    """

    #Object fields
    runConfig         = None  # The main runConfig object owning this (and perhaps more) solverSetups
         
    def __init__(self, name, runConfig):
        AcdOptiSolverManager.__init__(self, name, runConfig.folder)
        print "AcdOptiSolverSetup::__init__(), name='" + name + "', folder='" + runConfig.folder + "'"
        self.runConfig = runConfig 
        
        if not os.path.isdir(os.path.join(self.folder, "stage")):
            raise AcdOptiException_solverSetup_loadFail("Subfolder 'stage' is missing")
        
        self.refreshLockdown()

    
    def refreshLockdown(self):
        """
        Checks the status of the runConfig and uses that to determine the lockdown setting.
        """
        if self.runConfig.status == "not_initialized" or self.runConfig.status == "initialized":
            self.lockdown = False
        else:
            self.lockdown = True
        
    def stage(self):
        """
        Saves to disk and generates a setupFile,
        which is moved to the "stage" subfolder.
        """
        print "AcdOptiSolverSetup::stage()"
        # TODO: More Sanity check on this objects status?
        
        assert os.path.isdir(self.runConfig.stageFolder)
        
        self.write()
        self.generateSetup()
        os.rename(self.fileName, os.path.join(self.runConfig.stageFolder, self.name))
    
    
    @staticmethod
    def createNew_clone(folder, cloneFrom, newRunConfig):
        """
        Creates a new solverManager in a not previously existing folder,
        which has identical settings as an already existing solverSetup.
        The newly created solverManager is then returned wrapped in a solverSetup.
        """
        
        AcdOptiSolverManager.createNew_clone(folder, cloneFrom)
        return AcdOptiSolverSetup(cloneFrom.name, newRunConfig)