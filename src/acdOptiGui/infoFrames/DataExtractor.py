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
    
    __filterButton = None
    __addPlotButton = None
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
        
        self.__filterButton = gtk.Button("_Filters...")
        self.__filterButton.connect("clicked", self.event_button_filter,None)
        self.baseWidget.pack_start(self.__filterButton, expand=False)
        
        self.__addPlotButton = gtk.Button("_Add plot...")
        self.__addPlotButton.connect("clicked", self.event_button_addPlot,None)
        self.baseWidget.pack_start(self.__addPlotButton, expand=False)
        
        self.__exportButton = gtk.Button("_Export...")
        self.__exportButton.connect("clicked", self.event_button_export,None)
        self.baseWidget.pack_start(self.__exportButton, expand=False)
        
        self.__lockdownRunButton = gtk.Button("_Run") #Updated in __updateGui()
        self.__lockdownRunButton.connect("clicked", self.event_button_lockdownRun, None)
        self.baseWidget.pack_start(self.__lockdownRunButton, expand=False)
    
        self.__updateGui()
        self.baseWidget.show_all()
    
    def __updateGui(self):
        if self.dataExtractor.lockdown:
            self.__lockdownRunButton.set_label("_Clear lockdown")
        else:
            self.__lockdownRunButton.set_label("_Run")
    
    def event_button_filter(self,widget,data=None):
        pass
    
    def event_button_addPlot(self,widget,data=None):
        pass
    
    def event_button_export(self,widget,data=None):
        pass
    
    def event_button_lockdownRun(self,widget,data=None):
        if self.dataExtractor.lockdown:
            pass
        else:
            pass
        
        self.__updateGui()
        