from PyQt5.QtWidgets import QPushButton, QWidget
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout
from PyQt5.QtWidgets import QLineEdit, QFileDialog, QComboBox
from PyQt5.QtWidgets import QPlainTextEdit #SRW
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
import numpy as np
from hexplot import MplCanvas

import nabPy as Nab
import h5py as hd

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as colors
import matplotlib.cm as cmx


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height),
                          dpi=dpi, constrained_layout=True)
        self.ax = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)

# **********************************************
# We want to replace MplCanvas with nabPy code for pixelated detector plotting
# Below is the original code from SRW Jupyter notebook to plot pixelated detector
# hdfile = Nab.DataRun(hdfilePath, 1612)
# hdfile.plotHitLocations('noise', size = 1.3, rounding='int', alpha = 0.6, title='1612 File')


class MainWindow(QWidget):
    # def __init__(self, parent) -> None:
    def __init__(self, data):
        super(QWidget, self).__init__()
        self.layout = QVBoxLayout(self)
        pg.setConfigOption('background', 'w')

        # Initialize DATA
        self.data = data
        # Initialize Tab
        self.maintab = QWidget()

        # self.height
        self.width = 100

        # Create First Tab
        # self.tab1.layout = QVBoxLayout(self)
        self.mainlayout = QVBoxLayout()
        self.inlayout = QHBoxLayout()
        self.in2layout = QHBoxLayout()
        self.r1layout = QHBoxLayout()
        self.r2layout = QHBoxLayout()
        
        self.foldname = "../datafiles/hdf5files/"
        self.runno = 2447
        
        self.button_foldname = QPushButton('Select Folder')
        self.button_foldname.clicked.connect(self.dialog)
        self.field_foldname = QLineEdit(self.foldname)
        self.field_runno = QLineEdit(str(self.runno))
        
        # self.field_foldname.textChanged.connect(self.updatefoldname)
        # self.field_runno.textChanged.connect(self.updaterunno)
        
        self.data.foldname = self.foldname
        self.data.runno = self.runno
        
        self.button_load = QPushButton('LoadData')
        self.button_load.clicked.connect(self.loaddata)

        self.label_channo = QLabel("Channel")
        self.label_channo.setFixedWidth(60)
        self.sel_channo = QComboBox()
        self.sel_channo.addItems([str(i+1) for i in np.arange(24)])
        self.sel_channo.currentIndexChanged.connect(self.selectchannel)
        self.chan = 0

        self.evtno = 42
        self.lims = [2, 10]
        self.totevnt = 0
        self.totarea = 0
        self.tbinwidth = 320e-6
        self.evtsig = 0xaa55f154

        self.button_freerun = QPushButton('FreeRun')
        self.button_freerun.setCheckable(True)
        self.button_freerun.clicked.connect(self.runfreerun)

        self.button_nextevt = QPushButton('Next')
        self.button_nextevt.clicked.connect(self.shownextevent)

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
        self.label_lims = QLabel("Range")
        self.value_lims = QLineEdit(str(self.lims)[1:-1])
        self.label_lims.setFixedWidth(60)
        self.value_lims.textChanged.connect(self.updatestackplot)
        # self.field_fname.setMaximumWidth(self.width)
        # self.space = QSpacerItem(10,5)

        self.inlayout.addWidget(self.button_foldname)
        self.inlayout.addWidget(self.field_foldname)
        self.inlayout.addWidget(self.field_runno)
        self.inlayout.addWidget(self.button_load)
        #self.inlayout.addWidget(self.sel_channo)

        self.in2layout.addWidget(self.button_freerun)
        self.in2layout.addWidget(self.button_nextevt)
        self.in2layout.addWidget(self.label_evtno)
        self.in2layout.addWidget(self.value_evtno)
        self.in2layout.addWidget(self.label_lims)
        self.in2layout.addWidget(self.value_lims)

        self.in2layout.addWidget(self.label_totevt)
        self.in2layout.addWidget(self.value_totevt)
        self.in2layout.addWidget(self.label_totarea)
        self.in2layout.addWidget(self.value_totarea)

        # self.gwin = pg.GraphicsWindow()
        # self.rplt = self.gwin.addPlot()

        self.pen1 = pg.mkPen('r', width=2)
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

        
        
#******************** Get PixHits (With random data)   **********************       
        #self.size = 2
        #self.sc1 = MplCanvas(self, width=4*self.size, height=3.5*self.size, dpi=100)  # PixDec
        #randompixhist = np.random.random(127)                                         # Random pix hit without loading data
        #self.customcmap = self.getmycmap(basemap='cividis')                           # To get better colormaps that in nabpy
        #self.scalarMap = self.plotOneDetector(randompixhist, self.sc1.fig, self.sc1.ax, cmap=self.customcmap)
        # scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=self.customcmap)
        #self.sc1.fig.colorbar(self.scalarMap, ax=self.sc1.ax)
        #self.tmp = 1

