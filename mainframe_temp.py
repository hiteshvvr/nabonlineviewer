from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget
from PyQt5.QtWidgets import QTabWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt5.QtWidgets import QStyleFactory, QLineEdit, QFileDialog
from PyQt5.QtWidgets import QComboBox
import pyqtgraph as pg
from monitor1 import Monitor1Tab
from pyqtgraph.Qt import QtCore
import numpy as np


class MyTabWidget(QWidget):
    def __init__(self, parent) -> None:
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        pg.setConfigOption('background', 'w')

        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = Monitor1Tab()
        self.tab3 = QWidget()
        # self.loaddata = SelectDataTab()
        # self.loaddatatab = self.loaddata.gettab()

        # self.height = 30
        self.width = 100

        # Add tabs
        self.tabs.addTab(self.tab1, "Main window")
        self.tabs.addTab(self.tab2, "Monitor 1")
        self.tabs.addTab(self.tab3, "Monitor 2")

        # Create First Tab
        # self.tab1.layout = QVBoxLayout(self)
        self.mainlayout = QVBoxLayout()
        self.inlayout = QHBoxLayout()
        self.in2layout = QHBoxLayout()
        self.r1layout = QHBoxLayout()
        self.r2layout = QHBoxLayout()
        # self.l = QLabel()
        # self.l.setText("This is First Tab")
        # self.tab1.layout.addWidget(self.l)
        # self.alayout.addWidget(self.l)
        # self.tab1.setLayout(self.tab1.layout)
        self.button_fname = QPushButton('Select File')
        self.fname = "/Users/seeker/picarddata/2022/01Jan/070122/run-16043data-21"
        self.button_fname.clicked.connect(self.dialog)
        self.field_fname = QLineEdit(self.fname)
        self.field_fname.textChanged.connect(self.updatefname)
        self.data = None
        self.button_load = QPushButton('LoadData')
        self.button_load.clicked.connect(self.loaddata)

        self.label_channo = QLabel("Channel")
        self.label_channo.setFixedWidth(60)
        self.sel_channo = QComboBox()
        self.sel_channo.currentIndexChanged.connect(self.selectchannel)
        self.sel_channo.addItems([str(i) for i in np.arange(24)])
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
        self.label_evtno = QLabel("Event")
        # self.label_evtno.setFixedWidth(60)
        self.value_evtno = QLineEdit(str(self.evtno))

        self.label_totevt = QLabel("Total. Event")
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

        self.inlayout.addWidget(self.button_fname)
        self.inlayout.addWidget(self.field_fname)
        self.inlayout.addWidget(self.button_load)
        self.inlayout.addWidget(self.sel_channo)

        self.in2layout.addWidget(self.button_freerun)
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

#       INITIAL RANDOM DATA
        self.x = np.arange(100)
        self.y = np.random.random(100)
        self.bins = 40
        self.hy, self.hx = np.histogram(self.y, bins=self.bins)

