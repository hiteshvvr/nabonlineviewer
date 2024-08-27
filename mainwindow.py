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
    def __init__(self, data):
        super(QWidget, self).__init__()
        self.layout = QVBoxLayout(self)

        self.data = data
        self.ii = 0
        self.numfile = 0
        self.maintab = QWidget()

        self.settings = QSettings("./oldsettings.ini", QSettings.IniFormat)
        try:
            self.dirname = self.settings.value('directory')
            self.runno = self.settings.value('runno')
        except:
            self.dirname = "Select folder to record data"

        self.width = 100

        self.mainlayout = QVBoxLayout()
        self.inlayout = QHBoxLayout()
        self.in2layout = QHBoxLayout()
        self.in3layout = QHBoxLayout()



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

        self.series = QPieSeries()
        self.runseries = QPieSeries()

        self.series.append("Singles", 15)
        self.series.append("Coincidence", 35)
        self.series.append("Noise", 35)
        self.series.append("Pulser", 15)

        self.runseries.append("Singles", 2)
        self.runseries.append("Coincidence", 1)
        self.runseries.append("Noise", 1)
        self.runseries.append("Pulser", 2)

        self.chart = QChart()
        self.runchart = QChart()
        self.chart.addSeries(self.series)
        self.runchart.addSeries(self.runseries)
        self.chart.setTitle(" Subrun Total Triggers : 100")
        self.runchart.setTitle(" Run Total Triggers : 6")
        self.label_dataSummary = QLabel("Run Data Summary")
        self.chart.legend().setAlignment(Qt.AlignRight)
        self.runchart.legend().setAlignment(Qt.AlignRight)
        self._chart_view = QChartView()
        self._runchart_view = QChartView()
        self._chart_view.setChart(self.chart)
        self._runchart_view.setChart(self.runchart)

        self.getManualBox = QPlainTextEdit(self)
        manual = " "
        for line in open("./manual.txt"):
            manual = manual + line
        self.getManualBox.insertPlainText(manual)

        self.getManualBox.setReadOnly(True)
        self.label_manualBox = QLabel("GUI User Manual")

        self.in2layout.addWidget(self._runchart_view)
        self.in2layout.addWidget(self._chart_view)
        self.in3layout.addWidget(self.getManualBox)


        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.havenewsubrun)

        self.mainlayout.addLayout(self.inlayout)
        self.mainlayout.addLayout(self.in2layout)
        self.mainlayout.addLayout(self.in3layout)

        self.maintab.setLayout(self.mainlayout)

        self.layout.addWidget(self.maintab)
        self.setLayout(self.layout)



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
        print(self.runno)

    def updateDataSummary(self):
        self.series.clear()
        self.runseries.clear()
        for evttype, counts in self.data.subrunstats.items():
            self.series.append(evttype, counts)

        for evttype, counts in self.data.runstats.items():
            self.runseries.append(evttype, self.data.runstats[evttype])

        for slice in self.series.slices():
            label = slice.label() + "\t" + str(int(slice.value())) + "("
            label = label + "{:.2f}%".format(100 * slice.percentage()) + ")"
            slice.setLabel(label)

        for slice in self.runseries.slices():
            label = slice.label() + "\t" + str(int(slice.value())) + "("
            label = label + "{:.2f}%".format(100 * slice.percentage()) + ")"
            slice.setLabel(label)

        self.chart.setTitle("SubRun Total Triggers : " + str(self.data.subrunstats['Trigger']))
        self.runchart.setTitle("Run Total Triggers : " + str(self.data.runstats["Trigger"]))
        self._chart_view.update()
        self._runchart_view.update()

    def havenewsubrun(self):
        self.updatefoldname()
        self.updaterunno()
        print("Looking for new file")
        self.filepath = self.dirname + "/" + "Run" + str(self.runno) + "*.h5"
        self.files = gl.glob(self.filepath)
        self.files.sort(key=os.path.getmtime, reverse=True)
        if len(self.files) > self.noofdatafiles and len(self.files) > 2:
            self.data.filename = self.files[1]
            self.noofdatafiles = len(self.files)
        else:
            return
        self.data.getdatafromfile(self.readallsubruns)
        print("Read new file")
        self.updateDataSummary()

    def loaddata(self):
        """
        Get the data in the data class
        """
        self.updatefoldname()
        self.updaterunno()
        self.filepath = self.dirname + "/" + "Run" + str(self.runno) + "*.h5"
        print(self.filepath)
        self.files = gl.glob(self.filepath)
        self.files.sort(key=os.path.getmtime, reverse=True)
        self.noofdatafiles = len(self.files)
        self.data.filename = self.files[0]

        self.readallsubruns = self.button_wholedata.isChecked()
        if self.readallsubruns:
            for i in self.files[:20]:
                self.data.filename = i
                self.data.getdatafromfile(self.readallsubruns)
        else:
            self.data.getdatafromfile(self.readallsubruns)
        self.data.getbcpixmap()
        self.updateDataSummary()
        self.timer.start(5000)
        if self.readallsubruns:
            self.timer.stop()
