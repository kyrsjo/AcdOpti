import pygtk
pygtk.require('2.0')
import gtk

from InfoFrameComponent import InfoFrameComponent

class InfoMessage(InfoFrameComponent):
    """
    Simple message display
    """
    def __init__(self, frameManager, message):
        InfoFrameComponent.__init__(self, frameManager)
        
        self.baseWidget = gtk.Label(message)
        self.baseWidget.show()