#******************** Get Run Data Summary   ********************** 
        #self.pw1 = pg.PlotWidget( title='<span style="color: #000; font-size: 16pt;">Run Data Summary</span>')
        #self.p1 = self.pw1.plot(stepMode="center",fillLevel=0)#, fillOutline=True,brush=(100,0,0))
        #self.p1.setPen(color=(0, 0, 0), width=2)
        #self.pw1.setLabel('left', 'Counts', units='arb')
        #self.pw1.setLabel('bottom', 'Pixel', units='arb')
        #self.pw1.showGrid(x=True, y=True)
        
        #self.dataSummary = self.data.getDataSummary() #This is the line giving errors
        #self.p2.setData(self.dataSummary)

        self.dataSummary = QPlainTextEdit(self)
        #self.dataSummary.insertPlainText(self.data.getDataSummary()) #To add new lines we add the \n character.
        
        self.dataSummary.move(10,300) #(horizontal, vertical)
        self.dataSummary.resize(400,200)
        self.dataSummary.setReadOnly(True)
#********************* Get Second histogram with pix hist(with random data ***********) *******************

        # self.pw2 = pg.PlotWidget(title="Hit Pixel Data")
        self.pw2 = pg.PlotWidget( title='<span style="color: #000; font-size: 16pt;">Hit Pixel Data</span>')
        self.p2 = self.pw2.plot(stepMode="center",fillLevel=0)#, fillOutline=True,brush=(100,0,0))
        self.p2.setPen(color=(0, 0, 0), width=2)
        self.pw2.setLabel('left', 'Counts', units='arb')
        self.pw2.setLabel('bottom', 'Pixel', units='arb')
        self.pw2.showGrid(x=True, y=True)
        
        self.hy, self.hx = np.histogram(np.random.random(100),bins=20)
        self.p2.setData(self.hx, self.hy)
        
        # self.hy,self.hx = self.data.getpixelhistogram() #SRW newly written line
        # print("printing hx, hy", self.hx, self.hy)
        # print(len(self.hx), len(self.hy))

#********************* Third histogram Not used now ************************************      

        self.pw3 = pg.PlotWidget(title="Many Events One after other")
        self.p3 = self.pw3.plot()
        self.p3.setPen(color=(0, 0, 0), width=5)
        self.pw3.setLabel('left', 'Value', units='V')
        self.pw3.setLabel('bottom', 'Time', units='s')
        self.pw3.showGrid(x=True, y=True)

        self.noisedata = np.random.random(10)
        self.timeax = np.arange(10)
        
        self.p3.setData(x=self.timeax, y=self.noisedata)
        
#********************* Example of scatter plot if needed ***********  #
        self.pw4 = pg.PlotWidget( title='<span style="color: #000; font-size: 16pt;">Single Event Plot</span>')
        self.pw4.showGrid(x=True, y=True)
        self.pw4.setLabel('left', 'Value', units='arb')
        self.pw4.setLabel('bottom', 'Time', units='arb')
        
        self.p4 = pg.ScatterPlotItem(size=2, brush=pg.mkBrush(0, 0, 0, 200))
        self.pw4.addItem(self.p4)
       
        
        self.noisedata = np.random.random(1000)
        self.timeax = np.arange(1000)
        self.p4.addPoints(x=self.timeax, y=self.noisedata)
        
# #********************* Timer if needed ***********  #
        self.timer = QtCore.QTimer()

#********************* Layouts ***********  #
        #self.r1layout.addWidget(self.pw1)
        #self.r1layout.addWidget(self.sc1)  # PixDec
        #self.r1layout.addWidget(self.pw2)
        # self.r2layout.addWidget(self.pw3) #Originally commented out SRW
        #self.r2layout.addWidget(self.pw4)

        # self.alayout.addWidget(self.setallVolt)
        # self.alayout.addWidget(self.gwin)
        # self.alayout.addLayout(self.inlayout)
        self.mainlayout.addLayout(self.inlayout)
        #self.mainlayout.addLayout(self.in2layout)
        self.mainlayout.addLayout(self.r1layout)
        self.mainlayout.addLayout(self.r2layout)
        # self.alayout.addWidget(self.pw1)
        # self.alayout.addWidget(self.pw2)

        self.maintab.setLayout(self.mainlayout)
        # self.tab1.setLayout(self.alayout)

        # Add tabs to Widget
        self.layout.addWidget(self.maintab)
        self.setLayout(self.layout)

#************************************************************************** FUNCTIONS ****************************************************************************************  #

