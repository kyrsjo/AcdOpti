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


import pygtk #@UnresolvedImport
pygtk.require('2.0')
import gtk #@UnresolvedImport

from acdOpti.AcdOptiProject import AcdOptiProject
from acdOpti.AcdOptiGeometryCollection import AcdOptiGeometryCollection
from acdOpti.AcdOptiGeometryInstance import AcdOptiGeometryInstance
from acdOpti.AcdOptiMeshInstance import AcdOptiMeshInstance
from acdOpti.AcdOptiRunConfig import AcdOptiRunConfig
from acdOpti.analysis.AnalysisInterface import AnalysisInterface
from acdOpti.AcdOptiMeshTemplate import AcdOptiMeshTemplate
from acdOpti.AcdOptiMeshTemplateCollection import AcdOptiMeshTemplateCollection
from acdOpti.AcdOptiScanCollection import AcdOptiScanCollection
from acdOpti.AcdOptiScan import AcdOptiScan
from acdOpti.AcdOptiMetaAnalysisCollection import AcdOptiMetaAnalysisCollection
from acdOpti.AcdOptiMetaAnalysis import AcdOptiMetaAnalysis
from acdOpti.AcdOptiDataExtractorCollection import AcdOptiDataExtractorCollection
from acdOpti.AcdOptiDataExtractor import AcdOptiDataExtractor

from acdOpti.AcdOptiExceptions import *
from AcdOptiGuiExceptions import *
import exceptions, errno

from infoFrames.InfoFrameManager import InfoFrameManager
from infoFrames.ProjectInfo import ProjectInfo
from infoFrames.GeometryCollection import GeometryCollection
from infoFrames.GeometryInstance import GeometryInstance
from infoFrames.MeshInstance import MeshInstance
from infoFrames.RunConfig import RunConfig
from infoFrames.MeshTemplate import MeshTemplate
from infoFrames.AnalysisExportedResults import AnalysisExportedResults
from infoFrames.Scan import Scan
from infoFrames.MetaAnalysis import MetaAnalysis
from infoFrames.MetaAnalysisCollection import MetaAnalysisCollection
from infoFrames.DataExtractor import DataExtractor

import os

acdOptiGuiPath = os.path.split(__file__)[0] #"/home/kyrre/PhD/optimizer/code/acdOptiGui"
iconSize = "24x24"

