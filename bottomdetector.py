from PyQt5.QtWidgets import QPushButton, QWidget
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout
from PyQt5.QtWidgets import QLineEdit, QFileDialog, QComboBox
from PyQt5.QtGui import QTransform

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from pyqtgraph.widgets.MatplotlibWidget import MatplotlibWidget
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as colors
import matplotlib.cm as cmx


class BottomDetector(QWidget):  # SRW
    # def __init__(self, parent) -> None:
    def __init__(self, data):
        super(QWidget, self).__init__()
        self.layout = QVBoxLayout(self)
        pg.setConfigOption("background", "w")

        # Initialize DATA
        self.data = data
        # Initialize Tab
        self.maintab = QWidget()

        # self.height
        self.width = 100
        self.totpixhits = 0
        self.total_hits = 0
        self.single_index = None
        self.noise_index = None
        self.coincidence_index = None
        self.pulser_index = None

        # Create First Tab
        # self.tab1.layout = QVBoxLayout(self)
        self.mainlayout = QVBoxLayout()
        self.inlayout = QHBoxLayout()
        self.in2layout = QHBoxLayout()
        self.in3layout = QHBoxLayout()
        self.r1layout = QHBoxLayout()
        self.r2layout = QHBoxLayout()

        self.button_load = QPushButton("LoadData")
        self.button_load.clicked.connect(self.loaddata)

        # Creating dropdown menu to select event type
        self.label_eventType = QLabel("Event Type")
        self.label_eventType.setFixedWidth(60)
        self.sel_eventType = QComboBox()
        self.sel_eventType.addItems(
            [
                str("trigger"),
                str("single"),
                str("coincidence"),
                str("pulser"),
                str("noise"),
            ]
        )  # These are the only event types nabpy can take as an argument
        self.sel_eventType.currentIndexChanged.connect(self.selecteventType)
        self.eventType = "single"

        # Creating conditionals dropdown menu for energy histogram
        self.label_conditional = QLabel("Conditionals")
        self.label_conditional.setFixedWidth(60)
        self.sel_conditional = QComboBox()
        self.sel_conditional.addItems(
            [str(">"), str(">="), str("<"), str("<="), str("="), str("!="), str("or")]
        )  # These are the conditional symbols outlined in basicCuts from nabpy code
        self.sel_conditional.currentIndexChanged.connect(self.selectconditional)
        self.cond = 0

        # Creating dropdown menu to select the channel number
        self.label_channo = QLabel("Channel")
        self.label_channo.setFixedWidth(60)
        self.sel_channo = QComboBox()
        self.sel_channo.addItems(
            [str(i + 1) for i in np.arange(0,127)]
        )  # The channel numbers for top detector are 1-127
        self.sel_channo.currentIndexChanged.connect(self.selectchannel)
        self.chan = 0

        self.button_loadEnergyCuts = QPushButton("LoadEnergyCuts")
        self.button_loadEnergyCuts.clicked.connect(
            self.updateEnergyCut
        )  # Should I use loaddata or define new fucntion specifically for the cuts?
        self.button_loadPixelCuts = QPushButton("LoadPixelCuts")
        self.button_loadPixelCuts.clicked.connect(self.updatePixelCut)

        self.evtno = 42
        self.energyCut = "energy", ">", 0
        self.pixelCut = "pixel", ">", 0

        self.lims = [2, 10]
        self.totevnt = 0
        self.totarea = 0
        self.tbinwidth = 320e-6
        self.evtsig = 0xAA55F154
        self.norm = None

        self.label_Energy = QLabel("Energy Cuts")
        self.value_energyCut = QLineEdit(str(self.energyCut))

        self.label_Pixel = QLabel("Pixel Cuts")
        self.value_pixelCut = QLineEdit(str(self.pixelCut))

        self.button_freerun = QPushButton("FreeRun")
        self.button_freerun.setCheckable(True)
        self.button_freerun.clicked.connect(self.runfreerun)

        self.button_previousevt = QPushButton("Back")  # SRW
        self.button_previousevt.clicked.connect(self.showpreviousevent)  # SRW

        self.button_nextevt = QPushButton("Next")
        self.button_nextevt.clicked.connect(self.shownextevent)

        self.button_norm = QPushButton("logpixhit")
        self.button_norm.setCheckable(True)
        self.button_norm.clicked.connect(self.selectnormalization)

        self.label_evtno = QLabel("Event")
        # self.label_evtno.setFixedWidth(60)
        self.value_evtno = QLineEdit(str(self.evtno))

        self.label_totevt = QLabel("Total Event")
        # self.label_totevt.setFixedWidth(60)
        self.value_totevt = QLineEdit(str(self.totevnt))

        self.label_totarea = QLabel("Area")
        # self.label_totarea.setFixedWidth(60)
        self.value_totarea = QLineEdit(str(self.totarea))

        self.value_evtno.textChanged.connect(self.updateevent)
        self.value_energyCut.textChanged.connect(self.updateEnergyCut)
        self.value_pixelCut.textChanged.connect(self.updatePixelCut)
        self.label_lims = QLabel("Range")
        self.value_lims = QLineEdit(str(self.lims)[1:-1])
        self.label_lims.setFixedWidth(60)
        # self.value_lims.textChanged.connect(self.updatestackplot)
        # self.field_fname.setMaximumWidth(self.width)
        # self.space = QSpacerItem(10,5)

        # self.inlayout.addWidget(self.button_foldname)
        # self.inlayout.addWidget(self.field_foldname)
        # self.inlayout.addWidget(self.field_runno)
        self.inlayout.addWidget(self.button_load)
        self.inlayout.addWidget(
            self.sel_eventType
        )  # Dropdown menu that allows user to select the event type
        self.inlayout.addWidget(
            self.sel_conditional
        )  # Dropdown menu that allows user to select a conditional symbol
        self.inlayout.addWidget(self.sel_channo)

        self.in2layout.addWidget(self.label_Energy)
        self.in2layout.addWidget(self.value_energyCut)
        self.in2layout.addWidget(self.button_loadEnergyCuts)
        self.in2layout.addWidget(self.label_Pixel)
        self.in2layout.addWidget(self.value_pixelCut)

        self.in2layout.addWidget(self.button_loadPixelCuts)

        self.in3layout.addWidget(self.button_freerun)
        self.in3layout.addWidget(self.button_previousevt)  # SRW
        self.in3layout.addWidget(self.button_nextevt)
        self.in3layout.addWidget(self.button_norm)
        self.in3layout.addWidget(self.label_evtno)
        self.in3layout.addWidget(self.value_evtno)
        # self.in2layout.addWidget(self.label_lims)
        # self.in2layout.addWidget(self.value_lims)

        # self.in2layout.addWidget(self.label_totevt)
        # self.in2layout.addWidget(self.value_totevt)
        # self.in2layout.addWidget(self.label_totarea)
        # self.in2layout.addWidget(self.value_totarea)

        # self.gwin = pg.GraphicsWindow()
        # self.rplt = self.gwin.addPlot()

        self.pen1 = pg.mkPen("r", width=2)
        self.pen2 = pg.mkPen(color=(255, 15, 15), width=2)
        # self.pen3 = pg.mkPen(color=(000, 155, 115), style=QtCore.Qt.DotLine)
        # self.curve = self.rplt.plot(pen=self.pen3)
        # self.curve2 = self.rplt.plot(pen=self.pen2)
        # self.rplt.showGrid(x=True, y=True)
        # self.data = np.arange(100)
        # self.avg_data = []
        # self.count = 0
        # self.curve.setData(self.data)

        # ******************************************
        # We want to stop using random data! I think we want to add the defined function from mdata.py here. SRW
        #       INITIAL RANDOM DATA
        # self.x = np.arange(100)
        # self.y = np.random.random(100)
        # self.bins = 40
        # self.hy, self.hx = np.histogram(self.y, bins=self.bins)
        # *****************************************

        #       PLOTS
        # I removed lot of commented out code. HVR

        # ******************** Generate PixHit Plots   **********************
        self.size = 2
        self.pixel_plot_widget1 = MatplotlibWidget(
            (7.5 * self.size, 3.5 * self.size), dpi=100
        )
        self.pixel_plot_widget1.vbox.removeWidget(self.pixel_plot_widget1.toolbar)
        self.pixel_plot_widget1.toolbar.setVisible(False)

        self.size = 2
        self.multipleSignalsPlot = MatplotlibWidget(
            (5.5 * self.size, 3.5 * self.size), dpi=100
        )
        # self.multipleSignalsPlot.vbox.removeWidget(self.multipleSignalsPlot.toolbar)
        # self.multipleSignalsPlot.toolbar.setVisible(False)
        self.multipleSignalsFig = self.multipleSignalsPlot.getFigure()
        self.multipleSignalsAxis = self.multipleSignalsFig.add_subplot(111)

        self.pulseimg, self.xbin, self.ybin = np.histogram2d(
            np.random.random(100), np.random.random(100), bins=[20, 20]
        )
        meshx, meshy = np.meshgrid(self.xbin, self.ybin)
        mappable = self.multipleSignalsAxis.pcolormesh(meshx, meshy, self.pulseimg)
        self.multipleSignalsFig.colorbar(
            mappable, ax=self.multipleSignalsAxis, pad=0.01
        )
        self.multipleSignalsFig.tight_layout()
        self.multipleSignalsPlot.draw()

        self.getnewfig()

        # randompixhist = 1 * np.random.random(127)        # Random pix hit without loading data
        randompixhist = 1 * np.random.randint(
            100, size=127
        )  # Random pix hit without loading data
        # self.customcmap = self.getmycmap(basemap='plasma') # To get better colormaps that in nabpy
        self.customcmap = self.getmycmap(
            basemap="cividis"
        )  # To get better colormaps that in nabpy
        self.pixel_plot_figure1, self.pixel_plot_runaxis, self.clbar1 = (
            self.data.updatepixplot(
                randompixhist,
                self.pixel_plot_figure1,
                self.pixel_plot_runaxis,
                self.clbar,
                self.norm,
                self.customcmap,
            )
        )

        randompixhist = 1 * np.random.randint(
            100, size=127
        )  # Random pix hit without loading data
        self.pixel_plot_figure2, self.pixel_plot_subrunaxis, self.clbar2 = (
            self.data.updatepixplot(
                randompixhist,
                self.pixel_plot_figure1,
                self.pixel_plot_subrunaxis,
                self.clbar,
                self.norm,
                self.customcmap,
            )
        )

        # ********************* Get Second histogram with pix hist(with random data ***********) *******************

        # self.pw2 = pg.PlotWidget(title="Hit Pixel Data")
        self.pw2 = pg.PlotWidget(
            title='<span style="color: #000; font-size: 16pt;">Energy Histogram</span>'
        )
        self.p2 = self.pw2.plot(
            stepMode="center", fillLevel=0
        )  # , fillOutline=True,brush=(100,0,0))
        self.p2.setPen(color=(0, 0, 0), width=2)
        self.pw2.setLabel("left", "Energy", units="arb")
        self.pw2.setLabel("bottom", "Bin", units="arb")
        self.pw2.showGrid(x=True, y=True)

        # ********************* Third histogram Not used now ************************************

        self.pw3 = pg.PlotWidget(
            title='<span style="color: #000; font-size: 16pt;">Single Trace</span>'
        )
        self.p3 = self.pw3.plot()
        self.p3.setPen(color=(0, 0, 0), width=5)
        self.pw3.setLabel("left", "Value", units="V")
        self.pw3.setLabel("bottom", "Time", units="s")
        self.pw3.showGrid(x=True, y=True)

        self.noisedata = np.random.random(10)
        self.timeax = np.arange(10)

        self.p3.setData(x=self.timeax, y=self.noisedata)

        # #********************* Timer if needed ***********  #
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updatepixhits)
        self.timer.start(1000)
        # ********************* Layouts ***********  #
        # self.r1layout.addWidget(self.pw1)
        self.r1layout.addWidget(self.pixel_plot_widget1)  # PixDec
        # self.r1layout.addWidget(self.pixel_plot_widget2)  # PixDec
        self.r1layout.addWidget(self.pw2)
        self.r2layout.addWidget(self.pw3)
        # self.r2layout.addWidget(self.pw4)  # If we want plot from pyqtgraph
        self.r2layout.addWidget(self.multipleSignalsPlot)

        # self.alayout.addWidget(self.setallVolt)
        # self.alayout.addWidget(self.gwin)
        # self.alayout.addLayout(self.inlayout)
        self.mainlayout.addLayout(self.inlayout)
        self.mainlayout.addLayout(self.in2layout)
        self.mainlayout.addLayout(self.in3layout)
        self.mainlayout.addLayout(self.r1layout)
        self.mainlayout.addLayout(self.r2layout)
        # self.alayout.addWidget(self.pw1)
        # self.alayout.addWidget(self.pw2)

        self.maintab.setLayout(self.mainlayout)
        # self.tab1.setLayout(self.alayout)

        # Add tabs to Widget
        self.layout.addWidget(self.maintab)
        self.setLayout(self.layout)

    # ************************************************************************** FUNCTIONS ****************************************************************************************  #

    # ***************Functions for loading Data *****************************************************#
    def correctscale(self, plotitem, xscale, yscale):
        xs = xscale[1] - xscale[0]
        ys = yscale[1] - yscale[0]

        xmin = xscale.min()
        ymin = yscale.min()

        print(xs, ys, xmin, ymin)
        tr = QTransform()
        tr.translate(xmin, ymin)
        tr.scale(xs, ys)
        plotitem.setTransform(tr)  # assign transform

    def dialog(self):
        # file , check = QFileDialog.getOpenFileName(None, "QFileDialog.getOpenFileName()", "", "All Files (*);;Python Files (*.py);;Text Files (*.txt)")
        tempfile, self.check = QFileDialog.getOpenFileName(None, "SelectFile", "", "")
        if self.check:
            self.fname = tempfile
            self.field_fname.setText(self.fname)
            # print(type(tempfile))
        else:
            self.file = "file not found!!"

    def loaddata(self):
        """
        Get the data in the data class
        """
        # self.updatefoldname()
        # self.updaterunno()
        # self.data.getdatafromfile()
        self.updateall()
        # return(self.data)

    def getnewfig(self):
        try:
            del self.pixel_plot_runaxis
            del self.pixel_plot_subrunaxis
            del self.pixel_plot_figure1
            del self.clbar
        except:
            pass
        self.pixel_plot_figure1 = self.pixel_plot_widget1.getFigure()
        self.pixel_plot_runaxis = self.pixel_plot_figure1.add_subplot(121)
        self.pixel_plot_subrunaxis = self.pixel_plot_figure1.add_subplot(122)
        self.pixel_plot_runaxis.set_title("Run: " + str(self.data.runno))
        self.pixel_plot_subrunaxis.set_title("SubRun")
        self.clbar = None

    def getnew_multipesignalplot(self):
        try:
            del self.multipleSignalFig
            del self.multipleSignalAxis
        except:
            pass
        self.multipleSignalsFig = self.multipleSignalsPlot.getFigure()
        self.multipleSignalsAxis = self.multipleSignalsFig.add_subplot(111)

    # *************** Functions for Selecting stuff like channen no. event no etc. *****************************************************#
    def selectchannel(self):
        self.chan = int(self.sel_channo.currentText())
        # print(tchan, type(tchan))
        self.updateenergyhistogram()
        self.updatesingleevent()
        # self.updatemultipleevent()
        self.updatemultipleeventwithmatplotlib()
        # print(self.chan)

    # Connecting conditional selection to energy histogram code
    def selectconditional(self):
        tcond = int(self.sel_conditional.currentText()) - 1
        # print(tchan, type(tchan))
        self.cond = tcond
        # self.value_totarea.setText(str(self.data.getarea(self.chan)))
        self.updateenergyhistogram()  # changed from self.updateall()
        self.updatesingleevent()
        # self.updatemultipleevent()

    # Connecting event type selection to energy histogram and scatter plot
    def selecteventType(self):
        # teventType = int(self.sel_eventType.currentText()) - 1
        teventType = self.sel_eventType.currentText()

        # print(tchan, type(tchan))
        self.eventType = teventType
        print(self.eventType)
        # self.value_totarea.setText(str(self.data.getarea(self.chan)))
        self.updatesingleevent()  # Idk if this one is right; maybe add energy histogram if we can figure out later how to add event type
        self.updatepixhits()
        self.updatemultipleeventwithmatplotlib()
        # self.updatemultipleevents()

    def getevntno(self):
        self.tempevnt = self.value_evtno.text().split(sep=",")
        self.evtno = int(float(self.tempevnt[0]))

    def updateevent(self):
        self.getevntno()
        # self.updatexy()
        # self.sc1.draw()

    def getEnergyCut(self):
        self.tempEnergy = self.value_energyCut.text().split(sep=",")
        self.energyCut = int(float(self.tempEnergy[0]))

    def updateEnergyCut(self):
        self.getEnergyCut()

    def getPixelCut(self):
        self.tempPixel = self.value_pixelCut.text().split(sep=",")
        self.pixelCut = int(float(self.tempPixel[0]))

    def updatePixelCut(self):
        self.getPixelCut()

    # def geteventindexes(self):
    #     self.single_index = self.data.singleWaves().headers().query("pixel < 200").index.to_numpy()
    #     self.coincidence_index = self.data.coincWaves().headers().query("pixel < 200").index.to_numpy()
    #     self._index = singlewaves.headers().query("pixel < 200").index.to_numpy()
    #     self.single_index = singlewaves.headers().query("pixel < 200").index.to_numpy()

    # *************** Functions for Updating the plots *****************************************************#

    # **************** Function to update all plots *******************************#
    def updateall(self):
        if self.data is not None:
            self.updatepixhits()
            self.updatesingleevent()
            self.updatemultipleeventwithmatplotlib()

    # **************** Function to update Energy histogram *******************************#
    def updateenergyhistogram(self):  # SRW commenting out for now to remove errors
        self.counts, self.edges = self.data.getenergyhistogram(
            bins=200, channel=self.chan
        )
        self.p2.setData(self.edges, self.counts)

    # **************** Function to update Single Event *******************************#
    def updatemultipleeventwithmatplotlib(self):
        self.multipleSignalsAxis.cla()
        self.multipleSignalsFig.clf()
        indxarr = self.data.headerdf.query(
            "evttype == @self.eventType and pixel == @self.chan"
        ).index
        # print(len(indxarr))
        if len(indxarr) == 0:
            self.multipleSignalsFig.clear()
            return
        if len(indxarr) < 200:
            events = indxarr
        else:
            events = np.random.choice(indxarr, 200)

        if self.eventType == "trigger":
            self.pulseimg, self.xbin, self.ybin = self.data.getmultipleeventdata(
                "single", events=events
            )
        else:
            self.pulseimg, self.xbin, self.ybin = self.data.getmultipleeventdata(
                self.eventType, events=events
            )

        self.getnew_multipesignalplot()

        meshx, meshy = np.meshgrid(self.xbin, self.ybin)
        self.pulseimg[self.pulseimg < 1] = np.inf

        mappable = self.multipleSignalsAxis.pcolormesh(meshx, meshy, self.pulseimg.T)

        self.multipleSignalsFig.colorbar(mappable, ax=self.multipleSignalsAxis, pad=0.1)
        self.multipleSignalsFig.tight_layout()
        self.multipleSignalsPlot.draw()

    # **************** Function to update Single Event *******************************#
    def updatesingleevent(self):
        indxarr = self.data.headerdf.query(
            "evttype == @self.eventType and pixel == @self.chan"
        ).index
        print(len(indxarr))
        if len(indxarr) == 0:
            self.timeax, self.pulsedata = self.getrandomdata()
            self.p3.setData(self.timeax, self.pulsedata)
            return
        if len(indxarr) < self.evtno:
            self.evtno = len(indxarr) // 2
            self.value_evtno.setText(str(self.evtno))

        if self.eventType == "trigger":
            self.timeax, self.pulsedata = self.data.getsingleeventdata(
                "single", eventno=indxarr[self.evtno], chan=self.chan
            )
        else:
            self.timeax, self.pulsedata = self.data.getsingleeventdata(
                self.eventType, eventno=indxarr[self.evtno], chan=self.chan
            )
        self.p3.setData(self.timeax, self.pulsedata)
        # self.timeax, self.pulsedata = self.data.getsingleeventdata(self.eventType,'0',eventno=self.evtno)

    def updatemultipleevents(self):
        indxarr = self.data.headerdf.query(
            "evttype == @self.eventType and pixel == @self.chan"
        ).index
        print(len(indxarr))
        if len(indxarr) == 0:
            self.p4.clear()
            # return
        if len(indxarr) < 200:
            events = indxarr
        else:
            events = np.random.choice(indxarr, 200)

        if self.eventType == "trigger":
            self.pulseimg, self.xbin, self.ybin = self.data.getmultipleeventdata(
                "single", events=events
            )
        else:
            self.pulseimg, self.xbin, self.ybin = self.data.getmultipleeventdata(
                self.eventType, events=events
            )
        self.p4.clear()
        self.p4.setImage(self.pulseimg, autoLevels=True)  # , log = logval)
        self.correctscale(self.p4, xscale=self.xbin, yscale=self.ybin)
        self.pw4.setAspectLocked(False)

        # self.p4.setImage(self.pulseimg, xvals = self.xbin, yvals = self.ybin)
        # self.timeax, self.pulsedata = self.data.getsingleeventdata(self.eventType,'0',eventno=self.evtno)
        # self.timeax, self.noisedata = self.data.getnoisedata(self.evtno)
        # self.p4.setData(self.timeax,self.pulsedata)
        # self.p4.setColorMap('CET-L17')
        # if self.pw4.
        # self.pw4.addColorBar(self.p4, colorMap = 'CET-L9', values = (self.pulseimg.min(), self.pulseimg.max()))

    # **************** Function to update pixel hits *******************************#
    def updatepixhits(self):
        self.pixel_plot_figure1.clf()
        self.pixel_plot_runaxis.cla()
        self.pixel_plot_subrunaxis.cla()
        self.getnewfig()

        self.data.updatepixplot(
            self.data.subrundata["bottom"][self.eventType],
            self.pixel_plot_figure1,
            self.pixel_plot_subrunaxis,
            self.clbar,
            self.norm,
            self.customcmap,
        )

        self.data.updatepixplot(
            self.data.rundata["bottom"][self.eventType],
            self.pixel_plot_figure1,
            self.pixel_plot_runaxis,
            self.clbar,
            self.norm,
            self.customcmap,
        )

        self.pixel_plot_widget1.draw()

    # ***********************************************#*******************************#

    def updatexy(self):
        if self.data is not None:
            x, y = self.data.getsingle_chan_evnt(self.evtno, self.chan)
            self.p1.setData(x=x, y=y)

    def updaterangeplot(self):
        self.getlims()
        self.lims[0] = 0
        self.lims[1] = 20
        x, y = self.data.getrangedata(self.lims[0], self.lims[1], self.chan)
        self.p3.setData(x=x, y=y)

    def updatedistribution(self):
        hx, hy = self.data.gethistdistribution(self.chan)
        self.p2.setData(hx, hy)

    # *************** Other Functions not used now *****************************************************#
    def getlims(self):
        templims = self.value_lims.text().split(sep=",")
        if len(templims) == 2:
            self.lims = [int(float(i)) for i in templims]
            if self.lims[1] > self.data.totalevents:
                self.lims[1] = self.data.totalevents - 2
        if len(self.lims) == 2:
            self.evtno = self.lims[0]
            self.value_evtno.setText(str(self.evtno))
            self.updatexy()

    def getrandomdata(self):
        x = np.random.normal(size=(10))
        y = np.random.normal(size=(10))
        return (x, y)

    def runfreerun(self):
        if self.button_freerun.isChecked():
            self.timer.timeout.connect(self.shownextevent)
            self.timer.start(1000)
        else:
            self.timer.stop()

    def shownextevent(self):
        self.evtno = self.evtno + 1
        self.value_evtno.setText(str(self.evtno))
        self.updatesingleevent()
        # self.updatemultipleevent()

    def showpreviousevent(self):
        self.evtno = self.evtno - 1
        self.value_evtno.setText(str(self.evtno))
        self.updatesingleevent()
        # self.updatemultipleevent()

    def selectnormalization(self):
        if self.button_norm.isChecked():
            self.norm = "log"
        else:
            self.norm = None
        self.updatepixhits()

        # self.timeax, self.noisedata = self.data.getnoisedata(self.evtno)
        # print(self.timeax, self.noisedata)
        # self.p4.setData(self.timeax,self.noisedata)

    # *************** Function to plot detetor hits*****************************************************#

    def getmycmap(self, basemap="viridis"):
        ocmap = plt.get_cmap(basemap)
        ocmap = ocmap(np.linspace(0, 1, 256))
        ocmap[:1, :] = [0.95, 0.95, 0.95, 1]
        ncmap = colors.ListedColormap(ocmap)
        return ncmap
