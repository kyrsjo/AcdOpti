import pygtk
pygtk.require('2.0')
import gtk

from InfoFrameComponent import InfoFrameComponent
from acdOpti.AcdOptiSolverSetup import AcdOptiSolverSetup

class SolverSetup(InfoFrameComponent):
    
    solverSetup = None

    __dynamicTable = None
    __dynamicTableTree = None
    __dynamicTableCols = []
    
    __closeButton = None

    def __init__(self,frameManager,solverSetup):
        InfoFrameComponent.__init__(self, frameManager)
        print "SolverSetup::__init__()"
        self.solverSetup = solverSetup
        
        self.baseWidget = gtk.VBox()
        
        print self.solverSetup.name
        print self.solverSetup.type

        self.baseWidget.pack_start(gtk.Label("Solver setup file name : \"" + self.solverSetup.name + "\""), expand=False)
        self.baseWidget.pack_start(gtk.Label("Solver setup type      : \"" + self.solverSetup.type + "\""), expand=False)
        
        self.baseWidget.pack_start(gtk.HSeparator(), expand=False, padding=10)
        
        #Name, type, value, enabled, (backlink)
        self.__dynamicTableTree = gtk.TreeStore(str, str, str, bool, object)
        self.__dynamicTable = gtk.TreeView(self.__dynamicTableTree)
        self.__dynamicTableCols = []
        self.__dynamicTableCols.append(gtk.TreeViewColumn("Name"))
        self.__dynamicTableCols.append(gtk.TreeViewColumn("Data type"))
        self.__dynamicTableCols.append(gtk.TreeViewColumn("Current value"))
        self.__dynamicTableCols.append(gtk.TreeViewColumn("Enabled"))
        for w in self.__dynamicTableCols:
            self.__dynamicTable.append_column(w)
        
        
        self.updateDynamicTable()
        self.baseWidget.pack_start(self.__dynamicTable, expand = True)
        
        self.baseWidget.pack_start(gtk.HSeparator(), expand=False, padding=10)
        
        self.__closeButton = gtk.Button("Close")
        self.__closeButton.connect("clicked", self.event_button_close, None)
        self.baseWidget.pack_start(self.__closeButton,  expand = False)
        
        self.baseWidget.show_all()
    
    def updateSolverSetup(self):
        """
        Writes data from widgets into the SolverSetup,
        (unless the solverSetup is in lockdown.) #TODO: Implement
        """
        print "SolverSetup::updateSolverSetup()"
        
    def updateDynamicTable(self):
        """
        Redraws the dynamic table using data from the solver setup
        """
        print "SolverSetup::updateDynamicTable()"
        
        
        
    def event_button_close(self,widget,data=None):
        print "SolverSetup::event_button_close()"
        
        self.updateSolverSetup()
        self.frameManager.pop()