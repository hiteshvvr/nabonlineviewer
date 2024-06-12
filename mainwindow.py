from PyQt5.QtWidgets import QPushButton, QWidget
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout
from PyQt5.QtWidgets import QLineEdit, QFileDialog, QComboBox
from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem 
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from PyQt5.QtChart import QChart, QChartView, QPieSeries
from PyQt5.QtCore import Qt
import numpy as np
from hexplot import MplCanvas

import sys

nabPath = "/Users/seeker/TNwork/nabonlineanalysis/nabpyinstallations/pyNab/src"
deltaRicePath = "/Users/seeker/TNwork/nabonlineanalysis/nabpyinstallations/deltarice/build/lib.macosx-11.0-arm64-cpython-312/"

sys.path.append(deltaRicePath)
sys.path.append(nabPath)

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
        self.in4layout = QHBoxLayout()
        self.in5layout = QHBoxLayout()
        self.r1layout = QHBoxLayout()
        self.r2layout = QHBoxLayout()

        # self.dirname = "../datafiles/hdf5files/Aug2023/"
        # self.runno = 2447

        self.buttion_dirname = QPushButton('Select Folder')
        self.buttion_dirname.clicked.connect(self.dialog)
        self.field_dirname = QLineEdit(self.dirname)
        self.field_runno = QLineEdit(str(self.runno))

        # self.field_dirname.textChanged.connect(self.updatefoldname)
        # self.field_runno.textChanged.connect(self.updaterunno)

        self.data.dirname = self.dirname
        self.data.runno = self.runno

        self.button_load = QPushButton('LoadData')
        self.button_load.clicked.connect(self.loaddata)

        self.inlayout.addWidget(self.buttion_dirname)
        self.inlayout.addWidget(self.field_dirname)
        self.inlayout.addWidget(self.field_runno)
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
        
        # ******************** Initializing Textbox for Main Manual *******************************
        self.getManualBox = QPlainTextEdit(self)
        self.getManualBox.insertPlainText("""
            This manual gives basic information for operating the Nab Online Analysis GUI.\n 
            Before moving to other tabs in the GUI, make sure to start in the Main Window tab. Here you should begin
            by setting your local path by either manually typing your path into the first textfield, or by selecting
            the appropriate path using the SelectFolder button. Next, select the desired run number by typing the 
            number into the second textfield. We have automatically initialized this code with a run number of 2447.
            The final step in the Main Window tab is to press the LoadData button. Once completed, the Run Data Summary
            box should be populated with the event types and the number of each event in the selected run number.
            Now, you are free to move to the next tab!\n
            We now move to the Top Detector tab. Here, we begin by first pressing the LoadData button. Next, in order 
            to accurately visualize the data, open the first dropdown menu in the top row and change the event type 
            from singles to noise. This dropdown menu is currently connected to the Pixelated Detector plot and the
            Single Event Plot. After this step, you can select any event type desired. The second dropdown menu is
            a conditionals menu, but it currently is not used in the code. It will not make changes to the plots. The 
            third dropdown menu is a list of the channels for the top detector. This dropdown menu is currently connected
            to the Energy Histogram and will later be connected to the Single Event Plot. In the second row of this tab,
            we have textfields for Energy and Pixel Cuts. See Define Cuts Guide above for more details on what these 
            textfields accept. If you wish to make cuts based on either of these variables, define the cuts and then press
            the LoadEnergyCuts and/or the LoadPixelCuts button(s). These cuts will later be connected to the Pixelated
            Detector plot and the Energy Histogram. Finally, we move to the third row. The FreeRun button, when pressed, 
            displays different events plotted in the Single Event Plot automatically and continuously until the button is 
            pressed to stop this continuous display. The Next and Back buttons are also connected to the Single Event plot
            and allow the user to filter through events in this plot one-by-one. The textfield at the end of the third row
            is for the manual entry of an event number. Again, this is connected to the Single Event plot only. Two of the
            plots given in this tab are dynamic. The Energy Histogram and Single Event plot can be manipulated by scrolling
            up or down with your mouse or by clicking and dragging in any direction.\n
            The Bottom Detector tab follows the same format as the Top Detector tab. The only difference is the channel numbers
            listed in the third dropdown menu of the top row. 
            
        """)
        
        
        self.getManualBox.insertPlainText("""
            This manual gives basic information for operating the Nab Online Analysis GUI.\n 
            Before moving to other tabs in the GUI, make sure to start in the Main Window tab. Here you should begin
            by setting your local path by either manually typing your path into the first textfield, or by selecting
            the appropriate path using the SelectFolder button. Next, select the desired run number by typing the 
            number into the second textfield. We have automatically initialized this code with a run number of 2447.
            The final step in the Main Window tab is to press the LoadData button. Once completed, the Run Data Summary
            box should be populated with the event types and the number of each event in the selected run number.
            Now, you are free to move to the next tab!\n
            We now move to the Top Detector tab. Here, we begin by first pressing the LoadData button. Next, in order 
            to accurately visualize the data, open the first dropdown menu in the top row and change the event type 
            from singles to noise. This dropdown menu is currently connected to the Pixelated Detector plot and the
            Single Event Plot. After this step, you can select any event type desired. The second dropdown menu is
            a conditionals menu, but it currently is not used in the code. It will not make changes to the plots. The 
            third dropdown menu is a list of the channels for the top detector. This dropdown menu is currently connected
            to the Energy Histogram and will later be connected to the Single Event Plot. In the second row of this tab,
            we have textfields for Energy and Pixel Cuts. See Define Cuts Guide above for more details on what these 
            textfields accept. If you wish to make cuts based on either of these variables, define the cuts and then press
            the LoadEnergyCuts and/or the LoadPixelCuts button(s). These cuts will later be connected to the Pixelated
            Detector plot and the Energy Histogram. Finally, we move to the third row. The FreeRun button, when pressed, 
            displays different events plotted in the Single Event Plot automatically and continuously until the button is 
            pressed to stop this continuous display. The Next and Back buttons are also connected to the Single Event plot
            and allow the user to filter through events in this plot one-by-one. The textfield at the end of the third row
            is for the manual entry of an event number. Again, this is connected to the Single Event plot only. Two of the
            plots given in this tab are dynamic. The Energy Histogram and Single Event plot can be manipulated by scrolling
            up or down with your mouse or by clicking and dragging in any direction.\n
            The Bottom Detector tab follows the same format as the Top Detector tab. The only difference is the channel numbers
            listed in the third dropdown menu of the top row. 
            
        """)
        # self.getManualBox.resize(400,200) #Setting size of textbox; useless because I swithed to layouts
        self.getManualBox.setReadOnly(True)
        self.label_manualBox = QLabel("GUI User Manual")

        # ******************* Initializing Textbox for Define Cuts Manual *********************
        self.defineCutsManual = QPlainTextEdit(self)
        self.defineCutsManual.insertPlainText("""
            This manual shows all valid entries for the Energy and Pixel Cuts
            made in the Top Detector and Bottom Detector tabs. Sample entries 
            have been included in both textfields. These examples consist of 
            three components: the variable we wish to cut by, the conditional,
            and the number. The variable name (given as Energy or Pixel)
            should never be altered. The only two items in the list that should
            be changed are the conditional and the number. The conditional 
            symbols currently available to use are >, <, =, <=, >=, and !=. 
            The number can be any valid energy in keV or any valid pixel 
            number based on the detector the user is viewing.\n
            Examples: \n
            ('energy', '!=', 180)
            ('pixel', '>=', 7)

        """)

        self.label_defineCutsManual = QLabel("Define Cuts User Manual")
        self._chart_view = QChartView(self.chart)
        # ******************** Adding Textboxes to in2layout for structure ********************
        # Do not move this. You have to define the widgets BEFORE using these lines of code. See previous sections.
        self.in2layout.addWidget(self.label_dataSummary)
        self.in2layout.addWidget(self.label_defineCutsManual)
        self.in3layout.addWidget(self._chart_view)
        # self.in3layout.addWidget(self._chart_view)
        self.in3layout.addWidget(self.defineCutsManual)
        self.in4layout.addWidget(self.label_manualBox)
        self.in5layout.addWidget(self.getManualBox)

        # ********************* Get Second histogram with pix hist (with random data) *******************

        # #********************* Timer if needed ***********  #
        self.timer = QtCore.QTimer()

        # ********************* Layouts ***********  #
        self.mainlayout.addLayout(self.inlayout)
        self.mainlayout.addLayout(self.in2layout)
        self.mainlayout.addLayout(self.in3layout)
        self.mainlayout.addLayout(self.in4layout)
        self.mainlayout.addLayout(self.in5layout)
        self.mainlayout.addLayout(self.r1layout)
        self.mainlayout.addLayout(self.r2layout)

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
        self.foldname = self.field_dirname.text()
        self.data.foldname = self.foldname

    def updaterunno(self):
        try:
            self.runno = int(self.field_runno.text())
            self.settings.setValue("runno", str(self.runno))
            self.data.runno = self.runno
        except:
            self.field_runno.setText("Enter the integer") 
    # def loadSummary(self):
    #     self.xnew = self.data.getDataSummary()
    #     return(self.xnew)

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

    def loaddata(self):
        """
        Get the data in the data class
        """
        self.updatefoldname()
        self.updaterunno()
        self.data.getdatafromfile()
        self.updateall()
        self.updateDataSummary()
        return(self.data)

    # *************** Functions for Updating the plots *****************************************************#

    # **************** Function to update all plots *******************************#
    def updateall(self):
        if self.data is not None:
            print("Mainwindow do not update anything, all plotting is in Topdetector now")
            # self.updatepixhits()
            # self.updateenergyhistogram() #Should I comment this out SRW?
            # self.updatesingleevent()
            # self.updaterangeplot()
            # self.updatedistribution()
            # self.updatestackplot()

    def getmycmap(self, basemap='viridis'):
        ocmap = plt.get_cmap(basemap)
        ocmap = ocmap(np.linspace(0, 1, 256))
        ocmap[:1, :] = ([0.95, 0.95, 0.95, 1])
        ncmap = colors.ListedColormap(ocmap)
        return (ncmap)
