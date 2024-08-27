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


class Analysis(QWidget):
    def __init__(self, data):
        super(QWidget, self).__init__()
        self.layout = QVBoxLayout(self)

        self.data = data
        self.ii = 0
        self.numfile = 0
        self.maintab = QWidget()


        self.mainlayout = QVBoxLayout()
        self.inlayout = QHBoxLayout()
        self.in2layout = QHBoxLayout()
        self.in3layout = QHBoxLayout()

        self.dirname = "../datafiles/hdf5files/Aug2023/"
        self.runno = 2447


        self.buttion_dirname = QPushButton("Select Folder")
        self.field_dirname = QLineEdit(self.dirname)
        self.field_runno = QLineEdit(str(self.runno))

        self.button_wholedata = QRadioButton("ReadAllSubRuns")
        self.readallsubruns = False

        self.data.dirname = self.dirname
        self.data.runno = self.runno

        self.button_load = QPushButton("GetTearDrop")
        self.button_load.clicked.connect(self.getteardrop)

        self.inlayout.addWidget(self.buttion_dirname)
        self.inlayout.addWidget(self.field_dirname)
        self.inlayout.addWidget(self.field_runno)
        self.inlayout.addWidget(self.button_wholedata)
        self.inlayout.addWidget(self.button_load)

        self.size = 2
        self.pixel_plot_widget1 = MatplotlibWidget( (7.5 * self.size, 3.5 * self.size), dpi=100)

        self.getnewfig()

        self.customcmap = self.getmycmap( basemap="cividis")  # To get better colormaps that in nabpy

        self.in2layout.addWidget(self.pixel_plot_widget1)

        self.mainlayout.addLayout(self.inlayout)
        self.mainlayout.addLayout(self.in2layout)

        self.maintab.setLayout(self.mainlayout)

        self.layout.addWidget(self.maintab)
        self.setLayout(self.layout)

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
        self.protonpix_axis = self.analysis_figure.add_subplot(231)
        self.electronpix_axis = self.analysis_figure.add_subplot(232)
        self.electron_tofener_axis = self.analysis_figure.add_subplot(233)
        self.proton_tofener_axis = self.analysis_figure.add_subplot(234)
        self.raw_subrunteardrop_axis = self.analysis_figure.add_subplot(235)
        self.tight_fullteardrop_axis = self.analysis_figure.add_subplot(236)
        self.clbar = None


    def getmycmap(self, basemap="viridis"):
        ocmap = plt.get_cmap(basemap)
        ocmap = ocmap(np.linspace(0, 1, 256))
        ocmap[:1, :] = [0.95, 0.95, 0.95, 1]
        ncmap = colors.ListedColormap(ocmap)
        return ncmap

    def strict_coinc(self, propix,elepix):
        '''
         Strict coincidence Map.
        '''
        out = np.zeros(len(propix),dtype=bool)
        for i in np.arange(1,8):
            out += (propix==i)*((elepix==i)+(elepix==(i+1000+121-1)))
        for i in np.arange(8,16):
            out += (propix==i)*((elepix==i)+(elepix==(i+1000+113-8)))
        for i in np.arange(16,25):
            out += (propix==i)*((elepix==i)+(elepix==(i+1000+104-16)))
        for i in np.arange(25,35):
            out += (propix==i)*((elepix==i)+(elepix==(i+1000+94-25)))
        for i in np.arange(35,46):
            out += (propix==i)*((elepix==i)+(elepix==(i+1000+83-35)))
        for i in np.arange(46,58):
            out += (propix==i)*((elepix==i)+(elepix==(i+1000+71-46)))
        for i in np.arange(58,71):
            out += (propix==i)*((elepix==i)+(elepix==(i+1000)))
        for i in np.arange(71,83):
            out += (propix==i)*((elepix==i)+(elepix==(i+1000-71+46)))
        for i in np.arange(83,94):
            out += (propix==i)*((elepix==i)+(elepix==(i+1000-83+35)))
        for i in np.arange(94,103):
            out += (propix==i)*((elepix==i)+(elepix==(i+1000-94+25)))
        for i in np.arange(104,113):
            out += (propix==i)*((elepix==i)+(elepix==(i+1000-104+16)))
        for i in np.arange(113,121):
            out += (propix==i)*((elepix==i)+(elepix==(i+1000-113+8)))
        for i in np.arange(121,128):
            out += (propix==i)*((elepix==i)+(elepix==(i+1000-121+1)))

        return out

    def getdataarray(self):
        self.evtdf = self.data.coinEventdf.copy()

    def getteardrop(self):
        self.analysis_figure.clf()
        self.getnewfig()

        self.getdataarray()

        ppix = self.evtdf.ppix.to_numpy()
        self.protonpix_axis.clear()
        mappable = self.protonpix_axis.hist(ppix, bins = 500, log=True, histtype='step')

        self.protonpix_axis.set_title("Proton pixel distribution")
        self.protonpix_axis.set_xlabel("Proton hit pixel" )
        self.protonpix_axis.set_ylabel("counts")

        epix= self.evtdf.epix.to_numpy()
        self.electronpix_axis.clear()
        mappable = self.electronpix_axis.hist(epix, bins = 500, log=True, histtype='step')

        self.electronpix_axis.set_title("Electron pixel distribution")
        self.electronpix_axis.set_xlabel("Proton hit pixel" )
        self.electronpix_axis.set_ylabel("counts")

        self.cutdf = self.evtdf.query("ppix < 200 and ppix != 64 and pener < 150 ")

        x = self.cutdf.ptof.to_numpy()
        y = self.cutdf.eener.to_numpy()
        hist2d, binx, biny = np.histogram2d( y * 0.3, 1 / (x * x), bins=[np.linspace(0, 1000, 100), np.linspace(0, 0.008, 100)])
        meshx, meshy = np.meshgrid(binx, biny)
        hist2d_plt = hist2d
        hist2d_plt[hist2d_plt < 1] = np.inf
        self.raw_subrunteardrop_axis.clear()
        mappable = self.raw_subrunteardrop_axis.pcolormesh(meshx, meshy, hist2d.T)
        self.analysis_figure.colorbar(mappable, ax=self.raw_subrunteardrop_axis)

        self.raw_subrunteardrop_axis.grid()
        self.raw_subrunteardrop_axis.set_title("SubRun Teardrop")
        self.raw_subrunteardrop_axis.set_xlabel("Energy(~keV [0.3 x ADC])")
        self.raw_subrunteardrop_axis.set_ylabel("$t_p^{-2}$ ($\mu s^{-2}$)")

        tight_coinc = self.strict_coinc(self.cutdf.ppix.to_numpy(), self.cutdf.epix.to_numpy())
        x = self.cutdf.ptof.to_numpy()
        y = self.cutdf.eener.to_numpy()
        x = x[tight_coinc]
        y = y[tight_coinc]
        hist2d, binx, biny = np.histogram2d( y * 0.3, 1 / (x * x), bins=[np.linspace(0, 1000, 100), np.linspace(0, 0.008, 100)])
        meshx, meshy = np.meshgrid(binx, biny)
        hist2d_plt = hist2d
        hist2d_plt[hist2d_plt < 1] = np.inf
        self.tight_fullteardrop_axis.clear()
        mappable = self.tight_fullteardrop_axis.pcolormesh(meshx, meshy, hist2d.T)
        self.analysis_figure.colorbar(mappable, ax=self.tight_fullteardrop_axis)

        self.tight_fullteardrop_axis.grid()
        self.tight_fullteardrop_axis.set_title("Run Teardrop [tight cuts]")
        self.tight_fullteardrop_axis.set_xlabel("Energy(~keV [0.3 x ADC])")
        self.tight_fullteardrop_axis.set_ylabel("$t_p^{-2}$ ($\mu$s^{-2})")

        x = self.evtdf.ptof.to_numpy()
        y = self.evtdf.pener.to_numpy()
        hist2d, binx, biny = np.histogram2d( y * 0.3, x, bins=[100,100])
        meshx, meshy = np.meshgrid(binx, biny)
        hist2d_plt = hist2d
        hist2d_plt[hist2d_plt < 1] = np.inf
        self.proton_tofener_axis.clear()
        mappable = self.proton_tofener_axis.pcolormesh(meshx, meshy, hist2d.T)
        self.analysis_figure.colorbar(mappable, ax=self.proton_tofener_axis)

        self.proton_tofener_axis.grid()
        self.proton_tofener_axis.set_title("Proton Energy -TOF")
        self.proton_tofener_axis.set_xlabel("Energy(~keV [0.3 x ADC])" )
        self.proton_tofener_axis.set_ylabel("proton tof $\mu s$")

        x = self.evtdf.ptof.to_numpy()
        y = self.evtdf.eener.to_numpy()
        hist2d, binx, biny = np.histogram2d( y * 0.3, x, bins=[100,100])
        meshx, meshy = np.meshgrid(binx, biny)
        hist2d_plt = hist2d
        hist2d_plt[hist2d_plt < 1] = np.inf
        self.electron_tofener_axis.clear()
        mappable = self.electron_tofener_axis.pcolormesh(meshx, meshy, hist2d.T)
        self.analysis_figure.colorbar(mappable, ax=self.electron_tofener_axis)

        self.electron_tofener_axis.grid()
        self.electron_tofener_axis.set_title("Electron Energy -proton TOF")
        self.electron_tofener_axis.set_xlabel("Energy(~keV [0.3 x ADC])")
        self.electron_tofener_axis.set_ylabel("Electron tof $\mu s$")

        self.analysis_figure.tight_layout()
        self.pixel_plot_widget1.draw()

