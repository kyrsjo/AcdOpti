import pygtk
pygtk.require('2.0')
import gtk

import os

from InfoFrameComponent import InfoFrameComponent

from acdOpti.AcdOptiExceptions import AcdOptiException_scan_scanFail,\
                                      AcdOptiException_scan_generateRangeFail

class Scan(InfoFrameComponent):
    """
    Class that makes it possible to setup and execute
    a scan over geometry variables
    """
    
    #Class object fields
    scanInstance = None
    
    __geomBox = None
    __geomCombo = None
    __geomChangedHandlerID = None
    
    __scanVariableBox = None
    __scanVariableCombo = None
    __scanVariableDefLabel = None
    __scanVariableChangedHandlerID = None

    
    __rangeTable = None
    __rangeMaxEntry = None
    __rangeMinEntry = None
    __rangeStepEntry = None
    __previewRangeButton = None
    
    __createScanButton = None
    __stageScanButton = None
    __runScanButton = None
    #__createAndRunButton = None
    __getDataButton = None
    __runAnalysisButton = None
    
    def __init__(self,frameManager,scanInstance):
        InfoFrameComponent.__init__(self, frameManager)
        self.scanInstance = scanInstance
        
        self.baseWidget = gtk.VBox()
        
        #Geometry instance selector
        self.__geomBox = gtk.HBox()
        self.__geomCombo = gtk.combo_box_new_text()
        self.__geomChangedHandlerID = self.__geomCombo.connect("changed", self.event_comboChanged_geom, None)
        self.__geomBox.pack_start(gtk.Label("Geometry instance:"))
        self.__geomBox.pack_start(self.__geomCombo)
        self.baseWidget.pack_start(self.__geomBox, expand=False, padding=5)
        
        self.baseWidget.pack_start(gtk.HSeparator(), expand=False, padding=10)
                
        #Scan variable selector
        self.__scanVariableBox = gtk.HBox()
        self.__scanVariableCombo = gtk.combo_box_new_text()
        self.__scanVariableChangedHandlerID =  self.__scanVariableCombo.connect("changed", self.event_comboChanged_scanVar, None)
        self.__scanVariableBox.pack_start(gtk.Label("Scan variable:"))
        self.__scanVariableBox.pack_start(self.__scanVariableCombo)
        self.baseWidget.pack_start(self.__scanVariableBox, expand=False,padding=5)
        
        #Range selector
        self.__rangeTable = gtk.Table(rows=2,columns=3,homogeneous=True)
        self.__rangeMinEntry  = gtk.Entry()
        self.__rangeMaxEntry  = gtk.Entry()
        self.__rangeStepEntry = gtk.Entry()
        self.__rangeTable.attach(gtk.Label("Minimum value:"),0,1,0,1)
        self.__rangeTable.attach(gtk.Label("Maximum value:"),1,2,0,1)
        self.__rangeTable.attach(gtk.Label("Step size:"),2,3,0,1)
        self.__rangeTable.attach(self.__rangeMinEntry , 0,1,1,2)
        self.__rangeTable.attach(self.__rangeMaxEntry , 1,2,1,2)
        self.__rangeTable.attach(self.__rangeStepEntry, 2,3,1,2)
        self.baseWidget.pack_start(self.__rangeTable, expand=False, padding=5)
        
        self.__scanVariableDefLabel = gtk.Label("Default value: ") 
        self.baseWidget.pack_start(self.__scanVariableDefLabel, expand=False, padding=5)
        self.__previewRangeButton = gtk.Button("(Pre)view scan range")
        self.__previewRangeButton.connect("clicked", self.event_button_previewRange, None)
        self.baseWidget.pack_start(self.__previewRangeButton, expand=False)
        
        self.baseWidget.pack_start(gtk.HSeparator(), expand=True, padding=10) #Take up space!
        
        #Buttons
        self.__createScanButton   = gtk.Button("Create scan")
        self.__createScanButton.connect("clicked", self.event_button_createScan, None)
        self.baseWidget.pack_start(self.__createScanButton, expand=False)
        
        self.__stageScanButton    = gtk.Button("Stage runInstances")
        self.__stageScanButton.connect("clicked", self.event_button_stageScan, None)
        self.baseWidget.pack_start(self.__stageScanButton, expand=False)
        
        self.__runScanButton      = gtk.Button("Upload&run scan")
        self.__runScanButton.connect("clicked", self.event_button_runScan, None)
        self.baseWidget.pack_start(self.__runScanButton, expand=False)
        
