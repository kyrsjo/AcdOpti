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
from DataExtractorFilters import DataExtractorFilters
from DataExtractorPlots import DataExtractorPlots

from acdOpti.AcdOptiDataExtractor import AcdOptiDataExtractor

class DataExtractor(InfoFrameComponent):
    """
    Allows the user to setup, run, and postprocess a data extractor
    """
    
    dataExtractor = None
    
    __dataScroll  = None
    __dataView    = None
    __dataModel   = None
    __dataCols    = None
    __dataRenders = None
    
    __extractFnameEntry = None
    __keepKeyEntry      = None
    
    __filterButton = None
    __plotButton = None
    __exportButton = None
    __lockdownRunButton = None
    
    
    def __init__(self, frameManager, dataExtractor):
        InfoFrameComponent.__init__(self, frameManager)
        self.dataExtractor = dataExtractor
        assert isinstance(self.dataExtractor, AcdOptiDataExtractor)
        
        self.baseWidget = gtk.VBox()
        
        self.baseWidget.pack_start(gtk.Label("Data extractor, name = '" + self.dataExtractor.instName + "'"), expand=False, padding=5)
        
        self.__dataScroll = gtk.ScrolledWindow()
        self.__dataScroll.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.baseWidget.pack_start(self.__dataScroll,expand=True, padding=5)
        
        fnameEntryBox = gtk.HBox()
        fnameEntryBox.pack_start(gtk.Label("Export to filename:"), padding=5,expand=False)
        self.__extractFnameEntry = gtk.Entry()
        fnameEntryBox.pack_start(self.__extractFnameEntry, padding=5, expand=True)
        self.baseWidget.pack_start(fnameEntryBox,expand=False)
        
        keepKeyEntryBox = gtk.HBox()
        keepKeyEntryBox.pack_start(gtk.Label("Only keep key(s):"), padding=5, expand=False)
        self.__keepKeyEntry = gtk.Entry()
        keepKeyEntryBox.pack_start(self.__keepKeyEntry, padding = 5, expand=True)
        self.baseWidget.pack_start(keepKeyEntryBox,expand=False)
        
        self.__filterButton = gtk.Button("_Filters...")
        self.__filterButton.connect("clicked", self.event_button_filter,None)
        self.baseWidget.pack_start(self.__filterButton, expand=False)
        
        self.__plotButton = gtk.Button("_Plots...")
        self.__plotButton.connect("clicked", self.event_button_plot,None)
        self.baseWidget.pack_start(self.__plotButton, expand=False)
        
        self.__exportButton = gtk.Button("E_xport...")
        self.__exportButton.connect("clicked", self.event_button_export,None)
        self.baseWidget.pack_start(self.__exportButton, expand=False)
        
        self.__lockdownRunButton = gtk.Button("_Run") #Updated in __updateGui()
        self.__lockdownRunButton.connect("clicked", self.event_button_lockdownRun, None)
        self.baseWidget.pack_start(self.__lockdownRunButton, expand=False)
    
        self.__updateGui()
        self.baseWidget.show_all()
    
    def __updateGui(self):
        
        self.__extractFnameEntry.set_text(self.dataExtractor.extractFname)

        keepKeyString = ""
        for k in self.dataExtractor.keepKeys:
            keepKeyString += k + ", "
        keepKeyString = keepKeyString[:-2]
        self.__keepKeyEntry.set_text(keepKeyString)

        if self.dataExtractor.lockdown:
            self.__keepKeyEntry.set_sensitive(False)
            #self.__filterButton.set_sensitive(False)
            self.__exportButton.set_sensitive(True)
            self.__lockdownRunButton.set_label("_Clear lockdown")
            
            #Create the data view
            numCols = len(self.dataExtractor.keyNames)
            assert numCols > 0
            #self.__dataModel = eval("gtk.ListStore(" + "str,"*(numCols-1) + "str)", globals(), locals())
            self.__dataModel = gtk.ListStore(*[str]*numCols)
            self.__dataView = gtk.TreeView(self.__dataModel)
            
            self.__dataRenders = []
            self.__dataCols = []
            
            for (colName,idx) in zip(self.dataExtractor.keyNames,xrange(numCols)):
                self.__dataRenders.append(gtk.CellRendererText())
                self.__dataCols.append(gtk.TreeViewColumn(colName,self.__dataRenders[-1],text=idx))
                self.__dataView.append_column(self.__dataCols[-1])
            
            self.__dataScroll.add(self.__dataView)
            self.__dataView.show()
            
            #Populate the data view
            for row in self.dataExtractor.dataExtracted:
                rl = []
                for colName in self.dataExtractor.keyNames:
                    try:
                        rl.append(str(row[colName]))
                    except KeyError:
                        rl.append("")
                self.__dataModel.append(rl)
            
        else:
            #not lockdown
            self.__keepKeyEntry.set_sensitive(True)
            
            self.__filterButton.set_sensitive(True)
            self.__exportButton.set_sensitive(False)
            self.__lockdownRunButton.set_label("_Run")
            
            #Kill the data view
            if self.__dataView != None: #Empty on first run
                self.__dataScroll.remove(self.__dataView)
                self.__dataView    = None
                self.__dataModel   = None
                self.__dataCols    = None
                self.__dataRenders = None
        
        self.frameManager.mainWindow.updateProjectExplorer()
    
    def saveToDataExtractor(self):
        "Save current GUI content to DataExtractor"

        self.dataExtractor.extractFname = self.__extractFnameEntry.get_text()

        if not self.dataExtractor.lockdown:
            keepKeyString = self.__keepKeyEntry.get_text()
            keepKeyString = keepKeyString.split(",")
            del self.dataExtractor.keepKeys[:] #clear it!
            for k in keepKeyString:
                k2 = k.strip()
                if " " in k2:
                    print "keepKeyString element contained space, skipping '" + k2 + "'"
                    continue
                elif k2 == "":
                    print "keepKeyString element is empty string, skipping."
                    continue
                self.dataExtractor.keepKeys.append(k2)
                    
        self.dataExtractor.write()
    
    def event_button_filter(self,widget,data=None):
        self.frameManager.push(DataExtractorFilters(self.frameManager, self.dataExtractor,self.dataExtractor.lockdown))
    
    def event_button_plot(self,widget,data=None):
        #print "DataExtractor::event_button_plot()"
        self.frameManager.push(DataExtractorPlots(self.frameManager,self.dataExtractor))
    
    def event_button_export(self,widget,data=None):
        self.saveToDataExtractor()
        #self.dataExtractor.export("/home/kyrre/PhD/OptiData/cellData.csv", ["GEOM.idw", "GEOM.eow", "ANA.RFpost_local.maxFieldsOnSurface[0].surf[0].mode[0].Hmax_norm[0]"])
        #self.dataExtractor.export("/home/kyrre/PhD/OptiData/cellData.csv")
        self.dataExtractor.export()
    
    def event_button_lockdownRun(self,widget,data=None):
        self.saveToDataExtractor()
        
        if self.dataExtractor.lockdown:
            self.dataExtractor.clearLockdown()
        else:
            self.dataExtractor.runExtractor()
        
        self.__updateGui()
    
    def event_delete(self):
        return self.saveToDataExtractor()
    