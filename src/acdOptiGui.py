#!/usr/bin/env python
# -*- coding: utf8 -*-

import pygtk
pygtk.require('2.0')
import gtk

import sys

from acdOptiGui.MainWindow import MainWindow


assert __name__ == "__main__", "Intended to run as stand-alone"


##
## BEGIN exception hook
## http://29a.ch/2009/1/8/pygtk-exception-hook
##
_ = lambda s: s

def scrolled(widget, shadow=gtk.SHADOW_NONE):
    window = gtk.ScrolledWindow()
    window.set_shadow_type(shadow)
    window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    if widget.set_scroll_adjustments(window.get_hadjustment(),
                                      window.get_vadjustment()):
        window.add(widget)
    else:
        window.add_with_viewport(widget)
    return window


class ExceptionDialog(gtk.MessageDialog):
    def __init__(self, etype, evalue, etb):
        gtk.MessageDialog.__init__(self, buttons=gtk.BUTTONS_CLOSE, type=gtk.MESSAGE_ERROR)
        self.set_resizable(True)
        self.set_markup(_("An error has occured:\n%r\nYou should save "
                "your work and restart the application. If the error "
                "occurs again please report it to the developer." % evalue))
        import cgitb
        text = cgitb.text((etype, evalue, etb), 5)
        expander = gtk.Expander(_("Exception Details"))
        self.vbox.pack_start(expander)
        textview = gtk.TextView()
        textview.get_buffer().set_text(text)
        expander.add(scrolled(textview))
        self.show_all()

def install_exception_hook(dialog=ExceptionDialog):
    old_hook = sys.excepthook
    def new_hook(etype, evalue, etb):
        old_hook(etype, evalue, etb)
        if etype not in (KeyboardInterrupt, SystemExit):
            d = dialog(etype, evalue, etb)
            d.run()
            d.destroy()
    new_hook.old_hook = old_hook
    sys.excepthook = new_hook

install_exception_hook()

##
## END exception hook
##

mainWindow = MainWindow()

gtk.main()

print "Bye!"