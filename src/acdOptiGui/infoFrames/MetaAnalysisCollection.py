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

class MetaAnalysisCollection(InfoFrameComponent):
    """
    Maintains the InfoFrame representing the top-level project
    """
    
    #Logic
    metaAnalysisCollection = None
    
    #Widgets
    __rerunButton = None

    def __init__(self, frameManager, metaAnalysisCollection):
        InfoFrameComponent.__init__(self, frameManager)
        
        self.metaAnalysisCollection = metaAnalysisCollection
        
        #Setup GUI
        self.baseWidget = gtk.VBox(False,5)
        self.baseWidget.pack_start(gtk.Label("Meta-analysis collection"), expand=True)

        self.__rerunButton = gtk.Button(label="Rerun all now-ran analyses")
        self.__rerunButton.connect("clicked", self.event_button_rerun, None)
        self.baseWidget.pack_start(self.__rerunButton,expand=False)
        
        self.baseWidget.show_all()
        
    def event_button_rerun(self,widget,event,data=None):
        self.metaAnalysisCollection.rerunEverything()
        