#       PLOTS

        self.pw1 = pg.PlotWidget(name="testplot")
        self.pen1 = pg.mkPen(
            color=(0, 0, 0), style=QtCore.Qt.DotLine, width=2)
        self.p1 = self.pw1.plot(pen=self.pen1)
        # self.p1.setPen(color = (0,0,0), width = 2)
        self.pw1.setLabel('left', 'Value', units='V')
        self.pw1.setLabel('bottom', 'Time', units='s')
        self.p1.setData(x=self.x, y=self.y)
        self.pw1.showGrid(x=True, y=True)

        self.pw2 = pg.PlotWidget(name="testplot")

        self.p2 = self.pw2.plot(stepMode="center")
        #  fillLevel=0, fillOutline=True,brush=(100,0,0))
        self.p2.setPen(color=(0, 0, 0), width=2)
        self.pw2.setLabel('left', 'Counts', units='arb')
        self.pw2.setLabel('bottom', 'Volts', units='V')
        self.p2.setData(self.hx, self.hy)
        self.pw2.showGrid(x=True, y=True)

        self.pw3 = pg.PlotWidget(name="testplot")
        self.p3 = self.pw3.plot()
        self.p3.setPen(color=(0, 0, 0), width=5)
        self.pw3.setLabel('left', 'Value', units='V')
        self.pw3.setLabel('bottom', 'Time', units='s')
        self.p3.setData(x=self.x, y=self.y)
        self.pw3.showGrid(x=True, y=True)

        self.pw4 = pg.PlotWidget(name="testplot")
        self.p4 = pg.ScatterPlotItem(size=2, brush=pg.mkBrush(0, 0, 0, 200))
        self.p4.addPoints(x=self.x, y=self.y)

        self.p5 = self.pw4.plot()
        #  fillLevel=0, fillOutline=True,brush=(100,0,0))
        self.p5.setPen(color=(0, 0, 0), width=2)
        self.p5.setData(self.x, self.y)

        self.pw4.addItem(self.p4)
        self.pw4.setLabel('left', 'Value', units='V')
        self.pw4.setLabel('bottom', 'Time', units='s')
        # self.p4.setData(x=self.x, y = self.y)
        # self.pw4.showGrid(x=True, y=True)

        self.timer = QtCore.QTimer()

        self.r1layout.addWidget(self.pw1)
        self.r1layout.addWidget(self.pw2)
        self.r2layout.addWidget(self.pw3)
        self.r2layout.addWidget(self.pw4)

        # self.alayout.addWidget(self.setallVolt)
        # self.alayout.addWidget(self.gwin)
        # self.alayout.addLayout(self.inlayout)
        self.mainlayout.addLayout(self.inlayout)
        self.mainlayout.addLayout(self.in2layout)
        self.mainlayout.addLayout(self.r1layout)
        self.mainlayout.addLayout(self.r2layout)
        # self.alayout.addWidget(self.pw1)
        # self.alayout.addWidget(self.pw2)

        self.tab1.setLayout(self.mainlayout)
        # self.tab1.setLayout(self.alayout)

        # Add tabs to Widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

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

    def selectchannel(self):
        tchan = int(self.sel_channo.currentText())
        # print(tchan, type(tchan))
        self.chan = tchan
        self.updateall()

    def getevntno(self):
        tempevnt = self.value_evtno.text().split(sep=",")
        self.evtno = int(float(tempevnt[0]))

    def updateevent(self):
        self.getevntno()
        self.updatexy()

    def getoffset(self):
        header_index = 0
        data = np.fromfile(self.fname, dtype=np.uint32)
        for i in range(0, len(data)):
            if(data[i] == self.evtsig):
                header_index = i
                break
        if(i == len(data) - 1):
            header_index = 0
            tfname = self.fname
            self.field_fname.setText(
                "WARNING: ThIs FiLe Do NoT CoNtAiN PrOpEr HeAdEr")
            self.field_fname.setStyleSheet(
                "color: black;  background-color: red")
            self.fname = tfname
        return(header_index)

    def loaddata(self):
        """
        Get the data in the form of array of 48x40 (2d array)(48 channel column, and 40 rows which are samples)
        """
        # GET OFFSET
        self.field_fname.setStyleSheet(
            "color: black;  background-color: white")
        offset = self.getoffset()
        # offset = 0
        print(offset)

        tdata = np.core.records.fromfile(
            self.fname, formats='(48)int32,(40,48)int32', names='header,data', offset=offset * 4)

        tdata = tdata['data']
        tdata = tdata.transpose(0, 2, 1)
        tdata = tdata // (2**8)
        tdata = 20 * tdata / (2**24)
        self.data = tdata
        self.updateall()
        self.value_totevt.setText(str(len(self.data)))
        self.getarea()
        return(self.data)

    def updateall(self):
        if self.data is not None:
            self.updatexy()
            self.updaterangeplot()
            self.updatenoisehistogram()
            self.updatestackplot()

    def updatexy(self):
        if self.data is not None:
            tevtdata = self.data[self.evtno]
            tchndata = tevtdata[self.chan]
            self.x = np.arange(len(tchndata))
            self.x = self.x * self.tbinwidth
            self.y = tchndata
            self.p1.setData(x=self.x, y=self.y)

    def updaterangeplot(self):
        self.getlims()
        # self.ry = self.data[self.lims[0]:self.lims[1],self.chan].flatten()
        self.ry = self.data[0:20, self.chan].flatten()
        self.rx = np.arange(len(self.ry))
        self.p3.setData(x=self.rx, y=self.ry)

    def updatenoisehistogram(self):
        meandata = self.data.mean(axis=2)
        counts, edges = np.histogram(meandata[:, self.chan], bins=self.bins)
        self.hy, self.hx = counts, edges
        self.p2.setData(self.hx, self.hy)

    def updatefname(self):
        self.fname = self.field_fname.text()

    def getlims(self):
        templims = self.value_lims.text().split(sep=",")
        if(len(templims) == 2):
            self.lims = [int(float(i)) for i in templims]
            if(self.lims[1] > len(self.data)):
                self.lims[1] = len(self.data) - 2
        if(len(self.lims) == 2):
            self.evtno = self.lims[0]
            self.updatexy()

    def updatestackplot(self):
        self.getlims()
        # print(self.lims)
        self.sy = self.data[self.lims[0]:self.lims[1], self.chan].flatten()
        self.sx = np.tile(np.arange(0, len(self.data[0, self.chan])), len(
            self.data[self.lims[0]:self.lims[1], self.chan]))
        self.sx = self.sx * self.tbinwidth
        self.p4.setData(x=self.sx, y=self.sy)
        tmean = self.data[self.lims[0]:self.lims[1], self.chan].mean(axis=0)
        self.my = tmean
        self.mx = np.arange(0, len(self.data[0, self.chan]))
        # print(self.my)
        self.p5.setData(x=self.mx * self.tbinwidth, y=self.my)

    def getarea(self):
        if self.data is not None:
            # talldata = self.data[0:len(self.data)-1,self.chan].flatten()
            talldata = self.data[:, self.chan].flatten()

            # print(talldata.sum())
            self.value_totarea.setText(str(talldata.sum()))

    def runfreerun(self):
        if self.button_freerun.isChecked():
            self.timer.timeout.connect(self.randxy)
            self.timer.start(2000)
        else:
            self.timer.stop()

    def randxy(self):
        if self.data is not None:
            datalen = len(self.data)
            self.evtno = np.random.randint(datalen)
            self.value_evtno.setText(str(self.evtno))
            self.updatexy()
