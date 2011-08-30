import pygtk
pygtk.require('2.0')
import gtk

from InfoFrameComponent import InfoFrameComponent

from acdOpti.analysis.AnalysisInterface import AnalysisInterface

class AnalysisExportedResults(InfoFrameComponent):
    """
    Shows a tree with the exported results from an analysis,
    and has a button for runAnalysis/clearLockdown
    """
    analysis = None
    
    __scrollWindow = None
    __treeView     = None
    __treeModel    = None
    __treeCols     = None
    __treeRenders  = None
    
    __lockdownRunButton = None
    
    def __init__(self, frameManager, analysis):
        InfoFrameComponent.__init__(self, frameManager)
        self.analysis = analysis
        assert isinstance(self.analysis, AnalysisInterface)
        
        self.baseWidget = gtk.VBox()
        
        self.__treeModel = gtk.TreeStore(str, str)
        self.__treeView = gtk.TreeView(self.__treeModel)
        self.baseWidget.pack_start(self.__treeView, expand=True)
        self.__treeCols = []
        self.__treeRenders = []
        
        self.__treeRenders.append(gtk.CellRendererText())
        self.__treeCols.append(gtk.TreeViewColumn("Key", self.__treeRenders[-1], text=0))
        self.__treeView.append_column(self.__treeCols[-1])
        
        self.__treeRenders.append(gtk.CellRendererText())
        self.__treeCols.append(gtk.TreeViewColumn("Value", self.__treeRenders[-1], text=1))
        self.__treeView.append_column(self.__treeCols[-1])
        
        self.baseWidget.pack_start(gtk.HSeparator(), expand=False, padding=10)
        
        self.__lockdownRunButton = gtk.Button("Run analysis") #Updated in __updateGui()
        self.__lockdownRunButton.connect("clicked", self.event_button_lockdownRun, None)
        self.baseWidget.pack_start(self.__lockdownRunButton, expand=False)

        self.__updateGui()
        
        self.baseWidget.show_all()

    def __updateGui(self):
        print "AnalysisExportedResults::__updateGui()"
        #TreeView
        self.__treeModel.clear()
        self.__updateTable_recursive(self.analysis.exportResults, None)

        #Button
        if self.analysis.lockdown:
            self.__lockdownRunButton.set_label("Clear lockdown")
        else:
            self.__lockdownRunButton.set_label("Run analysis")
        
        #Main window project explorer
        self.frameManager.mainWindow.updateProjectExplorer()

    def __updateTable_recursive(self,exportedDict,parentIter):
        for (k,v) in exportedDict:
            if type(v) == str:
                self.__treeModel.append(parentIter, [k,v])
            else:
                #DataDict
                iter = self.__treeModel.append(parentIter, [k,""])
                self.__updateTable_recursive(v, iter)
                
    def event_button_lockdownRun(self, widget, data=None):
        print "AnalysisExportedResults::event_button_lockdownRun()"
        
        if self.analysis.lockdown:
            self.analysis.clearLockdown()
        else:
            self.analysis.runAnalysis()
        self.__updateGui()