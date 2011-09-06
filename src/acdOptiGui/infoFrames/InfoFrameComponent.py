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
