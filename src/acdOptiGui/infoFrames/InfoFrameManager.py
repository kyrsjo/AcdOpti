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

from InfoMessage import InfoMessage
from InfoFrameComponent import InfoFrameComponent

class InfoFrameManager:
    """
    Manages the infoFrame which is embedded in the main window.
    It works like a stack, allowing infoFrameComponents
    to be push()'ed and pop()'ed off it, always showing
    the topmost component.
    """

    mainWindow  = None #The MainWindow class
    container   = None #Container on which to add stuff
    
    frame       = None        
    childStack  = None

    def __init__(self, container, mainWindow):
        self.mainWindow = mainWindow
        
        self.container = container
        self.frame     = gtk.Frame()
        #self.container.pack_start(self.frame)
        self.container.add2(self.frame)
        
        self.childStack = []
    
    def writeMessage(self,message):
        """
        Convenience function for writing a text label
        with "message" in the midle of the frame
        """
        
        self.push(InfoMessage(self,message))
    
    def push(self,widget):
        """
        Push <widget> on top of the stack, and display it.
        """
        print "InfoFrameManager::push()"

        if len(self.childStack) > 0:
            self.frame.remove(self.childStack[-1].baseWidget)
        self.childStack.append(widget)
        self.frame.add(widget.baseWidget)
    
    def pop(self):
        """
        Removes and returns the currently displayed widget,
        instead displaying the one below it in the stack.

        If the stack was empty, raises an error.
        """
        print "InfoFrameManager::pop()"
        
        assert len(self.childStack) > 0
        
        top = self.childStack.pop()
        self.frame.remove(top.baseWidget)
        if len(self.childStack) > 0:
            self.frame.add(self.childStack[-1].baseWidget)
        
        return top

    def clear(self):
        """
        Pop's everything from the stack

        Called by the main gui manager when this is deleted,
        or when switching to another view.
        Returns False if all is well, True to abort the deletion.
        """
        print "InfoFrameManager::clear()"
        
        for i in xrange(len(self.childStack)):
            print "del, i =", i
            if self.childStack[-1].event_delete():
                return True
            self.pop()
        return False