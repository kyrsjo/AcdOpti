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

from InfoFrameComponent import InfoFrameComponent
from acdOpti.AcdOptiDataExtractor import AcdOptiDataExtractor
from acdOpti.AcdOptiDataExtractorPlot import *

class DataExtractorPlots(InfoFrameComponent):
    """
    Plots list
    """
    
    dataExtractor = None
    
    __tableScroll = None
    __tableWidget = None
    
    __addButton   = None
    __closeButton = None
    
    
    def __init__(self, frameManager, dataExtractor):
        InfoFrameComponent.__init__(self, frameManager)
        self.dataExtractor = dataExtractor
        assert isinstance(self.dataExtractor, AcdOptiDataExtractor)
        
        self.baseWidget = gtk.VBox()
        
        self.baseWidget.pack_start(gtk.Label("Plots for '" + self.dataExtractor.instName + "'"), expand = False, padding=5)
    
        self.__updateTable()
        self.__tableScroll = gtk.ScrolledWindow()
        self.__tableScroll.set_policy(gtk.POLICY_NEVER,gtk.POLICY_AUTOMATIC)
        self.__tableScroll.add_with_viewport(self.__tableWidget)
        self.__tableScroll.set_shadow_type(gtk.SHADOW_NONE)
        self.baseWidget.pack_start(self.__tableScroll, expand=True, padding = 10)
        
        self.__addButton = gtk.Button(stock=gtk.STOCK_ADD)
        self.__addButton.connect("clicked", self.event_button_add, None)
        self.baseWidget.pack_start(self.__addButton,expand=False)
        
        self.__closeButton = gtk.Button("_Close plots view")
        self.__closeButton.connect("clicked", self.event_button_close, None)
        self.baseWidget.pack_start(self.__closeButton,expand=False)

        self.baseWidget.show_all()
    
    def __updateTable(self):
        print "DataExtractorPlots::__updateTable()"
        
        numPlots = len(self.dataExtractor.plots)
        numCols = 4
        
        if self.__tableWidget != None:
            children = self.__tableWidget.get_children()
            for child in children:
                self.__tableWidget.remove(child)
            self.__tableWidget.resize(numPlots+2, numCols)
        else:
            self.__tableWidget=gtk.Table(numPlots+2, numCols, False)
            self.__tableWidget.set_row_spacings(3)
            self.__tableWidget.set_col_spacings(5)
            
            
        self.__tableWidget.attach(gtk.Label("Plot name"),       0,1,0,1, xoptions=gtk.FILL|gtk.EXPAND,yoptions=gtk.FILL)
        self.__tableWidget.attach(gtk.Label("Plot type"),       1,2,0,1, xoptions=gtk.FILL|gtk.EXPAND,yoptions=gtk.FILL)
        self.__tableWidget.attach(gtk.Label("Manipulate plot"), 2,3,0,1, xoptions=gtk.FILL,yoptions=gtk.FILL)
        self.__tableWidget.attach(gtk.Label("Delete"),          3,4,0,1, xoptions=gtk.FILL,yoptions=gtk.FILL)
        
        self.__tableWidget.attach(gtk.HSeparator(),0,4,1,2, xoptions=gtk.FILL,yoptions=gtk.FILL)
        
        for (f,idx) in zip(self.dataExtractor.plots,xrange(numPlots)):
            name = f.instName
            typ = f.plotType
            tidx = idx+2
            
            self.__tableWidget.attach(gtk.Label(name),        0,1,tidx,tidx+1, xoptions=gtk.FILL|gtk.EXPAND, yoptions=gtk.FILL)
            self.__tableWidget.attach(gtk.Label(typ),         1,2,tidx,tidx+1, xoptions=gtk.FILL|gtk.EXPAND, yoptions=gtk.FILL)

            manipButton = gtk.Button("Manipulate...")
            manipButton.connect("clicked", self.event_button_manipulate, f)
            self.__tableWidget.attach(manipButton, 2,3,tidx,tidx+1, xoptions=gtk.FILL, yoptions=gtk.FILL)
            
            delButton = gtk.Button("Delete")
            delButton.connect("clicked", self.event_button_delete, idx)
            self.__tableWidget.attach(delButton, 3,4,tidx,tidx+1,xoptions=gtk.FILL, yoptions=gtk.FILL)
                
        self.__tableWidget.show_all()
    
    def event_button_manipulate(self,widget,data):
        #data = pointer to plot object to manipulate
        if data.plotType == "DataExtractorPlot2D":
            self.frameManager.push(DataExtractorPlots_Plot2D(self.frameManager, data))
            pass
        
    def event_button_delete(self,widget,data):
        #data = element index in plots to delete
        del self.dataExtractor.plots[data]
        self.dataExtractor.write()
        self.__updateTable()
        
    
    def event_button_add(self,widget,data):
        
        (type, name, response) = self.getTypeAndNameDialog_currentBase(("DataExtractorPlot2D",), "New plotter")
        
        if response == gtk.RESPONSE_OK:
            if name == None:
                name = type
            self.dataExtractor.plots.append(AcdOptiDataExtractorPlot.getPlotClass(type, self.dataExtractor, name))
            self.dataExtractor.write()
            self.__updateTable()
            self.dataExtractor.write()
        
    def event_button_close(self,widget,data):
        #self.__saveTableToPlots()
        self.frameManager.pop()
        
