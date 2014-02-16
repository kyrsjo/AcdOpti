# -*- coding: utf8 -*-
#
# Copyright 2012, 2013 Kyrre Ness Sjøbæk
# This file is part of AcdOpti.
#
#    AcdOpti is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    AcdOpti is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with AcdOpti.  If not, see <http://www.gnu.org/licenses/>.

import pygtk
pygtk.require('2.0')
import gtk

from InfoFrameComponent import InfoFrameComponent
from acdOpti.AcdOptiDataExtractor import AcdOptiDataExtractor
from acdOpti.AcdOptiDataExtractorPlot import *

class DataExtractorPlots(InfoFrameComponent):
    """
    Plots list
    """
    
    dataExtractor = None
    
    __tableScroll = None
    __tableWidget = None
    
    __addButton   = None
    __closeButton = None
    
    
    def __init__(self, frameManager, dataExtractor):
        InfoFrameComponent.__init__(self, frameManager)
        self.dataExtractor = dataExtractor
        assert isinstance(self.dataExtractor, AcdOptiDataExtractor)
        
        self.baseWidget = gtk.VBox()
        
        self.baseWidget.pack_start(gtk.Label("Plots for '" + self.dataExtractor.instName + "'"), expand = False, padding=5)
    
        self.__updateTable()
        self.__tableScroll = gtk.ScrolledWindow()
        self.__tableScroll.set_policy(gtk.POLICY_NEVER,gtk.POLICY_AUTOMATIC)
        self.__tableScroll.add_with_viewport(self.__tableWidget)
        self.__tableScroll.set_shadow_type(gtk.SHADOW_NONE)
        self.baseWidget.pack_start(self.__tableScroll, expand=True, padding = 10)
        
        self.__addButton = gtk.Button(stock=gtk.STOCK_ADD)
        self.__addButton.connect("clicked", self.event_button_add, None)
        self.baseWidget.pack_start(self.__addButton,expand=False)
        
        self.__closeButton = gtk.Button("_Close plots view")
        self.__closeButton.connect("clicked", self.event_button_close, None)
        self.baseWidget.pack_start(self.__closeButton,expand=False)

        self.baseWidget.show_all()
    
    def __updateTable(self):
        print "DataExtractorPlots::__updateTable()"
        
        numPlots = len(self.dataExtractor.plots)
        numCols = 4
        
        if self.__tableWidget != None:
            children = self.__tableWidget.get_children()
            for child in children:
                self.__tableWidget.remove(child)
            self.__tableWidget.resize(numPlots+2, numCols)
        else:
            self.__tableWidget=gtk.Table(numPlots+2, numCols, False)
            self.__tableWidget.set_row_spacings(3)
            self.__tableWidget.set_col_spacings(5)
            
            
        self.__tableWidget.attach(gtk.Label("Plot name"),       0,1,0,1, xoptions=gtk.FILL|gtk.EXPAND,yoptions=gtk.FILL)
        self.__tableWidget.attach(gtk.Label("Plot type"),       1,2,0,1, xoptions=gtk.FILL|gtk.EXPAND,yoptions=gtk.FILL)
        self.__tableWidget.attach(gtk.Label("Manipulate plot"), 2,3,0,1, xoptions=gtk.FILL,yoptions=gtk.FILL)
        self.__tableWidget.attach(gtk.Label("Delete"),          3,4,0,1, xoptions=gtk.FILL,yoptions=gtk.FILL)
        
        self.__tableWidget.attach(gtk.HSeparator(),0,4,1,2, xoptions=gtk.FILL,yoptions=gtk.FILL)
        
        for (f,idx) in zip(self.dataExtractor.plots,xrange(numPlots)):
            name = f.instName
            typ = f.plotType
            tidx = idx+2
            
            self.__tableWidget.attach(gtk.Label(name),        0,1,tidx,tidx+1, xoptions=gtk.FILL|gtk.EXPAND, yoptions=gtk.FILL)
            self.__tableWidget.attach(gtk.Label(typ),         1,2,tidx,tidx+1, xoptions=gtk.FILL|gtk.EXPAND, yoptions=gtk.FILL)

            manipButton = gtk.Button("Manipulate...")
            manipButton.connect("clicked", self.event_button_manipulate, f)
            self.__tableWidget.attach(manipButton, 2,3,tidx,tidx+1, xoptions=gtk.FILL, yoptions=gtk.FILL)
            
            delButton = gtk.Button("Delete")
            delButton.connect("clicked", self.event_button_delete, idx)
            self.__tableWidget.attach(delButton, 3,4,tidx,tidx+1,xoptions=gtk.FILL, yoptions=gtk.FILL)
                
        self.__tableWidget.show_all()
    
    def event_button_manipulate(self,widget,data):
        #data = pointer to plot object to manipulate
        if data.plotType == "DataExtractorPlot2D":
            self.frameManager.push(DataExtractorPlots_Plot2D(self.frameManager, data))
        elif data.plotType == "DataExtractorPlot3D":
            self.frameManager.push(DataExtractorPlots_Plot3D(self.frameManager, data))
        elif data.plotType == "DataExtractorPlotScaleOptim":
            self.frameManager.push(DataExtractorPlots_ScaleOptim(self.frameManager, data))
        else:
            print "Error in DataExtractorPlots::event_button_manipulate(): Unknown plot type '" + data.plotType + "'"
    def event_button_delete(self,widget,data):
        #data = element index in plots to delete
        del self.dataExtractor.plots[data]
        self.dataExtractor.write()
        self.__updateTable()
        
    
    def event_button_add(self,widget,data):
        
        (type, name, response) = self.getTypeAndNameDialog_currentBase(("DataExtractorPlot2D","DataExtractorPlot3D", "DataExtractorPlotScaleOptim"), "New plotter")
        
        if response == gtk.RESPONSE_OK:
            if name == None:
                name = type
            self.dataExtractor.plots.append(AcdOptiDataExtractorPlot.getPlotClass(type, self.dataExtractor, name))
            self.dataExtractor.write()
            self.__updateTable()
            self.dataExtractor.write()
        
    def event_button_close(self,widget,data):
        #self.__saveTableToPlots()
        self.frameManager.pop()
        
class DataExtractorPlots_Plot2D(InfoFrameComponent):
    """
    2D plot
    """
    
    plotObject = None
    
    __varXentry = None
    __varYentry = None
    
    __plotButton = None
    
    __closeButton = None
    
    
    def __init__(self, frameManager, plotObject):
        InfoFrameComponent.__init__(self, frameManager)
        assert isinstance(plotObject, DataExtractorPlot2D) 
        self.plotObject = plotObject
        
        self.baseWidget = gtk.VBox()
        
        self.baseWidget.pack_start(gtk.Label("DataExtractorPlot2D, instName = " + self.plotObject.instName), padding=5, expand=False)
        
        varXbox = gtk.HBox()
        varXbox.pack_start(gtk.Label("X variable:"), padding=5,expand=False)
        self.__varXentry = gtk.Entry()
        self.__varXentry.set_text(self.plotObject.varX)
        varXbox.pack_start(self.__varXentry, padding=5, expand=True)
        self.baseWidget.pack_start(varXbox, padding=5, expand=False)
        
        varYbox = gtk.HBox()
        varYbox.pack_start(gtk.Label("Y variable:"), padding=5,expand=False)
        self.__varYentry = gtk.Entry()
        self.__varYentry.set_text(self.plotObject.varY)
        varYbox.pack_start(self.__varYentry, padding=5, expand=True)
        self.baseWidget.pack_start(varYbox, padding=5, expand=False)
        
        self.baseWidget.pack_start(gtk.Label("Available variables:\n (textbox just to enable copy/paste, nothing is saved)"), padding=5,expand=False)
        varString = ""
        for k in self.plotObject.dataExtractor.keyNames:
            varString += k + " "
        varString = varString[:-1]
        varEntry = gtk.Entry()
        varEntry.set_text(varString)
        self.baseWidget.pack_start(varEntry, padding=5, expand=True)
        
        self.__plotButton = gtk.Button("Show _plot!")
        if not self.plotObject.dataExtractor.lockdown:
            self.__plotButton.set_sensitive(False)
        self.__plotButton.connect("clicked", self.event_button_plot, None)
        self.baseWidget.pack_start(self.__plotButton, padding=5, expand=False)
        
        self.__closeButton = gtk.Button("_Close plot view")
        self.__closeButton.connect("clicked", self.event_button_close, None)
        self.baseWidget.pack_start(self.__closeButton,padding = 5, expand=False)

        self.baseWidget.show_all()
    
    def saveToPlot(self):
        x = self.__varXentry.get_text().strip()
        y = self.__varYentry.get_text().strip()
        if " " in x or " " in y:
            mDia = gtk.MessageDialog(self.getBaseWindow(),
                                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                     gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                     "Space in X or Y variable, not saving to plot." )
            mDia.run()
            mDia.destroy()
            return
        self.plotObject.varX = x
        self.plotObject.varY = y
        self.plotObject.updateSettingsDict()
        self.plotObject.dataExtractor.write()
    
    def event_button_plot(self, widget, data):
        self.saveToPlot()
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print "Could not import matplotlib.pyplot, aborting plot. You should still be able to doExport()!"
            return
        (X,Y) = self.plotObject.getData()
        plt.plot(X,Y, '+')
        plt.xlabel(self.plotObject.varX)
        plt.ylabel(self.plotObject.varY)
        
        xRange = abs(max(X)-min(X))
        yRange = abs(max(Y)-min(Y))
        plt.axis([min(X)-0.1*xRange, max(X)+0.1*xRange, min(Y)-0.1*yRange, max(Y)+0.1*yRange])
        
        plt.show()
        
        gtk.main()
    
    def event_button_close(self,widget,data):
        self.saveToPlot()
        self.frameManager.pop()
    def event_delete(self):
        #self.saveToPlot()
        return False

