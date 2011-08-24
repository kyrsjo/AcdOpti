import pygtk
pygtk.require('2.0')
import gtk

import acdOpti.AcdOptiProject as AcdOptiProject
from acdOpti.AcdOptiExceptions import *
from AcdOptiGuiExceptions import *
import exceptions, errno
from acdOpti.AcdOptiGeometryCollection import AcdOptiGeometryCollection
from acdOpti.AcdOptiGeometryInstance import AcdOptiGeometryInstance
from acdOpti.AcdOptiMeshTemplate import AcdOptiMeshTemplate

from infoFrames.InfoFrameManager import InfoFrameManager
from infoFrames.ProjectInfo import ProjectInfo
from infoFrames.GeometryCollection import GeometryCollection
from infoFrames.GeometryInstance import GeometryInstance
from infoFrames.MeshTemplate import MeshTemplate
from infoFrames.MeshInstance import MeshInstance

import os

acdOptiGuiPath = os.path.split(__file__)[0] #"/home/kyrre/PhD/optimizer/code/acdOptiGui"
iconSize = "24x24"

class MainWindow():
    """
    Draws and handles events for the main window
    """
    
    #Fields: GUI components
    window          = None
    __VBox1           = None
    __HBox2           = None
    __infoFrame       = None
    
    __toolbar                 = None
    __newButton               = None
    __openButton              = None
    __geomInstanceNewButton   = None
    __meshTemplateNewButton = None

    __treeModel       = None
    __treeView        = None
    __treeViewColumn  = None
    __cellRender      = None

    #Fields: Info frame
    activeProject_info = None

    #Fields: Logic
    activeProject = None
    __activeProject_treeReference = None
    __geomsTop_treeReference = None
    __geoms_treeReference = None
    __geoms_meshInstances_treeReference = None
    __meshesTop_treeReference = None
    __meshes_treeReference = None

    #Methods
    def __init__(self):
        #Setup the main window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("ACD project organizer")
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


        self.__VBox1.pack_start(self.__toolbar, False)

        #Sidebar/maindisplay HBox
        self.__HBox2 = gtk.HBox(False, 5)
        self.__VBox1.pack_start(self.__HBox2)
        
        #Tree view in left part of screen
        self.__treeModel      = gtk.TreeStore(str)
        self.__treeView       = gtk.TreeView(self.__treeModel)
        self.__treeViewColumn = gtk.TreeViewColumn('Project explorer')
        self.__cellRender     = gtk.CellRendererText()
        
        self.__treeView.append_column(self.__treeViewColumn)
        self.__treeViewColumn.pack_start(self.__cellRender)
        self.__treeViewColumn.add_attribute(self.__cellRender, 'text', 0)

        self.__treeView.connect("row-activated", self.event_treeView_rowActivated, None)

        self.__HBox2.pack_start(self.__treeView, False)
        
        #self.__treeModel.append(None, ["Load a project to start",])
        
        #Frame on which to display other info
        self.__infoFrame = InfoFrameManager(self.__HBox2,self)
        self.__infoFrame.writeMessage("Load a project to start")

        self.window.show_all()

        #Lazy me
        self.loadProject("../test")
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
                AcdOptiProject.AcdOptiProject.createNew(fname)
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
                        self.addGeom(name)
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
  

    def event_treeView_rowActivated(self,widget,path,column,data=None):
        print "MainWindow::event_treeView_rowActivated(), path =", path
        
        #Try to clear the __infoFrame
        if self.__infoFrame.clear():
            #Returned True - some widget was not ready.
            return
        
        #Was it the top-level project?
        if path == self.__activeProject_treeReference.get_path():
            print "MainWindow::event_treeView_rowActivated() : project"
            self.__infoFrame.push(self.activeProject_info)
        #Top-level "Geometries" item?
        elif path == self.__geomsTop_treeReference.get_path():
            print "MainWindow::event_treeView_rowActivated() : geoms"
            self.__infoFrame.push(GeometryCollection(self.__infoFrame,self.activeProject.geomCollection))
        #Top-level "Meshes" item?
        elif path == self.__meshesTop_treeReference.get_path():
            print "MainWindow::event_treeView_rowActivated() : meshes"
        
        #Geometry instance?
        elif path in [p.get_path() for p in self.__geoms_treeReference.values()]:
            value = self.__treeModel.get_value(self.__treeModel.get_iter(path), 0)
            print "MainWindow::event_treeView_rowActivated() : geom instance \"" + str(path) + "\", name = \"" + value + "\""
            self.__infoFrame.push(GeometryInstance(self.__infoFrame, self.activeProject.geomCollection.geomInstances[value]))
        
        #Mesh instance?
        elif path[:-1] in [p.get_path() for p in self.__geoms_treeReference.values()]:
            geomName = self.__treeModel.get_value(self.__treeModel.get_iter(path[:-1]), 0)
            meshName = self.__treeModel.get_value(self.__treeModel.get_iter(path), 0)
            print "MainWindow::event_treeView_rowActivated() : "\
                + "mesh instance \"" + str(path) + "\", geomName = \"" + geomName + "\""\
                + ", meshName = \"" + meshName + "\""
            meshInstance = self.activeProject.geomCollection.geomInstances[geomName].meshInsts[meshName]
            self.__infoFrame.push(MeshInstance(self.__infoFrame, meshInstance))

        #Mesh template?
        elif path in [p.get_path() for p in self.__meshes_treeReference.values()]:
            value = self.__treeModel.get_value(self.__treeModel.get_iter(path), 0)
            print "MainWindow::event_treeView_rowActivated() :"\
                + "mesh template \"" + str(path) + "\", name = \"" + value + "\""
            self.__infoFrame.push(MeshTemplate(self.__infoFrame, self.activeProject.meshTemplateCollection.meshTemplates[value]))
            
    def loadProject(self, fname):
        """
        This function actually loads a project into AcdOptiGui
        """
        print "MainWindow::loadProject()"
        
        #Load the project
        self.activeProject = AcdOptiProject.AcdOptiProject(fname)
        
        #Setup the explorer
        self.updateProjectExplorer()

        #Ready the infoFrame
        self.activeProject_info = ProjectInfo(self.__infoFrame, self.activeProject)
        self.__infoFrame.push(self.activeProject_info)

        #We have now loaded a project: Disable new and load buttons,
        # and enable other buttons
        self.__newButton.set_sensitive(False)
        self.__openButton.set_sensitive(False)
        self.__geomInstanceNewButton.set_sensitive(True)
        self.__meshTemplateNewButton.set_sensitive(True)

    def updateProjectExplorer(self):
        """
        Clears and repopulates the project explorer by scanning the project
        """
        self.__treeModel.clear()
        
        #Main project
        projIter = self.__treeModel.append(None, [self.activeProject.projectName_name,])
        self.__activeProject_treeReference = gtk.TreeRowReference(self.__treeModel,
                                                                  self.__treeModel.get_path(projIter))
        
        # GeomCollection
        gcIter = self.__treeModel.append(projIter, ["Geometries",])
        self.__geomsTop_treeReference = gtk.TreeRowReference(self.__treeModel,
                                                             self.__treeModel.get_path(gcIter))
        # GeomInstances
        self.__geoms_treeReference = {}
        self.__geoms_meshInstances_treeReference = {}
        for gi in self.activeProject.geomCollection.geomInstances:
            giIter = self.__treeModel.append(gcIter, [gi,])
            self.__geoms_treeReference[gi] = gtk.TreeRowReference(self.__treeModel,
                                                                  self.__treeModel.get_path(giIter))
            #  MeshInstances:
            self.__geoms_meshInstances_treeReference[gi] = {}
            for mii in self.activeProject.geomCollection.geomInstances[gi].meshInsts:
                miiIter = self.__treeModel.append(giIter,[mii,])
                self.__geoms_meshInstances_treeReference[gi][mii] = \
                    gtk.TreeRowReference(self.__treeModel, self.__treeModel.get_path(miiIter))
        

        mcIter = self.__treeModel.append(projIter, ["Mesh templates",])
        self.__meshesTop_treeReference = gtk.TreeRowReference(self.__treeModel,
                                                              self.__treeModel.get_path(mcIter))
        self.__meshes_treeReference = {}
        for mi in self.activeProject.meshTemplateCollection.meshTemplates:
            miIter = self.__treeModel.append(mcIter, [mi,])
            self.__meshes_treeReference[mi] = gtk.TreeRowReference(self.__treeModel,
                                                                   self.__treeModel.get_path(miIter))
        self.__treeView.expand_all()

    def addGeom(self, name):
        """
        Adding a geom to the project's geomCollection,
        and updates the GUI.
        """
        print "MainWindow::addGeom()"
        
        #Check that name is unique
        if name in self.activeProject.geomCollection.geomInstances.keys():
            raise AcdOptiGuiException_guiMain_nameTaken
        
        #Create the AcdOptiGeometryInstance
        geomFolder = self.activeProject.geomCollection.folder
        folder = os.path.join(geomFolder, name)
        AcdOptiGeometryInstance.createNew(folder)

        #Add it to the project/geomCollection
        self.activeProject.geomCollection.geomInstances[name] =\
            AcdOptiGeometryInstance(folder,self.activeProject.geomCollection)
        
        #Add it to the treeView
        #gcIter = self.__treeModel.get_iter(self.__geomsTop_treeReference.get_path())
        #giIter = self.__treeModel.append(gcIter, [name,])
        #self.__geoms_treeReference[name] = gtk.TreeRowReference(self.__treeModel,
        #                                                        self.__treeModel.get_path(giIter))
        #self.__geoms_meshInstances_treeReference[name] = {}
        self.updateProjectExplorer()
    
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
        #mcIter = self.__treeModel.get_iter(self.__meshesTop_treeReference.get_path())
        #mtIter = self.__treeModel.append(mcIter,[name,])
        #self.__meshes_treeReference[name] = gtk.TreeRowReference(self.__treeModel,
        #                                                         self.__treeModel.get_path(mtIter))
        self.updateProjectExplorer()
    
    #def addMeshInstanceToGUI(self, geomInstanceName,meshInstanceName):
    #    """
    #    Given the name of an already created meshInstance and
    #    the geomInstance it belongs to, add it to the GUI.
    #    """
    #    print "MainWindow::addMeshInstanceToGUI()"
    #    
    #    #  MeshInstances:
    #    giIter = self.__treeModel.get_iter(self.__geoms_treeReference[geomInstanceName].get_path())
    #    miiIter = self.__treeModel.append(giIter,[meshInstanceName,])
    #    self.__geoms_meshInstances_treeReference[geomInstanceName][meshInstanceName] = \
    #        gtk.TreeRowReference(self.__treeModel, self.__treeModel.get_path(miiIter))
            