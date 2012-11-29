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
from acdOpti.parameterScan.Scan2D import Scan2DException

class Scan2DFrame(InfoFrameComponent):
    """
    ParameterScan::Scan2D GUI
    """
      
    scan2D = None
    
    __geomBox = None
    __geomCombo = None
    __geomChangedHandlerID = None

    __scanVariable1Box = None
    __scanVariable1Combo = None
    __scanVariable1DefLabel = None
    __scanVariable1ChangedHandlerID = None
    
    __scanVariable1RangeBox = None
    __scanVariable1DefaultEntry = None
    __scanVariable1MinEntry = None
    __scanVariable1MaxEntry = None
    __scanVariable1NumEntry = None

    __scanVariable2Box = None
    __scanVariable2Combo = None
    __scanVariable2DefLabel = None
    __scanVariable2ChangedHandlerID = None
    
    __scanVariable2RangeBox = None
    __scanVariable2DefaultEntry = None
    __scanVariable2MinEntry = None
    __scanVariable2MaxEntry = None
    __scanVariable2NumEntry = None
    
    __checkRangeButton = None
    __doScanButton     = None
    __plotButton       = None
    
    def __init__(self,frameManager,scan):
        InfoFrameComponent.__init__(self, frameManager)
        self.scan2D = scan
        
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

        self.__doScanButton = gtk.Button("Create scan range")
        self.__doScanButton.connect("clicked", self.event_button_doScan, None)
        self.baseWidget.pack_start(self.__doScanButton, expand=False, padding = 5)
        
        self.baseWidget.pack_start(gtk.HSeparator(), expand=False, padding=10)
   
        self.__plotButton = gtk.Button("Plot scan range")
        self.__plotButton.connect("clicked", self.event_button_plot, None)
        self.baseWidget.pack_start(self.__plotButton, expand=False, padding = 5)
        
   
        self.updateDisplay()
        self.baseWidget.show_all()
        
    def updateDisplay(self):
        print "Scan2DFrame::updateDisplay()"
        
        #Combo box: Select geometry
        self.__geomCombo.handler_block(self.__geomChangedHandlerID)
        #Clear  whatever's in there
        for i in xrange(self.__geomCombo.get_model().iter_n_children(None)):
            self.__geomCombo.remove_text(0)
        #Refill
        idx = 0
        geomSelectedName = None
        if self.scan2D.baseGeomInstance !=  None:
            geomSelectedName = self.scan2D.baseGeomInstance.instName 
        for geom in sorted(self.scan2D.getProject().geomCollection.geomInstances.iterkeys()):
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
        scanVariable1Name = self.scan2D.scanParameter1_name
        for varName in self.scan2D.getProject().geomCollection.paramDefaults_getKeys():
            if varName == self.scan2D.scanParameter2_name:
                continue #Skip
            self.__scanVariable1Combo.append_text(varName)
            if varName == scanVariable1Name:
                self.__scanVariable1Combo.set_active(idx)
            idx += 1
        self.__scanVariable1Combo.handler_unblock(self.__scanVariable1ChangedHandlerID)
        
        if scanVariable1Name != "" and self.scan2D.baseGeomInstance != None:
            if scanVariable1Name in self.scan2D.baseGeomInstance.templateOverrides_getKeys():
                self.__scanVariable1DefaultEntry.set_text(str( self.scan2D.baseGeomInstance.templateOverrides_get(scanVariable1Name) ))
            else:
                self.__scanVariable1DefaultEntry.set_text(str( self.scan2D.getProject().geomCollection.paramDefaults_get(scanVariable1Name) ))
        else:
            self.__scanVariable1DefaultEntry.set_text(str("N/A"))
        
        self.__scanVariable1MinEntry.set_text(str( self.scan2D.scanParameter1_min ))
        self.__scanVariable1MaxEntry.set_text(str( self.scan2D.scanParameter1_max ))
        self.__scanVariable1NumEntry.set_text(str( self.scan2D.scanParameter1_num ))
        
        #Combo box: Select variable 2
        self.__scanVariable2Combo.handler_block(self.__scanVariable2ChangedHandlerID)
        #Clear  whatever's in there
        for i in xrange(self.__scanVariable2Combo.get_model().iter_n_children(None)):
            self.__scanVariable2Combo.remove_text(0)
        #Refill
        scanVariable2Name = self.scan2D.scanParameter2_name
        self.__scanVariable2Combo.append_text(" -- Disabled --")
        if scanVariable2Name == "":
            self.__scanVariable2Combo.set_active(0)
        idx = 1
        for varName in self.scan2D.getProject().geomCollection.paramDefaults_getKeys():
            if varName == self.scan2D.scanParameter1_name:
                continue #Skip
            self.__scanVariable2Combo.append_text(varName)
            if varName == scanVariable2Name:
                self.__scanVariable2Combo.set_active(idx)
            idx += 1
        self.__scanVariable2Combo.handler_unblock(self.__scanVariable2ChangedHandlerID)
    
        if scanVariable2Name != "" and self.scan2D.baseGeomInstance != None:
            if scanVariable2Name in self.scan2D.baseGeomInstance.templateOverrides_getKeys():
                self.__scanVariable2DefaultEntry.set_text(str( self.scan2D.baseGeomInstance.templateOverrides_get(scanVariable2Name) ))
            else:
                self.__scanVariable2DefaultEntry.set_text(str( self.scan2D.getProject().geomCollection.paramDefaults_get(scanVariable2Name) ))
        else:
            self.__scanVariable2DefaultEntry.set_text(str("N/A"))
    
        self.__scanVariable2MinEntry.set_text(str( self.scan2D.scanParameter2_min ))
        self.__scanVariable2MaxEntry.set_text(str( self.scan2D.scanParameter2_max ))
        self.__scanVariable2NumEntry.set_text(str( self.scan2D.scanParameter2_num ))
    
        if self.scan2D.lockdown:
            self.__geomCombo.set_sensitive(False)
            self.__scanVariable1Combo.set_sensitive(False)
            self.__scanVariable2Combo.set_sensitive(False)
    
    def saveToScan(self):
        print "Scan2DFrame::saveToScan()"
        if self.scan2D.lockdown == False:
            #Set baseGeom and scanVar if neccessary
            geomComboText = self.__geomCombo.get_active_text()
            if geomComboText != None:
                self.scan2D.setBaseGeom(geomComboText)
            
            scanVar1ComboText = self.__scanVariable1Combo.get_active_text()
            if scanVar1ComboText == None:
                self.scan2D.scanParameter1_name = ""
            elif scanVar1ComboText != None:
                self.scan2D.scanParameter1_name = scanVar1ComboText
            scanVar2ComboText = self.__scanVariable2Combo.get_active_text()
            if scanVar2ComboText == " -- Disabled --" or scanVar2ComboText == None:
                self.scan2D.scanParameter2_name = ""
            elif scanVar2ComboText != None:
                self.scan2D.scanParameter2_name = scanVar2ComboText

        try:
            self.scan2D.scanParameter1_min = float(self.__scanVariable1MinEntry.get_text())
            self.scan2D.scanParameter1_max = float(self.__scanVariable1MaxEntry.get_text())
            self.scan2D.scanParameter1_num = int(self.__scanVariable1NumEntry.get_text())
        
            self.scan2D.scanParameter2_min = float(self.__scanVariable2MinEntry.get_text())
            self.scan2D.scanParameter2_max = float(self.__scanVariable2MaxEntry.get_text())
            self.scan2D.scanParameter2_num = int(self.__scanVariable2NumEntry.get_text())
            print "Saved min/max/num for scan parameters"
        except ValueError:
            print "Error in Scan2DFrame::saveToScan(): could not convert contents to number"
        
        self.scan2D.write()
    
    def event_button_checkScanRange(self, widget, data=None):
        self.saveToScan()
        self.updateDisplay() #In case invalid entries found by saveToScan, update the GUI to see the reset values
        try:
            (range1,range2) = self.scan2D.getScanRanges()
        except Scan2DException as e:
            mDia = gtk.MessageDialog(self.getBaseWindow(),
                                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                     gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                     "Error while generating the range:\n%s" % (e.args[0],) )
            mDia.run()
            mDia.destroy()
            return
        
        if range2 != None:
            mDia = gtk.MessageDialog(self.getBaseWindow(),
                                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                     gtk.MESSAGE_INFO, gtk.BUTTONS_OK,
                                     "Got scan ranges:\n %s: %s\n %s: %s\n Total number of points: %i" % \
                                     ( self.scan2D.scanParameter1_name, str(range1), self.scan2D.scanParameter2_name, str(range2), len(range1)*len(range2) ) )
            mDia.run()
            mDia.destroy()
        else:
            mDia = gtk.MessageDialog(self.getBaseWindow(),
                                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                     gtk.MESSAGE_INFO, gtk.BUTTONS_OK,
                                     "Got scan ranges:\n %s: %s\n (2nd variable disabled)\n Total number of points: %i" % \
                                     ( self.scan2D.scanParameter1_name, str(range1), len(range1) ) )
            mDia.run()
            mDia.destroy()
    
    def event_button_doScan(self,widget,data=None):
        self.saveToScan()
        self.updateDisplay()
        
        #Just as a test
        try:
            (range1,range2) = self.scan2D.getScanRanges()
        except Scan2DException as e:
            mDia = gtk.MessageDialog(self.getBaseWindow(),
                                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                     gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                     "Error while generating the range:\n%s" % (e.args[0],) )
            mDia.run()
            mDia.destroy()
            return
        
        self.scan2D.createScan()
        
        self.updateDisplay()
        self.frameManager.mainWindow.updateProjectExplorer()
    
    def event_button_plot(self,widget,data=None):
        self.saveToScan()
        self.updateDisplay()
        
        if self.scan2D.scanParameter1_name == "":
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
            (range1,range2) = self.scan2D.getScanRanges()
        except Scan2DException as e:
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
        if self.scan2D.baseGeomInstance != None:
            X2 = []
            Y2 = []
            
            #BaseGeomInstance
            if self.scan2D.scanParameter1_name in self.scan2D.baseGeomInstance.templateOverrides_getKeys():
                X2.append(self.scan2D.baseGeomInstance.templateOverrides_get(self.scan2D.scanParameter1_name))
            else:
                X2.append(self.scan2D.getProject().geomCollection.paramDefaults_get(self.scan2D.scanParameter1_name))
            
            if self.scan2D.scanParameter2_name == "":
                Y2.append(0.0)
            elif self.scan2D.scanParameter2_name in self.scan2D.baseGeomInstance.templateOverrides_getKeys():
                Y2.append(self.scan2D.baseGeomInstance.templateOverrides_get(self.scan2D.scanParameter2_name))
            else:
                Y2.append(self.scan2D.getProject().geomCollection.paramDefaults_get(self.scan2D.scanParameter2_name))
            
            #SlaveGeoms
            for geom in self.scan2D.slaveGeoms.values():
                X2.append(geom.templateOverrides_get(self.scan2D.scanParameter1_name))
                if self.scan2D.scanParameter2_name == "":
                    Y2.append(0.0)
                else:
                    Y2.append(geom.templateOverrides_get(self.scan2D.scanParameter2_name))
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
        print "Scan2DFrame::event_comboChanged_geom, data =", data
        self.saveToScan()
        self.frameManager.mainWindow.updateProjectExplorer()
        self.updateDisplay()
    
    def event_comboChanged_scanVar(self, widget, data):
        print "Scan2DFrame::event_comboChanged_scanVar, data =", data
        self.saveToScan()
        self.updateDisplay()
            
    def event_delete(self):
        return self.saveToScan()
    