#***************Functions for loading Data *****************************************************#
   
    def dialog(self):
        # file , check = QFileDialog.getOpenFileName(None, "QFileDialog.getOpenFileName()", "", "All Files (*);;Python Files (*.py);;Text Files (*.txt)")
        tempfile, self.check = QFileDialog.getOpenFileName(
            None, "SelectFile", "", "")
        if self.check:
            self.fname = tempfile
            self.field_fname.setText(self.fname)
            # print(type(tempfile))
        else:
            self.file = "file not found!!"

    def updatefoldname(self):
        self.foldname = self.field_foldname.text()
        self.data.foldname = self.foldname

    def updaterunno(self):
        try:
            self.runno = int(self.field_runno.text())
            # print("what is runno:", self.runno)
            self.data.runno = self.runno
        except:
            self.field_runno.setText("Inter the integer") 
 
    def loaddata(self):
        """
        Get the data in the data class
        """
        self.updatefoldname()
        self.updaterunno()
        self.data.getdatafromfile()
        self.updateall()
        self.dataSummary.insertPlainText("something")
        print(self.data.getDataSummary())
        return(self.data)

#*************** Functions for Selecting stuff like channen no. event no etc. *****************************************************#
    def selectchannel(self):
        tchan = int(self.sel_channo.currentText()) - 1
        # print(tchan, type(tchan))
        self.chan = tchan
        # self.value_totarea.setText(str(self.data.getarea(self.chan)))
        self.updateall()

    def getevntno(self):
        tempevnt = self.value_evtno.text().split(sep=",")
        self.evtno = int(float(tempevnt[0]))

    def updateevent(self):
        self.getevntno()
        # self.updatexy()
        # self.sc1.draw()
        
#*************** Functions for Updating the plots *****************************************************#
   
#**************** Function to update all plots *******************************#
    def updateall(self):
        if self.data is not None:
            print("Mainwindow do not update anything, all plotting is in Topdetector now")
            # self.updatepixhits()
            # self.updateenergyhistogram() #Should I comment this out SRW?
            # self.updatesingleevent()
            # self.updaterangeplot()
            # self.updatedistribution()
            # self.updatestackplot()

#**************** Function to update Energy histogram *******************************#
#Commenting this IN because now we have this function in MData class SRW 
    def updateenergyhistogram(self):
        self.edges, self.counts = self.data.getenergyhistogram(bins = 10)
        #self.p2.setData(self.edges, self.counts)
 
#**************** Function to update Single Event *******************************#
    def updatesingleevent(self):
        self.timeax, self.data = self.data.getsingleeventdata(self.eventType,'0',eventno=0)
        # self.timeax, self.noisedata = self.data.getnoisedata(self.evtno)
        #self.p4.setData(self.timeax,self.noisedata)
    
#**************** Function to update pixel hits *******************************#
    #def updatepixhits(self):
        # self.sc1.fig.clear(keep_observers=True)
        #if self.data is not None:
            #self.pixhits= self.data.getDetPixData(self.eventType)
            #self.scalarMap = self.plotOneDetector(self.pixhits, self.sc1.fig, self.sc1.ax, cmap=self.customcmap)
            #self.sc1.draw()
        # print(self.pixhits)
        # self.sc1.ax.cla()
        # self.pixhits= self.tmp * np.random.random(127)                                         # Random pix hit without loading data
        # self.tmp = self.tmp * 10
        # self.sc1.fig.colorbar(scalarMap, ax=self.sc1.ax)
#***********************************************#*******************************#


    #def updatexy(self):
        #if self.data is not None:
            #x, y = self.data.getsingle_chan_evnt(self.evtno, self.chan)
            #self.p1.setData(x=x, y=y)

    def updaterangeplot(self):
        self.getlims()
        self.lims[0] = 0
        self.lims[1] = 20
        x, y = self.data.getrangedata(self.lims[0], self.lims[1], self.chan)
        self.p3.setData(x=x, y=y)

    #def updatedistribution(self):
        #hx, hy = self.data.gethistdistribution(self.chan)
        #self.p2.setData(hx, hy)

           
