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


import pygtk
pygtk.require('2.0')
import gtk

import os

from InfoFrameComponent import InfoFrameComponent

from acdOpti.AcdOptiExceptions import AcdOptiException_cubitTemplateFile_CUBITerror,\
                                      AcdOptiException_runConfig_createFail,\
                                      AcdOptiException_meshInstance_generateFail

from RunConfig import RunConfig

import acdOpti.AcdOptiCommandWrapper as AcdOptiCommandWrapper
from acdOpti.AcdOptiSettings import AcdOptiSettings


class MeshInstance(InfoFrameComponent):
    
    meshInstance = None    
    
    __topLabels       = None
    __labelCollection = None
    __entryCollection = None
    __checkCollection = None
    __tableWidget     = None
    __scrolledWindow  = None
    
    __meshTemplateNameLabel = None
    __meshBadIndicator = None
    
    __clearLockdownButton = None
    __cloneButton = None
    __runConfigButton = None
    __exportButton   = None
    __paraviewButton = None
    __generateButton = None
    
    
    def __init__(self,frameManager,meshInstance):
        print "MeshInstance::__init__()"
        InfoFrameComponent.__init__(self, frameManager)
        self.meshInstance = meshInstance
        
        #Create GUI
        self.__topLabels = []

        tlab = gtk.Label("Tag name")
        self.__topLabels.append(tlab)
        
        tlab = gtk.Label("Value")
        self.__topLabels.append(tlab)

        tlab = gtk.Label("Use default")
        self.__topLabels.append(tlab)

        

        self.__meshTemplateNameLabel = gtk.Label("Name of mesh template: \"" + self.meshInstance.meshTemplate.instName + "\"")
        
        self.__meshBadIndicator = gtk.Label("Mesh bad (ISOTEs): " + str(self.meshInstance.meshBad))        

        self.__clearLockdownButton = gtk.Button(label="Clear lockdown")
        self.__clearLockdownButton.connect("clicked", self.event_button_clearLockdown, None)
        
        self.__cloneButton = gtk.Button(label="Clone this mesh instance (deep copy)")
        self.__cloneButton.connect("clicked", self.event_button_clone, None)
        
        self.__runConfigButton = gtk.Button(label="Attach a runconfig...")
        self.__runConfigButton.connect("clicked", self.event_button_runConfig, None)
        
        self.__exportButton = gtk.Button(label="Export CUBIT journal to file...")
        self.__exportButton.connect("clicked", self.event_button_export, None)
        
        self.__paraviewButton = gtk.Button(label="Run ParaView...")
        self.__paraviewButton.connect("clicked", self.event_button_paraview)
        
        self.__generateButton = gtk.Button(label="Run CUBIT to generate mesh")
        self.__generateButton.connect("clicked", self.event_button_generate, None)


        self.updateTable()

        self.__scrolledWindow = gtk.ScrolledWindow()
        self.__scrolledWindow.set_policy(gtk.POLICY_NEVER,gtk.POLICY_AUTOMATIC)
        self.__scrolledWindow.add_with_viewport(self.__tableWidget)
        self.__scrolledWindow.set_shadow_type(gtk.SHADOW_NONE)
        
        self.baseWidget = gtk.VBox()
        self.baseWidget.pack_start(self.__meshTemplateNameLabel, expand=False)
        self.baseWidget.pack_start(self.__meshBadIndicator,      expand=False)
        self.baseWidget.pack_start(self.__scrolledWindow,        expand=True)
        self.baseWidget.pack_start(self.__clearLockdownButton,   expand=False)
        self.baseWidget.pack_start(self.__cloneButton,           expand=False)
        self.baseWidget.pack_start(self.__runConfigButton,       expand=False)
        self.baseWidget.pack_start(self.__exportButton,          expand=False)
        self.baseWidget.pack_start(self.__paraviewButton,        expand=False)
        self.baseWidget.pack_start(self.__generateButton,        expand=False)

        self.baseWidget.show_all()
    
    def updateTable(self):
        """
        Fills the __tableWidget
        """
        print "MeshInstance::updateTable()"
        
        numEntries = self.meshInstance.meshTemplate.paramDefaults_len()
        lockdown = self.meshInstance.lockdown

        #Initialize __tableWidget
        if not self.__tableWidget:
            self.__tableWidget=gtk.Table(numEntries+1, 3, False)                              

            self.__tableWidget.set_row_spacings(3)
            self.__tableWidget.set_col_spacings(3)
            
            self.__tableWidget.attach(self.__topLabels[0],
                                   0,1,0,1,
                                   xoptions=gtk.FILL,yoptions=gtk.FILL)
            self.__tableWidget.attach(self.__topLabels[1],
                                   1,2,0,1,
                                   xoptions=gtk.FILL|gtk.EXPAND,yoptions=gtk.FILL)
            self.__tableWidget.attach(self.__topLabels[2],
                                   2,3,0,1,
                                   xoptions=gtk.FILL,yoptions=gtk.FILL)
            
            self.__labelCollection = {}
            self.__entryCollection = {}
            self.__checkCollection = {}
        else:
            #Clear anything that might be there from before
            for k in self.meshInstance.meshTemplate.paramDefaults_getKeys():
                self.__tableWidget.remove(self.__labelCollection[k])
                self.__tableWidget.remove(self.__entryCollection[k])
                self.__tableWidget.remove(self.__checkCollection[k])
            self.__labelCollection.clear()
            self.__entryCollection.clear()
            self.__checkCollection.clear()

        #Create and attach the table entries
        for (k,i) in zip(sorted(self.meshInstance.meshTemplate.paramDefaults_getKeys()),
                         xrange(numEntries)):
            
            self.__labelCollection[k]=lab=gtk.Label(k)
            self.__tableWidget.attach(lab,0,1,i+1,i+2, xoptions=gtk.FILL, yoptions=gtk.FILL)
            
            self.__entryCollection[k]=ent=gtk.Entry()
            if k in self.meshInstance.templateOverrides_getKeys():
                ent.set_text(self.meshInstance.templateOverrides_get(k))
                if lockdown:
                    ent.set_sensitive(False)
            else:
                ent.set_text(self.meshInstance.meshTemplate.paramDefaults_get(k))
                ent.set_sensitive(False)
            self.__tableWidget.attach(ent,1,2,i+1,i+2, xoptions=gtk.FILL|gtk.EXPAND, yoptions=gtk.FILL)

            self.__checkCollection[k]=check=gtk.CheckButton()
            if k in self.meshInstance.templateOverrides_getKeys():
                check.set_active(False)
            else:
                check.set_active(True)
            if lockdown:
                check.set_sensitive(False)
            check.connect("toggled", self.event_check_toggled, k) #Toggle first, then message handler
            self.__tableWidget.attach(check,2,3,i+1,i+2, xoptions=gtk.FILL, yoptions=gtk.FILL)
        
        self.__tableWidget.show_all()
    
        #Update the meshBad label
        self.__meshBadIndicator.set_text("Mesh bad (ISOTEs): " + str(self.meshInstance.meshBad))
    
        #Update the lockdown button
        if lockdown:
            self.__clearLockdownButton.set_sensitive(True)
            self.__generateButton.set_sensitive(False)
        else:
            self.__clearLockdownButton.set_sensitive(False)
            self.__generateButton.set_sensitive(True)

        self.frameManager.mainWindow.updateProjectExplorer()
    
    def updateMeshInstance(self):
        """
        Copies information from the on-screen form into the geomInstance.
        Does NOT ask the meshInstance to write itself to file.
        
        If the meshInstance is in lockdown, do nothing.
        """
        print "MeshInstance::updateMeshInstance()"
        if self.meshInstance.lockdown:
            return
        for k in self.meshInstance.templateOverrides_getKeys():
            self.meshInstance.templateOverrides_insert(k, self.__entryCollection[k].get_text())
        
    
    def event_delete(self):
        print "MeshInstance::event_delete()"
        #Save to the meshInstance
        self.updateMeshInstance()
        #Ask the meshInstance to write itself to disk
        self.meshInstance.write()
        
    def event_button_export(self,widget,data=None):
        print "MeshInstance::event_button_export()"
        self.updateMeshInstance()
        
        (journal, extraKeys) = self.meshInstance.generateCubitJou()
        
        #Check for extra keys
        if len(extraKeys):
            dia = gtk.Dialog("Extra keys in template", self.getBaseWindow(),
                             gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                             (gtk.STOCK_NO, gtk.RESPONSE_NO,
                              gtk.STOCK_YES, gtk.RESPONSE_YES))
            dia.set_default_response(gtk.RESPONSE_YES)
            dia.vbox.pack_start(gtk.image_new_from_stock(
                         gtk.STOCK_DIALOG_QUESTION,
                         gtk.ICON_SIZE_DIALOG))
            dia.vbox.pack_start(gtk.Label("Extra keys found in template, continue?\n" + str(extraKeys) ))
            dia.show_all()

            response = dia.run()
            dia.destroy()
            
            if not response == gtk.RESPONSE_YES:
                #Stop now
                return
        
        #Ask where to save
        chooser = gtk.FileChooserDialog(title="Export file",
                                        parent=self.getBaseWindow(),
                                        action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                        buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        chooser.set_default_response(gtk.RESPONSE_OK)
        filter = gtk.FileFilter()
        filter.set_name("CUBIT journal file .jou")
        filter.add_mime_type("text/plain")
        filter.add_pattern("*.jou")
        chooser.add_filter(filter)
        response = chooser.run()
        
        if response == gtk.RESPONSE_OK:
            fname = chooser.get_filename()
            if not fname.endswith(".jou"):
                fname += ".jou"
            if os.path.isfile(fname):
                dia = gtk.Dialog("File already exists", chooser,
                                 gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                 (gtk.STOCK_NO, gtk.RESPONSE_NO,
                                  gtk.STOCK_YES, gtk.RESPONSE_YES))
                dia.set_default_response(gtk.RESPONSE_YES)
                dia.vbox.pack_start(gtk.image_new_from_stock\
                                    (gtk.STOCK_DIALOG_QUESTION,
                                     gtk.ICON_SIZE_DIALOG))
                dia.vbox.pack_start(gtk.Label("File already exists, overwrite?"))
                dia.show_all()

                response2 = dia.run()
                dia.destroy()
            
                if not response2 == gtk.RESPONSE_YES:
                    #Stop now!
                    print "MeshInstance::event_button_export()::AbortOverwrite"
                    chooser.destroy() #I'm to lazy to implement a proper event loop
                    return
            #File name free OR user clicked YES to overwrite
            chooser.destroy()
            
            print "MeshInstance::event_button_export()::write"
            ofile = open(fname,'w')
            ofile.write(journal)
            ofile.close()
            
        else:
            chooser.destroy()

    
    
    def event_button_generate(self,widget,data=None):
        print "MeshInstance::event_button_generate()"
        
        self.updateMeshInstance()
        
        try:
            self.meshInstance.generateMesh()
        except AcdOptiException_cubitTemplateFile_CUBITerror as e:
            self.makePing()
            md = gtk.MessageDialog(self.getBaseWindow(),
                                   gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
                                   gtk.BUTTONS_CLOSE, "Error during execution of CUBIT script, offending command:\n" + str(e.args[2]))
            md.run()
            md.destroy()
        except AcdOptiException_meshInstance_generateFail as e:
            self.makePing()
            md = gtk.MessageDialog(self.getBaseWindow(),
                                   gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
                                   gtk.BUTTONS_CLOSE, "There was a problem generating the mesh:\n" + str(e.args[0]))
            md.run()
            md.destroy()
        
        self.updateTable()
        
    def event_check_toggled(self, widget, data):
        print "MeshInstance::event_check_toggled(), data =", data

        if widget.get_active():
            #Checked
            dia = gtk.Dialog("Entry unchecked", self.getBaseWindow(),
                             gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                             (gtk.STOCK_NO, gtk.RESPONSE_NO,
                              gtk.STOCK_YES, gtk.RESPONSE_YES))
            dia.set_default_response(gtk.RESPONSE_YES)
            dia.vbox.pack_start(gtk.image_new_from_stock(
                         gtk.STOCK_DIALOG_QUESTION,
                         gtk.ICON_SIZE_DIALOG))
            dia.vbox.pack_start(gtk.Label("Delete override \"" + data + "\" ?"))
            dia.show_all()

            response = dia.run()

            if response == gtk.RESPONSE_YES:
                #Delete
                dia.destroy()
                
                self.meshInstance.templateOverrides_del(data)
                self.__entryCollection[data].set_sensitive(False)
                self.__entryCollection[data].set_text(self.meshInstance.meshTemplate.paramDefaults_get(data))
                
            else:
                #Abort
                dia.destroy()
                self.__checkCollection[data].set_active(False)
        else:
            #Unchecked
            self.meshInstance.templateOverrides_insert(data, self.meshInstance.meshTemplate.paramDefaults_get(data))
            self.__entryCollection[data].set_sensitive(True)
        
    def event_button_clearLockdown(self, widget, data=None):
        print "MeshInstance::event_button_clearLockdown()"
        
        self.meshInstance.clearLockdown()
        self.updateTable()
        self.frameManager.mainWindow.updateProjectExplorer()
        
    def event_button_runConfig(self, widget,data=None):
        print "MeshInstance::event_button_runConfig()"
        
        name = ""
        
        while True:
            dia = gtk.Dialog("Please enter name of new runconfig:", self.getBaseWindow(),
                             gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                             (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                              gtk.STOCK_OK, gtk.RESPONSE_OK))
            dia.set_default_response(gtk.RESPONSE_OK)
            nameBox = gtk.Entry()
            nameBox.set_text(name)
            nameBox.show()
            dia.vbox.pack_start(nameBox)
            dia.show_all()
    
            response = dia.run()
            name = nameBox.get_text()
    
            dia.destroy()
            
            if response == gtk.RESPONSE_OK:
                #Check for whitespace
                print "got: \"" + name + "\""
                if " " in name:
                    mDia = gtk.MessageDialog(self.getBaseWindow(),
                                             gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                             gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                             "Name cannot contain whitespace")
                    mDia.run()
                    mDia.destroy()
                #OK, try to add it...
                else:
                    if name in self.meshInstance.runConfigs:
                        mDia = gtk.MessageDialog(self.getBaseWindow(),
                                                 gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                                 gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                                 "Name already in use")
                        mDia.run()
                        mDia.destroy()
                        continue
                    else:
                        self.meshInstance.addRunConfig(name, "Hopper", "omega3P")
                        break #Done!
            #Response cancel or close
            else:
                break
            # END if response...
        # END while True
        self.updateTable()
        self.frameManager.mainWindow.updateProjectExplorer()
        
    def event_button_paraview(self, widget,data=None):
        print "MeshInstance::event_button_paraview()"
        paraViewPath = AcdOptiSettings().getSetting("paraviewpath")
        AcdOptiCommandWrapper.runProgramInFolder(paraViewPath, self.meshInstance.folder)
        
    def event_button_clone(self, widget, data=None):
        print "MeshInstance::event_button_clone()"
        #Ask for the new geomInstance name
        dia = gtk.Dialog("Please enter name of new mesh instance:", self.getBaseWindow(),
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                          gtk.STOCK_OK, gtk.RESPONSE_OK))
        dia.set_default_response(gtk.RESPONSE_OK)
        nameBox = gtk.Entry()
        nameBox.set_text(self.meshInstance.instName + "_clone")
        
        dia.vbox.pack_start(nameBox)
        dia.show_all()
        response = dia.run()
        cloneName = nameBox.get_text()
        dia.destroy()
            
        if response == gtk.RESPONSE_OK:
            #Check for whitespace
            if " " in cloneName:
                mDia = gtk.MessageDialog(self.getBaseWindow(),
                                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                         gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                         "Name cannot contain whitespace")
                mDia.run()
                mDia.destroy()
            elif cloneName == "":
                mDia = gtk.MessageDialog(self.getBaseWindow(),
                                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                         gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                         "Name cannot be empty")
                mDia.run()
                mDia.destroy()
            elif cloneName in self.meshInstance.geometryInstance.meshInsts:
                mDia = gtk.MessageDialog(self.getBaseWindow(),
                                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                         gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                         "Name already in use")
                mDia.run()
                mDia.destroy()
            #Everything OK: Try to attach the MeshInstance!
            else:    
                #self.geomInstance.template.cloneGeomInstance(self.geomInstance.instName, cloneName)        
                self.meshInstance.geometryInstance.cloneMeshInstance(self.meshInstance,cloneName)
                self.frameManager.mainWindow.updateProjectExplorer()