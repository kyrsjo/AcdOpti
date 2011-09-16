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

class InfoFrameComponent:
    """
    Base class for everything that writes to the infoFrame.
    These 
    """
    baseWidget = None #The widget pushed to the infoFrame (usually a container)
    frameManager = None

    #isActive = False

    def __init__(self, frameManager):
        self.frameManager = frameManager

    def getBaseWindow(self):
        """
        Finds the toplevel (windowmanager) window of self.baseWidget
        """
        #Dig down to find the main window
        parent = self.baseWidget
        while True:
            p2 =  parent.get_parent()
            if p2 != None:
                parent = p2
            else:
                break
        return parent

    def event_delete(self):
        """
        Cleanup method, override if necessary.
        Return True to abort deletion.
        """
        print "delete_event in InfoFrameComponent"
        return False
