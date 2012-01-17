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
from acdOpti.AcdOptiExceptions import AcdOptiException_analysis_runAnalysis
pygtk.require('2.0')
import gtk

from InfoFrameComponent import InfoFrameComponent
from SolverSetup import SolverSetup

from acdOpti.analysis.AnalysisInterface import AnalysisInterface

class AnalysisExportedResults(InfoFrameComponent):
    """
    Shows a tree with the exported results from an analysis,
    and has a button for runAnalysis/clearLockdown
    """
    analysis = None
    
    __settingsScroll  = None
    __settingsView    = None
    __settingsModel   = None
    __settingsCols    = None
    __settingsRenders = None
    
    __localSolverButton = None
    
    __scrollWindow = None
    __treeView     = None
    __treeModel    = None
    __treeCols     = None
    __treeRenders  = None
    
    __lockdownRunButton = None
    
    def __init__(self, frameManager, analysis):
        InfoFrameComponent.__init__(self, frameManager)
        self.analysis = analysis
        assert isinstance(self.analysis, AnalysisInterface)
        
        self.baseWidget = gtk.VBox()
        
        if self.analysis.settings != None:
            self.__settingsModel   = gtk.ListStore(str,str) #Key, value
            self.__settingsView    = gtk.TreeView(self.__settingsModel)
            self.__settingsCols    = []
            self.__settingsRenders = []
            
            self.__settingsRenders.append(gtk.CellRendererText())
            self.__settingsCols.append(gtk.TreeViewColumn("Key", self.__settingsRenders[-1], text=0))
            self.__settingsView.append_column(self.__settingsCols[-1])
        
            self.__settingsRenders.append(gtk.CellRendererText())
            self.__settingsRenders[-1].set_property("editable", True)
            self.__settingsRenders[-1].connect('edited', self.event_cellRenderer_settingsValue_edited, None)
            self.__settingsCols.append(gtk.TreeViewColumn("Value", self.__settingsRenders[-1], text=1))
            self.__settingsView.append_column(self.__settingsCols[-1])
            
            self.__settingsScroll = gtk.ScrolledWindow()
            self.__settingsScroll.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
            self.__settingsScroll.set_size_request(-1,125)
            self.__settingsScroll.add_with_viewport(self.__settingsView)
            
            self.baseWidget.pack_start(self.__settingsScroll, expand=False, padding=5)
        
        if self.analysis.localSolver != None:
            self.__localSolverButton = gtk.Button("_Setup local solver...")
            self.__localSolverButton.connect("clicked", self.event_button_localSolver, None)
            self.baseWidget.pack_start(self.__localSolverButton, expand=False, padding=5)
        
        self.__treeModel = gtk.TreeStore(str, str)
        self.__treeView = gtk.TreeView(self.__treeModel)
        self.__treeCols = []
        self.__treeRenders = []
        
        self.__treeRenders.append(gtk.CellRendererText())
        self.__treeCols.append(gtk.TreeViewColumn("Key", self.__treeRenders[-1], text=0))
        self.__treeRenders[-1].set_property("editable", True)
        self.__treeView.append_column(self.__treeCols[-1])
        
        self.__treeRenders.append(gtk.CellRendererText())
        self.__treeCols.append(gtk.TreeViewColumn("Value", self.__treeRenders[-1], text=1))
        self.__treeRenders[-1].set_property("editable", True)
        self.__treeView.append_column(self.__treeCols[-1])
         
        self.__scrollWindow = gtk.ScrolledWindow()
        self.__scrollWindow.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.__scrollWindow.add_with_viewport(self.__treeView)
        self.baseWidget.pack_start(self.__scrollWindow, expand=True, padding=5)

        self.baseWidget.pack_start(gtk.HSeparator(), expand=False, padding=10)
        
        self.__lockdownRunButton = gtk.Button("_Run analysis") #Updated in __updateGui()
        self.__lockdownRunButton.connect("clicked", self.event_button_lockdownRun, None)
        self.baseWidget.pack_start(self.__lockdownRunButton, expand=False)

        self.__updateGui()
        
        self.baseWidget.show_all()

    def __updateGui(self):
        print "AnalysisExportedResults::__updateGui()"
        #SettingsView
        if self.analysis.settings != None:
            self.__settingsModel.clear()
            for (k,v) in self.analysis.settings:
                self.__settingsModel.append([k,v])
            if self.analysis.lockdown:
                self.__settingsView.set_sensitive(False)
            else:
                self.__settingsView.set_sensitive(True)
            
        #TreeView
        self.__treeModel.clear()
        self.__updateTable_recursive(self.analysis.exportResults, None, self.__treeModel)
        self.__treeView.expand_all()
        
        #Button
        if self.analysis.lockdown:
            self.__lockdownRunButton.set_label("_Clear lockdown")
        else:
            self.__lockdownRunButton.set_label("_Run analysis")
        if self.analysis.runConfig.status == "finished":
            self.__lockdownRunButton.set_sensitive(True)
        else:
            self.__lockdownRunButton.set_sensitive(False)
            
        #Main window project explorer
        self.frameManager.mainWindow.updateProjectExplorer()

    def __updateTable_recursive(self,exportedDict,parentIter,model):
        for (k,v) in exportedDict:
            if type(v) == str:
                model.append(parentIter, [k,v])
            else:
                #DataDict
                iter = model.append(parentIter, [k,""])
                self.__updateTable_recursive(v, iter, model)
                
    def event_button_lockdownRun(self, widget, data=None):
        print "AnalysisExportedResults::event_button_lockdownRun()"
        
        if self.analysis.lockdown:
            self.analysis.clearLockdown()
        else:
            try:
                self.analysis.runAnalysis()
                self.makePing()
            except AcdOptiException_analysis_runAnalysis as e:
                self.makePing()
                mDia = gtk.MessageDialog(self.getBaseWindow(),
                                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                         gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                         "Couldn't run analysis, error message:\n'" + str(e.args) + "'")
                mDia.run()
                mDia.destroy()
        self.__updateGui()
    
    def event_button_localSolver(self, widget, data=None):
        print "AnalysisExportedResults::event_button_localSolver()"
        self.frameManager.push(SolverSetup(self.frameManager,self.analysis.localSolver))

    def event_cellRenderer_settingsValue_edited(self, cell, path, new_text, user_data=None):
        print "AnalysisExportedResults::event_cellRenderer_settingsValue_edited(), path='" + str(path) + "', new_text='" + new_text + "'"
        idx = int(path)
        self.analysis.settings.setValSingle(idx,new_text)
        self.__settingsModel[idx][1] = new_text
        
        