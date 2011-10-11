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

from acdOpti.AcdOptiExceptions import AcdOptiException_metaAnalysis_anaFail 

from InfoFrameComponent import InfoFrameComponent

import matplotlib
matplotlib.use("GtkAgg")
import matplotlib.pyplot
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg, NavigationToolbar2GTKAgg


import numpy as np

import os

class MetaAnalysis(InfoFrameComponent):
    """
    Run a meta analysis and graph the results
    """
    
    anaInstance = None
    
    __plotVBox    = None
    __plotFigure  = None
    __plotAxis    = None
    __plotCanvas  = None
    __plotToolbar = None
    __hasPlotNow = False
    
    __targetLineBox = None
    __targetLineEntry = None
    
    __varSelectorTable = None
    __varSelectorXEntry = None
    __varSelectorYEntry = None
    
    __runAnaButton = None
    __exportButton = None
    __clearLockdownButton = None
    
    def __init__(self, frameManager, metaAnalysis):
        InfoFrameComponent.__init__(self, frameManager)
        
        self.anaInstance = metaAnalysis
        
        self.baseWidget = gtk.VBox()
        self.__plotVBox = gtk.VBox()
        self.baseWidget.pack_start(self.__plotVBox, expand=True, padding=5)
        
        self.baseWidget.pack_start(gtk.HSeparator(), expand=False, padding=10)

        self.__targetLineBox = gtk.HBox()
        self.baseWidget.pack_start(self.__targetLineBox,expand=False)
        
        self.__targetLineBox.pack_start(gtk.Label("Target horizontal line = "),expand=False, padding=5)
        self.__targetLineEntry = gtk.Entry()
        self.__targetLineBox.pack_start(self.__targetLineEntry, expand=True, padding=5)
        
        self.baseWidget.pack_start(gtk.HSeparator(), expand=False, padding=10)

        self.__varSelectorTable = gtk.Table(1,4,True)
        self.__varSelectorTable.attach(gtk.Label("X variable:"), 0,1, 0,1)
        self.__varSelectorXEntry = gtk.Entry()
        self.__varSelectorTable.attach(self.__varSelectorXEntry, 1,2, 0,1)
        self.__varSelectorTable.attach(gtk.Label("Y variable:"), 2,3, 0,1)
        self.__varSelectorYEntry = gtk.Entry()
        self.__varSelectorTable.attach(self.__varSelectorYEntry, 3,4, 0,1)
        self.baseWidget.pack_start(self.__varSelectorTable, expand=False, padding=5)
        
        #self.baseWidget.pack_start(gtk.Label("Meta-language syntax: {GEOM|MESH|ANA}.key([idx]).key([idx]) ..."), expand=False, padding=5)
        self.baseWidget.pack_start(gtk.Label("Meta-language syntax: {GEOM|MESH|ANA}.key.key([idx]) .... For ANA, field[1] is analysis name, field[2] is a name in exportResults"), expand=False, padding=5)
        self.baseWidget.pack_start(gtk.HSeparator(), expand=False, padding=10)
        
        self.__runAnaButton = gtk.Button("Run analysis")
        self.__runAnaButton.connect("clicked", self.event_button_runAna, None)
        self.baseWidget.pack_start(self.__runAnaButton, expand=False)
        
        self.__exportButton = gtk.Button("Export data")
        self.__exportButton.connect("clicked", self.event_button_export, None)
        self.baseWidget.pack_start(self.__exportButton, expand=False)
        
        self.__clearLockdownButton = gtk.Button("Clear lockdown")
        self.__clearLockdownButton.connect("clicked", self.event_button_clearLockdown, None)
        self.baseWidget.pack_start(self.__clearLockdownButton, expand=False)
        
        self.updateDisplay()
        self.baseWidget.show_all()

    def __createNewFigure(self):
        #Setup for plotting
        if self.__hasPlotNow:
            self.__plotVBox.remove(self.__plotToolbar)
            self.__plotVBox.remove(self.__plotCanvas)
            del self.__plotToolbar
            self.__plotCanvas.destroy()
            del self.__plotFigure
               
        self.__plotFigure = matplotlib.pyplot.figure()
        self.__plotAxis   = self.__plotFigure.add_subplot(1,1,1)
        self.__plotCanvas = FigureCanvasGTKAgg(self.__plotFigure)
        self.__plotCanvas.show()
        self.__plotVBox.pack_start(self.__plotCanvas, expand=True)
        self.__plotToolbar = NavigationToolbar2GTKAgg(self.__plotCanvas, window=self.getBaseWindow().get_parent_window())
        self.__plotVBox.pack_start(self.__plotToolbar, expand=False)
        self.__hasPlotNow = True

        #Plot the data
        self.__plotAxis.set_xlabel(self.anaInstance.xVariable)
        self.__plotAxis.set_ylabel(self.anaInstance.yVariable)
        matplotlib.pyplot.plot(self.anaInstance.xArray, self.anaInstance.yArray, "*")
        if self.anaInstance.targetValue != None:
            matplotlib.pyplot.axhline(self.anaInstance.targetValue, color="r", linestyle="--")
            
