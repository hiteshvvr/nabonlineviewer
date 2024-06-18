from PyQt5.QtWidgets import QPushButton, QWidget, QRadioButton
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout
from PyQt5.QtWidgets import QLineEdit, QFileDialog
from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QComboBox
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from PyQt5.QtChart import QChart, QChartView, QPieSeries
from PyQt5.QtCore import Qt

import glob as gl
import os

import sys

nabPath = "/Users/seeker/TNwork/nabonlineanalysis/nabpyinstallations/pyNab/src"
deltaRicePath = "/Users/seeker/TNwork/nabonlineanalysis/nabpyinstallations/deltarice/build/lib.macosx-11.0-arm64-cpython-312/"

sys.path.append(deltaRicePath)
sys.path.append(nabPath)

import nabPy as Nab
import h5py as hd

class MainWindow(QWidget):
    # def __init__(self, parent) -> None:
    def __init__(self, data):
        super(QWidget, self).__init__()
        self.layout = QVBoxLayout(self)
        # pg.setConfigOption('background', 'w')

        # Initialize DATA
        self.data = data
        self.ii = 0
        self.numfile = 0
        # Initialize Tab
        self.maintab = QWidget()

        # Load previously set values
        self.settings = QSettings("./oldsettings.ini", QSettings.IniFormat)
        try:
            self.dirname = self.settings.value('directory')
            self.runno = self.settings.value('runno')
        except:
            self.dirname = "Select folder to record data"

        # self.height
        self.width = 100

        # Create First Tab
        # self.tab1.layout = QVBoxLayout(self)
        self.mainlayout = QVBoxLayout()
        self.inlayout = QHBoxLayout()
        self.in2layout = QHBoxLayout()
        self.in3layout = QHBoxLayout()

        # self.dirname = "../datafiles/hdf5files/Aug2023/"
        # self.runno = 2447

        # First Row with Folder name etc.

        self.buttion_dirname = QPushButton('Select Folder')
        self.buttion_dirname.clicked.connect(self.dialog)
        self.field_dirname = QLineEdit(self.dirname)
        self.field_runno = QLineEdit(str(self.runno))

        self.button_wholedata = QRadioButton("ReadAllSubRuns")
        self.readallsubruns = False

        self.data.dirname = self.dirname
        self.data.runno = self.runno

        self.button_load = QPushButton('LoadData')
        self.button_load.clicked.connect(self.loaddata)

        self.inlayout.addWidget(self.buttion_dirname)
        self.inlayout.addWidget(self.field_dirname)
        self.inlayout.addWidget(self.field_runno)
        self.inlayout.addWidget(self.button_wholedata)
        self.inlayout.addWidget(self.button_load)
        # self.inlayout.addWidget(self.sel_channo)

        self.series = QPieSeries()

        self.series.append("Trigger", 20)
        self.series.append("Singles", 20)
        self.series.append("Coincidence", 20)
        self.series.append("Noise", 20)
        self.series.append("Pulser", 20)

        self.chart = QChart()
        self.chart.addSeries(self.series)
        self.chart.setTitle("Total Triggers : 100")
        self.label_dataSummary = QLabel("Run Data Summary")
        self.chart.legend().setAlignment(Qt.AlignRight)
        self._chart_view = QChartView(self.chart)

        # ******************** Initializing Textbox for Main Manual *******************************
        self.getManualBox = QPlainTextEdit(self)
        manual = " "
        for line in open("./manual.txt"):
            manual = manual + line
        self.getManualBox.insertPlainText(manual)

        # self.getManualBox.resize(400,200) #Setting size of textbox; useless because I swithed to layouts
        self.getManualBox.setReadOnly(True)
        self.label_manualBox = QLabel("GUI User Manual")

        # self.in2layout.addWidget(self.label_dataSummary)
        self.in2layout.addWidget(self._chart_view)
        # self.in4layout.addWidget(self.label_manualBox)
        self.in3layout.addWidget(self.getManualBox)

        # ********************* Get Second histogram with pix hist (with random data) *******************

        # #********************* Timer if needed ***********  #
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.havenewsubrun)
        self.timer.start(200000)

        # ********************* Layouts ***********  #
        self.mainlayout.addLayout(self.inlayout)
        self.mainlayout.addLayout(self.in2layout)
        self.mainlayout.addLayout(self.in3layout)

        self.maintab.setLayout(self.mainlayout)
        # self.tab1.setLayout(self.alayout)

        # Add tabs to Widget
        self.layout.addWidget(self.maintab)
        self.setLayout(self.layout)

    # ************************************************************************** FUNCTIONS ****************************************************************************************  #

    # ***************Functions for loading Data *****************************************************#

    def dialog(self):
        self.dirname = QFileDialog.getExistingDirectory(
            caption= "Open Directory with data", directory = self.dirname)
        if self.dirname:
            self.field_dirname.setText(self.dirname)
            self.settings.setValue("directory", self.dirname)
        else:
            self.field_dirname.setText= "folder not found!!"

    def updatefoldname(self):
        self.dirname = self.field_dirname.text()
        self.data.dirname = self.dirname + "/"

    def updaterunno(self):
        try:
            self.runno = int(self.field_runno.text())
            self.settings.setValue("runno", str(self.runno))
            self.data.runno = self.runno
            self.numfile = 0
        except:
            self.field_runno.setText("Enter correct Run Number") 

    def updateDataSummary(self):
        trigger, self.dataSum = self.data.getDataSummary()
        self.series.clear()
        for evttype, counts in self.dataSum.items():
            self.series.append(evttype, counts)

        for slice in self.series.slices():
            label = slice.label() + "\t" + str(int(slice.value())) + "("
            label = label + "{:.2f}%".format(100 * slice.percentage()) + ")"
            slice.setLabel(label)

        self.chart.setTitle("Total Triggers : " + str(trigger))
        self._chart_view.update()
    
    def havenewsubrun(self):
        self.filepath = self.dirname + "/" + "Run" + str(self.runno) + "*.h5"
        self.files = gl.glob(self.filepath)
        self.files.sort(key=os.path.getmtime, reverse=True)
        self.data.filename = self.files[0]
        self.data.getdatafromfile(self.readallsubruns)
        self.updateDataSummary()

    def loaddata(self):
        """
        Get the data in the data class
        """
        self.filepath = self.dirname + "/" + "Run" + str(self.runno) + "*.h5"
        self.files = gl.glob(self.filepath)
        self.files.sort(key=os.path.getmtime, reverse=True)
        self.data.filename = self.files[0]
 
        self.updatefoldname()
        self.updaterunno()
        self.readallsubruns = self.button_wholedata.isChecked()
        self.data.getdatafromfile(self.readallsubruns)
        self.updateDataSummary()
        if self.readallsubruns:
            self.timer.stop()
        # return(self.data)
