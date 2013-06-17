# -*- coding: utf8 -*-
#
# Copyright 2012 Kyrre Ness Sjøbæk
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
        self.__varZentry.set_text(self.plotObject.varZ)
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
        z = self.__varZentry.get_text().strip()
        l = self.__plotLimitEntry.get_text().strip()
        nc = self.__numContoursEntry.get_text().strip()
        if " " in x or " " in y or " " in z or " " in l or " " in nc:
            mDia = gtk.MessageDialog(self.getBaseWindow(),
                                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                     gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                     "Space in X, Y, or Z variable, or plotLimit/numContours -- not saving to plot." )
            mDia.run()
            mDia.destroy()
            return

        self.plotObject.varX = x
        self.plotObject.varY = y
        self.plotObject.varZ = z
        self.plotObject.limit = l
        self.plotObject.numContours = nc
        
        if self.__plotLimitCheck.get_active():
            self.plotObject.useLimit = "True"
        else:
            self.plotObject.useLimit = "False"

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
        if self.__plotLimitCheck.get_active():
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
        if self.__plotLimitCheck.get_active():
            (X,Y,Z) = self.plotObject.getBelowLimit(limit)
        else:
            (X,Y,Z) = self.plotObject.getData()

        # print "X:", X
        # print "Y:", Y
        # print "Z:", Z
        # print "Deduplicating..."
        (X,Y,Z,N) = self.plotObject.deduplicate(X,Y,Z)
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
        if self.__plotLimitCheck.get_active():
            (X,Y,Z) = self.plotObject.getBelowLimit(limit)
        else:
            (X,Y,Z) = self.plotObject.getData()
        
        print "X:", X
        print "Y:", Y
        print "Z:", Z
        
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        ax.scatter(X, Y, Z)
        
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
    __varNormE_entry = None
    
    __constSC_entry = None
    __varNormSC_entry = None
    
    __constPC_entry = None
    __varFrequency_entry = None
    __varRQ_entry = None
    __varVg_entry = None
    __varRadius_entry = None
    
    __enable_E = None
    __enable_SC = None
    __enable_PC = None
    
    __plotButtonX = None
    __plotButtonY = None
    __plot2DButton = None
    
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
        constEbox.pack_start(gtk.Label("^6 [(MV/m)^6] * 200 ns"), padding=5,expand=False)
        self.baseWidget.pack_start(constEbox, padding=5, expand=False)
        
        varNormEbox = gtk.HBox()
        varNormEbox.pack_start(gtk.Label("varNormE:"), padding=5,expand=False)
        self.__varNormE_entry = gtk.Entry()
        self.__varNormE_entry.set_text(self.plotObject.varNormE)
        varNormEbox.pack_start(self.__varNormE_entry, padding=5, expand=True)
        self.baseWidget.pack_start(varNormEbox, padding=5, expand=False)
        
        self.baseWidget.pack_start(gtk.HSeparator(), padding=10, expand=False)
        
        constSCbox = gtk.HBox()
        constSCbox.pack_start(gtk.Label("constSC:"), padding=5,expand=False)
        self.__constSC_entry = gtk.Entry()
        self.__constSC_entry.set_text(self.plotObject.constSC)
        constSCbox.pack_start(self.__constSC_entry, padding=5, expand=True)
        constSCbox.pack_start(gtk.Label("^3 [(MW/mm^2)^3] * 200 ns"), padding=5,expand=False)
        self.baseWidget.pack_start(constSCbox, padding=5, expand=False)
        
        varNormSCbox = gtk.HBox()
        varNormSCbox.pack_start(gtk.Label("varNormSC:"), padding=5,expand=False)
        self.__varNormSC_entry = gtk.Entry()
        self.__varNormSC_entry.set_text(self.plotObject.varNormSC)
        varNormSCbox.pack_start(self.__varNormSC_entry, padding=5, expand=True)
        self.baseWidget.pack_start(varNormSCbox, padding=5, expand=False)
        
        self.baseWidget.pack_start(gtk.HSeparator(), padding=10, expand=False)
        
        constPCbox = gtk.HBox()
        constPCbox.pack_start(gtk.Label("constPC:"), padding=5,expand=False)
        self.__constPC_entry = gtk.Entry()
        self.__constPC_entry.set_text(self.plotObject.constPC)
        constPCbox.pack_start(self.__constPC_entry, padding=5, expand=True)
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
        
        enableBox = gtk.HBox(homogeneous=True)
        self.__enable_E = gtk.CheckButton(label="Enable _E")
        self.__enable_E.set_active(True)
        enableBox.pack_start(self.__enable_E, padding=5)
        self.__enable_SC = gtk.CheckButton(label="Enable _SC")
        self.__enable_SC.set_active(True)
        enableBox.pack_start(self.__enable_SC, padding=5)
        self.__enable_PC = gtk.CheckButton(label="Enable _P/C")
        self.__enable_PC.set_active(True)
        enableBox.pack_start(self.__enable_PC, padding=5)
        self.baseWidget.pack_start(enableBox, padding=5, expand=False)
        
        self.baseWidget.pack_start(gtk.HSeparator(), padding=10, expand=False)
        
        plotBox = gtk.HBox(homogeneous=True)
        self.__plotButtonX = gtk.Button("Show _plot (X)")
        if not self.plotObject.dataExtractor.lockdown:
            self.__plotButtonX.set_sensitive(False)
        self.__plotButtonX.connect("clicked", self.event_button_plot, None)
        plotBox.pack_start(self.__plotButtonX, padding=5, expand=False)
        self.__plotButtonY = gtk.Button("Show _plot (Y)")
        if not self.plotObject.dataExtractor.lockdown:
            self.__plotButtonY.set_sensitive(False)
        self.__plotButtonY.connect("clicked", self.event_button_plot, "Y")
        plotBox.pack_start(self.__plotButtonY, padding=5, expand=False)
        self.baseWidget.pack_start(plotBox, padding=5, expand=False)
        
        self.__plot2DButton = gtk.Button("Show _2D plot")
        if not self.plotObject.dataExtractor.lockdown:
            self.__plot2DButton.set_sensitive(False)
        self.__plot2DButton.connect("clicked", self.event_button_plot2D, None)
        self.baseWidget.pack_start(self.__plot2DButton, padding=5, expand=False)
        
        self.__closeButton = gtk.Button("_Close plot view")
        self.__closeButton.connect("clicked", self.event_button_close, None)
        self.baseWidget.pack_start(self.__closeButton,padding = 5, expand=False)

        self.baseWidget.show_all()
    
    def saveToPlot(self):
        varX         = self.__varX_entry.get_text().strip()
        varY         = self.__varY_entry.get_text().strip()
        
        constE       = self.__constE_entry.get_text().strip()
        varNormE     = self.__varNormE_entry.get_text().strip()
        
        constSC      = self.__constSC_entry.get_text().strip()
        varNormSC    = self.__varNormSC_entry.get_text().strip()
        
        constPC      = self.__constPC_entry.get_text().strip()
        varFrequency = self.__varFrequency_entry.get_text().strip()
        varRQ        = self.__varRQ_entry.get_text().strip()
        varVg        = self.__varVg_entry.get_text().strip()
        varRadius    = self.__varRadius_entry.get_text().strip()
        
        if " " in varX or " " in varY or " " in constE or " " in varNormE \
            or " " in constSC or " " in varNormSC or " " in constPC or " " in varFrequency \
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
        self.plotObject.varNormE = varNormE
        self.plotObject.constSC = constSC
        self.plotObject.varNormSC = varNormSC
        self.plotObject.constPC = constPC
        self.plotObject.varFrequency = varFrequency
        self.plotObject.varRQ = varRQ
        self.plotObject.varVg = varVg
        self.plotObject.varRadius = varRadius
        
        self.plotObject.updateSettingsDict()
        self.plotObject.dataExtractor.write()
    
    def event_button_plot(self, widget, data):
        self.saveToPlot()
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print "Could not import matplotlib.pyplot, aborting plot. You should still be able to doExport()!"
            return
        (X,Y, tE, tSC, tPC) = self.plotObject.getData()
        
        if data=="Y":
            X=Y
        
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
        if enableE:
            plt.plot(X, tE,  '+', label="E", color="blue")
            (Xmin,tmin) = dedupX(X,tE)
            plt.plot(Xmin, tmin, "--", color="blue")
            XAll += X
            tAll += tE
        if enableSC:
            plt.plot(X, tSC, '+', label="SC", color="green")
            (Xmin,tmin) = dedupX(X,tSC)
            plt.plot(Xmin, tmin, "--", color="green")
            XAll += X
            tAll += tSC
        if enablePC:
            plt.plot(X, tPC, '+', label="PC", color="red")
            (Xmin,tmin) = dedupX(X,tPC)
            plt.plot(Xmin, tmin, "--", color="red")
            XAll += X
            tAll += tPC
        (Xmin,tmin) = dedupX(XAll,tAll)
        plt.plot(Xmin,tmin, "--", color="black", label="Minimum")
        
        
        plt.xlabel(self.plotObject.varX)
        if data=="Y":
            plt.xlabel(self.plotObject.varY)
        plt.ylabel("Time * G^6 [(MV/m)^6 * ns]")
        
        xRange = abs(max(X)-min(X))
        #ymax = max(max(tE),max(tSC),max(tPC))
        #ymin = min(min(tE),min(tSC),min(tPC))
        #yRange = abs(ymax-ymin)
        #plt.axis([min(X)-0.1*xRange, max(X)+0.1*xRange, ymin-0.1*yRange, ymax+0.1*yRange])
        
        plt.legend()
        
        plt.show()
        
        gtk.main()
    
    def event_button_plot2D(self,widget,data):
        self.saveToPlot()
        try:
            import matplotlib.pyplot as plt
            import matplotlib.tri as tri
            import numpy as np
        except ImportError:
            print "Could not import matplotlib.pyplot, matplotlib.tri, or nump -- aborting plot. You should still be able to doExport()!"
            return
        (X,Y, tE, tSC, tPC) = self.plotObject.getData()
        
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
        
        #Merge data
        x = []
        y = []
        t = []
        if enableE:
            x += list(X)
            y += list(Y)
            t += list(tE)
        if enableSC:
            x += list(X)
            y += list(Y)
            t += list(tSC)
        if enablePC:
            x += list(X)
            y += list(Y)
            t += list(tPC)
        assert len(x) == len(y) and len(x) == len(t)
        
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
                Tdedup.append(t[i])
            else:
                #Found (X,Y). Is this better minimum?
                if t[i] < Tdedup[j]:
                    Tdedup[j] = t[i]
        
        #Plot
        triang = tri.Triangulation(Xdedup, Ydedup)
        plt.tricontourf(triang,Tdedup)
        plt.colorbar()
        
        plt.xlabel(self.plotObject.varX)
        plt.ylabel(self.plotObject.varY)
        
        plt.show()
        
        gtk.main()
        
        
    def event_button_close(self,widget,data):
        self.saveToPlot()
        self.frameManager.pop()
    def event_delete(self):
        #self.saveToPlot()
        return False