#        matplotlib.pyplot.plot(np.linspace(0,2*np.pi, 100), np.sin(np.linspace(0,2*np.pi, 100))/self.counter) #TEST

        
    def updateDisplay(self):
        print "MetaAnalysis::updateDisplay()"
        self.__createNewFigure()
        
        if self.anaInstance.targetValue != None:
            self.__targetLineEntry.set_text(str(self.anaInstance.targetValue))
        else:
            self.__targetLineEntry.set_text("")
        
        self.__varSelectorXEntry.set_text(self.anaInstance.xVariable)
        self.__varSelectorYEntry.set_text(self.anaInstance.yVariable)
    
        if self.anaInstance.lockdown:
            self.__targetLineEntry.set_sensitive(False)
            self.__varSelectorXEntry.set_sensitive(False)
            self.__varSelectorYEntry.set_sensitive(False)
            self.__runAnaButton.set_sensitive(False)
            self.__exportButton.set_sensitive(True)
            self.__clearLockdownButton.set_sensitive(True)
        else:
            self.__targetLineEntry.set_sensitive(True)
            self.__varSelectorXEntry.set_sensitive(True)
            self.__varSelectorYEntry.set_sensitive(True)
            self.__runAnaButton.set_sensitive(True)
            self.__exportButton.set_sensitive(False)
            self.__clearLockdownButton.set_sensitive(False)
    
    def saveToAna(self):
        print "MetaAnalysis::saveToAna()"
        
        try:
            self.anaInstance.targetValue = float(self.__targetLineEntry.get_text())
        except:
            self.anaInstance.targetValue = None
        
        self.anaInstance.xVariable = self.__varSelectorXEntry.get_text()
        self.anaInstance.yVariable = self.__varSelectorYEntry.get_text()
    
        self.anaInstance.write()
    
    def event_button_runAna(self, widget, data=None):
        print "MetaAnalysis::event_button_runAna()"
        self.saveToAna()
        try:
            self.anaInstance.runAnalysis()
        except AcdOptiException_metaAnalysis_anaFail as e:
            mDia = gtk.MessageDialog(self.getBaseWindow(),
                                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                     gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                     "Analysis failed with error message:\n" + e.args[0])
            mDia.run()
            mDia.destroy()
        self.updateDisplay()
    
    def event_button_export(self, widget, data=None):
        print "MetaAnalysis::event_button_export()"
        
        #Find the filename
        
        #call export in self.anaInstance 
    
    def event_button_clearLockdown(self, widget, data=None):
        print "MetaAnalysis::event_button_clearLockdown()"
        self.anaInstance.clearLockdown()
        self.anaInstance.write()
        self.updateDisplay()
        
    def event_delete(self):
        print "MetaAnalysis::event_delete()"
        self.saveToAna()
        return False