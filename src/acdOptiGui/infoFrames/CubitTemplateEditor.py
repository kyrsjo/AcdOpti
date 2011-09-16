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

class CubitTemplateEditor(InfoFrameComponent):
    """
    Editor for CubitTemplate files
    """

    templateFile = None #AcdOptiCubitTemplateFile instance
    readOnly = None

    __toolbar = None
    saveButton = None
    separator  = None
    quitButton = None

    scrolledWindow = None
    textView = None
    buff     = None

    def __init__(self, frameManager, templateFile, readOnly=False):
        InfoFrameComponent.__init__(self, frameManager)
        
        self.templateFile = templateFile
        self.readOnly = readOnly
         
        self.baseWidget = gtk.VBox(False,5)

        #Toolbar
        self.__toolbar = gtk.Toolbar()
        self.__toolbar.set_orientation(gtk.ORIENTATION_HORIZONTAL)
        self.__toolbar.set_style(gtk.TOOLBAR_BOTH)
        self.__toolbar.set_border_width(5)

        self.saveButton = gtk.ToolButton(gtk.STOCK_SAVE)
        self.saveButton.connect("clicked", self.event_toolbutton_save, None)
        self.__toolbar.insert(self.saveButton,-1)

        self.separator = gtk.SeparatorToolItem()
        self.separator.set_expand(True)
        self.__toolbar.insert(gtk.SeparatorToolItem(),-1)

        self.closeButton = gtk.ToolButton(gtk.STOCK_CLOSE)
        self.closeButton.connect("clicked", self.event_toolbutton_close, None)
        self.__toolbar.insert(self.closeButton,-1)

        self.baseWidget.pack_start(self.__toolbar, False)

        #Text editor
        self.scrolledWindow = gtk.ScrolledWindow()
        self.textView = gtk.TextView()
        if self.readOnly:
            self.textView.set_editable(False)
        self.scrolledWindow.add(self.textView)
        self.scrolledWindow.set_policy(\
            gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.baseWidget.pack_start(self.scrolledWindow)
        
        self.buff = self.textView.get_buffer()
        #Force a copy of the string
        self.buff.set_text(str(self.templateFile.template.template))
        monoTag = self.buff.create_tag(family="Monospace")
        self.buff.apply_tag(monoTag, \
                                self.buff.get_start_iter(),\
                                self.buff.get_end_iter())
        self.buff.connect("modified_changed", self.event_buff_modified, None)
        self.buff.set_modified(False)

        #Finalize
        self.baseWidget.show_all()
        
    def event_delete(self):
        print "event_delete in CubitTemplateEditor"
        return self.close()

    def event_toolbutton_save(self, widget, event, data=None):
        self.saveData()
    def saveData(self):
        theData = self.buff.get_text(self.buff.get_start_iter(),
                                     self.buff.get_end_iter())
        self.templateFile.update(theData)

        self.buff.set_modified(False)

    def event_toolbutton_close(self, widget, event, data=None):
        print "event_toolbutton_close"
        if not self.close():
            self.frameManager.pop()

    def close(self):
        """
        Close the the editor, asking if not saved.
        Returns False if ready to close,
        True if not saved and user selected cancel.
        """
        if self.buff.get_modified():
            #Not saved - ask first
            dia = gtk.Dialog("File modified", self.getBaseWindow(),
                             gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                             (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                              gtk.STOCK_NO, gtk.RESPONSE_NO,
                              gtk.STOCK_YES, gtk.RESPONSE_YES,))
            dia.set_default_response(gtk.RESPONSE_CANCEL)
            dia.vbox.pack_start(gtk.image_new_from_stock(
                         gtk.STOCK_DIALOG_QUESTION,
                         gtk.ICON_SIZE_DIALOG))
            dia.vbox.pack_start(gtk.Label("Save file before exit?"))
            dia.show_all()

            response = dia.run()
            print response

            if response == gtk.RESPONSE_YES:
                #Save and close
                self.saveData()
                dia.destroy()
                return False
            elif response == gtk.RESPONSE_NO:
                #Close without saving
                dia.destroy()
                return False
            else:
                #Do nothing / abort shutdown
                dia.destroy()
                return True
        else:
            #Already saved
            return False
            
    def event_buff_modified(self, widget, event, data=None):
        print "event_buff_modified", self.buff.get_modified()
        if self.buff.get_modified():
            self.saveButton.set_sensitive(True)
        else:
            self.saveButton.set_sensitive(False)
        