#        self.__createAndRunButton = gtk.Button("Create and run scan (=> do all of the above!)")
#        self.baseWidget.pack_start(self.__createAndRunButton, expand=False)

        self.__getDataButton      = gtk.Button("Download finished data")
        self.__getDataButton.connect("clicked", self.event_button_getData, None)
        self.baseWidget.pack_start(self.__getDataButton, expand=False)
        
        self.__runAnalysisButton  = gtk.Button("Run analysis")
        self.__runAnalysisButton.connect("clicked", self.event_button_runAnalysis, None)
        self.baseWidget.pack_start(self.__runAnalysisButton, expand=False)
        
        self.updateDisplay()
        self.baseWidget.show_all()

    def __getDefault(self, scanVariableName):
        if scanVariableName in self.scanInstance.baseGeomInstance.templateOverrides_getKeys():
            return self.scanInstance.baseGeomInstance.templateOverrides_get(scanVariableName)
        else:
            return self.scanInstance.baseGeomInstance.template.paramDefaults_get(scanVariableName)
    def __updateDefaultLabel(self):
        if self.scanInstance.baseGeomInstance == None:
            self.__scanVariableDefLabel.set_text("Default value: <No geomInstance selected>")
        elif self.__scanVariableCombo.get_active_text() != None:
            self.__scanVariableDefLabel.set_text("Default value: " + str(self.__getDefault(self.__scanVariableCombo.get_active_text())))
        else:
            self.__scanVariableDefLabel.set_text("Default value: <No variable  selected>")
    def updateDisplay(self):
        #Combo box: Select geometry
        self.__geomCombo.handler_block(self.__geomChangedHandlerID)
        #Clear  whatever's in there
        for i in xrange(self.__geomCombo.get_model().iter_n_children(None)):
            self.__geomCombo.remove_text(0)
        #Refill
        idx = 0
        geomSelectedName = None
        if self.scanInstance.baseGeomInstance !=  None:
            geomSelectedName = self.scanInstance.baseGeomInstance.instName 
        for geom in self.scanInstance.scanCollection.project.geomCollection.geomInstances.iterkeys():
            self.__geomCombo.append_text(geom)
            if geom == geomSelectedName:
                self.__geomCombo.set_active(idx)
            idx += 1
        self.__geomCombo.handler_unblock(self.__geomChangedHandlerID)
        
        #Combo box: Select variable
        self.__scanVariableCombo.handler_block(self.__scanVariableChangedHandlerID)
        #Clear  whatever's in there
        for i in xrange(self.__scanVariableCombo.get_model().iter_n_children(None)):
            self.__scanVariableCombo.remove_text(0)
        #Refill
        idx = 0
        scanVariableName = self.scanInstance.scanParameter_name
        for varName in self.scanInstance.getValidParamNames():
            self.__scanVariableCombo.append_text(varName)
            if varName == scanVariableName:
                self.__scanVariableCombo.set_active(idx)
            idx += 1
        self.__scanVariableCombo.handler_unblock(self.__scanVariableChangedHandlerID)
    
        #Range selection
        self.__updateDefaultLabel()
        if scanVariableName != None:
            self.__rangeMinEntry.set_text(str(self.scanInstance.scanParameter_range_min))
            self.__rangeMaxEntry.set_text(str(self.scanInstance.scanParameter_range_max))
            self.__rangeStepEntry.set_text(str(self.scanInstance.scanParameter_range_step))
            
        #Lockdown
        if self.scanInstance.lockdown == True:
            self.__geomCombo.set_sensitive(False)
            self.__scanVariableCombo.set_sensitive(False)
            
            self.__rangeMaxEntry.set_sensitive(False)
            self.__rangeMinEntry.set_sensitive(False)
            self.__rangeStepEntry.set_sensitive(False)
            
            self.__createScanButton.set_sensitive(False)
            if self.scanInstance.staged == True:
                self.__stageScanButton.set_sensitive(False)
                self.__runScanButton.set_sensitive(True)
            elif self.scanInstance.staged == False:
                self.__stageScanButton.set_sensitive(True)
                self.__runScanButton.set_sensitive(False)
            else:
                raise ValueError("Scan instance staged was not initialized?!?")

        elif self.scanInstance.lockdown == False:
            self.__geomCombo.set_sensitive(True)
            self.__scanVariableCombo.set_sensitive(True)
            
            self.__rangeMaxEntry.set_sensitive(True)
            self.__rangeMinEntry.set_sensitive(True)
            self.__rangeStepEntry.set_sensitive(True)
            
            self.__createScanButton.set_sensitive(True)
            self.__stageScanButton.set_sensitive(False)
            self.__runScanButton.set_sensitive(False)
        else:
            raise ValueError("Scan instance lockdown was not initialized?!?")
    
    def saveToScan(self):
        if self.__geomCombo.get_active_text() != None:
            self.scanInstance.baseGeomInstance = self.scanInstance.scanCollection.project.geomCollection.geomInstances[self.__geomCombo.get_active_text()]
        
        if self.__scanVariableCombo.get_active_text() != None:
            self.scanInstance.scanParameter_name = self.__scanVariableCombo.get_active_text()
            if self.__rangeMinEntry.get_text() == "" or self.__rangeMaxEntry.get_text() == "" or self.__rangeStepEntry.get_text() == "":
                mDia = gtk.MessageDialog(self.getBaseWindow(),
                                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                         gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                         "If scan variable is selected, please fill out scan range")
                mDia.run()
                mDia.destroy()
                return True #Return value as expected from event_delete() 
            else:
                self.scanInstance.scanParameter_range_min = float(self.__rangeMinEntry.get_text())
                self.scanInstance.scanParameter_range_max = float(self.__rangeMaxEntry.get_text())
                self.scanInstance.scanParameter_range_step = float(self.__rangeStepEntry.get_text())
                
        self.scanInstance.write()
        return False #Return value as expected from event_delete()
    
    def event_button_previewRange(self, widget, data=None):
        self.saveToScan()
        
        try:
            if not self.scanInstance.lockdown:
                self.scanInstance.generateRange()
            mDia = gtk.MessageDialog(self.getBaseWindow(),
                                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                     gtk.MESSAGE_INFO, gtk.BUTTONS_OK,
                                     "Number of entries: " + str(len(self.scanInstance.scanParameter_range)) + ", Range:\n" + str(self.scanInstance.scanParameter_range))
            mDia.run()
            mDia.destroy()
        except AcdOptiException_scan_generateRangeFail as e:
            mDia = gtk.MessageDialog(self.getBaseWindow(),
                                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                     gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                     "Could not generate range, got error '" + e.args[0] + "'")
            mDia.run()
            mDia.destroy()
    
    def event_button_createScan(self, widget, data=None):
        print "Scan::event_button_createScan()"
        self.saveToScan()
        try:
            self.scanInstance.createScan()
        except AcdOptiException_scan_scanFail as e:
                mDia = gtk.MessageDialog(self.getBaseWindow(),
                                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                         gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                         "Could not create scan, an error occured: '"+ e.args[0] + "'")
                mDia.run()
                mDia.destroy()
        self.updateDisplay()
        self.frameManager.mainWindow.updateProjectExplorer()

    def event_button_stageScan(self, widget, data=None):
        print "Scan::event_button_stageScan()"
        self.scanInstance.stageAll()#progressCallback=self.frameManager.mainWindow.updateProjectExplorer())
        self.updateDisplay()
        self.frameManager.mainWindow.updateProjectExplorer()
        
    def event_button_runScan(self, widget, data=None):
        print "Scan::event_button_runScan()"
    
    def event_button_getData(self, widget, data=None):
        print "Scan::event_button_getData()"
    
    def event_button_runAnalysis(self, widget, data=None):
        print "Scan::event_button_runAnalysis()"
    
    def event_comboChanged_geom(self, widget, data=None):
        print "Scan::event_comboChanged_geom()"
        #self.updateDisplay()
        self.saveToScan()
        self.__updateDefaultLabel()
    def event_comboChanged_scanVar(self, widget, data=None):
        print "Scan::event_comboChanged_scanVar()"
        #self.updateDisplay()
        self.__updateDefaultLabel()
        
    def event_delete(self):
        print "Scan::event_delete()"
        return self.saveToScan()