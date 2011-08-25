import pygtk
pygtk.require('2.0')
import gtk

from InfoFrameComponent import InfoFrameComponent
import acdOpti.AcdOptiCubitTemplateFile as AcdOptiCubitTemplateFile
from CubitTemplateEditor import CubitTemplateEditor

class ProjectInfo(InfoFrameComponent):
    """
    Maintains the InfoFrame representing the top-level project
    """
    
    #Logic
    project = None

    #Widgets
    __tableWidget = None

    projName_label = None
#    projName_entry = None

    projFolder_label = None
#    projFolder_entry = None

#    jouTemplate_label = None
#    jouTemplate_path  = None
#    jouTemplate_editButton = None
#    jouTemplate_newButton  = None
#    jouTemplate_openButton = None


    def __init__(self, frameManager, project):
        InfoFrameComponent.__init__(self, frameManager)
        
        self.project = project
        
        #Setup GUI
        self.baseWidget = gtk.VBox(False,5)
#        self.__tableWidget = gtk.Table(4,3,False)
#        self.__tableWidget.set_row_spacings(3)
#        self.__tableWidget.set_col_spacings(3)
#        self.baseWidget.pack_start(self.__tableWidget)
#        self.baseWidget.pack_start(gtk.DrawingArea()) #Some blank space

        # Name
        self.projName_label = gtk.Label("Project name: '" + self.project.projectName_name + "'")
#        self.projName_label.set_alignment(1.0,0.5)
#        self.__tableWidget.attach(self.projName_label, 0,1,0,1, yoptions=gtk.FILL)
        self.baseWidget.pack_start(self.projName_label, expand=False, padding=5)
        
#        self.projName_entry = gtk.Label(\
#            "\"" + self.project.projectName_name + "\"")
#        self.projName_entry.set_alignment(0.0,0.5)
#        self.__tableWidget.attach(self.projName_entry,
#                                1,3,0,1, yoptions=gtk.FILL)

        # Folder
        self.projFolder_label = gtk.Label("Stored in folder: '" + self.project.projectFolder_name + "'")
#        self.projFolder_label.set_alignment(1.0,0.5)
#        self.__tableWidget.attach(self.projFolder_label,0,1,1,2, yoptions=gtk.FILL)
        self.baseWidget.pack_start(self.projFolder_label, expand=False, padding=5)
        
#        self.projFolder_entry = gtk.Label(\
#            "\"" + self.project.projectFolder_name + "\"")
#        self.projFolder_entry.set_alignment(0.0,0.5)
#        self.__tableWidget.attach(self.projFolder_entry,
#                                1,3,1,2, yoptions=gtk.FILL)

#        # CUBIT journal template
#        self.jouTemplate_label = gtk.Label("Geometry template journal:")
#        self.jouTemplate_label.set_alignment(1.0,0.5)
#        self.__tableWidget.attach(self.jouTemplate_label,
#                                0,1,2,3, yoptions=gtk.FILL)
#
#        self.jouTemplate_path = gtk.Label()
#        self.jouTemplate_path.set_alignment(0.0,0.5)
#        self.__tableWidget.attach(self.jouTemplate_path,
#                                1,3,2,3, yoptions=gtk.FILL)
#        
#        self.jouTemplate_editButton = gtk.Button(\
#            stock=gtk.STOCK_EDIT)
#        self.jouTemplate_editButton.connect(\
#            "clicked", self.event_button_jouTemplate_edit, None)
#        self.__tableWidget.attach(self.jouTemplate_editButton,
#                                0,1,3,4, yoptions=gtk.FILL)
#        
#        self.jouTemplate_newButton = gtk.Button(\
#            stock=gtk.STOCK_NEW)
#        self.jouTemplate_newButton.connect(\
#            "clicked", self.event_button_jouTemplate_new, None)
#        self.__tableWidget.attach(self.jouTemplate_newButton,
#                                1,2,3,4, yoptions=gtk.FILL)
#
#        self.jouTemplate_openButton = gtk.Button(\
#            stock=gtk.STOCK_OPEN)
#        self.jouTemplate_openButton.connect(\
#            "clicked", self.event_button_jouTemplate_open, None)
#        self.__tableWidget.attach(self.jouTemplate_openButton,
#                                2,3,3,4, yoptions=gtk.FILL)
#        
#        self.jouTemplateWidgets_update()
        
        #Finalizing
        self.baseWidget.show_all()
    
#    def event_button_jouTemplate_edit(self,widget,event,data=None):
#        print "event_button_jouTemplate_edit"
#        assert self.project.geomTemplateFile != None
#        editor = CubitTemplateEditor(\
#            self.frameManager, self.project.geomTemplateFile)
#        self.frameManager.push(editor)
#
#    def event_button_jouTemplate_new(self,widget,event,data=None):
#        print "event_button_jouTemplate_new"
#        assert self.project.geomTemplateFile == None
#        
#        self.project.geomTemplateFile =\
#            AcdOptiCubitTemplateFile.AcdOptiCubitTemplateFile.createEmpty(\
#            self.project.geomTemplateFile_path)
#        
#        self.jouTemplateWidgets_update()
#
#    def event_button_jouTemplate_open(self,widget,event,data=None):
#        print "event_button_jouTemplate_open"

#    def jouTemplateWidgets_update(self):
#        if self.project.geomTemplateFile == None:
#            self.jouTemplate_path.set_text("None loaded")
#            self.jouTemplate_editButton.set_sensitive(False)
#            self.jouTemplate_newButton.set_sensitive(True)
#            self.jouTemplate_openButton.set_sensitive(True)
#        else:
#            self.jouTemplate_path.set_text(\
#                self.project.geomTemplateFile.fname)
#            self.jouTemplate_editButton.set_sensitive(True)
#            self.jouTemplate_newButton.set_sensitive(False)
#            self.jouTemplate_openButton.set_sensitive(False)
        
