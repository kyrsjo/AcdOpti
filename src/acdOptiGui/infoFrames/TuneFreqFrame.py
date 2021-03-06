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
from acdOpti.parameterScan.TuneFreq import TuneFreqException

class TuneFreqFrame(InfoFrameComponent):
    """
    ParameterScan::TuneFreq GUI
    """
    
    tuneFreq = None
    
    __geomBox = None
    __geomCombo = None
    __geomChangedHandlerID = None
    
    __scanVariableBox = None
    __scanVariableCombo = None
    __scanVariableChangedHandlerID = None

    __pointButtonBox = None
    __iterateButton  = None
    __addPointButton = None
    
    __anaVarBox = None
    __anaVarEntry = None
    __targetValBox = None
    __targetValEntry = None
    
    __predictButtonsBox = None
    __doPredictButton = None
    __addPredictedButton = None
    
    __fitBox = None
    __fittedA_Entry = None
    __fittedB_Entry = None
    __fittedSqrtR2_Entry = None
    __fittedNDOF_Entry = None
    __fittedPredicted_Box = None
    __fittedPredicted_Entry = None

    __plotButton = None

    def __init__(self,frameManager,tuneFreq):
        InfoFrameComponent.__init__(self, frameManager)
        self.tuneFreq = tuneFreq
        
        self.baseWidget = gtk.VBox()
        
        #Geometry instance selector
        self.__geomBox = gtk.HBox()
        self.__geomCombo = gtk.combo_box_new_text()
        self.__geomChangedHandlerID = self.__geomCombo.connect("changed", self.event_comboChanged_geom, None)
        self.__geomBox.pack_start(gtk.Label("Geometry instance:"),expand=False,padding=5)
        self.__geomBox.pack_start(self.__geomCombo,expand=True,padding=5)
        self.baseWidget.pack_start(self.__geomBox, expand=False, padding=5)
        
        #self.baseWidget.pack_start(gtk.HSeparator(), expand=False, padding=10)
                
        #Scan variable selector
        self.__scanVariableBox = gtk.HBox()
        self.__scanVariableCombo = gtk.combo_box_new_text()
        self.__scanVariableChangedHandlerID = self.__scanVariableCombo.connect("changed", self.event_comboChanged_scanVar, None)
        self.__scanVariableBox.pack_start(gtk.Label("Scan variable:"), expand=False, padding=5)
        self.__scanVariableBox.pack_start(self.__scanVariableCombo , expand=True, padding=5)
        self.baseWidget.pack_start(self.__scanVariableBox, expand=False, padding=5)

        self.baseWidget.pack_start(gtk.HSeparator(), expand=False, padding=10)
                
        self.__pointButtonBox = gtk.HBox(homogeneous=True)
        self.__iterateButton = gtk.Button("Iterate")
        self.__iterateButton.connect("clicked", self.event_button_iterate, None)
        self.__pointButtonBox.pack_start(self.__iterateButton, expand=True, padding=5)
        self.__addPointButton = gtk.Button("Add point") 
        self.__addPointButton.connect("clicked", self.event_button_addpoint, None)
        self.__pointButtonBox.pack_start(self.__addPointButton, expand=True, padding=5)
        self.baseWidget.pack_start(self.__pointButtonBox,expand=False,padding=5)
        
        self.__anaVarBox = gtk.HBox()
        self.__anaVarBox.pack_start(gtk.Label("Analysis variable:"), expand=False,padding=5)
        self.__anaVarEntry = gtk.Entry()
        self.__anaVarBox.pack_start(self.__anaVarEntry, expand=True, padding = 5)
        self.baseWidget.pack_start(self.__anaVarBox, expand=False,padding=5)
        self.__targetValBox = gtk.HBox()
        self.__targetValBox.pack_start(gtk.Label("Target value:"), expand=False,padding=5)
        self.__targetValEntry = gtk.Entry()
        self.__targetValBox.pack_start(self.__targetValEntry, expand=True, padding = 5)
        self.baseWidget.pack_start(self.__targetValBox, expand=False,padding=5)
        
        self.__predictButtonsBox = gtk.HBox(homogeneous=True)
        self.__doPredictButton = gtk.Button("Predict value")
        self.__doPredictButton.connect("clicked", self.event_button_doPredict, None)
        self.__predictButtonsBox.pack_start(self.__doPredictButton, expand=True, padding=5)
        self.__addPredictedButton = gtk.Button("Add predicted value point")
        self.__addPredictedButton.connect("clicked", self.event_button_addPredicted, None)
        self.__predictButtonsBox.pack_start(self.__addPredictedButton, expand=True, padding=5)
        self.baseWidget.pack_start(self.__predictButtonsBox, expand=False, padding=5)
        
        self.__fitBox = gtk.HBox()
        self.__fitBox.pack_start(gtk.Label("Fit:"), expand=False, padding=5)
        self.__fitBox.pack_start(gtk.Label("y ="), expand=False, padding=2)
        self.__fittedA_Entry = gtk.Entry()
        self.__fitBox.pack_start(self.__fittedA_Entry, expand=True, padding=2)
        self.__fitBox.pack_start(gtk.Label("* x +"), expand=False, padding=2)
        self.__fittedB_Entry = gtk.Entry()
        self.__fitBox.pack_start(self.__fittedB_Entry, expand=True, padding=2)
        self.__fitBox.pack_start(gtk.Label(";"), expand=False, padding=5)
        self.__fitBox.pack_start(gtk.Label("R ="), expand=False, padding=2)
        self.__fittedSqrtR2_Entry = gtk.Entry()
        self.__fitBox.pack_start(self.__fittedSqrtR2_Entry, expand=True, padding=2)
        self.__fitBox.pack_start(gtk.Label("NDOF ="), expand=False, padding=2)
        self.__fittedNDOF_Entry = gtk.Entry()
        self.__fitBox.pack_start(self.__fittedNDOF_Entry, expand=True, padding=2)
        self.baseWidget.pack_start(self.__fitBox, expand=False, padding=5)
        
        self.__fittedPredicted_Box = gtk.HBox()
        self.__fittedPredicted_Box.pack_start(gtk.Label("predicted :"), expand=False, padding=5)
        self.__fittedPredicted_Entry = gtk.Entry()
        self.__fittedPredicted_Box.pack_start(self.__fittedPredicted_Entry,expand=True,padding=5)
        self.baseWidget.pack_start(self.__fittedPredicted_Box, expand=False,padding=5)
        
        self.__fittedA_Entry.set_sensitive(False)
        self.__fittedB_Entry.set_sensitive(False)
        self.__fittedNDOF_Entry.set_sensitive(False)
        self.__fittedSqrtR2_Entry.set_sensitive(False)
        self.__fittedPredicted_Entry.set_sensitive(False)
        
        self.__plotButton = gtk.Button("Show plot")
        self.__plotButton.connect("clicked", self.event_button_plot, None)
        self.baseWidget.pack_start(self.__plotButton, expand=False, padding=10)
        
        self.updateDisplay()
        self.baseWidget.show_all()
    
    def updateDisplay(self):
        #Combo box: Select geometry
        self.__geomCombo.handler_block(self.__geomChangedHandlerID)
        #Clear  whatever's in there
        for i in xrange(self.__geomCombo.get_model().iter_n_children(None)):
            self.__geomCombo.remove_text(0)
        #Refill
        idx = 0
        geomSelectedName = None
        if self.tuneFreq.baseGeomInstance !=  None:
            geomSelectedName = self.tuneFreq.baseGeomInstance.instName 
        for geom in sorted(self.tuneFreq.getProject().geomCollection.geomInstances.iterkeys()):
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
        scanVariableName = self.tuneFreq.scanParameter_name
        for varName in self.tuneFreq.getProject().geomCollection.paramDefaults_getKeys():
            self.__scanVariableCombo.append_text(varName)
            if varName == scanVariableName:
                self.__scanVariableCombo.set_active(idx)
            idx += 1
        self.__scanVariableCombo.handler_unblock(self.__scanVariableChangedHandlerID)

        self.__anaVarEntry.set_text(self.tuneFreq.predict_anaVariable)
        self.__targetValEntry.set_text(str(self.tuneFreq.predict_targetValue))
    
        self.__fittedA_Entry.set_text(str(self.tuneFreq.predict_a))
        self.__fittedB_Entry.set_text(str(self.tuneFreq.predict_b))
        if self.tuneFreq.predict_R2 > 0.0:
            self.__fittedSqrtR2_Entry.set_text(str(m.sqrt(self.tuneFreq.predict_R2)))
            self.__addPredictedButton.set_sensitive(True)
        else:
            self.__fittedSqrtR2_Entry.set_text("N/A")
            self.__addPredictedButton.set_sensitive(False)
        self.__fittedNDOF_Entry.set_text(str(self.tuneFreq.predict_ndof))
        self.__fittedPredicted_Entry.set_text(str(self.tuneFreq.predict_x))
         
        if self.tuneFreq.lockdown:
            self.__geomCombo.set_sensitive(False)
            self.__scanVariableCombo.set_sensitive(False)
            self.__iterateButton.set_sensitive(True)
            self.__addPointButton.set_sensitive(True)
            self.__doPredictButton.set_sensitive(True)
        else:
            self.__geomCombo.set_sensitive(True)
            self.__scanVariableCombo.set_sensitive(True)
            self.__iterateButton.set_sensitive(False)
            if self.tuneFreq.baseGeomInstance != None and self.tuneFreq.scanParameter_name != "":
                self.__addPointButton.set_sensitive(True)
            else:
                self.__addPointButton.set_sensitive(False)
            self.__doPredictButton.set_sensitive(False)
    
    def saveToScan(self):
        if self.tuneFreq.lockdown == False:
            #Set baseGeom and scanVar if neccessary
            geomComboText = self.__geomCombo.get_active_text()
            if geomComboText != None:
                self.tuneFreq.setBaseGeom(geomComboText)
            
            scanVarComboText = self.__scanVariableCombo.get_active_text()
            if scanVarComboText != None:
                self.tuneFreq.scanParameter_name = scanVarComboText

        self.tuneFreq.predict_anaVariable = self.__anaVarEntry.get_text()
        self.tuneFreq.predict_targetValue = float(self.__targetValEntry.get_text())  

        self.tuneFreq.write()
    
    def event_delete(self):
        return self.saveToScan()
    
    def event_button_iterate(self, widget, data=None):
        self.updateDisplay()
        try:
            self.tuneFreq.iterate()
        except TuneFreqException:
            mDia = gtk.MessageDialog(self.getBaseWindow(),
                                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                     gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                     "Prediction error, couldn't iterate")
            mDia.run()
            mDia.destroy()
        self.updateDisplay()
        self.frameManager.mainWindow.updateProjectExplorer()

    
    def event_button_addpoint(self, widget, data=None):
        self.saveToScan()

        assert self.tuneFreq.baseGeomInstance != None
        assert self.tuneFreq.scanParameter_name != ""
        
        #Ask for the new geomInstance name
        dia = gtk.Dialog("Please enter new value for scan variable '" + self.tuneFreq.scanParameter_name + "' :", self.getBaseWindow(),
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                          gtk.STOCK_OK, gtk.RESPONSE_OK))
        dia.set_default_response(gtk.RESPONSE_OK)
        nameBox = gtk.Entry()
        
        if data == None:
            defaultValue = None
            if self.tuneFreq.scanParameter_name in self.tuneFreq.baseGeomInstance.templateOverrides_getKeys():
                defaultValue = self.tuneFreq.baseGeomInstance.templateOverrides_get(self.tuneFreq.scanParameter_name)
            elif self.tuneFreq.scanParameter_name in self.tuneFreq.baseGeomInstance.template.paramDefaults_getKeys():
                defaultValue = self.tuneFreq.baseGeomInstance.template.paramDefaults_get(self.tuneFreq.scanParameter_name)
            assert defaultValue != None, "scanParameter_name '" + self.tuneFreq.scanParameter_name + "' not found ?!?"
            nameBox.set_text(defaultValue)
        else:
            nameBox.set_text(data)
        
        dia.vbox.pack_start(nameBox)
        dia.show_all()
        response = dia.run()
        
        newValue = nameBox.get_text()
        dia.destroy()
            
        if response == gtk.RESPONSE_OK:
            #Check for whitespace
            if " " in newValue:
                mDia = gtk.MessageDialog(self.getBaseWindow(),
                                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                         gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                         "Value cannot contain whitespace")
                mDia.run()
                mDia.destroy()
            elif newValue == "":
                mDia = gtk.MessageDialog(self.getBaseWindow(),
                                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                         gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                         "Value cannot be empty")
                mDia.run()
                mDia.destroy()
            #Everything OK: Try to attach the MeshInstance!
            else:
                try:
                    self.tuneFreq.addPoint(newValue)
                except TuneFreqException:
                    mDia = gtk.MessageDialog(self.getBaseWindow(),
                                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                         gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                         "Couldn't create parameter point - does it already exist?")
                    mDia.run()
                    mDia.destroy() 
                self.frameManager.mainWindow.updateProjectExplorer()
                self.updateDisplay()

    
    def event_button_doPredict(self, widget, data=None):
        self.saveToScan()
        self.tuneFreq.doPredict()
        self.updateDisplay()
    
    def event_button_addPredicted(self, widget, data=None):
        self.event_button_addpoint(widget, str(self.tuneFreq.predict_x))
    
    def event_button_plot(self, widget, data=None):
        self.saveToScan()
        
        import matplotlib.pyplot as plt
        import numpy as np
        (X,Y) = self.tuneFreq.getXY()
        if len(X) > 1:
            plt.plot(X,Y, "+")
            xRANGE = abs(max(X)-min(X))
            yRANGE = abs(max(Y)-min(Y))
            plt.xlim(min(X)-0.1*xRANGE, max(X)+0.1*xRANGE)
            plt.ylim(min(Y)-0.1*yRANGE, max(Y)+0.1*yRANGE)
            print "NDOF=", self.tuneFreq.predict_ndof   
            if (self.tuneFreq.predict_ndof >= 0):
                xr = np.linspace(min(X)-0.1*xRANGE, max(X)+0.1*xRANGE)
                yr = self.tuneFreq.predict_a*xr + self.tuneFreq.predict_b
                plt.plot(xr,yr)
            plt.axhline(y=self.tuneFreq.predict_targetValue, ls='--')
        
            plt.xlabel(self.tuneFreq.scanParameter_name)
            plt.ylabel(self.tuneFreq.predict_anaVariable)
            
            plt.show()
            gtk.main() #Else everything is closed when window is closed 
        else:
            mDia = gtk.MessageDialog(self.getBaseWindow(),
                                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                     gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                     "No data to plot?" )
            mDia.run()
            mDia.destroy()
        
    
    def event_comboChanged_geom(self, widget, data=None):
        self.saveToScan()
        self.frameManager.mainWindow.updateProjectExplorer()
        self.updateDisplay()
    
    def event_comboChanged_scanVar(self, widget, data=None):
        self.saveToScan()
        self.updateDisplay()