class DataExtractorPlots_Plot3D(InfoFrameComponent):
    """
    3D plot
    """
    
    plotObject = None
    
    __varXentry = None
    __varYentry = None
    __varZentry = None
    
    __fittedModelEntry = None
    __fitPlaneButton = None
    __fitQuadButton = None
    __fittedNdofEntry = None
    __fittedREntry = None
    model = None
    
    __plotLimitEntry = None
    __plotLimitCheck = None
    __plotLimitPruneCheck = None

    __extractionModeButton_all  = None
    __extractionModeButton_mean = None
    __extractionModeButton_min  = None
    __extractionModeButton_max  = None
    
    __dedupButton_max  = None
    __dedupButton_mean = None
    __dedupButton_min  = None

    __plotDelunayButton = None
    __plotDelunayColorsButton = None
    __plotDelunayColorsLogButton = None
    __plotDelunayContoursButton = None
    __numContoursEntry = None

    __plot3DPointCloudButton = None
    __plot3DPointCloudFitButton = None
    
    __closeButton = None
    
    
    def __init__(self, frameManager, plotObject):
        InfoFrameComponent.__init__(self, frameManager)
        assert isinstance(plotObject, DataExtractorPlot3D) 
        self.plotObject = plotObject
        
        self.baseWidget = gtk.VBox()
        
        self.baseWidget.pack_start(gtk.Label("DataExtractorPlot3D, instName = " + self.plotObject.instName), padding=5, expand=False)
        
        varXbox = gtk.HBox()
        varXbox.pack_start(gtk.Label("X variable:"), padding=5,expand=False)
        self.__varXentry = gtk.Entry()
        self.__varXentry.set_text(self.plotObject.varX)
        varXbox.pack_start(self.__varXentry, padding=5, expand=True)
        self.baseWidget.pack_start(varXbox, padding=5, expand=False)
        
        varYbox = gtk.HBox()
        varYbox.pack_start(gtk.Label("Y variable:"), padding=5,expand=False)
        self.__varYentry = gtk.Entry()
        self.__varYentry.set_text(self.plotObject.varY)
        varYbox.pack_start(self.__varYentry, padding=5, expand=True)
        self.baseWidget.pack_start(varYbox, padding=5, expand=False)
        
        varZbox = gtk.HBox()
        varZbox.pack_start(gtk.Label("Z variable:"), padding=5,expand=False)
        self.__varZentry = gtk.Entry()
        ZentryTxt = ""
        for v in self.plotObject.varZ.vals:
            print v
            ZentryTxt += v + ", "
        ZentryTxt = ZentryTxt[:-2]
        print "ZentryTxt", ZentryTxt
        self.__varZentry.set_text(ZentryTxt)
        varZbox.pack_start(self.__varZentry, padding=5, expand=True)
        self.baseWidget.pack_start(varZbox, padding=5, expand=False)
        
        self.baseWidget.pack_start(gtk.HSeparator(), padding=10, expand=False)
        
        varAvailBox = gtk.HBox() 
        varAvailBox.pack_start(gtk.Label("Available variables:"), padding=5,expand=False)
        varString = ""
        for k in self.plotObject.dataExtractor.keyNames:
            varString += k + " "
        varString = varString[:-1]
        varEntry = gtk.Entry()
        varEntry.set_text(varString)
        varAvailBox.pack_start(varEntry, padding=5, expand=True)
        self.baseWidget.pack_start(varAvailBox,padding=5,expand=False)
        
        self.baseWidget.pack_start(gtk.HSeparator(), padding=10, expand=False)
        
        fittedModelBox = gtk.HBox()
        fittedModelBox.pack_start(gtk.Label("Fitted model:"), padding=5, expand=False)
        self.__fittedModelEntry = gtk.Entry()
        fittedModelBox.pack_start(self.__fittedModelEntry, padding=5, expand=True)
        self.baseWidget.pack_start(fittedModelBox, padding=5, expand=False)
        
        fitStatsBox = gtk.HBox()
        fitStatsBox.pack_start(gtk.Label("NDOF ="), padding=5, expand=False)
        self.__fittedNdofEntry = gtk.Entry()
        self.__fittedNdofEntry.set_sensitive(False)
        fitStatsBox.pack_start(self.__fittedNdofEntry, padding=5, expand=True)
        fitStatsBox.pack_start(gtk.Label("R ="), padding=5, expand=False)
        self.__fittedREntry = gtk.Entry()
        self.__fittedREntry.set_sensitive(False)
        fitStatsBox.pack_start(self.__fittedREntry, padding=5, expand=True)
        self.baseWidget.pack_start(fitStatsBox, padding=5,expand=False)

        fitButtonBox = gtk.HBox()
        self.__fitPlaneButton = gtk.Button("Fit plane")
        self.__fitPlaneButton.connect("clicked", self.event_button_fitPlane, None)
        if not self.plotObject.dataExtractor.lockdown:
            self.__fitPlaneButton.set_sensitive(False) 
        fitButtonBox.pack_start(self.__fitPlaneButton, padding=5, expand=True)
        self.__fitQuadButton = gtk.Button("Fit quad function")
        self.__fitQuadButton.connect("clicked", self.event_button_fitQuad, None)
        if not self.plotObject.dataExtractor.lockdown:
            self.__fitQuadButton.set_sensitive(False)
        fitButtonBox.pack_start(self.__fitQuadButton, padding=5, expand=True)
        self.baseWidget.pack_start(fitButtonBox, padding=5, expand=False)
        
        
        self.baseWidget.pack_start(gtk.HSeparator(), padding=10, expand=False)

        plotLimitBox = gtk.HBox()
        plotLimitBox.pack_start(gtk.Label("Plot points below z ="), padding=5, expand=False)
        self.__plotLimitEntry = gtk.Entry()
        self.__plotLimitEntry.set_text(self.plotObject.limit)
        plotLimitBox.pack_start(self.__plotLimitEntry, padding=5, expand=True)
        self.__plotLimitCheck = gtk.CheckButton(label="Use limit")
        if self.plotObject.useLimit == "True":
            self.__plotLimitCheck.set_active(True);
        else:
            self.__plotLimitCheck.set_active(False);
        plotLimitBox.pack_start(self.__plotLimitCheck, padding=5, expand=False)
        self.__plotLimitPruneCheck = gtk.CheckButton(label="Prune")
        self.__plotLimitPruneCheck.set_active(False);
        plotLimitBox.pack_start(self.__plotLimitPruneCheck, padding=5, expand=False)
        
        plotLimitBox.pack_start(gtk.VSeparator(), padding=5, expand=False)

        extractionModeBox = gtk.VBox()
        extractionModeLabel = gtk.Label("ExtractionMode")
        extractionModeLabel.set_angle(90)
        plotLimitBox.pack_start(extractionModeLabel,expand=False)
        self.__extractionModeButton_all = gtk.RadioButton(None,"All")
        extractionModeBox.pack_start(self.__extractionModeButton_all)
        self.__extractionModeButton_mean = gtk.RadioButton(self.__extractionModeButton_all,"Mean")
        extractionModeBox.pack_start(self.__extractionModeButton_mean)
        self.__extractionModeButton_min = gtk.RadioButton(self.__extractionModeButton_all,"Min")
        extractionModeBox.pack_start(self.__extractionModeButton_min)
        self.__extractionModeButton_max = gtk.RadioButton(self.__extractionModeButton_all,"Max")
        extractionModeBox.pack_start(self.__extractionModeButton_max)
        if self.plotObject.extractionMode=="all":
            self.__extractionModeButton_all.set_active(True)
        elif self.plotObject.extractionMode=="mean":
            self.__extractionModeButton_mean.set_active(True)
        elif self.plotObject.extractionMode=="min":
            self.__extractionModeButton_min.set_active(True)
        elif self.plotObject.extractionMode=="max":
            self.__extractionModeButton_max.set_active(True)
        plotLimitBox.pack_start(extractionModeBox,padding=5,expand=False)

        plotLimitBox.pack_start(gtk.VSeparator(), padding=5, expand=False)

        dedupBox = gtk.VBox()
        dedupLabel = gtk.Label("Dedup")
        dedupLabel.set_angle(90)
        plotLimitBox.pack_start(dedupLabel,expand=False)
        self.__dedupButton_max  = gtk.RadioButton(None,"Max")
        dedupBox.pack_start(self.__dedupButton_max)
        self.__dedupButton_mean = gtk.RadioButton(self.__dedupButton_max,"Mean")
        dedupBox.pack_start(self.__dedupButton_mean)
        self.__dedupButton_mean.set_active(True)
        self.__dedupButton_min  = gtk.RadioButton(self.__dedupButton_max,"Min")
        dedupBox.pack_start(self.__dedupButton_min)
        plotLimitBox.pack_start(dedupBox,padding=5,expand=False)

        self.baseWidget.pack_start(plotLimitBox, padding=5, expand=False);    

        self.__plotDelunayButton = gtk.Button("Show Delunay triangulation of points")
        if not self.plotObject.dataExtractor.lockdown:
            self.__plotDelunayButton.set_sensitive(False)
        self.__plotDelunayButton.connect("clicked", self.event_button_plotDelunay, None)
        self.baseWidget.pack_start(self.__plotDelunayButton, padding=5, expand=False)

        self.__plotDelunayColorsButton = gtk.Button("Show tripcolor plot")
        if not self.plotObject.dataExtractor.lockdown:
            self.__plotDelunayColorsButton.set_sensitive(False)
        self.__plotDelunayColorsButton.connect("clicked", self.event_button_plotDelunayColors, None)
        self.baseWidget.pack_start(self.__plotDelunayColorsButton, padding=5, expand=False)

        self.__plotDelunayColorsLogButton = gtk.Button("Show log-scale tripcolor plot")
        if not self.plotObject.dataExtractor.lockdown:
            self.__plotDelunayColorsLogButton.set_sensitive(False)
        self.__plotDelunayColorsLogButton.connect("clicked", self.event_button_plotDelunayColors, "log")
        self.baseWidget.pack_start(self.__plotDelunayColorsLogButton, padding=5, expand=False)
        
        contoursBox = gtk.HBox(homogeneous=True)
        self.__plotDelunayContoursButton = gtk.Button("Show tricontourf plot")
        if not self.plotObject.dataExtractor.lockdown:
            self.__plotDelunayContoursButton.set_sensitive(False)
        self.__plotDelunayContoursButton.connect("clicked", self.event_button_plotDelunayColors, "contour")
        contoursBox.pack_start(self.__plotDelunayContoursButton, padding=5, expand=False);
        self.__numContoursEntry = gtk.Entry()
        self.__numContoursEntry.set_text(self.plotObject.numContours)
        contoursBox.pack_start(self.__numContoursEntry, padding=5, expand=True)
        self.baseWidget.pack_start(contoursBox, padding=5, expand=False);

        self.baseWidget.pack_start(gtk.HSeparator(), padding=10, expand=False)

        self.__plot3DPointCloudButton = gtk.Button("Show 3D point cloud")
        if not self.plotObject.dataExtractor.lockdown:
            self.__plot3DPointCloudButton.set_sensitive(False)
        self.__plot3DPointCloudButton.connect("clicked", self.event_button_plotPointcloud, None)
        self.baseWidget.pack_start(self.__plot3DPointCloudButton, padding=5, expand=False)
        
        self.__plot3DPointCloudFitButton = gtk.Button("Show 3D point cloud + fit")
        self.__plot3DPointCloudFitButton.set_sensitive(False)
        self.__plot3DPointCloudFitButton.connect("clicked", self.event_button_plotPointcloud, "Fit")
        self.baseWidget.pack_start(self.__plot3DPointCloudFitButton, padding=5, expand=False)
        
        
        self.baseWidget.pack_start(gtk.HSeparator(), padding=10, expand=False)
        
        self.__closeButton = gtk.Button("_Close plot view")
        self.__closeButton.connect("clicked", self.event_button_close, None)
        self.baseWidget.pack_start(self.__closeButton,padding = 5, expand=False)

        self.baseWidget.show_all()
    
    def saveToPlot(self):
        x = self.__varXentry.get_text().strip()
        y = self.__varYentry.get_text().strip()
        #z = self.__varZentry.get_text().strip()
        zEntryTxt = self.__varZentry.get_text().split(",")
        z = []
        zEntryBAD = False
        for k in zEntryTxt:
            k2 = k.strip()
            if " " in k2:
                print "zEntry element contained space, skipping '" + k2 + "'"
                zEntryBAD = True
                continue
            z.append(k2)

        l = self.__plotLimitEntry.get_text().strip()
        nc = self.__numContoursEntry.get_text().strip()
        if " " in x or " " in y or zEntryBAD or " " in l or " " in nc:
            mDia = gtk.MessageDialog(self.getBaseWindow(),
                                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                     gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                     "Space in X, Y, or Z variable(s), or plotLimit/numContours -- not saving to plot." )
            mDia.run()
            mDia.destroy()
            return

        self.plotObject.varX = x
        self.plotObject.varY = y

        #self.plotObject.varZ = z
        self.plotObject.varZ = DataDict()
        for k in z:
            self.plotObject.varZ.pushBack("var", k)

        self.plotObject.limit = l
        self.plotObject.numContours = nc
        
        if self.__plotLimitCheck.get_active():
            self.plotObject.useLimit = "True"
        else:
            self.plotObject.useLimit = "False"

        if self.__extractionModeButton_all.get_active():
           self.plotObject.extractionMode = "all"
        elif self.__extractionModeButton_mean.get_active():
           self.plotObject.extractionMode = "mean"
        elif self.__extractionModeButton_min.get_active():
            self.plotObject.extractionMode = "min"
        elif self.__extractionModeButton_max.get_active():
            self.plotObject.extractionMode = "max"

        self.plotObject.updateSettingsDict()
        self.plotObject.dataExtractor.write()

    def event_button_fitPlane(self,widget,data):
        (model, ndof, R2) = self.plotObject.fitPlane()
        self.model = model
        modelTxt = str(model[0]) + "+" + str(model[1])+"*X+" + str(model[2])+"*Y" 
        self.__fittedModelEntry.set_text(modelTxt)
        self.__fittedNdofEntry.set_text(str(ndof))
        import math as m
        self.__fittedREntry.set_text(str(m.sqrt(R2)))
        self.__plot3DPointCloudFitButton.set_sensitive(True)

        
    def event_button_fitQuad(self,widget,data):
        (model, ndof, R2) = self.plotObject.fitQuad()
        self.model = model
        modelTxt = str(model[0]) + "+" + str(model[1])+"*X+" + str(model[2])+"*Y+" + str(model[3])+"*X^2+" + str(model[4])+"*Y^2+" + str(model[5])+"*X*Y" 
        self.__fittedModelEntry.set_text(modelTxt)
        self.__fittedNdofEntry.set_text(str(ndof))
        import math as m
        self.__fittedREntry.set_text(str(m.sqrt(R2)))
        self.__plot3DPointCloudFitButton.set_sensitive(True)

        
    def event_button_plotDelunay(self, widget, data):
        self.saveToPlot()
        try:
            import matplotlib.pyplot as plt
            import matplotlib.tri as tri
        except ImportError:
            print "Could not import matplotlib, aborting plot. You should still be able to doExport()!"
            return

        limit = None
        if self.__plotLimitCheck.get_active():
            try:
                limit = float(self.__plotLimitEntry.get_text())
            except ValueError:
                limit = None
        if self.__plotLimitCheck.get_active() and self.__plotLimitPruneCheck.get_active():
            (X,Y,Z) = self.plotObject.getBelowLimit(limit)
        else:
            (X,Y,Z) = self.plotObject.getData()

        print "X:", X
        print "Y:", Y
        print "Z:", Z
        print "Deduplicating..."
        (X,Y,Z,N) = self.plotObject.deduplicate(X,Y,Z)
        print "X:", X
        print "Y:", Y
        print "Z:", Z
        print "N:", N
        if len(X) < 3:
            mDia = gtk.MessageDialog(self.getBaseWindow(),
                                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                     gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                     "Need at least three distinct points to make grid, only have: X=%s, Y=%s" %(str(X), str(Y)) )
            mDia.run()
            mDia.destroy()
            return
        triang = tri.Triangulation(X, Y)
        plt.triplot(triang, 'bo-')
        
        plt.xlabel(self.plotObject.varX)
        plt.ylabel(self.plotObject.varY)
        
        xRange = abs(max(X)-min(X))
        yRange = abs(max(Y)-min(Y))
        plt.axis([min(X)-0.1*xRange, max(X)+0.1*xRange, min(Y)-0.1*yRange, max(Y)+0.1*yRange])
        
        plt.show()
        
        gtk.main()
    
    def event_button_plotDelunayColors(self, widget, data):
        self.saveToPlot()
        try:
            import matplotlib.pyplot as plt
            import matplotlib.tri as tri
            import numpy as np
        except ImportError:
            print "Could not import matplotlib or numpy, aborting plot. You should still be able to doExport()!"
            return

        limit = None
        if self.__plotLimitCheck.get_active():
            try:
                limit = float(self.__plotLimitEntry.get_text())
            except ValueError:
                limit = None
        if self.__plotLimitCheck.get_active() and self.__plotLimitPruneCheck.get_active():
            (X,Y,Z) = self.plotObject.getBelowLimit(limit)
        else:
            (X,Y,Z) = self.plotObject.getData()

        # print "X:", X
        # print "Y:", Y
        # print "Z:", Z
        # print "Deduplicating..."
        dedupMode = "mean"
        if self.__dedupButton_max.get_active():
            dedupMode = "max"
        elif self.__dedupButton_min.get_active():
            dedupMode = "min"            
        (X,Y,Z,N) = self.plotObject.deduplicate(X,Y,Z, dedupMode)
        # print "X:", X
        # print "Y:", Y
        # print "Z:", Z
        # print "N:", N
        if len(X) < 3:
            mDia = gtk.MessageDialog(self.getBaseWindow(),
                                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                     gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                     "Need at least three distinct points to make grid, only have: X=%s, Y=%s" %(str(X), str(Y)) )
            mDia.run()
            mDia.destroy()
            return
        triang = tri.Triangulation(X, Y)
        if data == "log":
            logZ = np.log10(Z);
            # print "logZ =", logZ
            # ticksMin = np.floor(min(logZ)*100)/100.0
            # ticksMax = np.ceil(max(logZ*100))/100.0
            # print "ticksMin =", ticksMin, "ticksMax =", ticksMax
            # ticks = np.linspace(ticksMin, ticksMax, ticksMax-ticksMin+1)-ticksMin;
            # print "ticks =", ticks
            plt.tripcolor(triang, logZ, shading='gouraud')
            cbar = plt.colorbar()
            #cbar.set_ticks(ticks)
            #ticklabels = map(lambda t: "$10^{"+( "%d"%(abs(t)+ticksMin,) )+"}$", ticks)
            #print "ticklabels =", ticklabels
            #cbar.set_ticklabels(ticklabels)
        elif data == "contour":
            try:
                nc = int(self.__numContoursEntry.get_text().strip())
            except ValueError:
                print "numContours invalid, use 10 countours"
                nc = 10
            if limit != None and not self.__plotLimitPruneCheck.get_active() and limit < max(Z):
                plt.tricontourf(triang,Z, np.linspace(min(Z),limit,nc), vmax=limit, extend='max')
            else:
                plt.tricontourf(triang,Z, nc)
            plt.colorbar()
        else:
            plt.tripcolor(triang, Z, shading='gouraud')
            plt.colorbar()

        (X2,Y2,Z2) = self.plotObject.getData()
        plt.plot(X2,Y2, 'b+')
        plt.plot(X,Y,'r+')

        plt.xlabel(self.plotObject.varX)
        plt.ylabel(self.plotObject.varY)

        plt.title("DataExtractorPlot3D, instName = " + self.plotObject.instName + ", data='" + str(data) + "'")
        
        xRange = abs(max(X)-min(X))
        yRange = abs(max(Y)-min(Y))
        plt.axis([min(X)-0.1*xRange, max(X)+0.1*xRange, min(Y)-0.1*yRange, max(Y)+0.1*yRange])
        
        plt.show()
        
        gtk.main()
    
    def event_button_plotPointcloud(self, widget, data):
        self.saveToPlot()
        try:
            import matplotlib.pyplot as plt
            from mpl_toolkits.mplot3d import Axes3D
        except ImportError:
            print "Could not import matplotlib, aborting plot. You should still be able to doExport()!"
            return

        limit = None
        if self.__plotLimitCheck.get_active():
            try:
                limit = float(self.__plotLimitEntry.get_text())
            except ValueError:
                limit = None
        if limit != None and self.__plotLimitPruneCheck.get_active():
            (X,Y,Z) = self.plotObject.getBelowLimit(limit)
        else:
            (X,Y,Z) = self.plotObject.getData()
        
        print "X:", X
        print "Y:", Y
        print "Z:", Z
        
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        ax.scatter(X, Y, Z)
        if limit != None and not self.__plotLimitPruneCheck.get_active() and limit > min(Z):
            ax.set_zlim(min(Z), limit+0.1*abs(limit-min(Z)))
        
        if data == "Fit":
            print "Ploting the fit..."
            import numpy as np
            Xr = np.linspace(min(X), max(X))
            Yr = np.linspace(min(Y), max(Y))
            Xr, Yr = np.meshgrid(Xr, Yr)
            #Zr = np.zeros_like(Xr)
            if len(self.model) == 3:
                Zr = self.model[0] + self.model[1]*Xr + self.model[2]*Yr
            elif len(self.model) == 6:
                Zr = self.model[0] + self.model[1]*Xr + self.model[2]*Yr + self.model[3]*Xr**2 + self.model[4]*Yr**2 + self.model[5]*Xr*Yr
            surf = ax.plot_surface(Xr, Yr, Zr)
            
        #xRange = abs(max(X)-min(X))
        #yRange = abs(max(Y)-min(Y))
        
        ax.set_xlabel(self.plotObject.varX)
        ax.set_ylabel(self.plotObject.varY)
        ax.set_zlabel(self.plotObject.varZ)
        
        plt.show()
        
        gtk.main()
    
    def event_button_close(self,widget,data):
        self.saveToPlot()
        self.frameManager.pop()
    def event_delete(self):
        #self.saveToPlot()
        return False

