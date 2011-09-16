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

#import exception

from InfoFrameExceptions import InfoFrameException_geometryCollection_dontDelete
from InfoFrameComponent import InfoFrameComponent
from CubitTemplateEditor import CubitTemplateEditor

from acdOpti.AcdOptiGeometryInstance import AcdOptiGeometryInstance #For checking with isinstance()

#TODO: Persistent ordering of keys

class GeometryCollection(InfoFrameComponent):
    """
    Shows information about what variables are defined
    for the geometry, and their default values.
    """

    geomCollection = None #AcdOptiGeometryCollection

    __tableWidget = None

    __topLabels = None
    __addButton = None    
    
    __labelCollection   = None
    __entryCollection   = None
    __delButtCollection = None
    __scrolledWindow    =  None

    __clearLockdownButton = None
    __editJournalButton = None

    def __init__(self,frameManager,geomCollection):
        InfoFrameComponent.__init__(self, frameManager)
        self.geomCollection = geomCollection

        #Create GUI
        self.__topLabels = []

        tlab = gtk.Label("Tag name")
        self.__topLabels.append(tlab)
        
        tlab = gtk.Label("Default value")
        self.__topLabels.append(tlab)

        tlab = gtk.Label("Delete tag")
        self.__topLabels.append(tlab)

        self.__addButton = gtk.Button(stock=gtk.STOCK_ADD)
        self.__addButton.connect("clicked", self.event_button_add, None)

        self.__clearLockdownButton = gtk.Button(label="Clear lockdown")
        self.__clearLockdownButton.connect("clicked", self.event_button_clearLockdown, None)

        self.__editJournalButton =  gtk.Button(label="Edit geometry template journal...") #Text changed by updateTable according to current lockdown setting
        self.__editJournalButton.connect("clicked", self.event_button_editJournal, None)

        self.updateTable()

        self.__scrolledWindow = gtk.ScrolledWindow()
        self.__scrolledWindow.set_policy(gtk.POLICY_NEVER,gtk.POLICY_AUTOMATIC)
        self.__scrolledWindow.add_with_viewport(self.__tableWidget)
        self.__scrolledWindow.set_shadow_type(gtk.SHADOW_NONE)

        self.baseWidget = gtk.VBox()
        self.baseWidget.pack_start(self.__scrolledWindow,      expand=True)
        self.baseWidget.pack_start(self.__clearLockdownButton, expand=False)
        self.baseWidget.pack_start(self.__editJournalButton,   expand=False)

        self.baseWidget.show_all()
        
    def updateTable(self):
        """
        Fills the tableWidget
        """
        numEntries = self.geomCollection.paramDefaults_len()
        lockdown   = self.geomCollection.lockdown

        #Initialize or clear tableWidget
        if not self.__tableWidget:
            self.__tableWidget=gtk.Table(numEntries+2, 3, False)
            self.__tableWidget.set_row_spacings(3)
            self.__tableWidget.set_col_spacings(3)
            
            self.__tableWidget.attach(self.__topLabels[0],
                                   0,1,0,1,
                                   xoptions=gtk.FILL,yoptions=gtk.FILL)
            self.__tableWidget.attach(self.__topLabels[1],
                                   1,2,0,1,
                                   xoptions=gtk.FILL|gtk.EXPAND,yoptions=gtk.FILL)
            self.__tableWidget.attach(self.__topLabels[2],
                                   2,3,0,1,
                                   xoptions=gtk.FILL,yoptions=gtk.FILL)
            self.__labelCollection = {}
            self.__entryCollection = {}
            self.__delButtCollection = {}

        else:
            for k in self.__labelCollection.keys():
                self.__tableWidget.remove(self.__labelCollection[k])
                self.__tableWidget.remove(self.__entryCollection[k])
                self.__tableWidget.remove(self.__delButtCollection[k])
            self.__labelCollection.clear()
            self.__entryCollection.clear()
            self.__delButtCollection.clear()
            self.__tableWidget.remove(self.__addButton)
            self.__tableWidget.resize(numEntries+2,3)

        #Create and attach the table entries
        for (k,i) in zip(self.geomCollection.paramDefaults_getKeys(),
                         xrange(numEntries)):
            
            self.__labelCollection[k]=lab=gtk.Label(k)
            self.__tableWidget.attach(lab,0,1,i+1,i+2, xoptions=gtk.FILL, yoptions=gtk.FILL)
            
            self.__entryCollection[k]=ent=gtk.Entry()
            ent.set_text(self.geomCollection.paramDefaults_get(k))
            self.__tableWidget.attach(ent,1,2,i+1,i+2, xoptions=gtk.FILL|gtk.EXPAND, yoptions=gtk.FILL)
            if lockdown:
                ent.set_sensitive(False)

            self.__delButtCollection[k]=but=gtk.Button(stock=gtk.STOCK_DELETE)
            but.connect("clicked", self.event_button_del, k)
            self.__tableWidget.attach(but,2,3,i+1,i+2, xoptions=gtk.FILL, yoptions=gtk.FILL)
            if lockdown:
                but.set_sensitive(False)

        self.__tableWidget.attach(self.__addButton,
                               0,3, numEntries+1,numEntries+2,
                               xoptions = gtk.FILL|gtk.EXPAND, yoptions=gtk.FILL)

        #Update fixed buttons to cope with lockdown
        if lockdown: 
            self.__addButton.set_sensitive(False)
            self.__clearLockdownButton.set_sensitive(True)
            self.__editJournalButton.set_label("View geometry template journal...")
        else:
            self.__addButton.set_sensitive(True)
            self.__clearLockdownButton.set_sensitive(False)
            self.__editJournalButton.set_label("Edit geometry template journal...")
        
        self.__tableWidget.show_all()

        self.frameManager.mainWindow.updateProjectExplorer()

    def checkData(self):
        """
        Checks that the data stored in the text boxes are valid,
        returns None if it is, a string with
        the first offending key found if it is not.

        Invalid data: Contains whitespace
        """
        for k in self.__entryCollection.keys():
            if " " in self.__entryCollection[k].get_text():
                return k
        return None
    def checkAndHighlight(self):
        """
        Checks that the data in the textboxes are valid.
        If it is not, it pops up an error message, highlights the offending field, and returns False.
        Else return True.
        """
        check = self.checkData()
        if check:
            mDia = gtk.MessageDialog(self.getBaseWindow(),
                                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                     gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                     "Key \"" + check + "\" contains whitespace or is reserved keyword, this is not allowed")
            mDia.run()
            mDia.destroy()
            
            self.__entryCollection[check].grab_focus()
            return False

        return True

    def saveData(self, skipKey=None, addKey=None):
        """
        Updates self.geomCollection.paramDefaults with
        the data currently written in the table.
        Use this method before clearing and updating the table
        with a new key.

        Skips key "skipKey", used if this key is to be deleted.
        Adds a new key addKey to the table.
        
        If trying to skip a key which is overridden by
        an GeometryInstance, raises error 
        
        """
        assert self.checkData() == None
        

        if skipKey:
            oops = self.geomCollection.mayDelete(skipKey)
            if oops:
                raise InfoFrameException_geometryCollection_dontDelete(oops)

        self.geomCollection.paramDefaults_clear()

        for k in self.__labelCollection.keys():
            if k == skipKey:
                continue
            #Store data from table in dict
            self.geomCollection.paramDefaults_insert(k, self.__entryCollection[k].get_text())

        if addKey:
            self.geomCollection.paramDefaults_insert(addKey, "")

    def event_button_del(self,widget, data):
        print "GeometryCollection::event_button_del(), data=", data
        assert data in self.geomCollection.paramDefaults_getKeys()
        try:
            self.saveData(skipKey=data)
            self.updateTable()
        except InfoFrameException_geometryCollection_dontDelete as E:
            #Data in use
            if isinstance(E.args[0],AcdOptiGeometryInstance):
                mDia = gtk.MessageDialog(self.getBaseWindow(),
                                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                         gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                         "Can't delete this tag, in use by geometry instance \"" +
                                         E.args[0].instname + "\"")
                mDia.run()
                mDia.destroy()    
            else:
                #Probably got a CubitFileTemplate
                raise NotImplementedError
            
    def event_button_add(self, widget, data=None):
        """
        Adds a new row to the table
        """
        print "GeometryCollection::event_button_add()"
        #Check that the data currently in the table is valid
        if not self.checkAndHighlight():
            return
            
        #Get the new key name
        name = ""
        while True:
            dia = gtk.Dialog("Please enter name of new key:", self.getBaseWindow(),
                             gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                             (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                              gtk.STOCK_OK, gtk.RESPONSE_OK))
            dia.set_default_response(gtk.RESPONSE_OK)
            nameBox = gtk.Entry()
            nameBox.set_text(name)
            nameBox.show()
            dia.vbox.pack_start(nameBox)
            dia.show_all()
    
            response = dia.run()
            name = nameBox.get_text()
    
            dia.destroy()
            
            if response == gtk.RESPONSE_OK:
                #Check for whitespace
                print "got: \"" + name + "\""
                if " " in name:
                    mDia = gtk.MessageDialog(self.getBaseWindow(),
                                             gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                             gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                             "Name cannot contain whitespace")
                    mDia.run()
                    mDia.destroy()
                    continue
                elif name in self.geomCollection.paramDefaults_getKeys():
                    mDia = gtk.MessageDialog(self.getBaseWindow(),
                                             gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                             gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                             "Name already in use")
                    mDia.run()
                    mDia.destroy()
                    continue
                else:
                    #OK, add the key & update
                    self.saveData(addKey=name)
                    self.updateTable()
                    return
            else:
                #Response cancel or close
                return

    def event_button_clearLockdown(self,widget,data=None):
        print "GeometryCollection::event_button_clearLockdown()"
        self.geomCollection.clearLockdown()
        self.updateTable()
    
    def event_button_editJournal(self, widget, data=None):
        print "GeometryCollection::event_button_editJournal()"
        editor = CubitTemplateEditor(self.frameManager, self.geomCollection.geomTemplateFile, self.geomCollection.lockdown)
        self.frameManager.push(editor)

    def event_delete(self):
        print "GeometryCollection::event_delete()"
        if self.geomCollection.lockdown:
            return False #If in lockdown everything has already been written
        if not self.checkAndHighlight():
            print "Check failed"
            return True
        self.saveData()
        self.geomCollection.write()
        return False
