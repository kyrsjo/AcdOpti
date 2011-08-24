import pygtk
pygtk.require('2.0')
import gtk

import os

from InfoFrameComponent import InfoFrameComponent
from acdOpti.AcdOptiMeshInstance import AcdOptiMeshInstance

from acdOpti.AcdOptiExceptions import   AcdOptiException_cubitTemplateFile_CUBITerror,\
                                        AcdOptiException_geomInstance_nameError


#TODO: Persistent ordering of keys, same as in GeometryCollection

class GeometryInstance(InfoFrameComponent):
    """
    Allows for manipulation of variables for one specific geometryInstance
    """
    
    #Class object fields
    geomInstance = None
    
    __topLabels = None
    __tableWidget = None
    
    __labelCollection = None
    __entryCollection = None
    __checkCollection = None
    
    __clearLockdownButton = None
    __exportButton   = None
    __generateButton = None
    __meshButton     = None
    
    __scrolledWindow = None
    
    def __init__(self,frameManager,geomInstance):
        InfoFrameComponent.__init__(self, frameManager)
        self.geomInstance = geomInstance
         
        #Create GUI
        self.__topLabels = []

        tlab = gtk.Label("Tag name")
        self.__topLabels.append(tlab)
        
        tlab = gtk.Label("Value")
        self.__topLabels.append(tlab)

        tlab = gtk.Label("Use default")
        self.__topLabels.append(tlab)

        self.__clearLockdownButton = gtk.Button(label="Clear lockdown")
        self.__clearLockdownButton.connect("clicked", self.event_button_clearLockdown, None)

        self.__exportButton = gtk.Button(label="Export CUBIT journal to file...")
        self.__exportButton.connect("clicked", self.event_button_export, None)
        
        self.__generateButton = gtk.Button(label="Run CUBIT to generate solid")
        self.__generateButton.connect("clicked", self.event_button_generate, None)

        self.__meshButton = gtk.Button(label="Attach a mesh...")
        self.__meshButton.connect("clicked", self.event_button_mesh)

        self.updateTable()

        self.__scrolledWindow = gtk.ScrolledWindow()
        self.__scrolledWindow.set_policy(gtk.POLICY_NEVER,gtk.POLICY_AUTOMATIC)
        self.__scrolledWindow.add_with_viewport(self.__tableWidget)
        self.__scrolledWindow.set_shadow_type(gtk.SHADOW_NONE)
        
        self.baseWidget = gtk.VBox()
        self.baseWidget.pack_start(self.__scrolledWindow,      expand=True)
        self.baseWidget.pack_start(self.__clearLockdownButton, expand=False)
        self.baseWidget.pack_start(self.__meshButton,          expand=False)
        self.baseWidget.pack_start(self.__exportButton,        expand=False)
        self.baseWidget.pack_start(self.__generateButton,      expand=False)
        
        self.baseWidget.show_all()
        
    def updateTable(self):
        """
        Fills self.__tableWidget
        """
        numEntries = self.geomInstance.template.paramDefaults_len()
        lockdown   = self.geomInstance.lockdown

        #Initialize __tableWidget
        if not self.__tableWidget:
            self.__tableWidget=gtk.Table(numEntries+1, 3, False)
            self.__tableWidget.set_row_spacings(3)
            self.__tableWidget.set_col_spacings(3)
            
            self.__tableWidget.attach(self.__topLabels[0],
                                   0,1,0,1,
                                   xoptions=gtk.FILL,yoptions=gtk.FILL)
            self.__tableWidget.attach(self.__topLabels[1],
                                   1,2,0,1,
                                   xoptions=gtk.FILL|gtk.EXPAND,yoptions=gtk.FILL)
            self.__tableWidget.attach(self.__topLabels[2],
                                   2,3,0,1,
                                   xoptions=gtk.FILL,yoptions=gtk.FILL)
            
            self.__labelCollection = {}
            self.__entryCollection = {}
            self.__checkCollection = {}
        else:
            #Clear anything that might be there from before
            for k in self.geomInstance.template.paramDefaults_getKeys():
                self.__tableWidget.remove(self.__labelCollection[k])
                self.__tableWidget.remove(self.__entryCollection[k])
                self.__tableWidget.remove(self.__checkCollection[k])
            self.__labelCollection.clear()
            self.__entryCollection.clear()
            self.__checkCollection.clear()
        
        #Create and attach the table entries
        for (k,i) in zip(self.geomInstance.template.paramDefaults_getKeys(),
                         xrange(numEntries)):
            
            self.__labelCollection[k]=lab=gtk.Label(k)
            self.__tableWidget.attach(lab,0,1,i+1,i+2, xoptions=gtk.FILL, yoptions=gtk.FILL)
            
            self.__entryCollection[k]=ent=gtk.Entry()
            if k in self.geomInstance.templateOverrides_getKeys():
                ent.set_text(self.geomInstance.templateOverrides_get(k))
                if lockdown:
                    ent.set_sensitive(False)
            else:
                ent.set_text(self.geomInstance.template.paramDefaults_get(k))
                ent.set_sensitive(False)
            self.__tableWidget.attach(ent,1,2,i+1,i+2, xoptions=gtk.FILL|gtk.EXPAND, yoptions=gtk.FILL)

            self.__checkCollection[k]=check=gtk.CheckButton()
            if k in self.geomInstance.templateOverrides_getKeys():
                check.set_active(False)
            else:
                check.set_active(True)
            if lockdown:
                check.set_sensitive(False)
            check.connect("toggled", self.event_check_toggled, k) #Toggle first, then message handler
            self.__tableWidget.attach(check,2,3,i+1,i+2, xoptions=gtk.FILL, yoptions=gtk.FILL)
        
        #Update the lockdown button
        if lockdown:
            self.__clearLockdownButton.set_sensitive(True)
        else:
            self.__clearLockdownButton.set_sensitive(False)
        
        self.__tableWidget.show_all()
    
    def updateGeomInstance(self):
        """
        Copies information from the on-screen form into the geomInstance.
        Does NOT ask the geomInstance to write itself to file.
        
        If geomInstance is in lockdown, do nothing.
        """
        if self.geomInstance.lockdown:
            return
        for k in self.geomInstance.templateOverrides_getKeys():
            self.geomInstance.templateOverrides_insert(k, self.__entryCollection[k].get_text())
        
    
    def event_check_toggled(self, widget, data):
        print "GeometryInstance::event_check_toggled(), data =", data

        if widget.get_active():
            #Checked
            dia = gtk.Dialog("Entry unchecked", self.getBaseWindow(),
                             gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                             (gtk.STOCK_NO, gtk.RESPONSE_NO,
                              gtk.STOCK_YES, gtk.RESPONSE_YES))
            dia.set_default_response(gtk.RESPONSE_YES)
            dia.vbox.pack_start(gtk.image_new_from_stock(
                         gtk.STOCK_DIALOG_QUESTION,
                         gtk.ICON_SIZE_DIALOG))
            dia.vbox.pack_start(gtk.Label("Delete override \"" + data + "\" ?"))
            dia.show_all()

            response = dia.run()

            if response == gtk.RESPONSE_YES:
                #Delete
                dia.destroy()
                
                self.geomInstance.templateOverrides_del(data)
                self.__entryCollection[data].set_sensitive(False)
                self.__entryCollection[data].set_text(self.geomInstance.template.paramDefaults_get(data))
                
            else:
                #Abort
                dia.destroy()
                self.__checkCollection[data].set_active(False)
        else:
            #Unchecked
            self.geomInstance.templateOverrides_insert(data, self.geomInstance.template.paramDefaults_get(data))
            self.__entryCollection[data].set_sensitive(True)
    
    def event_delete(self):
        print "GeometryInstance::event_delete"
        #Save to the geomInstance
        self.updateGeomInstance()
        #Ask the geomInstance to write itself to disk
        self.geomInstance.write()
    
    def event_button_clearLockdown(self,widget, data=None):
        print "GeometryInstance::event_button_clearLockdown()"
        self.geomInstance.clearLockdown()
        self.updateTable()
    
    def event_button_export(self, widget, data=None):
        print "GeometryInstance::event_button_export()"
        self.updateGeomInstance()
        
        (journal, extraKeys) = self.geomInstance.generateCubitJou()
        
        #Check for extra keys
        if len(extraKeys):
            dia = gtk.Dialog("Extra keys in template", self.getBaseWindow(),
                             gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                             (gtk.STOCK_NO, gtk.RESPONSE_NO,
                              gtk.STOCK_YES, gtk.RESPONSE_YES))
            dia.set_default_response(gtk.RESPONSE_YES)
            dia.vbox.pack_start(gtk.image_new_from_stock(
                         gtk.STOCK_DIALOG_QUESTION,
                         gtk.ICON_SIZE_DIALOG))
            dia.vbox.pack_start(gtk.Label("Extra keys found in template, continue?\n" + str(extraKeys) ))
            dia.show_all()

            response = dia.run()
            dia.destroy()
            
            if not response == gtk.RESPONSE_YES:
                #Stop now
                return
        
        #Ask where to save
        chooser = gtk.FileChooserDialog(title="Export file",
                                        parent=self.getBaseWindow(),
                                        action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                        buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        chooser.set_default_response(gtk.RESPONSE_OK)
        filter = gtk.FileFilter()
        filter.set_name("CUBIT journal file .jou")
        filter.add_mime_type("text/plain")
        filter.add_pattern("*.jou")
        chooser.add_filter(filter)
        response = chooser.run()
        
        if response == gtk.RESPONSE_OK:
            fname = chooser.get_filename()
            if not fname.endswith(".jou"):
                fname += ".jou"
            if os.path.isfile(fname):
                dia = gtk.Dialog("File already exists", chooser,
                                 gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                 (gtk.STOCK_NO, gtk.RESPONSE_NO,
                                  gtk.STOCK_YES, gtk.RESPONSE_YES))
                dia.set_default_response(gtk.RESPONSE_YES)
                dia.vbox.pack_start(gtk.image_new_from_stock\
                                    (gtk.STOCK_DIALOG_QUESTION,
                                     gtk.ICON_SIZE_DIALOG))
                dia.vbox.pack_start(gtk.Label("File already exists, overwrite?"))
                dia.show_all()

                response2 = dia.run()
                dia.destroy()
            
                if not response2 == gtk.RESPONSE_YES:
                    #Stop now!
                    print "GeometryInstance::event_button_export()::AbortOverwrite"
                    chooser.destroy() #I'm to lazy to implement a proper event loop
                    return
            #File name free OR user clicked YES to overwrite
            chooser.destroy()
            
            print "GeometryInstance::event_button_export()::write"
            ofile = open(fname,'w')
            ofile.write(journal)
            ofile.close()
            
        else:
            chooser.destroy()
        
    def event_button_generate(self, widget, data=None):
        print "GeometryInstance::event_button_generate()"
        
        self.updateGeomInstance()
        try:
            self.geomInstance.generateGeometry()
        except AcdOptiException_cubitTemplateFile_CUBITerror as e:
            md = gtk.MessageDialog(self.getBaseWindow(),
                                   gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
                                   gtk.BUTTONS_CLOSE, "Error during execution of CUBIT script, offending command:\n" + str(e.args[2]))
            md.run()
            md.destroy()
        
        self.updateTable()
    
    def event_button_mesh(self,widget,data=None):
        print "GeometryInstance::event_button_mesh()"
        
        dia = gtk.Dialog("Select mesh template", self.getBaseWindow(),
                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                         (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                          gtk.STOCK_OK, gtk.RESPONSE_OK))
        dia.set_default_response(gtk.RESPONSE_OK)

        #Setup the listModel        
        diaListModel = gtk.ListStore(str)
        diaListDict = {}
        for mt in self.geomInstance.template.project.meshTemplateCollection.meshTemplates:
            mti = diaListModel.append([mt,])
            diaListDict[mt] = gtk.TreeRowReference(diaListModel,diaListModel.get_path(mti))

        diaTreeView = gtk.TreeView(diaListModel)
        diaTreeViewCol = gtk.TreeViewColumn()
        diaCellRender = gtk.CellRendererText()
        diaTreeView.append_column(diaTreeViewCol)
        diaTreeViewCol.pack_start(diaCellRender)
        diaTreeViewCol.add_attribute(diaCellRender, 'text', 0)
        diaTreeView.set_headers_visible(False)
        
        dia.vbox.pack_start(diaTreeView)
        dia.show_all()
        response = dia.run()
        
        #Get the answer
        selected = diaTreeView.get_selection()
        selIter = selected.get_selected()[1]
        selPath = diaListModel.get_path(selIter)
        meshTemplateName = None
        for (mt, ref) in diaListDict.iteritems(): 
            if selPath == ref.get_path():
                meshTemplateName = mt
        assert meshTemplateName
        #Delete the dialog
        dia.destroy()
        
        if response == gtk.RESPONSE_OK:
            #Ask for the mesh instance name
            dia2 = gtk.Dialog("Please enter name of new mesh instance:", self.getBaseWindow(),
                             gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                             (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                              gtk.STOCK_OK, gtk.RESPONSE_OK))
            dia2.set_default_response(gtk.RESPONSE_OK)
            nameBox = gtk.Entry()
            nameBox.set_text(meshTemplateName)
            nameBox.show()
            dia2.vbox.pack_start(nameBox)
            dia2.show_all()
    
            response2 = dia2.run()
            meshInstanceName = nameBox.get_text()
            dia2.destroy()
            
            if response2 == gtk.RESPONSE_OK:
                #Check for whitespace
                if " " in meshInstanceName:
                    mDia = gtk.MessageDialog(self.getBaseWindow(),
                                             gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                             gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                             "Name cannot contain whitespace")
                    mDia.run()
                    mDia.destroy()
                #Everything OK: Try to attach the MeshInstance!
                else:
                    try:
                        self.geomInstance.addMeshInstance(meshTemplateName, meshInstanceName)
                        #self.frameManager.mainWindow.addMeshInstanceToGUI(self.geomInstance.instName, meshInstanceName)
                        self.frameManager.mainWindow.updateProjectExplorer()
                    except AcdOptiException_geomInstance_nameError:
                        #Nope
                        mDia = gtk.MessageDialog(self.getBaseWindow(),
                                                 gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                                 gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                                 "Name already in use")
                        mDia.run()
                        mDia.destroy()


            