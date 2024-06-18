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
            self.dirname = self.settings.value("directory")
            self.runno = self.settings.value("runno")
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

        self.buttion_dirname = QPushButton("Select Folder")
        # self.buttion_dirname.clicked.connect(self.dialog)
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
        self.size = 2
        self.pixel_plot_widget1 = MatplotlibWidget(
            (7.5 * self.size, 3.5 * self.size), dpi=100
        )
        self.pixel_plot_widget1.vbox.removeWidget(self.pixel_plot_widget1.toolbar)
        self.pixel_plot_widget1.toolbar.setVisible(False)

        self.getnewfig()

        # randompixhist = 1 * np.random.random(127)        # Random pix hit without loading data
        randompixhist = 1 * np.random.randint(
            100, size=127
        )  # Random pix hit without loading data
        # self.customcmap = self.getmycmap(basemap='plasma') # To get better colormaps that in nabpy
        self.customcmap = self.getmycmap( basemap="cividis")  # To get better colormaps that in nabpy
        # self.pixel_plot_figure1, self.pixel_plot_runaxis, self.clbar1 = ( self.data.updatepixplot( randompixhist, self.pixel_plot_figure1, self.pixel_plot_runaxis, self.clbar, self.norm, self.customcmap,))

        randompixhist = 1 * np.random.randint( 100, size=127)  # Random pix hit without loading data
        # self.pixel_plot_figure2, self.pixel_plot_subrunaxis, self.clbar2 = ( self.data.updatepixplot( randompixhist, self.pixel_plot_figure1, self.pixel_plot_subrunaxis, self.clbar, self.norm, self.customcmap,))
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
    def getteardrop(self):
        pass

    def getnewfig(self):
        try:
            del self.pixel_plot_runaxis
            del self.pixel_plot_subrunaxis
            del self.pixel_plot_figure1
            del self.clbar
        except:
            pass
        self.pixel_plot_figure1 = self.pixel_plot_widget1.getFigure()
        self.pixel_plot_runaxis = self.pixel_plot_figure1.add_subplot(111)
        # self.pixel_plot_runaxis = self.pixel_plot_figure1.add_subplot(121)
        # self.pixel_plot_subrunaxis = self.pixel_plot_figure1.add_subplot(122)
        self.pixel_plot_runaxis.set_title("teardrop")
        self.pixel_plot_runaxis.plot([1, 2, 3, 4], [1, 4, 2, 3])  
        # self.pixel_plot_subrunaxis.set_title("SubRun")
        self.clbar = None

    def getmycmap(self, basemap="viridis"):
        ocmap = plt.get_cmap(basemap)
        ocmap = ocmap(np.linspace(0, 1, 256))
        ocmap[:1, :] = [0.95, 0.95, 0.95, 1]
        ncmap = colors.ListedColormap(ocmap)
        return ncmap

    def parse_waveforms(self, waveSet,filtType="trap",filtPar=[1250,100,1250]):
        '''
            This function takes a set of Nab waveforms and turns them into data! 
            It's a wrapper for determineEnergyTiming. Expand it to do more things
        '''
        waveData = waveSet.determineEnergyTiming(method=filtType,params=filtPar)
        realTimes = (waveData.data()['timestamp'] - (3500 - waveData.data()['t0']))*4E-9
        waveData.addColumn("realtime",realTimes)

        return waveData

    def generate_tof_arrays(self, waveFrame,proWin=[0,200],tofWin=[10,80]):
        '''
        This takes the parse_waveforms data and uses it to produce a time of flight Pandas dataframe. 
        You can subsequently use this dataframe to do whatever sorts of plotting information you want.
        '''
        coinces = da.unique(waveFrame['eventid']).compute()
        numCoinc = len(coinces)

        t0 = np.zeros(numCoinc)
        tp = np.zeros(numCoinc)
        ee = np.zeros(numCoinc)
        ep = np.zeros(numCoinc)
        pixE = np.zeros(numCoinc)
        pixP = np.zeros(numCoinc)

        i=0
        # We're going to loop through each unique eventid.
        for c in np.arange(numCoinc):

            thisCoinc = coinces[c]
            thisEve = waveFrame.loc[((thisCoinc-1)<waveFrame['eventid'])*(waveFrame['eventid']<(thisCoinc+1))]

            if len(thisEve) < 2:
                continue

            # Do a cut on hit type to separate protons and electrons
            proMask = ((-1 < thisEve['hit type'])*(thisEve['hit type']<1))*(proWin[0] <= thisEve['energy'])*(thisEve['energy'] < proWin[1])
            protons = thisEve.loc[proMask]
            numPro = len(protons)

            eleMask = (1 < thisEve['hit type'])*(thisEve['hit type']<3)
            electrons = thisEve.loc[eleMask]
            numEle = len(electrons)

            # Record this event if we have a proton + some electrons
            if (numPro > 0) and (numEle > 0):

                timestamp = protons.iloc[0]['timestamp']

                pixETmp = electrons['pixel']
                pixPTmp = protons['pixel']

                eleEneArr = electrons['energy']
                proEne = protons['energy']
                eleEne = da.sum(eleEneArr)
                # Add 30 keV to the reconstructed energy of the upper detector
                if pixETmp.iloc[-1] < 1000:
                    eleEne += 30 

                tofTmp = protons.iloc[0]['timestamp'] - electrons.iloc[0]['timestamp']

                t0[i] = timestamp
                tp[i] = tofTmp
                ee[i] = eleEne
                ep[i] = proEne
                pixE[i] = pixETmp.iloc[0]
                pixP[i] = pixPTmp.iloc[0]
            i+=1
        realC = (tp > 0) # Cuts on non-real TOF
        t0 = t0[realC]
        tp = tp[realC] 
        ee = ee[realC]
        ep = ep[realC]
        pixE = pixE[realC]
        pixP = pixP[realC]

        outFrame = pd.DataFrame(np.hstack((t0[:,None],tp[:,None],ee[:,None],ep[:,None],pixE[:,None],pixP[:,None])),
                                columns=['timestamp','tof','energy','Ep','pixE','pixel'])

        return outFrame

    def one_pixel_coinc(self, pro,ele):
        '''
         This is a hardcoded one-pixel coincident map.
            It's fast but not great
        '''
        out = np.zeros(len(pro),dtype=bool)
        for i in np.arange(1,8):
            out += (pro==i)*((ele==i)+(ele==(i+1000+121-1)))
        for i in np.arange(8,16):
            out += (pro==i)*((ele==i)+(ele==(i+1000+113-8)))
        for i in np.arange(16,25):
            out += (pro==i)*((ele==i)+(ele==(i+1000+104-16)))
        for i in np.arange(25,35):
            out += (pro==i)*((ele==i)+(ele==(i+1000+94-25)))
        for i in np.arange(35,46):
            out += (pro==i)*((ele==i)+(ele==(i+1000+83-35)))
        for i in np.arange(46,58):
            out += (pro==i)*((ele==i)+(ele==(i+1000+71-46)))
        for i in np.arange(58,71):
            out += (pro==i)*((ele==i)+(ele==(i+1000)))
        for i in np.arange(71,83):
            out += (pro==i)*((ele==i)+(ele==(i+1000-71+46)))
        for i in np.arange(83,94):
            out += (pro==i)*((ele==i)+(ele==(i+1000-83+35)))
        for i in np.arange(94,103):
            out += (pro==i)*((ele==i)+(ele==(i+1000-94+25)))
        for i in np.arange(104,113):
            out += (pro==i)*((ele==i)+(ele==(i+1000-104+16)))
        for i in np.arange(113,121):
            out += (pro==i)*((ele==i)+(ele==(i+1000-113+8)))
        for i in np.arange(121,128):
            out += (pro==i)*((ele==i)+(ele==(i+1000-121+1)))
        # This next line excludes preamp "L", which has a different gain
        # out *= (pro!=1)*(pro!=8)*(pro!=9)*(pro!=17)*(pro!=18)*(pro!=27)

        return out

    def plot_teardrop(self, data,ees=[0,800/0.3],tofs=[0,0.007],eeSca=0.3,nbins=80,show=True):
        ''' 
        This is the teardrop! 
        I'm doing a dumb 0.3 keV/ADC scaling factor here. 
        For a real analysis we want to actually go convert the "energy" on a pixel-by-pixel basis,
        which means this scaling factor is wrong.
        '''
        hist2d,binx,biny = np.histogram2d(data['energy']*eeSca,1/(data['tof']*data['tof'])/(4e-3*4e-3),
                                          bins=[np.linspace(ees[0],ees[1],nbins)*eeSca,np.linspace(tofs[0],tofs[1],nbins)])
        meshx,meshy = np.meshgrid(binx,biny)
        hist2d_plt = hist2d
        if show:
            hist2d_plt[hist2d_plt<1]-=np.inf
        return hist2d,meshx,meshy

    def getteardrop(self):
        self.pixel_plot_figure1.clf()
        self.pixel_plot_runaxis.cla()
        self.getnewfig()
        pData = self.parse_waveforms(self.data.hdFile.coincWaves())
        pData.resetCuts()                           # I don't actually like this cut. 
        pData.defineCut("t0","between",3000,4000)   # Usually I do a rise time cut instead, but this kills baseline noise better.
        pFrame = self.generate_tof_arrays(pData.data())  # It ends up throwing away a lot of good waveforms though.
        goodC = self.one_pixel_coinc(pFrame['pixel'],pFrame['pixE'])
        hist2d, meshx, meshy = self.plot_teardrop(pFrame[goodC])
        self.pixel_plot_runaxis.pcolormesh(meshx, meshy, hist2d.T)
        self.pixel_plot_runaxis.grid()
        # self.pixel_plot_runaxis.xlabel("Electron Energy (~keV)")
        # self.pixel_plot_runaxis.ylabel("$t_p^{-2}$ ($\mu$s^{-2})")
        self.pixel_plot_widget1.draw()
