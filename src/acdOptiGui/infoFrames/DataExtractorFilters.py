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

from InfoFrameComponent import InfoFrameComponent
from acdOpti.AcdOptiDataExtractor import AcdOptiDataExtractor
from acdOpti.AcdOptiDataExtractorFilter import *

class DataExtractorFilters(InfoFrameComponent):
    """
    Filter setup
    """
    
    lockdown = None
    
    dataExtractor = None
    
    __tableScroll = None
    __tableWidget = None
    
    __inputCollection = None
    __delCollection   = None
    
    __addButton   = None
    __closeButton = None
    
    
    def __init__(self, frameManager, dataExtractor,lockdown=False):
        InfoFrameComponent.__init__(self, frameManager)
        self.dataExtractor = dataExtractor
        assert isinstance(self.dataExtractor, AcdOptiDataExtractor)
        self.lockdown = lockdown
        
        self.baseWidget = gtk.VBox()
        
        self.baseWidget.pack_start(gtk.Label("Filters for '" + self.dataExtractor.instName + "'"), expand = False, padding=5)
    
        self.__updateTable()
        self.__tableScroll = gtk.ScrolledWindow()
        self.__tableScroll.set_policy(gtk.POLICY_NEVER,gtk.POLICY_AUTOMATIC)
        self.__tableScroll.add_with_viewport(self.__tableWidget)
        self.__tableScroll.set_shadow_type(gtk.SHADOW_NONE)
        self.baseWidget.pack_start(self.__tableScroll, expand=True, padding = 5)
        
        self.__addButton = gtk.Button(stock=gtk.STOCK_ADD)
        self.__addButton.connect("clicked", self.event_button_add, None)
        self.__addButton.set_sensitive(not self.lockdown)
        self.baseWidget.pack_start(self.__addButton,expand=False)
        
        self.__closeButton = gtk.Button("_Close filter view")
        self.__closeButton.connect("clicked", self.event_button_close, None)
        self.baseWidget.pack_start(self.__closeButton,expand=False)

        self.baseWidget.show_all()
    
    def __updateTable(self):
        print "DataExtractorFilter::__updateTable()"
        
        numFilters = len(self.dataExtractor.filters)
        numCols = 3
        if self.lockdown:
            numCols = 4
        
        if self.__tableWidget != None:
            children = self.__tableWidget.get_children()
            for child in children:
                self.__tableWidget.remove(child)
            self.__tableWidget.resize(numFilters+1, numCols)
        else:
            self.__tableWidget=gtk.Table(numFilters+1, numCols, False)
            self.__tableWidget.set_row_spacings(3)
            self.__tableWidget.set_col_spacings(3)
            
            
        self.__tableWidget.attach(gtk.Label("Filter type"),     0,1,0,1, xoptions=gtk.FILL,yoptions=gtk.FILL)
        self.__tableWidget.attach(gtk.Label("Filter settings"), 1,2,0,1, xoptions=gtk.FILL|gtk.EXPAND,yoptions=gtk.FILL)
        self.__tableWidget.attach(gtk.Label("Delete"),          2,3,0,1, xoptions=gtk.FILL,yoptions=gtk.FILL)
        if self.lockdown:
            self.__tableWidget.attach(gtk.Label("# Filtered"), 3,4,0,1, xoptions=gtk.FILL,yoptions=gtk.FILL)
        
        self.__inputCollection = []
        self.__delCollection = []
        
        for (f,idx) in zip(self.dataExtractor.filters,xrange(1,numFilters+1)):
            typ = f.filterType
            
            self.__tableWidget.attach(gtk.Label(typ),        0,1,idx,idx+1, xoptions=gtk.FILL, yoptions=gtk.FILL)
            
            if typ == "EqualsFilter":
                #self.__tableWidget.attach(gtk.Label("ENTRY"), 1,2,idx,idx+1, xoptions=gtk.FILL|gtk.EXPAND, yoptions=gtk.FILL)
                equalsWidgets = []
                box = gtk.HBox()
                self.__tableWidget.attach(box, 1,2,idx,idx+1, xoptions=gtk.FILL|gtk.EXPAND, yoptions=gtk.FILL)
                
                equalsWidgets.append(gtk.Entry())
                equalsWidgets[-1].set_text(f.settingsDict["key"])
                equalsWidgets[-1].set_sensitive(not self.lockdown)
                box.pack_start(equalsWidgets[-1],expand=True)
                                
                box.pack_start(gtk.Label("="),padding=10,expand=False)
                
                equalsWidgets.append(gtk.Entry())
                equalsWidgets[-1].set_text(f.settingsDict["val"])
                equalsWidgets[-1].set_sensitive(not self.lockdown)
                box.pack_start(equalsWidgets[-1],expand=True)
                
                self.__inputCollection.append(equalsWidgets)
            elif typ == "RangeFilter":
                #self.__tableWidget.attach(gtk.Label("ENTRY"), 1,2,idx,idx+1, xoptions=gtk.FILL|gtk.EXPAND, yoptions=gtk.FILL)
                wc = []
                box = gtk.HBox()
                self.__tableWidget.attach(box, 1,2,idx,idx+1, xoptions=gtk.FILL|gtk.EXPAND, yoptions=gtk.FILL)
                
                wc.append(gtk.Entry())
                wc[-1].set_text(f.settingsDict["key"])
                wc[-1].set_sensitive(not self.lockdown)
                box.pack_start(wc[-1],expand=True)
                
                box.pack_start(gtk.Label("in"), padding=10,expand=False)
                box.pack_start(gtk.Label("("), padding=10,expand=False)
                
                wc.append(gtk.Entry())
                wc[-1].set_text(f.settingsDict["a"])
                wc[-1].set_sensitive(not self.lockdown)
                box.pack_start(wc[-1],expand=True)
                
                box.pack_start(gtk.Label(","), padding=10,expand=False)
                
                wc.append(gtk.Entry())
                wc[-1].set_text(f.settingsDict["b"])
                wc[-1].set_sensitive(not self.lockdown)
                box.pack_start(wc[-1],expand=True)
                
                box.pack_start(gtk.Label(")"), padding=10,expand=False)
                
                self.__inputCollection.append(wc)
            else:
                raise KeyError("typ='" + str(typ) + "'")
            
            self.__delCollection.append(gtk.Button(stock=gtk.STOCK_DELETE))
            self.__delCollection[-1].connect("clicked", self.event_button_delete, idx-1)
            self.__delCollection[-1].set_sensitive(not self.lockdown)
            self.__tableWidget.attach(self.__delCollection[-1], 2,3,idx,idx+1, xoptions=gtk.FILL, yoptions=gtk.FILL)

            if self.lockdown:
                self.__tableWidget.attach(gtk.Label(str(f.numFiltered)), 3,4,idx,idx+1, xoptions=gtk.FILL, yoptions=gtk.FILL)

        self.__tableWidget.show_all()
    
    def __saveTableToFilters(self):
        if self.lockdown:
            return
        
        for (f,wc) in zip(self.dataExtractor.filters,self.__inputCollection):
            typ = f.filterType
            if typ == "EqualsFilter":
                f.settingsDict["key"] = wc[0].get_text()
                f.settingsDict["val"] = wc[1].get_text()
            elif typ == "RangeFilter":
                f.settingsDict["key"] = wc[0].get_text()
                f.settingsDict["a"] = wc[1].get_text()
                f.settingsDict["b"] = wc[2].get_text()
            else:
                raise KeyError("typ='" + str(typ) + "'")
        self.dataExtractor.write()
    
    def event_button_add(self,widget,data=None):
        types = ["EqualsFilter", "RangeFilter"]
        
        dia = gtk.Dialog("Which type to add?", self.getBaseWindow(),
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                          gtk.STOCK_OK, gtk.RESPONSE_OK))
        dia.set_default_response(gtk.RESPONSE_OK)

        #Setup the listModel        
        diaListModel = gtk.ListStore(str)
        for t in types:
            diaListModel.append([t,])
        
        diaTreeView = gtk.TreeView(diaListModel)
        diaCellRender = gtk.CellRendererText()
        diaTreeViewCol = gtk.TreeViewColumn("Filter types", diaCellRender,text=0)
        diaTreeView.set_headers_visible(False)
        diaTreeView.append_column(diaTreeViewCol)
        dia.vbox.pack_start(diaTreeView, padding = 5)
        
        dia.show_all()
        
        if dia.run() != gtk.RESPONSE_OK:
            dia.destroy()
            return
        
        (path,column) = diaTreeView.get_cursor()
        typ = diaListModel[path][0]

        dia.destroy()
        
        self.__saveTableToFilters()
        
        #Add the right type
        if typ == "EqualsFilter":
            self.dataExtractor.filters.append(EqualsFilter())
        elif typ == "RangeFilter":
            self.dataExtractor.filters.append(RangeFilter())
        
        self.__updateTable()
    
    def event_button_close(self,widget,data=None):
        self.__saveTableToFilters()
        self.frameManager.pop()
    
    def event_button_delete(self,widget,data=None):
        print "DataExtractorFilter::event_button_delete(), data='" + str(data) + "'"
        self.__saveTableToFilters()
        del self.dataExtractor.filters[data]
        self.dataExtractor.write()
        self.__updateTable()
        
    def event_delete(self):
        self.__saveTableToFilters()
        return False
    