#*************** Other Functions not used now *****************************************************#
    def getlims(self):
        templims = self.value_lims.text().split(sep=",")
        if (len(templims) == 2):
            self.lims = [int(float(i)) for i in templims]
            if (self.lims[1] > self.data.totalevents):
                self.lims[1] = self.data.totalevents - 2
        if (len(self.lims) == 2):
            self.evtno = self.lims[0]
            self.value_evtno.setText(str(self.evtno))
            self.updatexy()

    def updatestackplot(self):
        self.getlims()
        sx, sy = self.data.getstackdata(self.lims[0], self.lims[1], self.chan)
        mx, my = self.data.gettimemean(self.lims[0], self.lims[1], self.chan)
        #.setData(x=sx, y=sy)
        self.p5.setData(x=mx, y=my)

    def runfreerun(self):
        if self.button_freerun.isChecked():
            self.timer.timeout.connect(self.randxy)
            self.timer.start(2000)
        else:
            self.timer.stop()

    def randxy(self):
        if self.data is not None:
            datalen = self.data.totalevents
            self.evtno = np.random.randint(datalen)
            self.value_evtno.setText(str(self.evtno))
            self.updatexy()

    def shownextevent(self):
        self.evtno = self.evtno + 1
        self.value_evtno.setText(str(self.evtno))
        self.updatesingleevent()
        
        # self.timeax, self.noisedata = self.data.getnoisedata(self.evtno)
        # print(self.timeax, self.noisedata)
        # self.p4.setData(self.timeax,self.noisedata)
    
    
#*************** Function to plot detetor hits*****************************************************#
    # this is a simple function that plots values over each pixel
    def plotOneDetector(self, values, fig=None, ax=None, numDet=1, cmap='cividis', size=2, showNum=True, showVal=True, alpha=1, rounding=None, title=None, norm=None, forceMin=None, forceMax=None, labels=None, filename=None, saveDontShow=False):
        # if fig is None or ax is None:
        #     fig, ax = plt.subplots(1, figsize=(
        #         size * 7 + size, size * 7), constrained_layout=True)
        # ax.cla()

        # try:
            # fig.delaxes(fig.axes[1])
        # except:
            # pass
 
        print("figure:", fig)
        print("axis:", ax)
        ax.set_xlim(-size * 13, size * 13)
        ax.set_ylim(-size * 13, size * 13)
        # cm = plt.get_cmap(cmap)
        cm = cmap
        cNorm = None
        minval = np.min(values)
        maxval = np.max(values)
        if forceMin is not None:
            minval = forceMin
        elif norm == 'log':
            if minval <= 0:
                minval = 0.01
        if forceMax is not None:
            maxval = forceMax
        if norm is None:
            cNorm = colors.Normalize(minval, maxval)
        elif norm == 'log':
            cNorm = colors.LogNorm(minval, maxval)
        else:
            print('unrecognized normalization option: needs to be log or not set')
            return (fig, ax)
        scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cm)
        vertOffset = size * np.sqrt(3)
        horOffset = size * 1.5
        colEnd = [7, 15, 24, 34, 45, 57, 70, 82, 93, 103, 112, 120, 127]
        colStart = [1, 8, 16, 25, 35, 46, 58, 71, 83, 94, 104, 113, 121]
        colLen = list(np.array(colEnd) - np.array(colStart) + 1)
        numCol = len(colEnd)
        for pixel in range(1, len(values)+1):
            col = 0
            for j in range(len(colEnd)):
                if pixel >= colStart[j] and pixel <= colEnd[j]:
                    col = j
            # number in the column from the top of the column
            numInCol = pixel - colStart[col]
            horPosition = (col - numCol/2)*horOffset
            topOfCol = colLen[col]/2*vertOffset - vertOffset/2
            verPosition = topOfCol - vertOffset*numInCol
            hex = patches.RegularPolygon((horPosition, verPosition), numVertices=6, radius=size, facecolor=scalarMap.to_rgba(
                values[pixel-1]), orientation=np.pi/2, alpha=alpha, edgecolor='black')
            ax.add_patch(hex)
            txt = ''
            if showNum == True:
                txt += str(pixel)
            if labels is not None:
                if txt != '':
                    txt += '\n'
                txt += str(labels[pixel-1])
            if showVal:
                if txt != '':
                    txt += '\n'
                if rounding is not None:
                    if rounding == 'int':
                        txt += str(int(values[pixel-1]))
                    else:
                        txt += str(round(values[pixel-1], rounding))
            if txt != '':
                ax.text(horPosition-size/2, verPosition,
                        txt, ma='center', va='center')
        # axColor = plt.axes([size*6, size*-6, size, size*])
        # plt.colorbar(scalarMap, cax = axColor, orientation="vertical")
        # try:
            # fig.delaxes(fig.axes[1])
        # except:
            # pass
        # fig.colorbar(scalarMap, ax=ax)
        # fig.colorbar(scalarMap, ax=ax)
        # plt.axis('off')
        return scalarMap

    def getmycmap(self, basemap='viridis'):
        ocmap = plt.get_cmap(basemap)
        ocmap = ocmap(np.linspace(0, 1, 256))
        ocmap[:1, :] = ([0.95, 0.95, 0.95, 1])
        ncmap = colors.ListedColormap(ocmap)
        return (ncmap)
