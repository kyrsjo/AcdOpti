# -*- coding: utf8 -*-
#
# Copyright 2012 Kyrre Ness Sjøbæk
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

import math as m

from InfoFrameComponent import InfoFrameComponent
from acdOpti.parameterScan.Scan2D_Tune import Scan2D_TuneException

class Scan2D_TuneFrame(InfoFrameComponent):
    """
    ParameterScan::Scan2D_Tune GUI
    """
      
    scan2D_Tune = None
    
    __geomBox = None
    __geomCombo = None
    __geomChangedHandlerID = None

    __scanVariable1Box = None
    __scanVariable1Combo = None
    __scanVariable1ChangedHandlerID = None
    
    __scanVariable1RangeBox = None
    __scanVariable1DefaultEntry = None
    __scanVariable1MinEntry = None
    __scanVariable1MaxEntry = None
    __scanVariable1NumEntry = None

    __scanVariable2Box = None
    __scanVariable2Combo = None
    __scanVariable2ChangedHandlerID = None
    
    __scanVariable2RangeBox = None
    __scanVariable2DefaultEntry = None
    __scanVariable2MinEntry = None
    __scanVariable2MaxEntry = None
    __scanVariable2NumEntry = None
    
    __checkRangeButton = None
    
    __tuneParameterBox = None
    __tuneParameterCombo = None
    __tuneParameterChangedHandlerID = None
    
    __tuneParameterValueBox = None
    __tuneParameterDefaultEntry = None
    __tuneParameterInitValEntry = None
    
    __tuneParameterAnaVarBox = None
    __tuneParameterAnaVarEntry = None
    
    __tuneParameterTargetVarBox = None
    __tuneParameterTargetVarEntry = None
    
    __tuneParameterFitModelBox = None
    __tuneParameterFitModelEntry = None
    __tuneParameterFitModelCheckEnable = None
    __tuneParameterCheckRangeButton = None
    
    __doScanButton     = None
    __plotButton       = None
    
    def __init__(self,frameManager,scan):
        InfoFrameComponent.__init__(self, frameManager)
        self.scan2D_Tune = scan
        
        self.baseWidget = gtk.VBox()
   
        #Geometry instance selector
        self.__geomBox = gtk.HBox()
        self.__geomCombo = gtk.combo_box_new_text()
        self.__geomChangedHandlerID = self.__geomCombo.connect("changed", self.event_comboChanged_geom, None)
        self.__geomBox.pack_start(gtk.Label("Geometry instance:"),expand=False,padding=5)
        self.__geomBox.pack_start(self.__geomCombo,expand=True,padding=5)
        self.baseWidget.pack_start(self.__geomBox, expand=False, padding=5)
   
        self.baseWidget.pack_start(gtk.HSeparator(), expand=False, padding=10)
                
        #Scan variable selectors
        self.__scanVariable1Box = gtk.HBox()
        self.__scanVariable1Combo = gtk.combo_box_new_text()
        self.__scanVariable1ChangedHandlerID = self.__scanVariable1Combo.connect("changed", self.event_comboChanged_scanVar, 1)
        self.__scanVariable1Box.pack_start(gtk.Label("Scan variable 1:"), expand=False, padding=5)
        self.__scanVariable1Box.pack_start(self.__scanVariable1Combo , expand=True, padding=5)
        self.baseWidget.pack_start(self.__scanVariable1Box, expand=False, padding=5)

        self.__scanVariable1RangeBox = gtk.HBox()
        self.__scanVariable1RangeBox.pack_start(gtk.Label("Default:"),expand=False,padding=2)
        self.__scanVariable1DefaultEntry = gtk.Entry()
        self.__scanVariable1DefaultEntry.set_sensitive(False)
        self.__scanVariable1RangeBox.pack_start(self.__scanVariable1DefaultEntry, expand=True,padding=2)
        self.__scanVariable1RangeBox.pack_start(gtk.Label("min:"),expand=False,padding=2)
        self.__scanVariable1MinEntry = gtk.Entry()
        self.__scanVariable1RangeBox.pack_start(self.__scanVariable1MinEntry, expand=True,padding=2)
        self.__scanVariable1RangeBox.pack_start(gtk.Label("max:"),expand=False,padding=2)
        self.__scanVariable1MaxEntry = gtk.Entry()
        self.__scanVariable1RangeBox.pack_start(self.__scanVariable1MaxEntry, expand=True,padding=2)
        self.__scanVariable1RangeBox.pack_start(gtk.Label("num:"),expand=False,padding=2)
        self.__scanVariable1NumEntry = gtk.Entry()
        self.__scanVariable1RangeBox.pack_start(self.__scanVariable1NumEntry, expand=True,padding=2)
        self.baseWidget.pack_start(self.__scanVariable1RangeBox,expand=False,padding=5)

        self.__scanVariable2Box = gtk.HBox()
        self.__scanVariable2Combo = gtk.combo_box_new_text()
        self.__scanVariable2ChangedHandlerID = self.__scanVariable2Combo.connect("changed", self.event_comboChanged_scanVar, 2)
        self.__scanVariable2Box.pack_start(gtk.Label("Scan variable 2:"), expand=False, padding=5)
        self.__scanVariable2Box.pack_start(self.__scanVariable2Combo , expand=True, padding=5)
        self.baseWidget.pack_start(self.__scanVariable2Box, expand=False, padding=5)

        self.__scanVariable2RangeBox = gtk.HBox()
        self.__scanVariable2RangeBox.pack_start(gtk.Label("Default:"),expand=False,padding=2)
        self.__scanVariable2DefaultEntry = gtk.Entry()
        self.__scanVariable2DefaultEntry.set_sensitive(False)
        self.__scanVariable2RangeBox.pack_start(self.__scanVariable2DefaultEntry, expand=True,padding=2)
        self.__scanVariable2RangeBox.pack_start(gtk.Label("min:"),expand=False,padding=2)
        self.__scanVariable2MinEntry = gtk.Entry()
        self.__scanVariable2RangeBox.pack_start(self.__scanVariable2MinEntry, expand=True,padding=2)
        self.__scanVariable2RangeBox.pack_start(gtk.Label("max:"),expand=False,padding=2)
        self.__scanVariable2MaxEntry = gtk.Entry()
        self.__scanVariable2RangeBox.pack_start(self.__scanVariable2MaxEntry, expand=True,padding=2)
        self.__scanVariable2RangeBox.pack_start(gtk.Label("num:"),expand=False,padding=2)
        self.__scanVariable2NumEntry = gtk.Entry()
        self.__scanVariable2RangeBox.pack_start(self.__scanVariable2NumEntry, expand=True,padding=2)
        self.baseWidget.pack_start(self.__scanVariable2RangeBox,expand=False,padding=5)

        self.__checkRangeButton = gtk.Button("Check scan ranges")
        self.__checkRangeButton.connect("clicked", self.event_button_checkScanRange, None)
        self.baseWidget.pack_start(self.__checkRangeButton, expand=False, padding=5)

        self.baseWidget.pack_start(gtk.HSeparator(), expand=False, padding=10)

        #Tuning setup
        self.__tuneParameterBox = gtk.HBox()
        self.__tuneParameterBox.pack_start(gtk.Label("Tuning parameter:"), expand=False, padding=5)
        self.__tuneParameterCombo = gtk.combo_box_new_text()
        self.__tuneParameterChangedHandlerID = self.__tuneParameterCombo.connect("changed", self.event_comboChanged_tuneParameter, None)
        self.__tuneParameterBox.pack_start(self.__tuneParameterCombo , expand=True, padding=5)
        self.baseWidget.pack_start(self.__tuneParameterBox, expand=False, padding=5)

        self.__tuneParameterValueBox = gtk.HBox()
        self.__tuneParameterValueBox.pack_start(gtk.Label("Default value:"), expand=False, padding=5)
        self.__tuneParameterDefaultEntry = gtk.Entry()
        self.__tuneParameterDefaultEntry.set_sensitive(False)
        self.__tuneParameterValueBox.pack_start(self.__tuneParameterDefaultEntry, expand=True, padding=5)
        self.__tuneParameterValueBox.pack_start(gtk.Label(","), expand=False, padding=10)
        self.__tuneParameterValueBox.pack_start(gtk.Label("Initial value(s):"), expand=False, padding=5)
        self.__tuneParameterInitValEntry = gtk.Entry()
        self.__tuneParameterValueBox.pack_start(self.__tuneParameterInitValEntry, expand=True, padding=5)
        self.baseWidget.pack_start(self.__tuneParameterValueBox, expand=False, padding=5)
        
        self.__tuneParameterAnaVarBox = gtk.HBox()
        self.__tuneParameterAnaVarBox.pack_start(gtk.Label("Analysis variable:"), expand=False, padding=5)
        self.__tuneParameterAnaVarEntry = gtk.Entry()
        self.__tuneParameterAnaVarBox.pack_start(self.__tuneParameterAnaVarEntry, expand=True, padding=5)
        self.baseWidget.pack_start(self.__tuneParameterAnaVarBox, expand=False, padding=5)

        self.__tuneParameterTargetVarBox = gtk.HBox()
        self.__tuneParameterTargetVarBox.pack_start(gtk.Label("Target value:"), expand=False, padding=5)
        self.__tuneParameterTargetVarEntry = gtk.Entry()
        self.__tuneParameterTargetVarBox.pack_start(self.__tuneParameterTargetVarEntry, expand=True, padding=5)
        self.baseWidget.pack_start(self.__tuneParameterTargetVarBox, expand=False, padding=5)

        self.__tuneParameterFitModelBox = gtk.HBox()
        self.__tuneParameterFitModelBox.pack_start(gtk.Label("Fitted plane/quadsurf\n from dataExtractor:"), expand=False, padding=5)
        self.__tuneParameterFitModelEntry = gtk.Entry()
        self.__tuneParameterFitModelBox.pack_start(self.__tuneParameterFitModelEntry, expand=True, padding=5)
        self.__tuneParameterFitModelCheckEnable = gtk.CheckButton("Use model")
        self.__tuneParameterFitModelCheckEnable.connect("toggled", self.event_modelEnableCheck_toggled, None)
        self.__tuneParameterFitModelBox.pack_start(self.__tuneParameterFitModelCheckEnable, expand=False, padding=5)
        self.baseWidget.pack_start(self.__tuneParameterFitModelBox, expand=False, padding=5)
        
        self.__tuneParameterCheckRangeButton = gtk.Button("Check scan range and tuning")
        self.__tuneParameterCheckRangeButton.connect("clicked", self.event_button_tuneParameterCheckRange, None)
        self.baseWidget.pack_start(self.__tuneParameterCheckRangeButton, expand=False, padding=5)
        
        self.baseWidget.pack_start(gtk.HSeparator(), expand=False, padding=10)

        #General stuff
        self.__doScanButton = gtk.Button("Create scan range")
        self.__doScanButton.connect("clicked", self.event_button_doScan, None)
        self.baseWidget.pack_start(self.__doScanButton, expand=False, padding = 5)
        
        self.baseWidget.pack_start(gtk.HSeparator(), expand=False, padding=10)
   
        #Plotting
        self.__plotButton = gtk.Button("Plot scan range")
        self.__plotButton.connect("clicked", self.event_button_plot, None)
        self.baseWidget.pack_start(self.__plotButton, expand=False, padding = 5)
        
   
        self.updateDisplay()
        self.baseWidget.show_all()
        
    def updateDisplay(self):
        print "scan2D_TuneFrame::updateDisplay()"
        
        #Combo box: Select geometry
        self.__geomCombo.handler_block(self.__geomChangedHandlerID)
        #Clear  whatever's in there
        for i in xrange(self.__geomCombo.get_model().iter_n_children(None)):
            self.__geomCombo.remove_text(0)
        #Refill
        idx = 0
        geomSelectedName = None
        if self.scan2D_Tune.baseGeomInstance !=  None:
            geomSelectedName = self.scan2D_Tune.baseGeomInstance.instName 
        for geom in sorted(self.scan2D_Tune.getProject().geomCollection.geomInstances.iterkeys()):
            self.__geomCombo.append_text(geom)
            if geom == geomSelectedName:
                self.__geomCombo.set_active(idx)
            idx += 1
        self.__geomCombo.handler_unblock(self.__geomChangedHandlerID)
        
        #Combo box: Select variable 1
        self.__scanVariable1Combo.handler_block(self.__scanVariable1ChangedHandlerID)
        #Clear  whatever's in there
        for i in xrange(self.__scanVariable1Combo.get_model().iter_n_children(None)):
            self.__scanVariable1Combo.remove_text(0)
        #Refill
        idx = 0
        scanVariable1Name = self.scan2D_Tune.scanParameter1_name
        for varName in self.scan2D_Tune.getProject().geomCollection.paramDefaults_getKeys():
            if varName == self.scan2D_Tune.scanParameter2_name or varName == self.scan2D_Tune.tune_parameter:
                continue #Skip
            self.__scanVariable1Combo.append_text(varName)
            if varName == scanVariable1Name:
                self.__scanVariable1Combo.set_active(idx)
            idx += 1
        self.__scanVariable1Combo.handler_unblock(self.__scanVariable1ChangedHandlerID)
        
        if scanVariable1Name != "" and self.scan2D_Tune.baseGeomInstance != None:
            if scanVariable1Name in self.scan2D_Tune.baseGeomInstance.templateOverrides_getKeys():
                self.__scanVariable1DefaultEntry.set_text(str( self.scan2D_Tune.baseGeomInstance.templateOverrides_get(scanVariable1Name) ))
            else:
                self.__scanVariable1DefaultEntry.set_text(str( self.scan2D_Tune.getProject().geomCollection.paramDefaults_get(scanVariable1Name) ))
        else:
            self.__scanVariable1DefaultEntry.set_text(str("N/A"))
        
        self.__scanVariable1MinEntry.set_text(str( self.scan2D_Tune.scanParameter1_min ))
        self.__scanVariable1MaxEntry.set_text(str( self.scan2D_Tune.scanParameter1_max ))
        self.__scanVariable1NumEntry.set_text(str( self.scan2D_Tune.scanParameter1_num ))
        
        #Combo box: Select variable 2
        self.__scanVariable2Combo.handler_block(self.__scanVariable2ChangedHandlerID)
        #Clear  whatever's in there
        for i in xrange(self.__scanVariable2Combo.get_model().iter_n_children(None)):
            self.__scanVariable2Combo.remove_text(0)
        #Refill
        scanVariable2Name = self.scan2D_Tune.scanParameter2_name
        self.__scanVariable2Combo.append_text(" -- Disabled --")
        if scanVariable2Name == "":
            self.__scanVariable2Combo.set_active(0)
        idx = 1
        for varName in self.scan2D_Tune.getProject().geomCollection.paramDefaults_getKeys():
            if varName == self.scan2D_Tune.scanParameter1_name or varName == self.scan2D_Tune.tune_parameter:
                continue #Skip
            self.__scanVariable2Combo.append_text(varName)
            if varName == scanVariable2Name:
                self.__scanVariable2Combo.set_active(idx)
            idx += 1
        self.__scanVariable2Combo.handler_unblock(self.__scanVariable2ChangedHandlerID)
    
        if scanVariable2Name != "" and self.scan2D_Tune.baseGeomInstance != None:
            if scanVariable2Name in self.scan2D_Tune.baseGeomInstance.templateOverrides_getKeys():
                self.__scanVariable2DefaultEntry.set_text(str( self.scan2D_Tune.baseGeomInstance.templateOverrides_get(scanVariable2Name) ))
            else:
                self.__scanVariable2DefaultEntry.set_text(str( self.scan2D_Tune.getProject().geomCollection.paramDefaults_get(scanVariable2Name) ))
        else:
            self.__scanVariable2DefaultEntry.set_text(str("N/A"))
    
        self.__scanVariable2MinEntry.set_text(str( self.scan2D_Tune.scanParameter2_min ))
        self.__scanVariable2MaxEntry.set_text(str( self.scan2D_Tune.scanParameter2_max ))
        self.__scanVariable2NumEntry.set_text(str( self.scan2D_Tune.scanParameter2_num ))
    
        #Combo box: Select tuning parameter
        self.__tuneParameterCombo.handler_block(self.__tuneParameterChangedHandlerID)
        #Clear  whatever's in there
        for i in xrange(self.__tuneParameterCombo.get_model().iter_n_children(None)):
            self.__tuneParameterCombo.remove_text(0)
        #Refill
        tuneParameterName = self.scan2D_Tune.tune_parameter
        self.__tuneParameterCombo.append_text(" -- None selected -- ")
        if tuneParameterName == "":
            self.__tuneParameterCombo.set_active(0)
        idx = 1
        for varName in self.scan2D_Tune.getProject().geomCollection.paramDefaults_getKeys():
            if varName != "" and varName == scanVariable1Name or varName == scanVariable2Name:
                continue
            self.__tuneParameterCombo.append_text(varName)
            if varName == tuneParameterName:
                self.__tuneParameterCombo.set_active(idx)
            idx += 1
        self.__tuneParameterCombo.handler_unblock(self.__tuneParameterChangedHandlerID)
        
        if tuneParameterName != "" and self.scan2D_Tune.baseGeomInstance != None:
            if tuneParameterName in self.scan2D_Tune.baseGeomInstance.templateOverrides_getKeys():
                self.__tuneParameterDefaultEntry.set_text(str( self.scan2D_Tune.baseGeomInstance.templateOverrides_get(tuneParameterName) ))
            else:
                self.__tuneParameterDefaultEntry.set_text(str( self.scan2D_Tune.getProject().geomCollection.paramDefaults_get(tuneParameterName) ))
        else:
            self.__tuneParameterDefaultEntry.set_text(str("N/A"))
        
        initValuesString = ""
        for p in self.scan2D_Tune.tune_initialPoints:
            initValuesString += str(p) + ", "
        initValuesString = initValuesString[:-2] #strip last ", "
        self.__tuneParameterInitValEntry.set_text(initValuesString)
        
        self.__tuneParameterAnaVarEntry.set_text(self.scan2D_Tune.tune_anaVariable)
        
        self.__tuneParameterTargetVarEntry.set_text(str(self.scan2D_Tune.tune_targetValue))
        
        #Model
        if self.scan2D_Tune.tune_useModelPoints == True:
            self.__tuneParameterInitValEntry.set_sensitive(False)
            self.__tuneParameterFitModelEntry.set_sensitive(True)
            self.__tuneParameterFitModelCheckEnable.set_active(True)
        elif self.scan2D_Tune.tune_useModelPoints == False:
            self.__tuneParameterInitValEntry.set_sensitive(True)
            self.__tuneParameterFitModelEntry.set_sensitive(False)
            self.__tuneParameterFitModelCheckEnable.set_active(False)
        else:
            raise ValueError
        if len(self.scan2D_Tune.tune_model) == 3:
            mod = self.scan2D_Tune.tune_model
            modelString = str(mod[0]) + "+" + \
                str(mod[1]) + "*" + self.scan2D_Tune.scanParameter1_name + "+" +\
                str(mod[2]) + "*" + self.scan2D_Tune.scanParameter2_name 
            self.__tuneParameterFitModelEntry.set_text(modelString)
            self.__tuneParameterCheckRangeButton.set_sensitive(True)
        elif len(self.scan2D_Tune.tune_model) == 6:
            mod = self.scan2D_Tune.tune_model
            modelString = str(mod[0]) + "+" + \
                str(mod[1]) + "*" + self.scan2D_Tune.scanParameter1_name + "+" +\
                str(mod[2]) + "*" + self.scan2D_Tune.scanParameter2_name + "+" +\
                str(mod[3]) + "*" + self.scan2D_Tune.scanParameter1_name + "^2+" + \
                str(mod[4]) + "*" + self.scan2D_Tune.scanParameter2_name + "^2+" + \
                str(mod[5]) + "*" + self.scan2D_Tune.scanParameter1_name + "*" + self.scan2D_Tune.scanParameter2_name 
            self.__tuneParameterFitModelEntry.set_text(modelString)
            self.__tuneParameterCheckRangeButton.set_sensitive(True)
        else:
            self.__tuneParameterCheckRangeButton.set_sensitive(False)
        
        
        if self.scan2D_Tune.lockdown:
            self.__geomCombo.set_sensitive(False)
            self.__scanVariable1Combo.set_sensitive(False)
            self.__scanVariable2Combo.set_sensitive(False)
            self.__tuneParameterCombo.set_sensitive(False)
            self.__tuneParameterAnaVarEntry.set_sensitive(False)
            self.__tuneParameterTargetVarEntry.set_sensitive(False)
            
        if self.scan2D_Tune.scanParameter1_name == "" or self.scan2D_Tune.scanParameter2_name == "":
            self.__tuneParameterFitModelCheckEnable.set_sensitive(False)
            self.__tuneParameterFitModelEntry.set_sensitive(False)
            self.__tuneParameterCheckRangeButton.set_sensitive(False)
        
        if self.scan2D_Tune.scanParameter1_name == "" or self.scan2D_Tune.tune_parameter == "" or self.scan2D_Tune.tune_anaVariable == "":
            self.__doScanButton.set_sensitive(False)
        else:
            self.__doScanButton.set_sensitive(True)
    
    def saveToScan(self):
        print "scan2D_TuneFrame::saveToScan()"
        if self.scan2D_Tune.lockdown == False:
            #Set baseGeom and scanVar if neccessary
            geomComboText = self.__geomCombo.get_active_text()
            if geomComboText != None:
                self.scan2D_Tune.setBaseGeom(geomComboText)
            
            scanVar1ComboText = self.__scanVariable1Combo.get_active_text()
            if scanVar1ComboText == None:
                self.scan2D_Tune.scanParameter1_name = ""
            else:
                self.scan2D_Tune.scanParameter1_name = scanVar1ComboText
            
            scanVar2ComboText = self.__scanVariable2Combo.get_active_text()
            if scanVar2ComboText == " -- Disabled --" or scanVar2ComboText == None:
                self.scan2D_Tune.scanParameter2_name = ""
            else:
                self.scan2D_Tune.scanParameter2_name = scanVar2ComboText
            
            tuneParameterComboText = self.__tuneParameterCombo.get_active_text()
            if tuneParameterComboText == " -- None selected -- " or tuneParameterComboText == None:
                self.scan2D_Tune.tune_parameter = ""
            else:
                self.scan2D_Tune.tune_parameter = tuneParameterComboText
            
            anaVar = self.__tuneParameterAnaVarEntry.get_text()
            if " " in anaVar:
                mDia = gtk.MessageDialog(self.getBaseWindow(),
                                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                         gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                         "Blank in analysis variable, couldn't store it" )
                mDia.run()
                mDia.destroy()
            else:
                self.scan2D_Tune.tune_anaVariable = anaVar
            
            try:
                self.scan2D_Tune.tune_targetValue = float(self.__tuneParameterTargetVarEntry.get_text())
            except ValueError:
                mDia = gtk.MessageDialog(self.getBaseWindow(),
                                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                         gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                         "Could not convert target value to float" )
                mDia.run()
                mDia.destroy()
        #END if lockdown
        
        initValsString = self.__tuneParameterInitValEntry.get_text()
        initValsString = initValsString.split(",")
        del self.scan2D_Tune.tune_initialPoints[:] #clear it!
        for s in initValsString:
            s2 = s.strip()
            if " " in s2:
                print "initValsString element contained space, skipping '" + s2 + "'"
                continue
            self.scan2D_Tune.tune_initialPoints.append(s2)
            
        try:
            self.scan2D_Tune.scanParameter1_min = float(self.__scanVariable1MinEntry.get_text())
            self.scan2D_Tune.scanParameter1_max = float(self.__scanVariable1MaxEntry.get_text())
            self.scan2D_Tune.scanParameter1_num = int(self.__scanVariable1NumEntry.get_text())
        except ValueError:
            mDia = gtk.MessageDialog(self.getBaseWindow(),
                                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                     gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                     "Could not convert contents to float for scanParameter 1" )
            mDia.run()
            mDia.destroy()
            
        try:
            self.scan2D_Tune.scanParameter2_min = float(self.__scanVariable2MinEntry.get_text())
            self.scan2D_Tune.scanParameter2_max = float(self.__scanVariable2MaxEntry.get_text())
            self.scan2D_Tune.scanParameter2_num = int(self.__scanVariable2NumEntry.get_text())
            print "Sucessfully Saved min/max/num for scan parameters"
        except ValueError:
            mDia = gtk.MessageDialog(self.getBaseWindow(),
                                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                     gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                     "Could not convert contents to float for scanParameter 1" )
            mDia.run()
            mDia.destroy()
        
        #Parse model
        modelString = self.__tuneParameterFitModelEntry.get_text()
        modelString = modelString.split("+")
        if len(modelString) == 3:
            #Plane
            try:
                model = []

                model.append(float(modelString[0]))
                
                s = modelString[1].split("*")
                assert s[1] == "X" or s[1] == self.scan2D_Tune.scanParameter1_name
                assert len(s) == 2
                model.append(float(s[0]))
                
                s = modelString[2].split("*")
                assert s[1] == "Y" or s[1] == self.scan2D_Tune.scanParameter2_name
                assert len(s) == 2
                model.append(float(s[0]))
                
                self.scan2D_Tune.tune_model = model
            except:
                print "Scan2D_TuneFrame::write(): Problem parsing the modelString (plane)"
                
        elif len(modelString) == 6:
            #Quad
            try:
                model = []

                model.append(float(modelString[0]))
                
                s = modelString[1].split("*")
                assert s[1] == "X" or s[1] == self.scan2D_Tune.scanParameter1_name
                assert len(s) == 2
                model.append(float(s[0]))
                
                s = modelString[2].split("*")
                assert s[1] == "Y" or s[1] == self.scan2D_Tune.scanParameter2_name
                assert len(s) == 2
                model.append(float(s[0]))
                
                s = modelString[3].split("*")
                assert s[1] == "X^2" or s[1] == (self.scan2D_Tune.scanParameter1_name + "^2")
                assert len(s) == 2
                model.append(float(s[0]))
                
                s = modelString[4].split("*")
                assert s[1] == "Y^2" or s[1] == (self.scan2D_Tune.scanParameter2_name + "^2")
                assert len(s) == 2
                model.append(float(s[0]))
                
                s = modelString[5].split("*")
                assert s[1] == "X" or s[1] == self.scan2D_Tune.scanParameter1_name
                assert s[2] == "Y" or s[2] == self.scan2D_Tune.scanParameter2_name
                assert len(s) == 3
                model.append(float(s[0]))
                
                self.scan2D_Tune.tune_model = model
            except:
                print "Scan2D_TuneFrame::write(): Problem parsing the modelString (quad)"
        else:
            print "Unexpected length of modelString =", modelString
        print "tune_model =", self.scan2D_Tune.tune_model
            
        self.scan2D_Tune.tune_useModelPoints = self.__tuneParameterFitModelCheckEnable.get_active()
        
        self.scan2D_Tune.write()
    
    def event_button_checkScanRange(self, widget, data=None):
        self.saveToScan()
        self.updateDisplay() #In case invalid entries found by saveToScan, update the GUI to see the reset values
        try:
            (range1,range2) = self.scan2D_Tune.getScanRanges()
        except Scan2D_TuneException as e:
            mDia = gtk.MessageDialog(self.getBaseWindow(),
                                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                     gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                     "Error while generating the range:\n%s" % (e.args[0],) )
            mDia.run()
            mDia.destroy()
            return
        
        if range2 != None:
            msgStr = None
            if data == "Model":
                msgStr = "Scanning %s and %s, tuning with %s from model. Generated values:\n"\
                     % ( self.scan2D_Tune.scanParameter1_name, self.scan2D_Tune.scanParameter2_name, self.scan2D_Tune.tune_parameter )
                for i in xrange(len(range1)):
                    for j in xrange(len(range2)):
                        msgStr += str(range1[i]) + ", " + str(range2[j]) + "; " + str(self.scan2D_Tune.getTunedModel(range1[i], range2[j])) + "\n"
                msgStr = msgStr[:-1] #trim last "\n"
            elif data == None:
                msgStr = "Got scan ranges:\n %s: %s\n %s: %s\n Total number of points: %i" % \
                        ( self.scan2D_Tune.scanParameter1_name, str(range1), self.scan2D_Tune.scanParameter2_name, str(range2), len(range1)*len(range2) )
            mDia = gtk.MessageDialog(self.getBaseWindow(),
                                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                     gtk.MESSAGE_INFO, gtk.BUTTONS_OK,
                                     msgStr )
            mDia.run()
            mDia.destroy()
        else:
            mDia = gtk.MessageDialog(self.getBaseWindow(),
                                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                     gtk.MESSAGE_INFO, gtk.BUTTONS_OK,
                                     "Got scan ranges:\n %s: %s\n (2nd variable disabled)\n Total number of points: %i" % \
                                     ( self.scan2D_Tune.scanParameter1_name, str(range1), len(range1) ) )
            mDia.run()
            mDia.destroy()
    
    def event_button_tuneParameterCheckRange(self, widget,data=None):
        self.event_button_checkScanRange(widget, "Model")
    
    def event_button_doScan(self,widget,data=None):
        self.saveToScan()
        self.updateDisplay()
        
        #Just as a test
        try:
            (range1,range2) = self.scan2D_Tune.getScanRanges()
        except Scan2D_TuneException as e:
            mDia = gtk.MessageDialog(self.getBaseWindow(),
                                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                     gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                     "Error while generating the range:\n%s" % (e.args[0],) )
            mDia.run()
            mDia.destroy()
            return
        
        self.scan2D_Tune.createScan()
        
        self.updateDisplay()
        self.frameManager.mainWindow.updateProjectExplorer()
    
    def event_button_plot(self,widget,data=None):
        self.saveToScan()
        self.updateDisplay()
        
        if self.scan2D_Tune.scanParameter1_name == "":
            mDia = gtk.MessageDialog(self.getBaseWindow(),
                                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                     gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                     "Must set at least one scan parameter!" )
            mDia.run()
            mDia.destroy()
            return
        
        import numpy as np
        import matplotlib.pyplot as plt
        
        try:
            (range1,range2) = self.scan2D_Tune.getScanRanges()
        except Scan2D_TuneException as e:
            mDia = gtk.MessageDialog(self.getBaseWindow(),
                                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                     gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                     "Error while generating the range:\n%s" % (e.args[0],) )
            mDia.run()
            mDia.destroy()
            return
        
        showPlot = False
        
        X = [] #parameter 1
        Y = [] #parameter 2
        if range2 != None:
            for i in xrange(len(range2)):
                X += list(range1)
                Y += [range2[i]]*len(range1)
        else:
             X = list(range1)
             Y = list(np.zeros_like(range1))
        if len(X) > 0:
            plt.plot(X,Y, '+', label="Proposed range")
            showPlot = True
        
        #Todo: Show current geometries also
        if self.scan2D_Tune.baseGeomInstance != None:
            X2 = []
            Y2 = []
            
            #BaseGeomInstance
            if self.scan2D_Tune.scanParameter1_name in self.scan2D_Tune.baseGeomInstance.templateOverrides_getKeys():
                X2.append(self.scan2D_Tune.baseGeomInstance.templateOverrides_get(self.scan2D_Tune.scanParameter1_name))
            else:
                X2.append(self.scan2D_Tune.getProject().geomCollection.paramDefaults_get(self.scan2D_Tune.scanParameter1_name))
            
            if self.scan2D_Tune.scanParameter2_name == "":
                Y2.append(0.0)
            elif self.scan2D_Tune.scanParameter2_name in self.scan2D_Tune.baseGeomInstance.templateOverrides_getKeys():
                Y2.append(self.scan2D_Tune.baseGeomInstance.templateOverrides_get(self.scan2D_Tune.scanParameter2_name))
            else:
                Y2.append(self.scan2D_Tune.getProject().geomCollection.paramDefaults_get(self.scan2D_Tune.scanParameter2_name))
            
            #SlaveGeoms
            for geom in self.scan2D_Tune.slaveGeoms.values():
                X2.append(geom.templateOverrides_get(self.scan2D_Tune.scanParameter1_name))
                if self.scan2D_Tune.scanParameter2_name == "":
                    Y2.append(0.0)
                else:
                    Y2.append(geom.templateOverrides_get(self.scan2D_Tune.scanParameter2_name))
            X2 = map(float, X2)
            Y2 = map(float, Y2)
            if len(X2) > 0:
                plt.plot(X2,Y2, 'x', label="Current slaveGeoms")
                showPlot = True
        
        if showPlot:
            xRANGE = abs(max(X+X2)-min(X+X2)) #X,X2 are lists
            yRANGE = abs(max(Y+Y2)-min(Y+Y2))
            if yRANGE == 0:
                yRANGE = 1.0 #In case of no 2nd parameter
            plt.xlim(min(X+X2)-0.1*xRANGE, max(X+X2)+0.1*xRANGE)
            plt.ylim(min(Y+Y2)-0.1*yRANGE, max(Y+Y2)+0.1*yRANGE)

            plt.legend()
            plt.show()
            gtk.main()
        else:
            mDia = gtk.MessageDialog(self.getBaseWindow(),
                                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                     gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                     "No data to plot?" )
            mDia.run()
            mDia.destroy()
    
    def event_comboChanged_geom(self, widget, data=None):
        print "scan2D_TuneFrame::event_comboChanged_geom, data =", data
        self.saveToScan()
        self.frameManager.mainWindow.updateProjectExplorer()
        self.updateDisplay()
    
    def event_comboChanged_scanVar(self, widget, data):
        print "scan2D_TuneFrame::event_comboChanged_scanVar, data =", data
        self.saveToScan()
        self.updateDisplay()
    
    def event_comboChanged_tuneParameter(self, widget, data):
        print "scan2D_TuneFrame::event_comboChanged_tuneParameter, data =", data
        
        self.saveToScan()
        self.updateDisplay()
    
    def event_modelEnableCheck_toggled(self, widget, data):
        print "scan2D_TuneFrame::event_modelEnableCheck_toggled"
        self.saveToScan()
        self.updateDisplay()
    
    def event_delete(self):
        return self.saveToScan()
    