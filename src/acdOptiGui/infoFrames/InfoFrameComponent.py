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
  
    @staticmethod
    def makePing():
        "Play a short sound (finished notification etc.)"
        try:
            from pygame import mixer
            mixer.init()
            mixer.Sound("/usr/share/sounds/gnome/default/alerts/drip.ogg").play()
        except ImportError:
            #If it didn't work, no sound for you".
            print "makePing(): No sound available :("
    
    
    
    def getTypeAndNameDialog_currentBase(self,types,diaTitle):
        self.getTypeAndNameDialog(types, diaTitle, self.getBaseWindow())
    
    @staticmethod
    def getTypeAndNameDialog(types,diaTitle,baseWindow,mustName=False):
        """
        Helper method for creating a dialog asking for a type and a name.
        Input:
         - types: List of strings describing the types
         - diaTitle: Title of dialog box
         - baseWindow: Base window for the dialog box
        Returns:
        (type, name, response)
         - type: One of the items in types
         - name: The name typed in by the user, or None if nothing entered 
         - response: Response code of the dialog (one of the gtk.RESPONSE_??? constants)
        """
        dia = gtk.Dialog(diaTitle, baseWindow,
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
        diaTreeViewCol = gtk.TreeViewColumn("Solver types", diaCellRender,text=0)
        diaTreeView.set_headers_visible(False)
        diaTreeView.append_column(diaTreeViewCol)
        #diaTreeView.set_headers_visible(True)
        dia.vbox.pack_start(diaTreeView, padding = 5)
        
        dia.vbox.pack_start(gtk.HSeparator(), padding=10)
        
        diaEntry = gtk.Entry()
        diaEntry.set_text("Name...")
        if mustName == False:
            diaCheck = gtk.CheckButton(label="Use default name")
            diaCheck.connect("toggled", lambda widget,data=None: diaEntry.set_sensitive(not widget.get_active()), None)
            diaCheck.set_active(True)
            dia.vbox.pack_start(diaCheck)
        dia.vbox.pack_start(diaEntry)
        
        dia.show_all()
        response = dia.run()
        
        #Get the answers
        (path,column) = diaTreeView.get_cursor()
        type = diaListModel[path][0] 
        name = None
        if mustName or not diaCheck.get_active():
            name = diaEntry.get_text() 
        
        #Delete the dialog
        dia.destroy()
        
        return (type, name, response)
