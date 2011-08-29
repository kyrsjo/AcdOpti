import pygtk
pygtk.require('2.0')
import gtk

from InfoFrameComponent import InfoFrameComponent
from SolverSetup import SolverSetup
from RunnerSetup import getRunnerSetup, RunnerSetup_Hopper

from acdOpti.AcdOptiSolverSetup import AcdOptiSolverSetup
from acdOpti.AcdOptiRunConfig import AcdOptiRunConfig
from acdOpti.AcdOptiExceptions import AcdOptiException_solverSetup_createFail,\
                                      AcdOptiException_solverSetup_createFail_nameTaken,\
    AcdOptiException_runConfig_stageError

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
        self.__stageOrLockdownButton.connect("clicked", self.event_button_stageOrClearLockdown, None)
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
            if status == "remote::uploaded":
                self.__statusButton.set_sensitive(False)
                self.__stageOrLockdownButton.set_label("Delete remote data")
                self.__stageOrLockdownButton.set_sensitive(True)
                self.__uploadDownloadButton.set_label("Download data")
                self.__uploadDownloadButton.set_sensitive(False)
                self.__runCancelButton.set_label("Run")
                self.__runCancelButton.set_sensitive(True)
            elif status == "remote::queued" or status == "remote::running":
                self.__statusButton.set_sensitive(True)
                self.__stageOrLockdownButton.set_label("Delete remote data")
                self.__stageOrLockdownButton.set_sensitive(False)
                self.__uploadDownloadButton.set_label("Download data")
                self.__uploadDownloadButton.set_sensitive(False)
                self.__runCancelButton.set_label("Cancel")
                self.__runCancelButton.set_sensitive(True)
            elif status == "remote::unclean":
                self.__statusButton.set_sensitive(False)
                self.__stageOrLockdownButton.set_label("Delete remote data")
                self.__stageOrLockdownButton.set_sensitive(True)
                self.__uploadDownloadButton.set_label("Download data")
                self.__uploadDownloadButton.set_sensitive(True)
                self.__runCancelButton.set_label("Cancel")
                self.__runCancelButton.set_sensitive(False)
            elif status == "remote::finished":
                self.__statusButton.set_sensitive(False)
                self.__stageOrLockdownButton.set_label("Delete remote data")
                self.__stageOrLockdownButton.set_sensitive(True)
                self.__uploadDownloadButton.set_label("Download data")
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
            self.__statusButton.set_sensitive(False)
            self.__stageOrLockdownButton.set_label("Clear lockdown, delete staging and solution")
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
        
        dia = gtk.Dialog("Select solver type", self.getBaseWindow(),
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                          gtk.STOCK_OK, gtk.RESPONSE_OK))
        dia.set_default_response(gtk.RESPONSE_OK)

        #Setup the listModel        
        diaListModel = gtk.ListStore(str)
        for type in AcdOptiSolverSetup.getTypes():
            diaListModel.append([type,])
        
        diaTreeView = gtk.TreeView(diaListModel)
        diaCellRender = gtk.CellRendererText()
        diaTreeViewCol = gtk.TreeViewColumn("Solver types", diaCellRender,text=0)
        diaTreeView.append_column(diaTreeViewCol)
        #diaTreeView.set_headers_visible(True)
        dia.vbox.pack_start(diaTreeView, padding = 5)
        
        dia.vbox.pack_start(gtk.HSeparator(), padding=10)
        
        diaEntry = gtk.Entry()
        diaEntry.set_text("Name...")
        diaCheck = gtk.CheckButton(label="Use default name")
        diaCheck.connect("toggled", lambda widget,data=None: diaEntry.set_sensitive(not widget.get_active()), None)
        diaCheck.set_active(True)
        dia.vbox.pack_start(diaCheck)
        dia.vbox.pack_start(diaEntry)
        
        dia.show_all()
        response = dia.run()
        
        #Get the answers
        (path,column) = diaTreeView.get_cursor()
        type = diaListModel[path][0]
        defaultName = diaCheck.get_active()
        name = None
        if not defaultName:
            name = diaEntry.get_text() 
        
        #Delete the dialog
        dia.destroy()
        
        if response == gtk.RESPONSE_OK:
            try:
                newSS_name = AcdOptiSolverSetup.createNew(type, self.runConfig.folder, name)
            except AcdOptiException_solverSetup_createFail_nameTaken as e:
                mDia = gtk.MessageDialog(self.getBaseWindow(),
                                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                         gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                         "Name '" + e.args[1] + "' already in use")
                mDia.run()
                mDia.destroy()
                return
            self.runConfig.solverSetups.append(AcdOptiSolverSetup(newSS_name,self.runConfig))
            self.updateDisplay()
                
        
    def event_button_solverSetupDel(self, widget, data=None):
        print "RunConfig::event_button_solverSetupDel()"
        print "Not implemented!"
        
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
            except AcdOptiException_runConfig_stageError as e:
                mDia = gtk.MessageDialog(self.getBaseWindow(),
                                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                         gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                         e.args[0] + ": " + e.args[1])
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
        #Get the currently selected row
        (path,column) = self.__solverSetupTreeView.get_cursor()
        if not path:
            #Nothing selected...
            self.__solverSetupDelButton.set_sensitive(False)
            return
        else:
            self.__solverSetupDelButton.set_sensitive(True)
        