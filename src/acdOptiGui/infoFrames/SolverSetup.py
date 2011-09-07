import pygtk
pygtk.require('2.0')
import gtk

from InfoFrameComponent import InfoFrameComponent
from acdOpti.AcdOptiSolverSetup import AcdOptiSolverSetup
from acdOpti.AcdOptiFileParser import DataDict

class SolverSetup(InfoFrameComponent):
    
    solverSetup = None

    __scrollWindow = None
    __dynamicTable = None
    __dynamicTableTree = None
    __dynamicTableCols = None
    __dynamicTableCRs  = None
    
    __buttonHBox = None
    __copyButton = None
    __delButton = None
    
    __closeButton = None

    def __init__(self,frameManager,solverSetup):
        InfoFrameComponent.__init__(self, frameManager)
        print "SolverSetup::__init__()"
        self.solverSetup = solverSetup
        
        self.baseWidget = gtk.VBox()

        self.baseWidget.pack_start(gtk.Label("Solver setup file name : \"" + self.solverSetup.name + "\""), expand=False)
        self.baseWidget.pack_start(gtk.Label("Solver setup type      : \"" + self.solverSetup.type + "\""), expand=False)
        
        self.baseWidget.pack_start(gtk.HSeparator(), expand=False, padding=10)
        
        #Name, type, value, enabled, mustNot, editable, (backlink)
        self.__dynamicTableTree = gtk.TreeStore(str, str, str, bool, bool, bool, object)
        self.__dynamicTable = gtk.TreeView(self.__dynamicTableTree)
        self.__dynamicTableCols = []
        self.__dynamicTableCRs = []
        
        self.__dynamicTableCRs.append(gtk.CellRendererText())
        self.__dynamicTableCols.append(gtk.TreeViewColumn("Name", self.__dynamicTableCRs[-1], text=0))
        self.__dynamicTableCols[-1].set_expand(True)
        self.__dynamicTable.append_column(self.__dynamicTableCols[-1])
        
        self.__dynamicTableCRs.append(gtk.CellRendererText())
        self.__dynamicTableCols.append(gtk.TreeViewColumn("Data type", self.__dynamicTableCRs[-1], text=1))
        self.__dynamicTable.append_column(self.__dynamicTableCols[-1])

        self.__dynamicTableCRs.append(gtk.CellRendererText())
        self.__dynamicTableCols.append(gtk.TreeViewColumn("Current value", self.__dynamicTableCRs[-1], text=2, editable=5))
        self.__dynamicTableCRs[-1].connect('edited', self.event_cellRenderer_value_edited, None)
        self.__dynamicTable.append_column(self.__dynamicTableCols[-1])
        
        self.__dynamicTableCRs.append(gtk.CellRendererToggle())
        self.__dynamicTableCols.append(gtk.TreeViewColumn("Enabled", self.__dynamicTableCRs[-1], active=3, activatable=4))
        self.__dynamicTableCRs[-1].connect("toggled", self.event_cellRenderer_enabled_toggled, None)
        self.__dynamicTable.append_column(self.__dynamicTableCols[-1])            
    
        self.__scrollWindow = gtk.ScrolledWindow()
        self.__scrollWindow.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.__scrollWindow.add_with_viewport(self.__dynamicTable)
        self.baseWidget.pack_start(self.__scrollWindow, expand=True)
    
        self.__buttonHBox = gtk.HBox()
        self.__copyButton = gtk.Button("Copy current line")
        self.__copyButton.connect("clicked", self.event_button_copy, None)
        self.__copyButton.set_sensitive(False)
        self.__buttonHBox.pack_start(self.__copyButton)
        self.__delButton  = gtk.Button("Delete current line")
        self.__delButton.connect("clicked", self.event_button_del, None)
        self.__delButton.set_sensitive(False)
        self.__buttonHBox.pack_start(self.__delButton)
        self.baseWidget.pack_start(self.__buttonHBox, expand=False)
        self.__dynamicTable.connect("cursor-changed",self.event_dynamicTable_cursorChanged,None)
        
        self.baseWidget.pack_start(gtk.HSeparator(), expand=False, padding=10)
        
        self.__closeButton = gtk.Button("Close")
        self.__closeButton.connect("clicked", self.event_button_close, None)
        self.baseWidget.pack_start(self.__closeButton,  expand=False)
        
        self.updateDynamicTable()
        if self.solverSetup.lockdown:
            self.__copyButton.set_sensitive(False)
            self.__delButton.set_sensitive(False)
            self.__dynamicTable.set_sensitive(False)
        
        self.baseWidget.show_all()
    
    def updateSolverSetup(self):
        """
        Writes data from widgets into the SolverSetup,
        (unless the solverSetup is in lockdown.) #TODO: ImplementMe
        """
        print "SolverSetup::updateSolverSetup()"
        
    def updateDynamicTable(self):
        """
        Redraws the dynamic table using data from the solver setup
        """
        print "SolverSetup::updateDynamicTable()"
        
        self.__dynamicTableTree.clear()
        print self.solverSetup.metaSetup
        self.__updateDynamicTable_recursive(self.solverSetup.metaSetup, None)
        self.__dynamicTable.expand_all()
        self.event_dynamicTable_cursorChanged(self.__dynamicTable, None) #Disable the buttons
        
    def __updateDynamicTable_recursive(self,metaSetup,parentIter):
        """
        Method that recursively calls itself whenever it encounters
        a "dict" entry in the metaSetupFile.
        """
        print "SolverSetup::__updateDynamicTable_recursive()"
        
        for (key,val) in metaSetup:
            #print (key,val)
            type = val["type"]
            if type == "dict":
                iter = self.__dynamicTableTree.append(parentIter,\
                    [key, type, "", DataDict.boolconv(val["enabled"]), not DataDict.boolconv(val["must"]), False, val])
                self.__updateDynamicTable_recursive(val["children"], iter)
            #elif type=="fnameNoEx" or type=="fnameEx" or type=="string":
            else:
                iter = self.__dynamicTableTree.append(parentIter,\
                    [key, type, val["value"], DataDict.boolconv(val["enabled"]), not DataDict.boolconv(val["must"]), True, val])
        print "SolverSetup::__updateDynamicTable_recursive() - return"

    
    def __rowStringer(self,row):
        "Helper method converting a row->string"
        #Name, type, value, enabled, must, editable, (backlink)
        return "Name='" + str(row[0]) + ", type='" + str(row[1]) + "', value='" + str(row[2]) +\
                "', enabled='" + str(row[3]) + ", mustNot='" + str(row[4]) + "', editable='" + str(row[5]) + "', object='" + str(row[6]) + "'"
    
    def event_button_close(self,widget,data=None):
        print "SolverSetup::event_button_close()"
        
        self.updateSolverSetup()
        self.frameManager.pop()
    
    def event_button_copy(self,widget,data=None):
        print "SolverSestup::event_button_copy"
        
        #Get the currently selected row
        (path,column) = self.__dynamicTable.get_cursor()
        assert path, "Nothing selected?!"
        row = self.__dynamicTableTree[path]
        
        #Find the parent "children" dict
        parent = None
        if len(path) == 1:
            #Top-level
            parent = self.solverSetup.metaSetup
        else:
            parentRow = self.__dynamicTableTree[path[:-1]]
            parent = parentRow[-1]
        
        #Add the child to the mother dataDict
        parent["children"].pushBack(row[0], row[-1].copy())        
        
        #Add entry to the TreeModel
        self.updateDynamicTable()
        
        
    def event_button_del(self,widget,data=None):
        print "SolverSestup::event_button_del"
        
        #Get the currently selected row
        (path,column) = self.__dynamicTable.get_cursor()
        assert path, "Nothing selected?!"
        row = self.__dynamicTableTree[path]
        
        #Find the parent "children" dict
        parent = None
        if len(path) == 1:
            #Top-level
            parent = self.solverSetup.metaSetup
        else:
            parentRow = self.__dynamicTableTree[path[:-1]]
            parent = parentRow[-1]
        
        #Delete the child from the mother dataDict
        parent["children"].delItem(path[-1])        
        
        #Add entry to the TreeModel
        self.updateDynamicTable()
    
    def event_cellRenderer_value_edited(self, cell, path, new_text, user_data=None):
        print "SolverSetup::event_cellRenderer_value_edited(), path='" + str(path) + "', new_text='" + new_text + "'"
        
        #Get the underlying DataDict object
        data = self.__dynamicTableTree[path][-1]
        
        #Check that the new input is valid
        problem = AcdOptiSolverSetup.isInputInvalid(data, new_text)
        if problem:
            print "Invalid data, problem='" + problem + "'"
            return
        
        #Store it to the underlying structure
        data.setValSingle("value", new_text)

        #Update the display
        self.__dynamicTableTree[path][2] = new_text
        
    def event_cellRenderer_enabled_toggled(self, cellrenderertoggle, path, data=None):
        print "SolverSetup::event_cellRenderer_enabled_toggled(), path='" + str(path) + "', row= '" + self.__rowStringer(self.__dynamicTableTree[path]) + "'"  
        
        data =  self.__dynamicTableTree[path][-1]
        if DataDict.boolconv(data["enabled"]):
            data.setValSingle("enabled", "False")
        else:
            data.setValSingle("enabled", "True")
        
        self.__dynamicTableTree[path][3] = not self.__dynamicTableTree[path][3]
        
    def event_dynamicTable_cursorChanged(self, widget, data=None):
        print "SolverSetup::event_dynamicTable_cursorChanged()"
        
        #Get the currently selected row
        (path,column) = self.__dynamicTable.get_cursor()
        if not path:
            #Nothing selected...
            self.__copyButton.set_sensitive(False)
            self.__delButton.set_sensitive(False)
            return
                
        row = self.__dynamicTableTree[path]
        
        if DataDict.boolconv(row[-1]["single"]):
            self.__copyButton.set_sensitive(False)
            self.__delButton.set_sensitive(False)
        else:
            self.__copyButton.set_sensitive(True)
            
            #Is it alone? Can't delete the last instance...
            
            #Find the parent "children" dict
            parent = None
            if len(path) == 1:
                #Top-level
                parent = self.solverSetup.metaSetup
                parentChild = parent#["options"]
            else:
                parentRow = self.__dynamicTableTree[path[:-1]]
                parent = parentRow[-1]
                parentChild = parent["children"]
            
            #Search for siblings with same name
            findings = 0
            for (k,v) in parentChild:
                if k == row[0]:
                    findings += 1
            
            if findings > 1:
                self.__delButton.set_sensitive(True)
            else:
                self.__delButton.set_sensitive(False)
                
                