import pygtk
pygtk.require('2.0')
import gtk

from InfoFrameComponent import InfoFrameComponent

def getRunnerSetup(frameManager, runner):
    print "getRunnerSetup()"
    if runner.type == "Hopper":
        return RunnerSetup_Hopper(frameManager,runner)

class RunnerSetup_Hopper(InfoFrameComponent):
    runner = None
    
    __closeButton = None

    def __init__(self,frameManager,runner):
        print "RunnerSetup_Hopper::__init__()"
        InfoFrameComponent.__init__(self, frameManager)
        self.runner = runner
        
        self.baseWidget = gtk.VBox()
        
        
        
        self.baseWidget.pack_start(gtk.HSeparator(), expand=False,padding=10)
        
        self.__closeButton = gtk.Button("Close")
        self.__closeButton.connect("clicked", self.event_button_close, None)
        self.baseWidget.pack_start(self.__closeButton)
        
        self.baseWidget.show_all()
    
    def updateRunner(self):
        pass
    
    def event_button_close(self,widget,data=None):
        self.updateRunner()
        self.frameManager.pop()