class MainWindow():
    """
    Draws and handles events for the main window
    """
    
    #Fields: GUI components
    window            = None
    __VBox1           = None
    __HBox2           = None
    __infoFrame       = None
    
    __toolbar                 = None
    __newButton               = None
    __openButton              = None
    __geomInstanceNewButton   = None
    __meshTemplateNewButton   = None
    __scanNewButton           = None
    __metaAnalysisNewButton   = None
    __dataExtractorButton     = None

    __scrolledWindow  = None
    __treeModel       = None
    __treeView        = None
    __treeViewColumn  = None
    __cellRender      = None
    __cellRenderIcon  = None

    __meshIcon  = None
    __geomIcon  = None
    __graphIcon = None

    #Fields: Logic
    activeProject = None


    #Methods
    def __init__(self):
        #Setup the main window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("AcdOpti GUI")
        self.window.set_border_width(5)
        self.window.set_default_size(800,600)
        self.window.connect("delete_event", self.event_delete)
        
        #Top level VBox
        self.__VBox1 = gtk.VBox(False, 5)
        self.window.add(self.__VBox1)

        #Toolbar
        self.__toolbar = gtk.Toolbar()
        self.__toolbar.set_orientation(gtk.ORIENTATION_HORIZONTAL)
        self.__toolbar.set_style(gtk.TOOLBAR_BOTH)
        self.__toolbar.set_border_width(5)

        self.__newButton = gtk.ToolButton(gtk.STOCK_NEW)
        self.__newButton.connect("clicked", self.event_toolbutton_new, None)
        self.__toolbar.insert(self.__newButton,-1)

        self.__openButton = gtk.ToolButton(gtk.STOCK_OPEN)
        self.__openButton.connect("clicked", self.event_toolbutton_open, None)
        self.__toolbar.insert(self.__openButton,-1)

        self.__toolbar.insert(gtk.SeparatorToolItem(),-1)
        
        self.__geomInstanceNewButton = gtk.ToolButton(icon_widget=gtk.image_new_from_file(\
                os.path.join(acdOptiGuiPath, "pix", iconSize, "new-geom.png")), label="Add geometry instance")
        self.__geomInstanceNewButton.connect("clicked", self.event_toolbutton_geomInstanceNewButton, None)
        self.__geomInstanceNewButton.set_sensitive(False)
        self.__toolbar.insert(self.__geomInstanceNewButton, -1)

        self.__meshTemplateNewButton = gtk.ToolButton(icon_widget=gtk.image_new_from_file(\
                os.path.join(acdOptiGuiPath, "pix", iconSize, "new-mesh.png")), label="Add mesh template")
        self.__meshTemplateNewButton.connect("clicked", self.event_toolbutton_meshTemplateNewButton, None)
        self.__meshTemplateNewButton.set_sensitive(False)
        self.__toolbar.insert(self.__meshTemplateNewButton, -1)

        self.__scanNewButton = gtk.ToolButton(label="Add parameter scan")
        self.__scanNewButton.set_stock_id(gtk.STOCK_EXECUTE)
        self.__scanNewButton.connect("clicked", self.event_toolbutton_scanNewButton, None)
        self.__scanNewButton.set_sensitive(False)
        self.__toolbar.insert(self.__scanNewButton, -1)

        self.__metaAnalysisNewButton = gtk.ToolButton(icon_widget=gtk.image_new_from_file(\
                os.path.join(acdOptiGuiPath, "pix", "32x32", "chart_curve_add.png")), label="Add meta-analysis")
        self.__metaAnalysisNewButton.connect("clicked", self.event_toolbutton_metaAnalysisNewButton, None)
        self.__metaAnalysisNewButton.set_sensitive(False)
        self.__toolbar.insert(self.__metaAnalysisNewButton, -1)

        self.__dataExtractorButton = gtk.ToolButton(icon_widget=gtk.image_new_from_file(\
                os.path.join(acdOptiGuiPath,"pix", "32x32", "system-search.png")), label="Add data extractor")
        #self.__dataExtractorButton = gtk.ToolButton(label="Add data extractor")
        #self.__dataExtractorButton.set_stock_id(gtk.STOCK_CONVERT)
        self.__dataExtractorButton.connect("clicked", self.event_toolbutton_dataExtractor, None)
        self.__dataExtractorButton.set_sensitive(False)
        self.__toolbar.insert(self.__dataExtractorButton, -1)

        self.__VBox1.pack_start(self.__toolbar, False)

        #Sidebar/maindisplay HBox
        #self.__HBox2 = gtk.HBox(False, 5)
        self.__HBox2 = gtk.HPaned()
        self.__VBox1.pack_start(self.__HBox2)
        
        #Tree view in left part of screen
        self.__meshIcon       = gtk.gdk.pixbuf_new_from_file(os.path.join(acdOptiGuiPath, "pix", "24x24", "mesh.png"))
        self.__geomIcon       = gtk.gdk.pixbuf_new_from_file(os.path.join(acdOptiGuiPath, "pix", "24x24", "geom.png"))
        self.__graphIcon      = gtk.gdk.pixbuf_new_from_file(os.path.join(acdOptiGuiPath, "pix", "16x16", "chart_curve.png"))
        self.__deIcon         = gtk.gdk.pixbuf_new_from_file(os.path.join(acdOptiGuiPath, "pix", "16x16", "system-search.png"))
        
        # tree store stores object name, icon, background color, and the object itself
        self.__treeModel      = gtk.TreeStore(str, gtk.gdk.Pixbuf, str, object)
        self.__treeView       = gtk.TreeView(self.__treeModel)
        self.__treeViewColumn = gtk.TreeViewColumn('Project explorer')
        self.__cellRender     = gtk.CellRendererText()
        #self.__cellRender.props.scale = 0.7
        self.__cellRenderIcon = gtk.CellRendererPixbuf()
        
        self.__treeModel.set_sort_column_id(0, gtk.SORT_ASCENDING)

        self.__treeView.append_column(self.__treeViewColumn)
        self.__treeViewColumn.pack_start(self.__cellRenderIcon)
        self.__treeViewColumn.add_attribute(self.__cellRenderIcon, 'pixbuf', 1)
        self.__treeViewColumn.pack_start(self.__cellRender, True)
        self.__treeViewColumn.add_attribute(self.__cellRender, 'text', 0)
        self.__treeViewColumn.add_attribute(self.__cellRender, 'cell-background', 2)

        self.__treeView.connect("row-activated", self.event_treeView_rowActivated, None)

        self.__scrolledWindow = gtk.ScrolledWindow()
        self.__scrolledWindow.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.__scrolledWindow.add_with_viewport(self.__treeView)
        #self.__HBox2.pack_start(self.__scrolledWindow, False)
        self.__scrolledWindow.set_size_request(300,-1)
        self.__HBox2.add1(self.__scrolledWindow)
        
        #self.__treeModel.append(None, ["Load a project to start",])
        
        #Frame on which to display other info
        #self.__infoFrameFrame = gtk.Frame()
        #self.__HBox2.add2(self.__infoFrameFrame)
        self.__infoFrame = InfoFrameManager(self.__HBox2, self)
        self.__infoFrame.writeMessage("Load a project to start")

        self.window.show_all()

        #Lazy me...
        #self.loadProject("../pillbox")
    #END __init__()

    def event_delete(self, widget, event, data=None):
        print "MainWindow::event_delete()"
        
        #Ask the infoFrameManager managed widgets to save
        if not self.__infoFrame.clear():
            gtk.main_quit()
            return False
        else:
            return True

    def event_toolbutton_new(self, widget, event, data=None):
        if self.activeProject != None:
            md = gtk.MessageDialog(self.window, 
                                   gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_WARNING,
                                   gtk.BUTTONS_CLOSE, "A project is already loaded")
            md.run()
            md.destroy()
            return

        chooser = gtk.FileChooserDialog(title="Select project folder",
                                        parent=self.window,
                                        action=gtk.FILE_CHOOSER_ACTION_CREATE_FOLDER,
                                        buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        chooser.set_default_response(gtk.RESPONSE_OK)
        response = chooser.run()
        
        if response == gtk.RESPONSE_OK:
            fname = chooser.get_filename()
            print "Got fname=" + fname, os.path.isdir(fname)
            chooser.destroy()

            os.rmdir(fname) #Chooser does a mkdir(), but only if the dir does not exist.
                            # This is not wanted, as the optiProject also does this.

            try:
                AcdOptiProject.createNew(fname)
            except exceptions.OSError as e:
                if e.errno == errno.EEXIST:
                    md = gtk.MessageDialog(self.window, 
                                           gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
                                           gtk.BUTTONS_CLOSE, "A file or folder with this name already exists here.")
                    md.run()
                    md.destroy()
                    return
                else:
                    raise
        elif response == gtk.RESPONSE_CANCEL or response == gtk.RESPONSE_DELETE_EVENT:
            chooser.destroy() 
            return
        else:
            print response
            assert False, "WTF?!"
            exit(1)
        
        self.loadProject(fname)
    # END event_toolbutton_new()

    def event_toolbutton_open(self, widget, event, data=None):
        if self.activeProject != None:
            md = gtk.MessageDialog(self.window, 
                                   gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_WARNING,
                                   gtk.BUTTONS_CLOSE, "A project is already loaded")
            md.run()
            md.destroy()
            return

        chooser = gtk.FileChooserDialog(title="Select project folder",
                                        parent=self.window,
                                        action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                        buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        chooser.set_default_response(gtk.RESPONSE_OK)
        response = chooser.run()
        
        if response == gtk.RESPONSE_OK:
            fname = chooser.get_filename()
            print "Got fname=" + fname
            chooser.destroy()
        elif response == gtk.RESPONSE_CANCEL or response == gtk.RESPONSE_DELETE_EVENT:
            chooser.destroy() 
            return
        else:
            print response
            assert False, "WTF?!"
            exit(1)
        
        self.loadProject(fname)
    # END event_toolbutton_open()

    def event_toolbutton_geomInstanceNewButton(self, widget, event, data=None):
        print "MainWindow::event_toolbutton_geomInstanceNewButton()"
        
        name = ""

        while True:
            dia = gtk.Dialog("Please enter name of new geometry instance:", self.window,
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
                if " " in name:
                    mDia = gtk.MessageDialog(self.window,
                                             gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                             gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                             "Name cannot contain whitespace")
                    mDia.run()
                    mDia.destroy()
                #OK, try to make the folder..
                else:
                    try:
                        self.activeProject.geomCollection.addGeomInstance(name)
                        self.updateProjectExplorer()
                        #self.addGeom(name)
                        break #Done!
                    except AcdOptiException_geomInstance_createFail as e:
                        #Nope, try again

                        print "Exception args: " + str(e.args)
                        mDia = gtk.MessageDialog(self.window,
                                                 gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                                 gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                                 "Name already in use")
                        mDia.run()
                        mDia.destroy()
                        continue;
            #Response cancel or close
            else:
                break

    def event_toolbutton_meshTemplateNewButton(self, widget, event, data=None):
        print "MainWindow::event_toolbutton_meshTemplateNewButton()"
        
        name = ""

        while True:
            dia = gtk.Dialog("Please enter name of new mesh template:", self.window,
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
                    mDia = gtk.MessageDialog(self.window,
                                             gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                             gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                             "Name cannot contain whitespace")
                    mDia.run()
                    mDia.destroy()
                #OK, try to make the folder..
                else:
                    try:
                        self.addMesh(name)
                        break #Done!
                    except AcdOptiGuiException_guiMain_nameTaken:
                        #Nope, try again
                        print "got: \"" + name + "\""
                        mDia = gtk.MessageDialog(self.window,
                                                 gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                                 gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                                 "Name already in use")
                        mDia.run()
                        mDia.destroy()
                        continue;
            #Response cancel or close
            else:
                break
    def event_toolbutton_scanNewButton(self, widget,data=None):
        print "MainWindow::event_toolbutton_scanNewButton()"

        name = ""
        while True:
            dia = gtk.Dialog("Please enter name of new parameter scan:", self.window,
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
                    mDia = gtk.MessageDialog(self.window,
                                             gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                             gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                             "Name cannot contain whitespace")
                    mDia.run()
                    mDia.destroy()
                #OK, try to make the folder..
                else:
                    try:
                        self.activeProject.scanCollection.add(name)
                        self.updateProjectExplorer()
                        break #Done!
                    except AcdOptiException_scan_createFail:
                        #Nope, try again
                        print "got: \"" + name + "\""
                        mDia = gtk.MessageDialog(self.window,
                                                 gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                                 gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                                 "Name already in use")
                        mDia.run()
                        mDia.destroy()
                        continue;
            #Response cancel or close
            else:
                break
    def event_toolbutton_metaAnalysisNewButton(self, widget,data=None):
        print "MainWindow::event_toolbutton_metaAnalysisNewButton()"
        
        name = ""
        while True:
            dia = gtk.Dialog("Please enter name of new meta-analysis :", self.window,
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
                    mDia = gtk.MessageDialog(self.window,
                                             gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                             gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                             "Name cannot contain whitespace")
                    mDia.run()
                    mDia.destroy()
                #OK, try to make the folder..
                else:
                    try:
                        self.activeProject.metaAnalysisCollection.add(name)
                        self.updateProjectExplorer()
                        break #Done!
                    except AcdOptiException_metaAnalysis_createFail:
                        #Nope, try again
                        print "got: \"" + name + "\""
                        mDia = gtk.MessageDialog(self.window,
                                                 gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                                 gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                                 "Name already in use")
                        mDia.run()
                        mDia.destroy()
                        continue;
            #Response cancel or close
            else:
                break
    
    def event_toolbutton_dataExtractor(self, widget, data=None):
        print "event_toolbutton_dataExtractor()"
        
        name = ""
        while True:
            dia = gtk.Dialog("Please enter name of new data extractor :", self.window,
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
                    mDia = gtk.MessageDialog(self.window,
                                             gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                             gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                             "Name cannot contain whitespace")
                    mDia.run()
                    mDia.destroy()
                #OK, try to make the folder..
                else:
                    try:
                        self.activeProject.dataExtractorCollection.add(name)
                        self.updateProjectExplorer()
                        break #Done!
                    except AcdOptiException_dataExtractor_createFail:
                        #Nope, try again
                        print "got: \"" + name + "\""
                        mDia = gtk.MessageDialog(self.window,
                                                 gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                                 gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                                 "Name already in use")
                        mDia.run()
                        mDia.destroy()
                        continue;
            #Response cancel or close
            else:
                break
        
        
    def event_treeView_rowActivated(self,widget,path,column,data=None):
        print "MainWindow::event_treeView_rowActivated(), path =", path
        
        #Try to clear the __infoFrame
        if self.__infoFrame.clear():
            #Returned True - some widget was not ready.
            return
        
        #Get the row
        row = self.__treeModel[path]
        if isinstance(row[-1], AcdOptiProject):
            print "MainWindow::event_treeView_rowActivated() : project"
            self.__infoFrame.push(ProjectInfo(self.__infoFrame, self.activeProject))
        elif isinstance(row[-1], AcdOptiGeometryCollection):
            print "MainWindow::event_treeView_rowActivated() : GeometryCollection"
            self.__infoFrame.push(GeometryCollection(self.__infoFrame,self.activeProject.geomCollection))
        elif isinstance(row[-1], AcdOptiGeometryInstance):
            print "MainWindow::event_treeView_rowActivated() : geom instance, name='" + row[0] + "'"
            self.__infoFrame.push(GeometryInstance(self.__infoFrame, row[-1]))
        elif isinstance(row[-1], AcdOptiMeshInstance):
            print "MainWindow::event_treeView_rowActivated() : mesh instance, name='" + row[0] + "'"
            self.__infoFrame.push(MeshInstance(self.__infoFrame, row[-1]))
        elif isinstance(row[-1], AcdOptiRunConfig):
            print "MainWindow::event_treeView_rowActivated() : run config, name='" + row[0] + "'"
            self.__infoFrame.push(RunConfig(self.__infoFrame,row[-1]))
        elif isinstance(row[-1], AnalysisInterface):
            print "MainWindow::event_treeView_rowActivated() : analysis, name='" + row[0] + "'"
            self.__infoFrame.push(AnalysisExportedResults(self.__infoFrame, row[-1]))
        elif isinstance(row[-1], AcdOptiMeshTemplateCollection):
            print "MainWindow::event_treeView_rowActivated() : mesh template collection"
        elif isinstance(row[-1], AcdOptiMeshTemplate):
            print "MainWindow::event_treeView_rowActivated() : mesh template, name='" + row[0] + "'"
            self.__infoFrame.push(MeshTemplate(self.__infoFrame, row[-1]))
        elif isinstance(row[-1], AcdOptiScanCollection):
            print "MainWindow::event_treeView_rowActivated() : Scan collection"
            self.__infoFrame.writeMessage("Scan collection")
        elif isinstance(row[-1], AcdOptiScan):
            print "MainWindow::event_treeView_rowActivated() : scan, name='" + row[0] + "'"
            self.__infoFrame.push(Scan(self.__infoFrame, row[-1]))
        elif isinstance(row[-1], AcdOptiMetaAnalysisCollection):
            print "MainWindow::event_treeView_rowActivated() : Meta analysis collection"
            #self.__infoFrame.writeMessage("Meta-analysis collection")
            self.__infoFrame.push(MetaAnalysisCollection(self.__infoFrame, self.activeProject.metaAnalysisCollection))
        elif isinstance(row[-1], AcdOptiMetaAnalysis):
            print "MainWindow::event_treeView_rowActivated() : Meta analysis, name='" + row[0] + "'"
            self.__infoFrame.push(MetaAnalysis(self.__infoFrame,row[-1]))
            #self.__infoFrame.writeMessage("Meta-analysis, name='" + row[0] + "'='" + row[-1].instName)
        elif isinstance(row[-1], AcdOptiDataExtractorCollection):
            print "MainWindow::event_treeView_rowActivated() : Data extractor collection, name='" + row[0] + "'"
            #self.__infoFrame.push(MetaAnalysis(self.__infoFrame,row[-1]))
            self.__infoFrame.writeMessage("Data extractor collection, name='" + row[0] + "'")
        elif isinstance(row[-1], AcdOptiDataExtractor):
            print "MainWindow::event_treeView_rowActivated() : Data extractor, name='" + row[0] + "'"
            self.__infoFrame.push(DataExtractor(self.__infoFrame,row[-1]))
            #self.__infoFrame.writeMessage("Data extractor collection, name='" + row[0] + "'")
        else:
            raise NotImplementedError("Unknown class encountered in row[-1]?!? name='" + row[0] + "', row[-1]='" + str(row[-1]) + "'")
            
            
    def loadProject(self, fname):
        """
        This function actually loads a project into AcdOptiGui
        """
        print "MainWindow::loadProject()"
        
        #Load the project
        self.activeProject = AcdOptiProject(fname)
        
        #Setup the explorer
        self.updateProjectExplorer()

        #Ready the infoFrame
        self.__infoFrame.push(ProjectInfo(self.__infoFrame, self.activeProject))

        #We have now loaded a project: Disable new and load buttons,
        # and enable other buttons
        self.__newButton.set_sensitive(False)
        self.__openButton.set_sensitive(False)
        self.__geomInstanceNewButton.set_sensitive(True)
        self.__meshTemplateNewButton.set_sensitive(True)
        self.__scanNewButton.set_sensitive(True)
        self.__metaAnalysisNewButton.set_sensitive(True)
        self.__dataExtractorButton.set_sensitive(True)

    def updateProjectExplorer(self):
        """
        Clears and repopulates the project explorer by scanning the project
        """
        self.__treeModel.clear()
        color = "white"
        
        #Main project
        projIter = self.__treeModel.append(None, [self.activeProject.projectName_name,\
                                                  self.__treeView.render_icon(gtk.STOCK_OPEN, gtk.ICON_SIZE_MENU),\
                                                  "white", self.activeProject])
        
        # GeomCollection
        if self.activeProject.geomCollection.lockdown:
            color = "green"
        else:
            color = "yellow"
        gcIter = self.__treeModel.append(projIter, ["Geometries", self.__geomIcon, color, self.activeProject.geomCollection])
        
        #All geomInstances *not* belonging to a scanInstance
        geomColMap = {}
        for (k,v) in self.activeProject.geomCollection.geomInstances.iteritems(): 
            if len(v.scanInstances) == 0:
                geomColMap[k] = v
        self.__updateProjectExplorer_helper_geomInstancesWithChildren(geomColMap, gcIter)

        #Mesh template collection
        mcIter = self.__treeModel.append(projIter, ["Mesh templates", self.__meshIcon, "white", self.activeProject.meshTemplateCollection])
        #Mesh templates
        for (mtName,mt) in self.activeProject.meshTemplateCollection.meshTemplates.iteritems():
            if mt.lockdown:
                color = "green"
            else:
                color = "yellow"
            mtIter = self.__treeModel.append(mcIter, [mtName, self.__meshIcon, color, mt])

        #Scan collection
        scIter = self.__treeModel.append(projIter, ["Scans", self.__treeView.render_icon(gtk.STOCK_EXECUTE, gtk.ICON_SIZE_MENU), "white", self.activeProject.scanCollection])
        #Scans
        for (scanName, scan) in self.activeProject.scanCollection.scans.iteritems():
            if scan.lockdown:
                color = "green"
            else:
                color = "yellow"
            sIter = self.__treeModel.append(scIter,[scanName, self.__treeView.render_icon(gtk.STOCK_EXECUTE, gtk.ICON_SIZE_MENU), color, scan])
            geomColMap = {}
            for (k,v) in self.activeProject.geomCollection.geomInstances.iteritems(): 
                if scan in v.scanInstances:
                    geomColMap[k] = v
            self.__updateProjectExplorer_helper_geomInstancesWithChildren(geomColMap, sIter)
        
        #Meta-analysis-collection
        macIter = self.__treeModel.append(projIter, ["Meta-analysis", self.__graphIcon, "white", self.activeProject.metaAnalysisCollection])
        #Meta analysis
        for (metAnaName, metAna) in self.activeProject.metaAnalysisCollection.metaAnalysis.iteritems():
            if metAna.lockdown:
                color = "green"
            else:
                color = "yellow"
            maIter = self.__treeModel.append(macIter,[metAnaName, self.__graphIcon, color, metAna])

        #DataExtractorCollection
        decIter = self.__treeModel.append(projIter, ["DataExtractor", self.__graphIcon, "white", self.activeProject.dataExtractorCollection])
        #DataExtractor
        for (deName, de) in self.activeProject.dataExtractorCollection.dataExtractors.iteritems():
            if de.lockdown:
                color = "green"
            else:
                color = "yellow"
            deIter = self.__treeModel.append(decIter,[deName, self.__deIcon, color, de])


        self.__treeView.expand_all()

    def __updateProjectExplorer_helper_geomInstancesWithChildren(self,geomInstancesMap,baseTreeIter):
        # GeomInstances
        for (giName, gi) in geomInstancesMap.iteritems():
            if gi.lockdown:
                color = "green"
            else:
                color = "yellow"
            giIter = self.__treeModel.append(baseTreeIter, [giName, self.__geomIcon, color, gi])

            #  MeshInstances:
            for (miName, mi) in gi.meshInsts.iteritems():
                if mi.lockdown:
                    if mi.meshBad:
                        color = "orange"
                    else:
                        color = "green"
                else:
                    color = "yellow"
                miIter = self.__treeModel.append(giIter,[miName, self.__meshIcon, color, mi])

                # RunCollections
                for (rcName, rc) in mi.runConfigs.iteritems():
                    if rc.status == "not_initialized":
                        color = "red"
                    elif rc.status == "initialized":
                        color =  "yellow"
                    elif rc.status == "staged":
                        color = "blue"
                    elif rc.status.startswith("remote::") or rc.status.startswith("local::"):
                        color = "cyan"
                        if rc.status.endswith("::finished"):
                            color = "magenta" 
                    elif rc.status == "finished":
                        color = "green"
                    rcIter = self.__treeModel.append(miIter, [rcName, self.__treeView.render_icon(gtk.STOCK_PROPERTIES, gtk.ICON_SIZE_MENU), color, rc])
                    
                    #Analysis
                    for (anaName,ana) in rc.analysis.iteritems():
                        if ana.lockdown == True:
                            color = "green"
                        elif ana.lockdown == False:
                            color = "yellow"
                        else:
                            raise NotImplementedError
                        anaIter = self.__treeModel.append(rcIter, [anaName, self.__treeView.render_icon(gtk.STOCK_INFO, gtk.ICON_SIZE_MENU), color, ana])
        
    
    def addMesh(self,name):
        """
        Adding a mesh template to the projects MeshTemplateCollection,
        and updates the GUI.
        """
        print "MainWindow::addMesh()"
        
        #Check that the name is unique
        if name in self.activeProject.meshTemplateCollection.meshTemplates.keys():
            raise AcdOptiGuiException_guiMain_nameTaken
        
        #Create the AcdOptiMeshTemplate
        meshFolder = self.activeProject.meshTemplateCollection.folder
        folder = os.path.join(meshFolder,name)
        AcdOptiMeshTemplate.createNew(folder)
        
        #Add it to the project/MeshTemplateCollection
        self.activeProject.meshTemplateCollection.meshTemplates[name] =\
            AcdOptiMeshTemplate(folder)
        
        #Add it to the treeView
        self.updateProjectExplorer()
