import pygtk
pygtk.require('2.0')
import gtk

from InfoFrameComponent import InfoFrameComponent
from SolverSetup import SolverSetup

from acdOpti.AcdOptiRunConfig import AcdOptiRunConfig

class RunConfig(InfoFrameComponent):
    
    runConfig = None
    
    __configNameLabel = None
    
    __solverSetupListStore = None
    __solverSetupTreeView = None
    __solverSetupColumnName = None
    __solverSetupColumnNameRender = None
    __solverSetupColumnType = None
    __solverSetupColumnTypeRender = None
    __solverSetupAddButton = None
    
    __jobSetupLabel = None
    __jobSetupEditButton = None
    __jobSetupChangeButton = None
    __jobSetupBox = None
    
    __statusLabel =  None
    __statusButton = None    
    __uploadDownloadButton = None
    
    __stageOrLockdownButton = None
    __runCancelButton = None
    
    
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
        self.__solversTreeReference = {}
        
        self.__solverSetupAddButton = gtk.Button(label="Add solver setup...")
        self.baseWidget.pack_start(self.__solverSetupAddButton, expand=False)
        self.__solverSetupAddButton.connect("clicked", self.event_button_solverSetupAdd, None)

        self.baseWidget.pack_start(gtk.HSeparator(), expand=False, padding=10)

        self.__jobSetupLabel = gtk.Label("Current job setup type: " + self.runConfig.runner.type) #Refreshed by updateDisplay()
        self.baseWidget.pack_start(self.__jobSetupLabel, expand=False, padding=10)
        self.__jobSetupEditButton = gtk.Button(label="Edit job setup...")
        self.__jobSetupEditButton.connect("clicked", self.event_button_jobSetupEdit, None)
        self.__jobSetupChangeButton = gtk.Button(label="Switch type of job setup...")
        self.__jobSetupChangeButton.connect("clicked", self.event_button_jobSetupChange, None)
        self.__jobSetupBox = gtk.HBox()
        self.__jobSetupBox.pack_start(self.__jobSetupEditButton)
        self.__jobSetupBox.pack_start(self.__jobSetupChangeButton)
        self.baseWidget.pack_start(self.__jobSetupBox, expand=False)

        self.baseWidget.pack_start(gtk.HSeparator(), expand=False, padding=10)

        #Status control
        self.__statusLabel = gtk.Label("Current status: " + self.runConfig.status) #Refreshed by updateDisplay()
        self.baseWidget.pack_start(self.__statusLabel, expand=False, padding=10)
        self.__statusButton = gtk.Button("Refresh remote status") #Refreshed by updateDisplay()
        self.__statusButton.connect("clicked", self.event_button_refreshStatus, None)
        self.baseWidget.pack_start(self.__statusButton, expand=False)

        stageRunCancelBox = gtk.HBox()
        self.__stageOrLockdownButton = gtk.Button("Clear lockdown") #Refreshed by updateDisplay()
        self.__stageOrLockdownButton.connect("clicked", self.event_button_stageOrClearLocdown, None)
        stageRunCancelBox.pack_start(self.__stageOrLockdownButton)
        
        self.__uploadDownloadButton = gtk.Button("Upload  data") #Refreshed by updateDisplay
        self.__uploadDownloadButton.connect("clicked", self.event_button_uploadDownload, None)
        stageRunCancelBox.pack_start(self.__uploadDownloadButton)
        
        self.baseWidget.pack_start(stageRunCancelBox, expand=False)
        
        self.__runCancelButton =  gtk.Button("Run job") #Refreshed by updateDisplay()
        self.__runCancelButton.connect("clicked", self.event_button_runCancel, None)
        self.baseWidget.pack_start(self.__runCancelButton, expand=False)

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
        elif status == "initialized":
            self.__statusButton.set_sensitive(False)
            self.__stageOrLockdownButton.set_label("Stage data")
            self.__stageOrLockdownButton.set_sensitive(True)
            self.__uploadDownloadButton.set_label("Upload data")
            self.__uploadDownloadButton.set_sensitive(False)
            self.__runCancelButton.set_label("Run")
            self.__runCancelButton.set_sensitive(False)
        elif status == "staged":
            self.__statusButton.set_sensitive(False)
            self.__stageOrLockdownButton.set_label("Clear lockdown, delete staging")
            self.__stageOrLockdownButton.set_sensitive(True)
            self.__uploadDownloadButton.set_label("Upload data")
            self.__uploadDownloadButton.set_sensitive(True)
            self.__runCancelButton.set_label("Run")
            self.__runCancelButton.set_sensitive(False)
        elif status.startswith("remote::"):
            self.__statusButton.set_sensitive(True)
            if status == "remote::uploaded":
                self.__stageOrLockdownButton.set_label("Clear lockdown, delete staging")
                self.__stageOrLockdownButton.set_sensitive(False)
                self.__uploadDownloadButton.set_label("Download data")
                self.__uploadDownloadButton.set_sensitive(False)
                self.__runCancelButton.set_label("Run")
                self.__runCancelButton.set_sensitive(True)
            elif status == "remote::queued" or status == "remote::running":
                self.__stageOrLockdownButton.set_label("Clear lockdown, delete staging")
                self.__stageOrLockdownButton.set_sensitive(False)
                self.__uploadDownloadButton.set_label("Download data")
                self.__uploadDownloadButton.set_sensitive(False)
                self.__runCancelButton.set_label("Cancel")
                self.__runCancelButton.set_sensitive(True)
            elif status == "remote::finished":
                self.__stageOrLockdownButton.set_label("Clear lockdown, delete staging")
                self.__stageOrLockdownButton.set_sensitive(False)
                self.__uploadDownloadButton.set_label("Download data")
                self.__uploadDownloadButton.set_sensitive(True)
                self.__runCancelButton.set_label("Cancel")
                self.__runCancelButton.set_sensitive(False)
            else:
                assert not status in AcdOptiRunConfig.statuses 
                raise NotImplementedError
        elif status.startswith("local::"):
            if status == "local::running":
                raise NotImplementedError
        else:
            assert not status in AcdOptiRunConfig.statuses 
            raise NotImplementedError
    
    def event_delete(self):
        print "RunConfig::event_delete()"
        self.runConfig.write()
            
    def event_button_solverSetupAdd(self, widget, data=None):
        print "RunConfig::event_button_solverSetupAdd()"
    def event_button_jobSetupEdit(self, widget, data=None):
        print "RunConfig::event_button_jobSetupEdit()"
    def event_button_jobSetupChange(self, widget, data=None):
        print "RunConfig::event_button_jobSetupChange()"
        
    def event_button_refreshStatus(self, widget, data=None):
        print "RunConfig::event_button_refreshStatus()"
    def event_button_runCancel(self,widget,data=None):
        print "RunConfig::event_button_runCancel()"
        
    def event_button_stageOrClearLocdown(self,widget,data=None):
        print "RunConfig::event_button_stageOrClearLocdown()"
        status = self.runConfig.status
        assert not status.startswith("remote")

        if self.runConfig.status == "initialized":
            self.runConfig.stage()
        elif self.runConfig.status == "staged":
            self.runConfig.clearLockdown()
            
        self.updateDisplay()
    
    def event_button_uploadDownload(self,widget,data=None):
        print "RunConfig::event_button_uploadDownload()"
        
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