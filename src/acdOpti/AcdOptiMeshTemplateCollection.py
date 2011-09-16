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


import AcdOptiFileParser
import AcdOptiMeshTemplate, AcdOptiMeshInstance
import AcdOptiExceptions, exceptions
import os

class AcdOptiMeshTemplateCollection:
    """
    Collection class doing little else
    than organizing the contents of the
    meshTemplates folder.
    """
    def __init__(self,folder):
        """
        Initialize (load) a MeshTemplateCollection
        stored in some folder
        """
        self.folder = folder

        #Load the param file
        try:
            self.paramFile = AcdOptiFileParser.AcdOptiFileParser_simple(\
                os.path.join(folder, "paramFile.set"), 'rw')
        except IOError:
            raise AcdOptiExceptions.\
                AcdOptiException_meshTemplateCollection_loadFail(\
                "File paramFile.set not found")

        if self.paramFile.dataDict.getValSingle("fileID")\
                != "meshTemplateCollectionParamFile":
            raise AcdOptiExceptions.\
                AcdOptiException_meshTemplateCollection_loadFail
        
        #Find subfolders and check if they are geometry instances
        self.meshTemplates = {}
        for d in os.listdir(folder):
            dAbs = os.path.abspath(os.path.join(folder,d))
            if not os.path.isdir(dAbs):
                #Skip files etc.
                continue
            try:
                self.meshTemplates[d] = \
                    AcdOptiMeshTemplate.AcdOptiMeshTemplate(dAbs)
            except AcdOptiExceptions.\
                    AcdOptiException_meshTemplate_loadFail:
                raise AcdOptiExceptions.\
                    AcdOptiException_meshTemplateCollection_loadFail(\
                    "Problem loading mesh template instance \"" + d + "\"")

    @staticmethod
    def createNew(folder):
        """
        Sets up the basic structure inside
        a given folder, which is created.
        """
        #Create the directory
        os.mkdir(folder)
        
        #File that holds the parameters and their default values
        paramFile = AcdOptiFileParser.AcdOptiFileParser_simple(\
            os.path.join(folder,"paramFile.set"), 'w')
        paramFile.dataDict.pushBack("fileID", "meshTemplateCollectionParamFile")
        paramFile.write()

    #Object variables
    paramFile = None
    meshTemplates = None
    folder = None