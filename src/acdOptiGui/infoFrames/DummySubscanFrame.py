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
from acdOpti.parameterScan.DummySubscan import DummySubscan

class DummySubscanFrame(InfoFrameComponent):
    """
    Dummy subscan test widget
    """
    
    dummySubscan = None
    
    __nameBox = None
    __nameEntry = None
    __geomButton = None
    __scanButton = None
    
    def __init__(self, frameManager, dummySubscan):
        InfoFrameComponent.__init__(self, frameManager)
        self.dummySubscan = dummySubscan
        assert isinstance(self.dummySubscan, DummySubscan)
        
        self.baseWidget = gtk.VBox()
        
        self.__nameBox = gtk.HBox()
        self.__nameBox.pack_start(gtk.Label("Name:"), expand=False)
        self.__nameEntry = gtk.Entry()
        self.__nameBox.pack_start(self.__nameEntry, expand=True)
        self.baseWidget.pack_start(self.__nameBox, expand=False)
        
        self.__geomButton = gtk.Button("Add geometry")
        self.__geomButton.connect("clicked", self.event_button_geomButton,None)
        self.baseWidget.pack_start(self.__geomButton, expand=False)
        
        self.__scanButton = gtk.Button("Add scan")
        self.__scanButton.connect("clicked", self.event_button_scanButton,None)
        self.baseWidget.pack_start(self.__scanButton, expand=False)
        
        self.baseWidget.show_all()
    
    def event_button_geomButton(self, widget, data=None):
        self.dummySubscan.addGeom(self.__nameEntry.get_text())
        self.frameManager.mainWindow.updateProjectExplorer()
    
    def event_button_scanButton(self, widget, data=None):
        self.dummySubscan.addSubscan(self.__nameEntry.get_text())
        self.frameManager.mainWindow.updateProjectExplorer()
