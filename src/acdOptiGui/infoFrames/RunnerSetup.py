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
#from twisted.python.formmethod import InputError # ??? What is this used for? Seems like Eclipse automatic stuff...
pygtk.require('2.0')
import gtk

from InfoFrameComponent import InfoFrameComponent
from acdOpti.AcdOptiRunner import AcdOptiRunner, AcdOptiRunner_Hopper
from acdOpti.AcdOptiFileParser import DataDict

def getRunnerSetup(frameManager, runner):
    print "getRunnerSetup()"
    if runner.type == "Hopper":
        return RunnerSetup_Hopper(frameManager,runner)

class RunnerSetup_Hopper(InfoFrameComponent):
    runner = None

    __torqueTable = None
    __queueCombo      = None
    __walltimeEdit    = None
    __repoEdit        = None
    __importvarsCheck = None
    
    __scrollWindow   = None
    __tasksList      = None
    __tasksListStore = None
    __tasksRenderers = None
    __tasksColumns   = None
    
    __tasksButtonsBox     = None
    __tasksAddButton      = None
    __tasksDelButton      = None
    __tasksMoveUpButton   = None
    __tasksMoveDownButton = None
    
    __closeButton = None

    def __init__(self,frameManager,runner):
        print "RunnerSetup_Hopper::__init__()"
        InfoFrameComponent.__init__(self, frameManager)
        self.runner = runner
        
        self.baseWidget = gtk.VBox()
        
        #Torque stuff:
        tqm = self.runner.getTorqueMeta()
        print tqm
        self.baseWidget.pack_start(gtk.Label("Torque information:"), expand=False,padding=5)
        self.__torqueTable   = gtk.Table(4,2,False)
        
        self.__queueCombo    = gtk.combo_box_entry_new_text()
        #self.__queueCombo.append_text(tqm["queue"])
        self.__queueCombo.append_text("regular")
        self.__queueCombo.append_text("debug")
        if tqm["queue"] == "regular":
            self.__queueCombo.set_active(0)
        else:
            self.__queueCombo.set_active(1)
        self.__torqueTable.attach(gtk.Label("Queue:"), 0,1,0,1, xoptions=gtk.FILL|gtk.EXPAND, yoptions=gtk.FILL)
        self.__torqueTable.attach(self.__queueCombo , 1,2,0,1, xoptions=gtk.FILL|gtk.EXPAND, yoptions=gtk.FILL)
        
        self.__walltimeEdit = gtk.Entry()
        if self.__checkWalltime(tqm["walltime"]):
            self.__walltimeEdit.set_text(tqm["walltime"])
        else:
            self.__walltimeEdit.set_text("hh:mm:ss")
        self.__torqueTable.attach(gtk.Label("Walltime:"), 0,1,1,2,xoptions=gtk.FILL|gtk.EXPAND, yoptions=gtk.FILL)
        self.__torqueTable.attach(self.__walltimeEdit   , 1,2,1,2,xoptions=gtk.FILL|gtk.EXPAND, yoptions=gtk.FILL)
        
        self.__repoEdit = gtk.Entry()
        self.__repoEdit.set_text(tqm["repo"])
        self.__torqueTable.attach(gtk.Label("Repository:"), 0,1,2,3,xoptions=gtk.FILL|gtk.EXPAND, yoptions=gtk.FILL)
        self.__torqueTable.attach(self.__repoEdit         , 1,2,2,3,xoptions=gtk.FILL|gtk.EXPAND, yoptions=gtk.FILL)
        
        self.__importvarsCheck = gtk.CheckButton()
        if DataDict.boolconv(tqm["importVars"]):
            self.__importvarsCheck.set_active(True)
        else:
            self.__importvarsCheck.set_active(False)
        self.__torqueTable.attach(gtk.Label("Import variables:"), 0,1,3,4,xoptions=gtk.FILL|gtk.EXPAND, yoptions=gtk.FILL)
        self.__torqueTable.attach(self.__importvarsCheck        , 1,2,3,4,xoptions=gtk.FILL|gtk.EXPAND, yoptions=gtk.FILL)
        
        self.baseWidget.pack_start(self.__torqueTable, expand=False)
        self.baseWidget.pack_start(gtk.HSeparator(), expand=False,padding=10)
        
        #Commands stuff
        #Name, command, commandArgs, tasks, tasksNode, tasksNuma, ?aprun, job 
        self.__tasksListStore = gtk.ListStore(str, str, str, int, int, int, bool, object)
        self.__tasksList = gtk.TreeView(self.__tasksListStore)
        self.__tasksRenderers = []
        self.__tasksColumns = []
        
        self.__tasksRenderers.append(gtk.CellRendererText())
        self.__tasksRenderers[-1].set_property("editable", True)
        self.__tasksRenderers[-1].connect('edited', self.event_tasksList_textEdit, "name")
        self.__tasksColumns.append(gtk.TreeViewColumn("Name", self.__tasksRenderers[-1], text=0))
        self.__tasksList.append_column(self.__tasksColumns[-1])
        
        self.__tasksRenderers.append(gtk.CellRendererText())
        self.__tasksRenderers[-1].set_property("editable", True)
        self.__tasksRenderers[-1].connect('edited', self.event_tasksList_textEdit, "command")
        self.__tasksColumns.append(gtk.TreeViewColumn("Command", self.__tasksRenderers[-1], text=1))
        self.__tasksColumns[-1].set_expand(True)
        self.__tasksList.append_column(self.__tasksColumns[-1])
        
        self.__tasksRenderers.append(gtk.CellRendererText())
        self.__tasksRenderers[-1].connect('edited', self.event_tasksList_textEdit, "commandArgs")
        self.__tasksColumns.append(gtk.TreeViewColumn("Command arguments", self.__tasksRenderers[-1], text=2, visible=6, editable=6))
        self.__tasksList.append_column(self.__tasksColumns[-1])

        self.__tasksRenderers.append(gtk.CellRendererText())
        self.__tasksRenderers[-1].connect('edited', self.event_tasksList_textEdit, "tasks")
        self.__tasksColumns.append(gtk.TreeViewColumn("# Tasks", self.__tasksRenderers[-1], text=3, visible=6, editable=6))
        self.__tasksList.append_column(self.__tasksColumns[-1])

        self.__tasksRenderers.append(gtk.CellRendererText())
        self.__tasksRenderers[-1].connect('edited', self.event_tasksList_textEdit, "tasksNode")
        self.__tasksColumns.append(gtk.TreeViewColumn("(# tasks pr. node)", self.__tasksRenderers[-1], text=4, visible=6, editable=6))
        self.__tasksList.append_column(self.__tasksColumns[-1])

        self.__tasksRenderers.append(gtk.CellRendererText())
        self.__tasksRenderers[-1].connect('edited', self.event_tasksList_textEdit, "tasksNuma")
        self.__tasksColumns.append(gtk.TreeViewColumn("(# tasks pr. NUMAnode)", self.__tasksRenderers[-1], text=5, visible=6, editable=6))
        self.__tasksList.append_column(self.__tasksColumns[-1])
        
        self.__tasksRenderers.append(gtk.CellRendererToggle())
        self.__tasksRenderers[-1].connect("toggled", self.event_tasksList_aprunToggled, None)
        self.__tasksColumns.append(gtk.TreeViewColumn("Use aprun", self.__tasksRenderers[-1], active=6))
        self.__tasksList.append_column(self.__tasksColumns[-1])
        
        self.__scrollWindow = gtk.ScrolledWindow()
        self.__scrollWindow.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.__scrollWindow.add(self.__tasksList)
        self.baseWidget.pack_start(self.__scrollWindow, expand=True)
        
        self.__populateTasksList()
        self.__tasksList.connect("cursor-changed", self.event_tasksList_cursorChanged, None)

        self.__tasksButtonsBox = gtk.HBox()
        self.__tasksMoveUpButton = gtk.Button("Move entry up")
        self.__tasksButtonsBox.pack_start(self.__tasksMoveUpButton)
        self.__tasksMoveUpButton.connect("clicked", self.event_button_moveUp, None)
        self.__tasksAddButton = gtk.Button("_Add new task")
        self.__tasksButtonsBox.pack_start(self.__tasksAddButton)
        self.__tasksAddButton.connect("clicked", self.event_button_add, None)
        self.__tasksDelButton = gtk.Button("_Delete task")
        self.__tasksButtonsBox.pack_start(self.__tasksDelButton)
        self.__tasksDelButton.connect("clicked", self.event_button_del, None)
        self.__tasksMoveDownButton = gtk.Button("Move entry down")
        self.__tasksButtonsBox.pack_start(self.__tasksMoveDownButton)
        self.__tasksMoveDownButton.connect("clicked", self.event_button_moveDown, None)
        self.event_tasksList_cursorChanged(self.__tasksList, None)
        self.baseWidget.pack_start(self.__tasksButtonsBox, expand=False)
        
        self.baseWidget.pack_start(gtk.HSeparator(), expand=False,padding=10)
        self.__closeButton = gtk.Button("_Close")
        self.__closeButton.connect("clicked", self.event_button_close, None)
        self.baseWidget.pack_start(self.__closeButton, expand=False)
        
        if self.runner.lockdown:
            self.__queueCombo.set_sensitive(False)
            self.__walltimeEdit.set_sensitive(False)
            self.__repoEdit.set_sensitive(False)
            self.__importvarsCheck.set_sensitive(False)
            self.__tasksList.set_sensitive(False)
            self.__tasksAddButton.set_sensitive(False)
            self.__tasksDelButton.set_sensitive(False)
            self.__tasksMoveUpButton.set_sensitive(False)
            self.__tasksMoveDownButton.set_sensitive(False)
        
        self.baseWidget.show_all()
    
    def __checkWalltime(self,wtstr):
        "Check if a string is a valid walltime"
        #TODO: Regexp magic
        #TODO: Move to AcdOptiRunner?
        return True
    
    def __populateTasksList(self):
        print "RunnerSetup::__populateTasksList()"
        self.__tasksListStore.clear()
        for (jobName, job) in self.runner.getJobs():
            #Name, command, args, tasks, tasksNode, tasksNuma, ?aprun, jobObject
            self.__tasksListStore.append([jobName, job["command"], job["commandArgs"],\
                                          int(job["tasks"]), int(job["tasksNode"]), int(job["tasksNuma"]),\
                                          DataDict.boolconv(job["aprun"]), job])
            #aprun = DataDict.boolconv(job["aprun"])
            #if aprun:
            #    self.__tasksListStore.append([jobName, job["command"], job["tasks"], job["tasksNode"], job["tasksNuma"], True,  job])
            #else:
            #    self.__tasksListStore.append([jobName, job["command"], -1,-1,-1,-1,False,job])
    
    def __updateRunner(self):
        print "RunnerSetup::__updateRunner()"
        "Update the runner with current contents of the widgets and tasksList"
        
        #TorqueMeta
        tqm = self.runner.getTorqueMeta()
        tqm.setValSingle("queue", self.__queueCombo.child.get_text())
        if self.__checkWalltime(self.__walltimeEdit.get_text()):
            tqm.setValSingle("walltime", self.__walltimeEdit.get_text())
        else:
            raise ValueError("Invalid walltime!")
        tqm.setValSingle("repo", self.__repoEdit.get_text())
        if self.__importvarsCheck.get_active():
            tqm.setValSingle("importVars", "True")
        else:
            tqm.setValSingle("importVars", "False")
        
        #Jobs
        jobs = self.runner.getJobs()
        jobs.clear()
        #Re-append the jobs in the order found in the tasksListStore,
        # possibly with a new name. It is assumed that each job object is kept up-to-date.
        for row in self.__tasksListStore:
            jobs.pushBack(row[0], row[-1])
        
    
    def event_button_close(self,widget,data=None):
        print "RunnerSetup::event_button_close()"
        self.__updateRunner() 
        self.runner.write()
        self.frameManager.pop()
    
    def event_button_moveUp(self, widget, data=None):
        print "RunnerSetup::event_button_moveUp()"
        (path,column) = self.__tasksList.get_cursor()
        iter = self.__tasksListStore.get_iter(path)
        path2 = (path[0]-1)
        iter2 = self.__tasksListStore.get_iter(path2)
        self.__tasksListStore.move_before(iter,iter2)
        self.event_tasksList_cursorChanged(self.__tasksList, None)
    def event_button_moveDown(self, widget, data=None):
        print "RunnerSetup::event_button_moveDown()"
        (path,column) = self.__tasksList.get_cursor()
        iter = self.__tasksListStore.get_iter(path)
        path2 = (path[0]+1)
        iter2 = self.__tasksListStore.get_iter(path2)
        self.__tasksListStore.move_after(iter,iter2)
        self.event_tasksList_cursorChanged(self.__tasksList, None)
    def event_button_del(self,widget,data=None):
        print "RunnerSetup::event_button_del()"
        (path,column) = self.__tasksList.get_cursor()
        iter = self.__tasksListStore.get_iter(path)
        self.__tasksListStore.remove(iter)
        self.event_tasksList_cursorChanged(self.__tasksList, None)
    def event_button_add(self,widget,data=None):
        print "RunnerSetup::event_button_add()"
        newJob = DataDict()
        newJob.pushBack("aprun", "False")
        newJob.pushBack("command", "")
        newJob.pushBack("commandArgs", "")
        newJob.pushBack("tasks", "-1")
        newJob.pushBack("tasksNode", "-1")
        newJob.pushBack("tasksNuma", "-1")
        self.__tasksListStore.append(["NewTask", "", -1, -1, -1, -1, False, newJob])
        self.event_tasksList_cursorChanged(self.__tasksList, None)
    def event_delete(self):
        print "RunnerSetup::event_delete()"
        #Update the runner
        self.__updateRunner()
        #Write to disk
        self.runner.write()
        
        #Everything is OK
        return False
    
    def event_tasksList_cursorChanged(self,widget,data=None):
        print "RunnerSetup::event_tasksList_cursorChanged()"
        (path,column) = self.__tasksList.get_cursor()
        if not path:
            #Nothing selected...
            self.__tasksDelButton.set_sensitive(False)
            self.__tasksMoveUpButton.set_sensitive(False)
            self.__tasksMoveDownButton.set_sensitive(False)
        else:
            self.__tasksDelButton.set_sensitive(True)
            if len(self.__tasksListStore) > 1:
                self.__tasksMoveUpButton.set_sensitive(True)
                self.__tasksMoveDownButton.set_sensitive(True)
                if path[0] == 0:
                    self.__tasksMoveUpButton.set_sensitive(False)
                elif path[0] == len(self.__tasksListStore)-1:
                    self.__tasksMoveDownButton.set_sensitive(False)
            else:
                self.__tasksMoveUpButton.set_sensitive(False)
                self.__tasksMoveDownButton.set_sensitive(False)
    
    def event_tasksList_textEdit(self, cell, path, new_text, data=None):
        print "RunnerSetup::event_tasksLists_textEdit(), path='" + str(path) + "', new_text='" + new_text + "', data='" + data + "'"
        if new_text.strip() != new_text:
            print "New entry can't start/end with whitespace"
            #TODO: Real error message...
            return
            
        if data=="name":
            print "name"
            self.__tasksListStore[path][0] =  new_text        
        elif data=="command":
            self.__tasksListStore[path][1] =  new_text
            self.__tasksListStore[path][-1].setValSingle("command", new_text)
        elif data=="commandArgs":
            self.__tasksListStore[path][2] =  new_text
            self.__tasksListStore[path][-1].setValSingle("commandArgs", new_text)
        elif data=="tasks":
            self.__tasksListStore[path][3] = int(new_text)
            self.__tasksListStore[path][-1].setValSingle("tasks", new_text)
        elif data=="tasksNode":
            self.__tasksListStore[path][4] = int(new_text)
            self.__tasksListStore[path][-1].setValSingle("tasksNode", new_text)
        elif data=="tasksNuma":
            self.__tasksListStore[path][5] = int(new_text)
            self.__tasksListStore[path][-1].setValSingle("tasksNuma", new_text)
            
    def event_tasksList_aprunToggled(self,cellrenderertoggle, path, data=None):
        print "SolverSetup::event_cellRenderer_enabled_toggled(), path='" + str(path) + "'"
        job = self.__tasksListStore[path][-1]
        self.__tasksListStore[path][6] = not self.__tasksListStore[path][6]
        job.setValSingle("aprun", str(not DataDict.boolconv(job["aprun"])))
            
                
                