class DataExtractorPlots_Plot2D(InfoFrameComponent):
    """
    2D plot
    """
    
    plotObject = None
    
    __varXentry = None
    __varYentry = None
    
    __plotButton = None
    
    __closeButton = None
    
    
    def __init__(self, frameManager, plotObject):
        InfoFrameComponent.__init__(self, frameManager)
        assert isinstance(plotObject, DataExtractorPlot2D) 
        self.plotObject = plotObject
        
        self.baseWidget = gtk.VBox()
        
        self.baseWidget.pack_start(gtk.Label("DataExtractorPlot2D, instName = " + self.plotObject.instName), padding=5, expand=False)
        
        varXbox = gtk.HBox()
        varXbox.pack_start(gtk.Label("X variable:"), padding=5,expand=False)
        self.__varXentry = gtk.Entry()
        self.__varXentry.set_text(self.plotObject.varX)
        varXbox.pack_start(self.__varXentry, padding=5, expand=True)
        self.baseWidget.pack_start(varXbox, padding=5, expand=False)
        
        varYbox = gtk.HBox()
        varYbox.pack_start(gtk.Label("Y variable:"), padding=5,expand=False)
        self.__varYentry = gtk.Entry()
        self.__varYentry.set_text(self.plotObject.varY)
        varYbox.pack_start(self.__varYentry, padding=5, expand=True)
        self.baseWidget.pack_start(varYbox, padding=5, expand=False)
        
        self.baseWidget.pack_start(gtk.Label("Available variables:\n (textbox just to enable copy/paste, nothing is saved)"), padding=5,expand=False)
        varString = ""
        for k in self.plotObject.dataExtractor.keyNames:
            varString += k + " "
        varString = varString[:-1]
        varEntry = gtk.Entry()
        varEntry.set_text(varString)
        self.baseWidget.pack_start(varEntry, padding=5, expand=True)
        
        self.__plotButton = gtk.Button("Show _plot!")
        if not self.plotObject.dataExtractor.lockdown:
            self.__plotButton.set_sensitive(False)
        self.__plotButton.connect("clicked", self.event_button_plot, None)
        self.baseWidget.pack_start(self.__plotButton, padding=5, expand=False)
        
        self.__closeButton = gtk.Button("_Close plot view")
        self.__closeButton.connect("clicked", self.event_button_close, None)
        self.baseWidget.pack_start(self.__closeButton,padding = 5, expand=False)

        self.baseWidget.show_all()
    
    def saveToPlot(self):
        x = self.__varXentry.get_text().strip()
        y = self.__varYentry.get_text().strip()
        if " " in x or " " in y:
            mDia = gtk.MessageDialog(self.getBaseWindow(),
                                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                     gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                     "Space in X or Y variable, not saving to plot." )
            mDia.run()
            mDia.destroy()
            return
        self.plotObject.varX = x
        self.plotObject.varY = y
        self.plotObject.updateSettingsDict()
        self.plotObject.dataExtractor.write()
    
    def event_button_plot(self, widget, data):
        self.saveToPlot()
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print "Could not import matplotlib.pyplot, aborting plot. You should still be able to doExport()!"
            return
        (X,Y) = self.plotObject.getData()
        plt.plot(X,Y, '+')
        plt.xlabel(self.plotObject.varX)
        plt.ylabel(self.plotObject.varY)
        
        xRange = abs(max(X)-min(X))
        yRange = abs(max(Y)-min(Y))
        plt.axis([min(X)-0.1*xRange, max(X)+0.1*xRange, min(Y)-0.1*yRange, max(Y)+0.1*yRange])
        
        plt.show()
        
        gtk.main()
    
    def event_button_close(self,widget,data):
        self.saveToPlot()
        self.frameManager.pop()