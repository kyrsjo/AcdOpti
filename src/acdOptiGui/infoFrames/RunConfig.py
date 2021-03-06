# -*- coding: utf8 -*-
#
# Copyright 2011, 2013 Kyrre Ness Sjøbæk
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

from acdOpti.analysis.AnalysisInterface import AnalysisInterface,\
                                               AnalysisException_createFail


from InfoFrameComponent import InfoFrameComponent
from SolverSetup import SolverSetup
from RunnerSetup import getRunnerSetup, RunnerSetup_Hopper

from acdOpti.AcdOptiSolverSetup import AcdOptiSolverSetup
from acdOpti.AcdOptiRunConfig import AcdOptiRunConfig
from acdOpti.AcdOptiExceptions import AcdOptiException_solverSetup_createFail,\
                                      AcdOptiException_solverSetup_createFail_nameTaken,\
                                      AcdOptiException_runConfig_stageError

import acdOpti.AcdOptiCommandWrapper as AcdOptiCommandWrapper
from acdOpti.AcdOptiSettings import AcdOptiSettings

import os

class RunConfig(InfoFrameComponent):
    
    runConfig = None
    
    __configNameLabel = None
    
    __solverSetupListStore = None
    __solverSetupTreeView = None
    __solverSetupColumnName = None
    __solverSetupColumnNameRender = None
    __solverSetupColumnType = None
    __solverSetupColumnTypeRender = None
    __solverSetupAddDelBox = None
    __solverSetupAddButton = None
    __solverSetupDelButton = None
    
    __jobSetupLabel = None
    __jobSetupEditButton = None
    __jobSetupChangeButton = None
    __jobSetupBox = None
    
    __statusLabel =  None
    __statusButton = None    
    __uploadDownloadButton = None
    
    __stageOrLockdownButton = None
    __runCancelButton = None

    __openTerminalButton = None
    __addAnalysisButton = None
    
    def __init__(self, frameManager, runConfig):
        print "RunConfig::__init__()"
        InfoFrameComponent.__init__(self, frameManager)

        self.runConfig = runConfig

        self.baseWidget = gtk.VBox()
        
        #Information
        self.__configNameLabel = gtk.Label("Name of runConfig: \"" + self.runConfig.instName + "\"")
        self.baseWidget.pack_start(self.__configNameLabel, expand=False, padding=10)
        
        self.baseWidget.pack_start(gtk.HSeparator(), expand=False, padding=10)
        
        #Solver and job setup
        self.__solverSetupListStore = gtk.ListStore(str, str)
        self.__solverSetupTreeView = gtk.TreeView(self.__solverSetupListStore)
        self.__solverSetupColumnName = gtk.TreeViewColumn("Solver setup name")
        self.__solverSetupColumnType = gtk.TreeViewColumn("Solver setup type")
        self.__solverSetupTreeView.append_column(self.__solverSetupColumnName)
        self.__solverSetupTreeView.append_column(self.__solverSetupColumnType)
        self.__solverSetupColumnNameRender = gtk.CellRendererText()
        self.__solverSetupColumnName.pack_start(self.__solverSetupColumnNameRender, True)
        self.__solverSetupColumnName.add_attribute(self.__solverSetupColumnNameRender, 'text', 0)
        self.__solverSetupColumnTypeRender = gtk.CellRendererText()
        self.__solverSetupColumnType.pack_start(self.__solverSetupColumnTypeRender, False)
        self.__solverSetupColumnType.add_attribute(self.__solverSetupColumnTypeRender, 'text', 1)
        self.baseWidget.pack_start(self.__solverSetupTreeView, expand=True)
        self.__solverSetupTreeView.connect("row-activated", self.event_solverSetupTreeView_rowActivated, None)
        self.__solverSetupTreeView.connect("cursor-changed",self.event_solverSetupTreeView_cursorChanged,None)
        self.baseWidget.pack_start(gtk.Label("Double-click a solver setup to edit..."), expand=False, padding=5)


        self.__solverSetupAddDelBox = gtk.HBox()        
        self.__solverSetupAddButton = gtk.Button(label="Add solver setup...")
        self.__solverSetupAddButton.connect("clicked", self.event_button_solverSetupAdd, None)
        self.__solverSetupAddDelBox.pack_start(self.__solverSetupAddButton)
        self.__solverSetupDelButton = gtk.Button(label="Delete solver setup")
        self.__solverSetupDelButton.connect("clicked", self.event_button_solverSetupDel, None)
        self.__solverSetupDelButton.set_sensitive(False)
        self.__solverSetupAddDelBox.pack_start(self.__solverSetupDelButton)
        self.baseWidget.pack_start(self.__solverSetupAddDelBox, expand=False)
        
        self.baseWidget.pack_start(gtk.HSeparator(), expand=False, padding=10)

        self.__jobSetupLabel = gtk.Label("Current job setup type: " + self.runConfig.runner.type) #Refreshed by updateDisplay()
        self.baseWidget.pack_start(self.__jobSetupLabel, expand=False, padding=10)
        self.__jobSetupEditButton = gtk.Button(label="Edit job setup...")
        self.__jobSetupEditButton.connect("clicked", self.event_button_jobSetupEdit, None)
        self.__jobSetupChangeButton = gtk.Button(label="Switch type of job setup...")
        self.__jobSetupChangeButton.connect("clicked", self.event_button_jobSetupChange, None)
        self.__jobSetupBox = gtk.HBox(homogeneous=True)
        self.__jobSetupBox.pack_start(self.__jobSetupEditButton)
        self.__jobSetupBox.pack_start(self.__jobSetupChangeButton)
        self.baseWidget.pack_start(self.__jobSetupBox, expand=False)

        self.baseWidget.pack_start(gtk.HSeparator(), expand=False, padding=10)

        #Status control
        self.__statusLabel = gtk.Label("Current status: " + self.runConfig.status) #Refreshed by updateDisplay()
        self.baseWidget.pack_start(self.__statusLabel, expand=False, padding=10)
        self.__statusButton = gtk.Button("_Refresh remote status") #Refreshed by updateDisplay()
        self.__statusButton.connect("clicked", self.event_button_refreshStatus, None)
        self.baseWidget.pack_start(self.__statusButton, expand=False)

        stageRunCancelBox = gtk.HBox(homogeneous=True)
        self.__stageOrLockdownButton = gtk.Button("_Clear lockdown") #Refreshed by updateDisplay()
        self.__stageOrLockdownButton.connect("clicked", self.event_button_stageOrClearLockdown, None)
        stageRunCancelBox.pack_start(self.__stageOrLockdownButton)
        
        self.__uploadDownloadButton = gtk.Button("_Upload  data") #Refreshed by updateDisplay
        self.__uploadDownloadButton.connect("clicked", self.event_button_uploadDownload, None)
        stageRunCancelBox.pack_start(self.__uploadDownloadButton)
        
        self.baseWidget.pack_start(stageRunCancelBox, expand=False)
        
        self.__runCancelButton =  gtk.Button("_Run job") #Refreshed by updateDisplay()
        self.__runCancelButton.connect("clicked", self.event_button_runCancel, None)
        self.baseWidget.pack_start(self.__runCancelButton, expand=False)

        self.baseWidget.pack_start(gtk.HSeparator(), expand=False, padding=10)
        
        self.__openTerminalButton = gtk.Button("Open _terminal")
        self.__openTerminalButton.connect("clicked", self.event_button_openterminal, None)
        self.baseWidget.pack_start(self.__openTerminalButton, expand=False)
        
        self.__addAnalysisButton = gtk.Button("_Add analysis")
        self.__addAnalysisButton.connect("clicked", self.event_button_addAnalysis, None)
        self.baseWidget.pack_start(self.__addAnalysisButton, expand=False)
        
        self.updateDisplay()

        self.baseWidget.show_all()
        
    def updateDisplay(self):
        print "RunConfig::updateDisplay()"
        
        self.__jobSetupLabel.set_label("Current job setup type: " + self.runConfig.runner.type)
        
        #Refresh the solver list
        self.__solverSetupListStore.clear()
        for ss in self.runConfig.solverSetups:
            self.__solverSetupListStore.append([ss.name, ss.type])
            
        #Activate and set button labels by looking at status flags
        status = self.runConfig.status
        
        if self.runConfig.runner.type != "Hopper":
            raise NotImplementedError("'local::'-stash not really implemented yet.")
        
        self.__statusLabel.set_label("Current status: " + status)
        if status == "not_initialized":
            self.__statusButton.set_sensitive(False)
            self.__stageOrLockdownButton.set_label("Stage data")
            self.__stageOrLockdownButton.set_sensitive(False)
            self.__uploadDownloadButton.set_label("Upload data")
            self.__uploadDownloadButton.set_sensitive(False)
            self.__runCancelButton.set_label("Run")
            self.__runCancelButton.set_sensitive(False)
            self.__solverSetupAddButton.set_sensitive(True)
            self.__solverSetupDelButton.set_sensitive(True)
            self.event_solverSetupTreeView_cursorChanged(None, None)
        elif status == "initialized":
            self.__statusButton.set_sensitive(False)
            self.__stageOrLockdownButton.set_label("_Stage data")
            self.__stageOrLockdownButton.set_sensitive(True)
            self.__uploadDownloadButton.set_label("Upload data")
            self.__uploadDownloadButton.set_sensitive(False)
            self.__runCancelButton.set_label("Run")
            self.__runCancelButton.set_sensitive(False)
            self.__solverSetupAddButton.set_sensitive(True)
            self.event_solverSetupTreeView_cursorChanged(None, None)
        elif status == "staged":
            self.__statusButton.set_sensitive(False)
            self.__stageOrLockdownButton.set_label("_Clear lockdown, delete staging")
            self.__stageOrLockdownButton.set_sensitive(True)
            self.__uploadDownloadButton.set_label("_Upload data")
            self.__uploadDownloadButton.set_sensitive(True)
            self.__runCancelButton.set_label("Run")
            self.__runCancelButton.set_sensitive(False)
            self.__solverSetupAddButton.set_sensitive(False)
            self.__solverSetupDelButton.set_sensitive(False)
        elif status.startswith("remote::"):
            self.__solverSetupAddButton.set_sensitive(False)
            self.__solverSetupDelButton.set_sensitive(False)
            if status == "remote::uploaded":
                self.__statusButton.set_sensitive(False)
                self.__stageOrLockdownButton.set_label("D_elete remote data")
                self.__stageOrLockdownButton.set_sensitive(True)
                self.__uploadDownloadButton.set_label("Download data")
                self.__uploadDownloadButton.set_sensitive(False)
                self.__runCancelButton.set_label("_Run")
                self.__runCancelButton.set_sensitive(True)
            elif status == "remote::queued" or status == "remote::running":
                self.__statusButton.set_sensitive(True)
                self.__stageOrLockdownButton.set_label("Delete remote data")
                self.__stageOrLockdownButton.set_sensitive(False)
                self.__uploadDownloadButton.set_label("Download data")
                self.__uploadDownloadButton.set_sensitive(False)
                self.__runCancelButton.set_label("_Cancel")
                self.__runCancelButton.set_sensitive(True)
            elif status == "remote::unclean":
                self.__statusButton.set_sensitive(False)
                self.__stageOrLockdownButton.set_label("D_elete remote data")
                self.__stageOrLockdownButton.set_sensitive(True)
                self.__uploadDownloadButton.set_label("_Download data")
                self.__uploadDownloadButton.set_sensitive(True)
                self.__runCancelButton.set_label("Cancel")
                self.__runCancelButton.set_sensitive(False)
            elif status == "remote::finished":
                self.__statusButton.set_sensitive(False)
                self.__stageOrLockdownButton.set_label("D_elete remote data")
                self.__stageOrLockdownButton.set_sensitive(True)
                self.__uploadDownloadButton.set_label("_Download data")
                self.__uploadDownloadButton.set_sensitive(True)
                self.__runCancelButton.set_label("Cancel")
                self.__runCancelButton.set_sensitive(False)
            else:
                assert status in AcdOptiRunConfig.statuses, "status='" + status + "'"
                raise NotImplementedError
        elif status.startswith("local::"):
            if status == "local::running":
                raise NotImplementedError
        elif status == "finished":
            self.__solverSetupAddButton.set_sensitive(False)
            self.__solverSetupDelButton.set_sensitive(False)
            self.__statusButton.set_sensitive(False)
            self.__stageOrLockdownButton.set_label("_Clear lockdown, delete staging and solution")
            self.__stageOrLockdownButton.set_sensitive(True)
            self.__uploadDownloadButton.set_label("Download data")
            self.__uploadDownloadButton.set_sensitive(False)
            self.__runCancelButton.set_label("Cancel")
            self.__runCancelButton.set_sensitive(False)
        else:
            assert not status in AcdOptiRunConfig.statuses 
            raise NotImplementedError
        self.frameManager.mainWindow.updateProjectExplorer()
        
    def event_delete(self):
        print "RunConfig::event_delete()"
        self.runConfig.write()
        
    def event_button_solverSetupAdd(self, widget, data=None):
        print "RunConfig::event_button_solverSetupAdd()"
        
        (typ,name,response) = self.getTypeAndNameDialog_currentBase(AcdOptiSolverSetup.getTypes(), "Select solver type")
        if response == gtk.RESPONSE_OK:
            try:
                newSS_name = AcdOptiSolverSetup.createNew(typ, self.runConfig.folder, name)
            except AcdOptiException_solverSetup_createFail_nameTaken as e:
                mDia = gtk.MessageDialog(self.getBaseWindow(),
                                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                         gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                         "Name '" + e.args[1] + "' already in use")
                mDia.run()
                mDia.destroy()
                return
            self.runConfig.solverSetups.append(AcdOptiSolverSetup(newSS_name,self.runConfig))
            self.runConfig.write()
            self.updateDisplay()
        
    def event_button_solverSetupDel(self, widget, data=None):
        print "RunConfig::event_button_solverSetupDel()"
        
        #What do we want to delete?
        (path,col) = self.__solverSetupTreeView.get_cursor()
        assert path, "Nothing selected?!"
        name = self.__solverSetupListStore[path][0]

        #Delete it! (don't bother with a ~impossible exception,
        # can't do much but raise an error message anyway
        self.runConfig.delSolverSetup(name)
        
        self.updateDisplay()
        
    def event_button_jobSetupEdit(self, widget, data=None):
        print "RunConfig::event_button_jobSetupEdit()"
        self.frameManager.push(getRunnerSetup(self.frameManager, self.runConfig.runner))
    def event_button_jobSetupChange(self, widget, data=None):
        print "RunConfig::event_button_jobSetupChange()"
        
    def event_button_uploadDownload(self,widget,data=None):
        print "RunConfig::event_button_uploadDownload()"
        if self.runConfig.status == "staged":
            self.runConfig.upload()
        elif self.runConfig.status == "remote::unclean" or self.runConfig.status == "remote::finished":
            self.runConfig.getRemote()
        self.makePing()
        self.updateDisplay()
    def event_button_refreshStatus(self, widget, data=None):
        print "RunConfig::event_button_refreshStatus()"
        self.runConfig.refreshStatus()
        self.updateDisplay()
    def event_button_runCancel(self,widget,data=None):
        print "RunConfig::event_button_runCancel()"
        assert self.runConfig.runner.isRemote(), "Not implemented local yet..."
        if self.runConfig.status == "remote::uploaded":
            self.runConfig.run()
        elif self.runConfig.status == "remote::running" or self.runConfig.status == "remote::queued":
            self.runConfig.cancel()
        else:
            raise NotImplementedError("Unexpected status '" + self.runConfig.status + "'")
        self.updateDisplay()
        
    def event_button_stageOrClearLockdown(self,widget,data=None):
        print "RunConfig::event_button_stageOrClearLockdown()"
        status = self.runConfig.status
        assert not status.startswith("local::"), "Local not implemented yet!"

        if self.runConfig.status == "initialized":
            try:
                self.runConfig.stage()
                self.makePing()
            except AcdOptiException_runConfig_stageError as e:
                mDia = gtk.MessageDialog(self.getBaseWindow(),
                                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                         gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                         e.args[0])
                mDia.run()
                mDia.destroy()
        elif self.runConfig.status == "staged":
            self.runConfig.clearLockdown()
        elif self.runConfig.status == "remote::uploaded" or self.runConfig.status == "remote::unclean" or self.runConfig.status == "remote::finished":
            self.runConfig.remoteCleanup()
        elif self.runConfig.status == "finished":
            self.runConfig.clearLockdown()
        else:
            raise NotImplementedError("Unexpected status '" + self.runConfig.status + "'")
        self.updateDisplay()
    
    def event_solverSetupTreeView_rowActivated(self,widget,path,column,data=None):
        print "RunConfig::event_solverSetupTreeView_rowActivated"
        
        #Find the correct solverSetup
        name = self.__solverSetupListStore.get_value(self.__solverSetupListStore.get_iter(path), 0)
        solver = None
        for ss in self.runConfig.solverSetups:
            if name == ss.name:
                solver = ss
                break
        assert solver #It should be there, as the listStore is generated from runConfig.solverSetups
        
        self.frameManager.push(SolverSetup(self.frameManager,solver))
        
    def event_solverSetupTreeView_cursorChanged(self, widget,data=None):
        print "RunConfig::event_solverSetupTreeView_cursorChanged"
        #Get the currently selected row
        (path,column) = self.__solverSetupTreeView.get_cursor()
        if not path:
            #Nothing selected...
            self.__solverSetupDelButton.set_sensitive(False)
            return
        elif self.runConfig.status == "not_initialized" or self.runConfig.status == "initialized":
            self.__solverSetupDelButton.set_sensitive(True)
    
    def event_button_addAnalysis(self,widget,data=None):
        print "RunConfig::event_button_addAnalysis()"
        (typ,name,response) = self.getTypeAndNameDialog_currentBase(AnalysisInterface.getTypes(), "Select analysis type")
        if response == gtk.RESPONSE_OK:
            try:
                self.runConfig.addAnalysis(typ,name)
            except AnalysisException_createFail as e:
                mDia = gtk.MessageDialog(self.getBaseWindow(),
                                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                         gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                         "Error when creating analysis:\n" + str(e.args))
                mDia.run()
                mDia.destroy()
            self.updateDisplay()
    
    def event_button_openterminal(self, widget, data=None):
        print "RunConfig::event_button_openterminal"
        terminalcommand = AcdOptiSettings().getSetting("terminalcommand")
        AcdOptiCommandWrapper.runProgramInFolder(terminalcommand, self.runConfig.folder)
