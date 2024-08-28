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
import dask.array as da  # Multithreaded arrays
import dask.dataframe as dd  # Multithreaded dataframes
import pandas as pd


import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from pyqtgraph.widgets.MatplotlibWidget import MatplotlibWidget
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as colors
import matplotlib.cm as cmx

import numpy as np

from pyqtgraph.widgets.MatplotlibWidget import MatplotlibWidget

import glob as gl
import os

import sys

nabPath = "/Users/seeker/TNwork/nabonlineanalysis/nabpyinstallations/pyNab/src"
deltaRicePath = "/Users/seeker/TNwork/nabonlineanalysis/nabpyinstallations/deltarice/build/lib.macosx-11.0-arm64-cpython-312/"

sys.path.append(deltaRicePath)
sys.path.append(nabPath)

import nabPy as Nab
import h5py as hd


class TimeEvolution(QWidget):
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

        # self.height
        # self.width = 100

        # Create First Tab
        # self.tab1.layout = QVBoxLayout(self)
        self.mainlayout = QVBoxLayout()
        self.inlayout = QHBoxLayout()
        self.in2layout = QHBoxLayout()
        self.in3layout = QHBoxLayout()

        # First Row with Folder name etc.

        self.button_load = QPushButton("GetPlots")
        self.button_load.clicked.connect(self.getplots)

        # Creating dropdown menu to select the channel number
        self.label_channo = QLabel("Channel")
        self.label_channo.setFixedWidth(60)
        self.sel_channo = QComboBox()
        self.sel_channo.addItems([str(i+1) for i in np.arange(127)]) #The channel numbers for top detector are 1-127 
        self.sel_channo.currentIndexChanged.connect(self.selectchannel)
        self.chan = 0

        self.inlayout.addWidget(self.sel_channo)
        self.inlayout.addWidget(self.button_load)
        # self.inlayout.addWidget(self.sel_channo)

        # ******************** Initializing Textbox for Main Manual *******************************
        self.size = 2
        self.pixel_plot_widget1 = MatplotlibWidget( (7.5 * self.size, 3.5 * self.size), dpi=100)
        # self.pixel_plot_widget1.vbox.removeWidget(self.pixel_plot_widget1.toolbar)
        # self.pixel_plot_widget1.toolbar.setVisible(False)

        self.getnewfig()

        self.customcmap = self.getmycmap( basemap="cividis")  # To get better colormaps that in nabpy
        self.in2layout.addWidget(self.pixel_plot_widget1)
        # ********************* Get Second histogram with pix hist (with random data) *******************

        # ********************* Layouts ***********  #
        self.mainlayout.addLayout(self.inlayout)
        self.mainlayout.addLayout(self.in2layout)
        # self.mainlayout.addLayout(self.in3layout)

        self.maintab.setLayout(self.mainlayout)
        # self.tab1.setLayout(self.alayout)

        # Add tabs to Widget
        self.layout.addWidget(self.maintab)
        self.setLayout(self.layout)

    # ************************************************************************** FUNCTIONS ****************************************************************************************  #
    def getnewfig(self):
        try:
            del self.raw_subrunteardrop_axis
            del self.raw_fullteardrop_axis
            del self.tight_fullteardrop_axis
            del self.protontof_axis
            del self.protonener
            del self.electronener
            del self.analysis_figure
            del self.clbar
        except:
            pass
        self.analysis_figure = self.pixel_plot_widget1.getFigure()
        self.analysis_figure.tight_layout(pad=0)
        # self.pixel_plot_runaxis = self.analysis_figure.add_subplot(111)
        self.avg_p_energy_axis = self.analysis_figure.add_subplot(111)
        # self.avg_p_energy_axis = self.analysis_figure.add_subplot(231)
        # self.electronpix_axis = self.analysis_figure.add_subplot(232)
        # self.electron_tofener_axis = self.analysis_figure.add_subplot(233)
        # self.proton_tofener_axis = self.analysis_figure.add_subplot(234)
        # self.raw_subrunteardrop_axis = self.analysis_figure.add_subplot(235)
        # self.tight_fullteardrop_axis = self.analysis_figure.add_subplot(236)
        self.clbar = None

    def getmycmap(self, basemap="viridis"):
        ocmap = plt.get_cmap(basemap)
        ocmap = ocmap(np.linspace(0, 1, 256))
        ocmap[:1, :] = [0.95, 0.95, 0.95, 1]
        ncmap = colors.ListedColormap(ocmap)
        return ncmap

    def getdataarray(self):
        self.evtdf = self.data.coinEventdf.copy()
    
    def selectchannel(self):
        self.chan = int(self.sel_channo.currentText())
        self.getplots()


    def getplots(self):
        self.analysis_figure.clf()
        # self.pixel_plot_runaxis.cla()
        self.getnewfig()

        self.getdataarray()
        self.log = False
        self.avg_p_energy_axis.clear()
        self.mintime = self.evtdf.tstamp.min()
        tdf = self.evtdf.query("ppix == @self.chan")
        tdf['tstamp'] = tdf.tstamp * 4e-9
        tbins = np.linspace(tdf.tstamp.min(), tdf.tstamp.max(), 100)
        avgpener = tdf.groupby(pd.cut(tdf.tstamp, tbins)).pener.mean().to_numpy()
        avgpener_err = tdf.groupby(pd.cut(tdf.tstamp, tbins)).pener.std().to_numpy()
        # mappable = self.avg_p_energy_axis.scatter(tbins[1:], avgpener)#, log = self.log)
        mappable = self.avg_p_energy_axis.errorbar(tbins[1:], avgpener, yerr=avgpener_err, fmt='o')#, log = self.log)
        self.avg_p_energy_axis.grid()
        self.avg_p_energy_axis.set_title("Proton Energy OverTime")
        self.avg_p_energy_axis.set_xlabel("Time in sec" )
        self.avg_p_energy_axis.set_ylabel("adc val")

        # epix= self.evtdf.epix.to_numpy()
        # self.electronpix_axis.clear()
        # epix_bottom_det = epix[epix>300] - 1000
        # epix_top_det = epix[epix<300]
        # mappable = self.electronpix_axis.hist( epix_top_det, bins=500, log=True, histtype="step", alpha=0.99, label="Top")
        # mappable = self.electronpix_axis.hist( epix_bottom_det, bins=500, log=True, histtype="step", alpha=0.99, label="Bottom")
        # self.electronpix_axis.legend(loc="upper right")

        # # self.electronpix_axis.grid()
        # self.electronpix_axis.set_title("Electron pixel distribution")
        # self.electronpix_axis.set_xlabel("Proton hit pixel")
        # self.electronpix_axis.set_ylabel("counts")

        # self.cutdf = self.evtdf.query("ppix < 200 and ppix != 64 and pener < 150 ")

        # x = self.cutdf.ptof.to_numpy()
        # y = self.cutdf.eener.to_numpy()
        # hist2d, binx, biny = np.histogram2d( y * 0.3, 1 / (x * x), bins=[np.linspace(0, 1000, 100), np.linspace(0, 0.008, 100)])
        # meshx, meshy = np.meshgrid(binx, biny)
        # hist2d_plt = hist2d
        # hist2d_plt[hist2d_plt < 1] = np.inf
        # self.raw_subrunteardrop_axis.clear()
        # mappable = self.raw_subrunteardrop_axis.pcolormesh(meshx, meshy, hist2d.T)
        # self.analysis_figure.colorbar(mappable, ax=self.raw_subrunteardrop_axis)

        # self.raw_subrunteardrop_axis.grid()
        # # self.raw_subrunteardrop_axis.colorbars()
        # self.raw_subrunteardrop_axis.set_title("SubRun Teardrop")
        # self.raw_subrunteardrop_axis.set_xlabel("Energy(~keV [0.3 x ADC])")
        # self.raw_subrunteardrop_axis.set_ylabel("$t_p^{-2}$ ($\mu s^{-2}$)")

        # tight_coinc = self.strict_coinc(self.cutdf.ppix.to_numpy(), self.cutdf.epix.to_numpy())
        # x = self.cutdf.ptof.to_numpy()
        # y = self.cutdf.eener.to_numpy()
        # x = x[tight_coinc]
        # y = y[tight_coinc]
        # hist2d, binx, biny = np.histogram2d( y * 0.3, 1 / (x * x), bins=[np.linspace(0, 1000, 100), np.linspace(0, 0.008, 100)])
        # meshx, meshy = np.meshgrid(binx, biny)
        # hist2d_plt = hist2d
        # hist2d_plt[hist2d_plt < 1] = np.inf
        # self.tight_fullteardrop_axis.clear()
        # mappable = self.tight_fullteardrop_axis.pcolormesh(meshx, meshy, hist2d.T)
        # self.analysis_figure.colorbar(mappable, ax=self.tight_fullteardrop_axis)

        # self.tight_fullteardrop_axis.grid()
        # self.tight_fullteardrop_axis.set_title("Run Teardrop [tight cuts]")
        # self.tight_fullteardrop_axis.set_xlabel("Energy(~keV [0.3 x ADC])")
        # self.tight_fullteardrop_axis.set_ylabel("$t_p^{-2}$ ($\mu$s^{-2})")

        # x = self.evtdf.ptof.to_numpy()
        # y = self.evtdf.pener.to_numpy()
        # hist2d, binx, biny = np.histogram2d( y * 0.3, x, bins=[100,100])
        # meshx, meshy = np.meshgrid(binx, biny)
        # hist2d_plt = hist2d
        # hist2d_plt[hist2d_plt < 1] = np.inf
        # self.proton_tofener_axis.clear()
        # mappable = self.proton_tofener_axis.pcolormesh(meshx, meshy, hist2d.T)
        # self.analysis_figure.colorbar(mappable, ax=self.proton_tofener_axis)

        # self.proton_tofener_axis.grid()
        # self.proton_tofener_axis.set_title("Proton Energy -TOF")
        # self.proton_tofener_axis.set_xlabel("Energy(~keV [0.3 x ADC])" )
        # self.proton_tofener_axis.set_ylabel("proton tof $\mu s$")

        # x = self.evtdf.ptof.to_numpy()
        # y = self.evtdf.eener.to_numpy()
        # hist2d, binx, biny = np.histogram2d( y * 0.3, x, bins=[100,100])
        # meshx, meshy = np.meshgrid(binx, biny)
        # hist2d_plt = hist2d
        # hist2d_plt[hist2d_plt < 1] = np.inf
        # self.electron_tofener_axis.clear()
        # mappable = self.electron_tofener_axis.pcolormesh(meshx, meshy, hist2d.T)
        # self.analysis_figure.colorbar(mappable, ax=self.electron_tofener_axis)

        # self.electron_tofener_axis.grid()
        # self.electron_tofener_axis.set_title("Electron Energy -proton TOF")
        # self.electron_tofener_axis.set_xlabel("Energy(~keV [0.3 x ADC])")
        # self.electron_tofener_axis.set_ylabel("Electron tof $\mu s$")

        self.analysis_figure.tight_layout()
        self.pixel_plot_widget1.draw()

# plt.hist2d(y, 1/(x*x)/(4e-3*4e-3),bins=100,range=[[0,1000],[0,0.008]])
# plt.colorbar()
# plt.show()