class DataExtractorPlots_ScaleOptim(InfoFrameComponent):
    """
    ScaleOptim plot
    """
    
    plotObject = None
    
    __varX_entry = None
    __varY_entry = None
    
    __constE_entry = None
    __constE_2_entry = None
    __varNormE_entry = None
    
    __constSC_entry = None
    __constSC_2_entry = None
    __varNormSC_entry = None
    
    __constPC_entry = None
    __constPC_2_entry = None
    __varFrequency_entry = None
    __varRQ_entry = None
    __varVg_entry = None
    __varRadius_entry = None
    
    __enable_E = None
    __enable_SC = None
    __enable_PC = None
    
    __optimistic_optimistic  = None
    __optimistic_both        = None
    __optimistic_pessimistic = None
    
    __minORmean_min  = None
    __minORmean_mean = None
    
    __filterDoubles_none    = None
    __filterDoubles_best    = None
    __filterDoubles_average = None

    __enable_gradientRepresentation = None

    __plotButtonX = None
    __plotButtonY = None

    __plotTripcontourfButton = None
    __numContoursEntry = None

    __plot3DpointCloudButton = None
    __plot3DtrisurfButton = None

    __closeButton = None
    
    
    def __init__(self, frameManager, plotObject):
        InfoFrameComponent.__init__(self, frameManager)
        assert isinstance(plotObject, DataExtractorPlotsScaleOptim) 
        self.plotObject = plotObject
        
        self.baseWidget = gtk.VBox()
        
        self.baseWidget.pack_start(gtk.Label("DataExtractorPlotScaleOptim, instName = " + self.plotObject.instName), padding=5, expand=False)
        
        varXbox = gtk.HBox()
        varXbox.pack_start(gtk.Label("X variable:"), padding=5,expand=False)
        self.__varX_entry = gtk.Entry()
        self.__varX_entry.set_text(self.plotObject.varX)
        varXbox.pack_start(self.__varX_entry, padding=5, expand=True)
        self.baseWidget.pack_start(varXbox, padding=5, expand=False)
        
        varYbox = gtk.HBox()
        varYbox.pack_start(gtk.Label("Y variable:"), padding=5,expand=False)
        self.__varY_entry = gtk.Entry()
        self.__varY_entry.set_text(self.plotObject.varY)
        varYbox.pack_start(self.__varY_entry, padding=5, expand=True)
        self.baseWidget.pack_start(varYbox, padding=5, expand=False)
        
        self.baseWidget.pack_start(gtk.HSeparator(), padding=10, expand=False)
        
        constEbox = gtk.HBox()
        constEbox.pack_start(gtk.Label("constE:"), padding=5,expand=False)
        self.__constE_entry = gtk.Entry()
        self.__constE_entry.set_text(self.plotObject.constE)
        constEbox.pack_start(self.__constE_entry, padding=5, expand=True)
        constEbox.pack_start(gtk.Label("-"), padding=5,expand=False)
        self.__constE_2_entry = gtk.Entry()
        self.__constE_2_entry.set_text(self.plotObject.constE_2)
        constEbox.pack_start(self.__constE_2_entry, padding=5, expand=True)
        constEbox.pack_start(gtk.Label("^6 [(MV/m)^6] * 200 ns"), padding=5,expand=False)
        self.baseWidget.pack_start(constEbox, padding=5, expand=False)
        
        varNormEbox = gtk.HBox()
        varNormEbox.pack_start(gtk.Label("varNormE:"), padding=5,expand=False)
        self.__varNormE_entry = gtk.Entry()
        varNormE_entry_text = ""
        for v in self.plotObject.varNormE:
            varNormE_entry_text += v + ", "
        varNormE_entry_text = varNormE_entry_text[:-2]
        self.__varNormE_entry.set_text(varNormE_entry_text)
        varNormEbox.pack_start(self.__varNormE_entry, padding=5, expand=True)
        self.baseWidget.pack_start(varNormEbox, padding=5, expand=False)
        
        self.baseWidget.pack_start(gtk.HSeparator(), padding=10, expand=False)
        
        constSCbox = gtk.HBox()
        constSCbox.pack_start(gtk.Label("constSC:"), padding=5,expand=False)
        self.__constSC_entry = gtk.Entry()
        self.__constSC_entry.set_text(self.plotObject.constSC)
        constSCbox.pack_start(self.__constSC_entry, padding=5, expand=True)
        constSCbox.pack_start(gtk.Label("-"), padding=5,expand=False)
        self.__constSC_2_entry = gtk.Entry()
        self.__constSC_2_entry.set_text(self.plotObject.constSC_2)
        constSCbox.pack_start(self.__constSC_2_entry, padding=5, expand=True)
        constSCbox.pack_start(gtk.Label("^3 [(MW/mm^2)^3] * 200 ns"), padding=5,expand=False)
        self.baseWidget.pack_start(constSCbox, padding=5, expand=False)
        
        varNormSCbox = gtk.HBox()
        varNormSCbox.pack_start(gtk.Label("varNormSC:"), padding=5,expand=False)
        self.__varNormSC_entry = gtk.Entry()
        varNormSC_entry_text = ""
        for v in self.plotObject.varNormSC:
            varNormSC_entry_text += v + ", "
        varNormSC_entry_text = varNormSC_entry_text[:-2]
        self.__varNormSC_entry.set_text(varNormSC_entry_text)
        varNormSCbox.pack_start(self.__varNormSC_entry, padding=5, expand=True)
        self.baseWidget.pack_start(varNormSCbox, padding=5, expand=False)
        
        self.baseWidget.pack_start(gtk.HSeparator(), padding=10, expand=False)
        
        constPCbox = gtk.HBox()
        constPCbox.pack_start(gtk.Label("constPC:"), padding=5,expand=False)
        self.__constPC_entry = gtk.Entry()
        self.__constPC_entry.set_text(self.plotObject.constPC)
        constPCbox.pack_start(self.__constPC_entry, padding=5, expand=True)
        constPCbox.pack_start(gtk.Label("-"), padding=5,expand=False)
        self.__constPC_2_entry = gtk.Entry()
        self.__constPC_2_entry.set_text(self.plotObject.constPC_2)
        constPCbox.pack_start(self.__constPC_2_entry, padding=5, expand=True)
        constPCbox.pack_start(gtk.Label("^3 [(MW/mm)^3] * 200 ns"), padding=5,expand=False)
        self.baseWidget.pack_start(constPCbox, padding=5, expand=False)
        
        varFrequencybox = gtk.HBox()
        varFrequencybox.pack_start(gtk.Label("varFrequency:"), padding=5,expand=False)
        self.__varFrequency_entry = gtk.Entry()
        self.__varFrequency_entry.set_text(self.plotObject.varFrequency)
        varFrequencybox.pack_start(self.__varFrequency_entry, padding=5, expand=True)
        varFrequencybox.pack_start(gtk.Label("(in [Hz])"), padding=5,expand=False)
        self.baseWidget.pack_start(varFrequencybox, padding=5, expand=False)
        
        varRQbox = gtk.HBox()
        varRQbox.pack_start(gtk.Label("varRQ:"), padding=5,expand=False)
        self.__varRQ_entry = gtk.Entry()
        self.__varRQ_entry.set_text(self.plotObject.varRQ)
        varRQbox.pack_start(self.__varRQ_entry, padding=5, expand=True)
        varRQbox.pack_start(gtk.Label("(In [Ohm/mm])"), padding=5,expand=False)
        self.baseWidget.pack_start(varRQbox, padding=5, expand=False)
        
        varVgbox = gtk.HBox()
        varVgbox.pack_start(gtk.Label("varVg:"), padding=5,expand=False)
        self.__varVg_entry = gtk.Entry()
        self.__varVg_entry.set_text(self.plotObject.varVg)
        varVgbox.pack_start(self.__varVg_entry, padding=5, expand=True)
        varVgbox.pack_start(gtk.Label("(In [m/s])"), padding=5,expand=False)
        self.baseWidget.pack_start(varVgbox, padding=5, expand=False)
        
        varRadiusbox = gtk.HBox()
        varRadiusbox.pack_start(gtk.Label("varRadius:"), padding=5,expand=False)
        self.__varRadius_entry = gtk.Entry()
        self.__varRadius_entry.set_text(self.plotObject.varRadius)
        varRadiusbox.pack_start(self.__varRadius_entry, padding=5, expand=True)
        varRadiusbox.pack_start(gtk.Label("(In [mm])"), padding=5,expand=False)
        self.baseWidget.pack_start(varRadiusbox, padding=5, expand=False)
        
        self.baseWidget.pack_start(gtk.HSeparator(), padding=10, expand=False)
        
        varAvailBox = gtk.HBox() 
        varAvailBox.pack_start(gtk.Label("Available variables:"), padding=5,expand=False)
        varString = ""
        for k in self.plotObject.dataExtractor.keyNames:
            varString += k + " "
        varString = varString[:-1]
        varEntry = gtk.Entry()
        varEntry.set_text(varString)
        varAvailBox.pack_start(varEntry, padding=5, expand=True)
        self.baseWidget.pack_start(varAvailBox,padding=5,expand=False)
        
        self.baseWidget.pack_start(gtk.HSeparator(), padding=10, expand=False)
        
        setupBox = gtk.HBox(homogeneous=False)
        
        enableBox = gtk.VBox(homogeneous=True)
        enableBox.pack_start(gtk.Label("Show which fields?"))
        self.__enable_E = gtk.CheckButton(label="Enable _E")
        self.__enable_E.set_active(True)
        enableBox.pack_start(self.__enable_E)
        self.__enable_SC = gtk.CheckButton(label="Enable _SC")
        self.__enable_SC.set_active(True)
        enableBox.pack_start(self.__enable_SC)
        self.__enable_PC = gtk.CheckButton(label="Enable _P/C")
        self.__enable_PC.set_active(True)
        enableBox.pack_start(self.__enable_PC)
        setupBox.pack_start(enableBox, padding=5)

        setupBox.pack_start(gtk.VSeparator(), padding=5, expand=False)

        optimisticBox = gtk.VBox(homogeneous=True)
        optimisticBox.pack_start(gtk.Label("Select scaling constants:"))
        self.__optimistic_optimistic  = gtk.RadioButton(None,"Optimistic")
        optimisticBox.pack_start(self.__optimistic_optimistic)
        self.__optimistic_both        = gtk.RadioButton(self.__optimistic_optimistic,"Both")
        self.__optimistic_both.set_active(True)
        optimisticBox.pack_start(self.__optimistic_both)        
        self.__optimistic_pessimistic = gtk.RadioButton(self.__optimistic_optimistic,"Pessimistic")
        optimisticBox.pack_start(self.__optimistic_pessimistic)
        setupBox.pack_start(optimisticBox,padding=0);

        setupBox.pack_start(gtk.VSeparator(), padding=5, expand=False)

        minORmeanBox = gtk.VBox(homogeneous=True)
        minORmeanBox.pack_start(gtk.Label("Draw lines where?"))
        self.__minORmean_min  = gtk.RadioButton(None,"Min")
        self.__minORmean_min.set_active(True)
        minORmeanBox.pack_start(self.__minORmean_min)
        self.__minORmean_mean = gtk.RadioButton(self.__minORmean_min,"Mean")
        minORmeanBox.pack_start(self.__minORmean_mean)        
        setupBox.pack_start(minORmeanBox, padding=0)

        setupBox.pack_start(gtk.VSeparator(), padding=5, expand=False)

        filterDoublesBox = gtk.VBox(homogeneous=True)
        filterDoublesBox.pack_start(gtk.Label("Pre-filter data points with same (X,Y)?"))
        self.__filterDoubles_none    = gtk.RadioButton(None, "No filter")
        self.__filterDoubles_none.set_active(True)
        filterDoublesBox.pack_start(self.__filterDoubles_none)
        self.__filterDoubles_best    = gtk.RadioButton(self.__filterDoubles_none, "Use lowest field")
        filterDoublesBox.pack_start(self.__filterDoubles_best)
        self.__filterDoubles_average = gtk.RadioButton(self.__filterDoubles_none, "Use average field")
        filterDoublesBox.pack_start(self.__filterDoubles_average)
        setupBox.pack_start(filterDoublesBox, padding=5)

        plotSetupBox = gtk.VBox(homogeneous=True)
        plotSetupBox.pack_start(gtk.Label("Plot setup"))
        self.__enable_gradientRepresentation = gtk.CheckButton(label="Gradient representation")
        self.__enable_gradientRepresentation.set_active(False)
        plotSetupBox.pack_start(self.__enable_gradientRepresentation)
        setupBox.pack_start(plotSetupBox,padding=0)

        self.baseWidget.pack_start(setupBox, padding=5, expand=False)
        
        self.baseWidget.pack_start(gtk.HSeparator(), padding=10, expand=False)
        
        plotBox = gtk.HBox(homogeneous=True)
        self.__plotButtonX = gtk.Button("Show _plot (X)")
        if not self.plotObject.dataExtractor.lockdown:
            self.__plotButtonX.set_sensitive(False)
        self.__plotButtonX.connect("clicked", self.event_button_plot, "X")
        plotBox.pack_start(self.__plotButtonX, padding=5, expand=False)
        self.__plotButtonY = gtk.Button("Show _plot (Y)")
        if not self.plotObject.dataExtractor.lockdown:
            self.__plotButtonY.set_sensitive(False)
        self.__plotButtonY.connect("clicked", self.event_button_plot, "Y")
        plotBox.pack_start(self.__plotButtonY, padding=5, expand=False)
        self.baseWidget.pack_start(plotBox, padding=5, expand=False)
        
        contoursBox = gtk.HBox(homogeneous=True)
        self.__plotTripcontourfButton = gtk.Button("Show tricontourf plot")
        self.__plotTripcontourfButton.connect("clicked", self.event_button_plotTripcontourf, None)
        contoursBox.pack_start(self.__plotTripcontourfButton,padding=5, expand=False)
        self.__numContoursEntry = gtk.Entry()
        self.__numContoursEntry.set_text("10")
        contoursBox.pack_start(self.__numContoursEntry,padding=5, expand=True)
        if not self.plotObject.dataExtractor.lockdown:
            self.__plotTripcontourfButton.set_sensitive(False)
            self.__numContoursEntry.set_sensitive(False)
        self.baseWidget.pack_start(contoursBox, padding=5, expand=False)
        
        treeDeeBox = gtk.HBox(homogeneous=True)
        self.__plot3DpointCloudButton = gtk.Button("Plot 3D point cloud")
        self.__plot3DpointCloudButton.connect("clicked", self.event_button_3DpointCloud, None)
        treeDeeBox.pack_start(self.__plot3DpointCloudButton, padding=5, expand=True)
        self.__plot3DtrisurfButton = gtk.Button("Plot 3D trisurf")
        self.__plot3DtrisurfButton.connect("clicked", self.event_button_3DpointCloud, "trisurf")
        treeDeeBox.pack_start(self.__plot3DtrisurfButton, padding=5, expand=True)
        if not self.plotObject.dataExtractor.lockdown:
            self.__plot3DpointCloudButton.set_sensitive(False)
            self.__plot3DtrisurfButton.set_sensitive(False)
        self.baseWidget.pack_start(treeDeeBox, padding=5, expand=False)
        
        self.__closeButton = gtk.Button("_Close plot view")
        self.__closeButton.connect("clicked", self.event_button_close, None)
        self.baseWidget.pack_start(self.__closeButton,padding = 5, expand=False)

        self.baseWidget.show_all()
    
    def saveToPlot(self):
        varX         = self.__varX_entry.get_text().strip()
        varY         = self.__varY_entry.get_text().strip()
        
        constE       = self.__constE_entry.get_text().strip()
        constE_2     = self.__constE_2_entry.get_text().strip()
        #varNormE     = self.__varNormE_entry.get_text().strip()
        varNormE_entry_text = self.__varNormE_entry.get_text()
        varNormE_entry_text = varNormE_entry_text.split(",")
        varNormE = []
        varNormE_BAD = False
        for k in varNormE_entry_text:
            k2 = k.strip()
            if " " in k2:
                print "varNormE element contained space, skipping '" + k2 + "'"
                varNormE_BAD = True;
                continue
            elif k2 == "":
                print "varNormE element is empty string, skipping."
                varNormE_BAD = True;
                continue
            varNormE.append(k2)
        
        constSC      = self.__constSC_entry.get_text().strip()
        constSC_2    = self.__constSC_2_entry.get_text().strip()
        #varNormSC    = self.__varNormSC_entry.get_text().strip()
        varNormSC_entry_text = self.__varNormSC_entry.get_text()
        varNormSC_entry_text = varNormSC_entry_text.split(",")
        varNormSC = []
        varNormSC_BAD = False
        for k in varNormSC_entry_text:
            k2 = k.strip()
            if " " in k2:
                print "varNormSC element contained space, skipping '" + k2 + "'"
                varNormSC_BAD = True;
                continue
            elif k2 == "":
                print "varNormSC element is empty string, skipping."
                varNormSC_BAD = True;
                continue
            varNormSC.append(k2)
        
        constPC      = self.__constPC_entry.get_text().strip()
        constPC_2    = self.__constPC_2_entry.get_text().strip()
        varFrequency = self.__varFrequency_entry.get_text().strip()
        varRQ        = self.__varRQ_entry.get_text().strip()
        varVg        = self.__varVg_entry.get_text().strip()
        varRadius    = self.__varRadius_entry.get_text().strip()
        
        if " " in varX or " " in varY or " " in constE or " " in constPC_2 or varNormE_BAD \
            or " " in constSC or " " in constSC_2 or varNormSC_BAD \
            or " " in constPC or " " in constPC_2 or " " in varFrequency \
            or " " in varRQ or " " in varVg or " " in varRadius :
            mDia = gtk.MessageDialog(self.getBaseWindow(),
                                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                     gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                     "Space in a variable, not saving to plot." )
            mDia.run()
            mDia.destroy()
            return
        self.plotObject.varX = varX
        self.plotObject.varY = varY
        self.plotObject.constE = constE
        self.plotObject.constE_2 = constE_2
        self.plotObject.varNormE = varNormE
        self.plotObject.constSC = constSC
        self.plotObject.constSC_2 = constSC_2
        self.plotObject.varNormSC = varNormSC
        self.plotObject.constPC = constPC
        self.plotObject.constPC_2 = constPC_2
        self.plotObject.varFrequency = varFrequency
        self.plotObject.varRQ = varRQ
        self.plotObject.varVg = varVg
        self.plotObject.varRadius = varRadius
        
        self.plotObject.updateSettingsDict()
        self.plotObject.dataExtractor.write()

    def dedup2D(self,x,y,t, minORmean="min"):
        assert minORmean == "min" or minORmean == "mean" or minORmean =="max"
        # print minORmean

        #Deduplicate
        Xdedup = []
        Ydedup = []
        Tdedup = []
        for i in xrange(len(x)):
            j = 0
            while j < len(Xdedup):
                if x[i] == Xdedup[j] and y[i] == Ydedup[j]:
                    break
                j += 1
            if j == len(Xdedup):
                #Didn't find (X,Y)
                Xdedup.append(x[i])
                Ydedup.append(y[i])
                Tdedup.append([t[i],])
                # print "Adding new:", x[i], y[i], t[i]
            else:
                assert Xdedup[j] == x[i]
                assert Ydedup[j] == y[i]
                # print "complimenting: ", Xdedup[j], x[i], Ydedup[j], y[i], t[i]
                Tdedup[j].append(t[i])

        for i in xrange(len(Tdedup)):
            # print Xdedup[i], Ydedup[i], Tdedup[i],
            if minORmean=="min":
                Tdedup[i] = np.min(Tdedup[i])
            if minORmean=="max":
                Tdedup[i] = np.max(Tdedup[i])                
            elif minORmean=="mean":
                Tdedup[i] = np.mean(Tdedup[i])
        # print Tdedup[i]
        return(Xdedup, Ydedup, Tdedup)

    def event_button_plot(self, widget, data):
        assert data == "X" or data == "Y"
        self.saveToPlot()
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print "Could not import matplotlib.pyplot, aborting plot. You should still be able to doExport()!"
            return
        (X,Y, tE, tSC, tPC) = self.plotObject.getData(scalingFactor2=False, gradientRepresentation=self.__enable_gradientRepresentation.get_active())
        (X_2,Y_2, tE_2, tSC_2, tPC_2) = self.plotObject.getData(scalingFactor2=True, gradientRepresentation=self.__enable_gradientRepresentation.get_active())
        assert X == X_2
        assert Y == Y_2

        if data=="Y":
            Xtmp=X
            X=Y
            Y=Xtmp

            Xtmp=X_2
            X_2=Y_2
            Y_2 = Xtmp
        
        enableE  = self.__enable_E.get_active()
        enableSC = self.__enable_SC.get_active()
        enablePC = self.__enable_PC.get_active()
        if not (enableE or enableSC or enablePC):
            mDia = gtk.MessageDialog(self.getBaseWindow(),
                                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                     gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                     "Nothing enabled, not plotting" )
            mDia.run()
            mDia.destroy()
            return

        doOptimistic  = self.__optimistic_optimistic.get_active()  or self.__optimistic_both.get_active()
        doPessimistic = self.__optimistic_pessimistic.get_active() or self.__optimistic_both.get_active()
        

        if self.__filterDoubles_best.get_active():
            (X_E,Y_E,tE)  = self.dedup2D(X,Y,tE,  "max")
            (X_SC,Y_SC,tSC) = self.dedup2D(X,Y,tSC, "max")
            (X_PC,Y_PC,tPC) = self.dedup2D(X,Y,tPC, "max")

            (X_E_2,Y_E_2,tE_2)  = self.dedup2D(X_2,Y_2,tE_2,  "max")
            (X_SC_2,Y_SC_2,tSC_2) = self.dedup2D(X_2,Y_2,tSC_2, "max")
            (X_PC_2,Y_PC_2,tPC_2) = self.dedup2D(X_2,Y_2,tPC_2, "max")
        elif self.__filterDoubles_average.get_active():
            (X_E,Y_E,tE)  = self.dedup2D(X,Y,tE,  "mean")
            (X_SC,Y_SC,tSC) = self.dedup2D(X,Y,tSC, "mean")
            (X_PC,Y_PC,tPC) = self.dedup2D(X,Y,tPC, "mean")

            (X_E_2,Y_E_2,tE_2)  = self.dedup2D(X_2,Y_2,tE_2,  "mean")
            (X_SC_2,Y_SC_2,tSC_2) = self.dedup2D(X_2,Y_2,tSC_2, "mean")
            (X_PC_2,Y_PC_2,tPC_2) = self.dedup2D(X_2,Y_2,tPC_2, "mean")
        else:
            X_E = X_SC = X_PC = X
            X_E_2 = X_SC_2 = X_PC_2 = X_2
            Y_E = Y_SC = Y_PC = Y
            Y_E_2 = Y_SC_2 = Y_PC_2 = Y_2

        def dedupX(X, t, minORmean="min"):
            Xret = []
            tret = []
            for i in xrange(len(X)):
                if X[i] in Xret:
                    continue
                Xret.append(X[i])
                ttemp = []
                for j in xrange(len(X)):
                    if X[j]==X[i]:
                        ttemp.append(t[j])
                if minORmean == "min":
                    tret.append(np.min(ttemp))
                elif minORmean == "mean":
                    tret.append(np.mean(ttemp))
                else:
                    print "dedupX expects minORmean = {min|mean}"
            sortIDX = np.argsort(Xret)
            return (np.asarray(Xret)[sortIDX], np.asarray(tret)[sortIDX])
        
        XAll = []
        tAll = []

        def plotData(X,t, MARKER, LABEL, COLOR, XAll, tAll, minORmean="min"):
            if LABEL:
                plt.plot(X, t,  MARKER, label=LABEL, color=COLOR)
            else:
                plt.plot(X, t,  MARKER, color=COLOR)
            (Xmin,tmin) = dedupX(X,t, minORmean)
            plt.plot(Xmin, tmin, "--", color=COLOR)
            XAll += X
            tAll += t

        minORmean=None
        if self.__minORmean_min.get_active():
            minORmean="min"
        else:
            assert self.__minORmean_mean.get_active()
            minORmean="mean"

        if enableE:
            if doOptimistic and doPessimistic:
                plotData(X_E,tE, '+', "E", "blue", XAll, tAll, minORmean)
                plotData(X_E_2,tE_2, '*', None, "blue", XAll, tAll, minORmean)
            elif doOptimistic:
                plotData(X_E_2,tE_2, '*', "E", "blue", XAll, tAll, minORmean)
            elif doPessimistic:
                plotData(X_E,tE, '+', "E", "blue", XAll, tAll, minORmean)
        if enableSC:
            if doOptimistic and doPessimistic:
                plotData(X_SC,tSC, '+', "SC", "green", XAll, tAll, minORmean)
                plotData(X_SC_2,tSC_2, '*', None, "green", XAll, tAll, minORmean)
            elif doOptimistic:
                plotData(X_SC_2,tSC_2, '*', "SC", "green", XAll, tAll, minORmean)
            elif doPessimistic:
                plotData(X_SC,tSC, '+', "SC", "green", XAll, tAll, minORmean)
        if enablePC:
            if doOptimistic and doPessimistic:
                plotData(X_PC,tPC, '+', "PC", "red", XAll, tAll, minORmean)
                plotData(X_PC_2,tPC_2, '*', None, "red", XAll, tAll, minORmean)
            elif doOptimistic:
                plotData(X_PC,tPC_2, '*', "PC", "red", XAll, tAll, minORmean)
            elif doPessimistic:
                plotData(X_PC,tPC, '+', "PC", "red", XAll, tAll, minORmean)

            # plt.plot(X, tPC, '+', label="PC", color="red")
            # (Xmin,tmin) = dedupX(X,tPC)
            # plt.plot(Xmin, tmin, "--", color="red")
            # XAll += X
            # tAll += tPC
        (Xmin,tmin) = dedupX(XAll,tAll)
        plt.plot(Xmin,tmin, "--", color="black", label="Minimum")
        
        if data=="X":
            plt.xlabel(self.plotObject.varX)
        if data=="Y":
            plt.xlabel(self.plotObject.varY)
        
        if self.__enable_gradientRepresentation.get_active():
            plt.ylabel(r"Max gradient $\left[\left(\frac{\mathrm{MV}}{\mathrm{m}}\right)\right]$ @ 200 ns")
        else:
            plt.ylabel("Time * G^6 [(MV/m)^6 * ns]")
        
        xRange = abs(max(X)-min(X))
        #ymax = max(max(tE),max(tSC),max(tPC))
        #ymin = min(min(tE),min(tSC),min(tPC))
        #yRange = abs(ymax-ymin)
        #plt.axis([min(X)-0.1*xRange, max(X)+0.1*xRange, ymin-0.1*yRange, ymax+0.1*yRange])
        
        plt.legend()
        
        plt.show()
        
        gtk.main()
    
    def event_button_plotTripcontourf(self,widget,data):
        self.saveToPlot()
        try:
            import matplotlib.pyplot as plt
            import matplotlib.tri as tri
            import numpy as np
        except ImportError:
            print "Could not import matplotlib.pyplot, matplotlib.tri, or nump -- aborting plot. You should still be able to doExport()!"
            return

        doOptimistic  = self.__optimistic_optimistic.get_active()  or self.__optimistic_both.get_active()
        doPessimistic = self.__optimistic_pessimistic.get_active() or self.__optimistic_both.get_active()        
        if doOptimistic and doPessimistic:
            mDia = gtk.MessageDialog(self.getBaseWindow(),
                                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                     gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                     "Choose either optimistic or pessimistic, not plotting" )
            mDia.run()
            mDia.destroy()
            return
        
        try:
            numContours = int(self.__numContoursEntry.get_text())
        except ValueError:
            mDia = gtk.MessageDialog(self.getBaseWindow(),
                                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                     gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                     "Number of countours '" + self.__numContoursEntry.get_text() + "' is not a valid integer." )
            mDia.run()
            mDia.destroy()
            return
            
            

        #Assume that optimistic always more optimistic than pessimistic
        (X,Y, tE, tSC, tPC) = self.plotObject.getData(scalingFactor2=doOptimistic,gradientRepresentation=self.__enable_gradientRepresentation.get_active())
        
        enableE  = self.__enable_E.get_active()
        enableSC = self.__enable_SC.get_active()
        enablePC = self.__enable_PC.get_active()
        if not (enableE or enableSC or enablePC):
            mDia = gtk.MessageDialog(self.getBaseWindow(),
                                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                     gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                     "Nothing enabled, not plotting" )
            mDia.run()
            mDia.destroy()
            return
        
        dataFilter = None
        if self.__filterDoubles_none.get_active():
            dataFilter = None
        elif self.__filterDoubles_best.get_active():
            dataFilter = "best"
        elif self.__filterDoubles_average.get_active():
            dataFilter = "average"
            

        #Merge data
        x = []
        y = []
        t = []
        if enableE:
            if dataFilter == "best":
                (X2,Y2,tE2) = self.dedup2D(X,Y,tE,"max")
            elif dataFilter == "average":
                (X2,Y2,tE2) = self.dedup2D(X,Y,tE,"mean")
            else:
                X2 = X; Y2=Y; tE2 = tE

            x += list(X2)
            y += list(Y2)
            t += list(tE2)
        if enableSC:
            if dataFilter == "best":
                (X2,Y2,tSC2) = self.dedup2D(X,Y,tSC,"max")
            elif dataFilter == "average":
                (X2,Y2,tSC2) = self.dedup2D(X,Y,tSC,"mean")
            else:
                X2 = X; Y2=Y; tSC2 = tSC
            x += list(X2)
            y += list(Y2)
            t += list(tSC2)
        if enablePC:
            if dataFilter == "best":
                (X2,Y2,tPC2) = self.dedup2D(X,Y,tPC,"max")
            elif dataFilter == "average":
                (X2,Y2,tPC2) = self.dedup2D(X,Y,tPC,"mean")
            else:
                X2 = X; Y2=Y; tPC2 = tPC
            x += list(X2)
            y += list(Y2)
            t += list(tPC2)

        assert len(x) == len(y) and len(x) == len(t)

        #Standard assumption: "min"
        (Xdedup, Ydedup, Tdedup) = self.dedup2D(x,y,t)
        
        #Plot
        triang = tri.Triangulation(Xdedup, Ydedup)
        plt.tricontourf(triang,Tdedup, numContours)
        plt.colorbar()

        plt.plot(Xdedup, Ydedup, 'r+')

        plt.xlabel(self.plotObject.varX)
        plt.ylabel(self.plotObject.varY)
        #plt.title("instName = " + self.plotObject.instName)

        plt.subplots_adjust(right=1.0)

        plt.show()
        
        gtk.main()
    
    def event_button_3DpointCloud(self,widget,data):
        print "DataExtractorPlots_ScaleOptim::event_button_3DpointCloud(data='"+str(data)+"')"
        assert data==None or data=="trisurf"
        self.saveToPlot()
        try:
            import matplotlib.pyplot as plt
            from mpl_toolkits.mplot3d import Axes3D
        except ImportError:
            print "Could not import matplotlib.pyplot, aborting plot. You should still be able to doExport()!"
            return

        (X,Y, tE, tSC, tPC) = self.plotObject.getData(scalingFactor2=False,gradientRepresentation=self.__enable_gradientRepresentation.get_active())
        (X_2,Y_2, tE_2, tSC_2, tPC_2) = self.plotObject.getData(scalingFactor2=True,gradientRepresentation=self.__enable_gradientRepresentation.get_active())
        assert X == X_2
        assert Y == Y_2
        
        enableE  = self.__enable_E.get_active()
        enableSC = self.__enable_SC.get_active()
        enablePC = self.__enable_PC.get_active()
        if not (enableE or enableSC or enablePC):
            mDia = gtk.MessageDialog(self.getBaseWindow(),
                                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                     gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                     "Nothing enabled, not plotting" )
            mDia.run()
            mDia.destroy()
            return

        doOptimistic  = self.__optimistic_optimistic.get_active()  or self.__optimistic_both.get_active()
        doPessimistic = self.__optimistic_pessimistic.get_active() or self.__optimistic_both.get_active()
        
        if self.__filterDoubles_best.get_active():
            (X_E,Y_E,tE)  = self.dedup2D(X,Y,tE,  "max")
            (X_SC,Y_SC,tSC) = self.dedup2D(X,Y,tSC, "max")
            (X_PC,Y_PC,tPC) = self.dedup2D(X,Y,tPC, "max")

            (X_E_2,Y_E_2,tE_2)  = self.dedup2D(X_2,Y_2,tE_2,  "max")
            (X_SC_2,Y_SC_2,tSC_2) = self.dedup2D(X_2,Y_2,tSC_2, "max")
            (X_PC_2,Y_PC_2,tPC_2) = self.dedup2D(X_2,Y_2,tPC_2, "max")
        elif self.__filterDoubles_average.get_active():
            (X_E,Y_E,tE)  = self.dedup2D(X,Y,tE,  "mean")
            (X_SC,Y_SC,tSC) = self.dedup2D(X,Y,tSC, "mean")
            (X_PC,Y_PC,tPC) = self.dedup2D(X,Y,tPC, "mean")

            (X_E_2,Y_E_2,tE_2)  = self.dedup2D(X_2,Y_2,tE_2,  "mean")
            (X_SC_2,Y_SC_2,tSC_2) = self.dedup2D(X_2,Y_2,tSC_2, "mean")
            (X_PC_2,Y_PC_2,tPC_2) = self.dedup2D(X_2,Y_2,tPC_2, "mean")
        else:
            if data=="trisurf":
                mDia = gtk.MessageDialog(self.getBaseWindow(),
                                         gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                         gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                         "When plotting whith trisurf, must enable deduplification!" )
                mDia.run()
                mDia.destroy()
                return
            X_E = X_SC = X_PC = X
            X_E_2 = X_SC_2 = X_PC_2 = X_2
            Y_E = Y_SC = Y_PC = Y
            Y_E_2 = Y_SC_2 = Y_PC_2 = Y_2

        fig = plt.figure()
        ax = fig.gca(projection='3d')
        
        if doPessimistic:
            if enableE:
                if data=="trisurf":
                    ax.plot_trisurf(X_E,Y_E,tE,color="blue")
                else:
                    ax.scatter(X_E, Y_E, tE, c='b', marker='+')
            if enableSC:
                if data=="trisurf":
                    ax.plot_trisurf(X_SC, Y_SC, tSC, color='green')
                else:
                    ax.scatter(X_SC, Y_SC, tSC, c='green', marker='+')
            if enablePC:
                if data=="trisurf":
                    ax.plot_trisurf(X_PC, Y_PC, tPC, color='red')
                else:
                    ax.scatter(X_PC, Y_PC, tPC, c='red', marker='+')
        if doOptimistic:
            if enableE:
                if data=="trisurf":
                    ax.plot_trisurf(X_E_2,Y_E_2,tE_2,color="blue")
                else:
                    ax.scatter(X_E_2, Y_E_2, tE_2, c='b', marker='*')
            if enableSC:
                if data=="trisurf":
                    ax.plot_trisurf(X_SC_2, Y_SC_2, tSC_2, color='green')
                else:
                    ax.scatter(X_SC_2, Y_SC_2, tSC_2, c='green', marker='*')
            if enablePC:
                if data=="trisurf":
                    ax.plot_trisurf(X_PC_2, Y_PC_2, tPC_2, color='red')
                else:
                    ax.scatter(X_PC_2, Y_PC_2, tPC_2, c='red', marker='*')
        
        ax.set_xlabel(self.plotObject.varX)
        ax.set_ylabel(self.plotObject.varY)
        if self.__enable_gradientRepresentation.get_active():
            ax.set_zlabel(r"Max gradient $\left[\left(\frac{\mathrm{MV}}{\mathrm{m}}\right)\right]$ @ 200 ns")
        else:
            ax.set_zlabel("Time * G^6")
        
        plt.subplots_adjust(left=0.0,right=1.0,top=1.0,bottom=0.0)
        
        plt.show()

        gtk.main()
        
    def event_button_close(self,widget,data):
        self.saveToPlot()
        self.frameManager.pop()
    def event_delete(self):
        #self.saveToPlot()
        return False

