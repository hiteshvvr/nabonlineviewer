from matplotlib.pyplot import axis
import numpy as np

# import h5py as hd
import pandas as pd
import glob as gl
import sys
import os

nabPath = "/Users/seeker/TNwork/nabonlineanalysis/nabpyinstallations/pyNab/src"
deltaRicePath = "/Users/seeker/TNwork/nabonlineanalysis/nabpyinstallations/deltarice/build/lib.macosx-11.0-arm64-cpython-312/"

sys.path.append(deltaRicePath)
sys.path.append(nabPath)

import nabPy as Nab


class MData:
    def __init__(self) -> None:
        self.data = None
        self.dirname = None
        self.filename = None
        self.runno = None
        # self.eventsig = 0xaa55f154
        self.mdata = None
        self.headerinfo = 1
        self.totalevents = 0
        self.dataarea = 0
        self.timebinwidth = 320e-6
        self.bins = 100
        self._detector = ["top", "bottom"]
        self._eventType = ["trigger", "single", "coincidence", "pulser", "noise"]
        self.reset_containers()

        # self.coinEventdf = pd.DataFrame({'evttype':np.zeros(2), 'numtrig':np.zeros(2), 'ptof':np.zeros(2), 'pener':np.zeros(2), 'ppix':np.zeros(2), 'eener':np.zeros(2), 'epix':np.zeros(2), 'tstamp': np.zeros(2)})

    def reset_containers(self):

        self.coinEventdf = pd.DataFrame()

        self.runstats = {
            "Trigger": 7,
            "Single": 3,
            "Coincidence": 2,
            "Pulser": 1,
            "Noise": 1,
        }
        self.subrunstats = {
            "Trigger": 7,
            "Single": 3,
            "Coincidence": 2,
            "Pulser": 1,
            "Noise": 1,
        }

        self.subrundata = {
            "top": {
                "trigger": np.random.randint(1, size=127),
                "single": np.random.randint(1, size=127),
                "coincidence": np.random.randint(1, size=127),
                "pulser": np.random.randint(1, size=127),
                "noise": np.random.randint(1, size=127),
            },
            "bottom": {
                "trigger": np.random.randint(1, size=127),
                "single": np.random.randint(1, size=127),
                "coincidence": np.random.randint(1, size=127),
                "pulser": np.random.randint(1, size=127),
                "noise": np.random.randint(1, size=127),
            },
        }

        self.rundata = {
            "top": {
                "trigger": np.random.randint(1, size=127),
                "single": np.random.randint(1, size=127),
                "coincidence": np.random.randint(1, size=127),
                "pulser": np.random.randint(1, size=127),
                "noise": np.random.randint(1, size=127),
            },
            "bottom": {
                "trigger": np.random.randint(1, size=127),
                "single": np.random.randint(1, size=127),
                "coincidence": np.random.randint(1, size=127),
                "pulser": np.random.randint(1, size=127),
                "noise": np.random.randint(1, size=127),
            },
        }

    def geteventdataframe(self):
        self.rawdata = hd.File(self.fname, "r")
        self.eventsdata = self.rawdata["events"][()]
        teventlist = []
        for i in range(len(self.eventsdata)):
            evtstr = {
                "event_id": self.eventsdata[i][0],
                "event_type": self.eventsdata[i][1],
                "nu_waveforms": self.eventsdata[i][2],
                "wave_len": self.eventsdata[i][3],
                "base_tmstamp": self.eventsdata[i][4],
                "nu_trigs": self.eventsdata[i][5],
                "triggers": self.eventsdata[i][6][0],
            }
            teventlist.append(evtstr)
        self.eventsdf = pd.DataFrame(teventlist)
        print(self.eventsdf.shape)

        return self.eventsdf

    def getdatafromfile(self, readallsubruns=False):
        """
        Load various datas in the current viewer
        readallsubruns argument will be deprecated in future!
        """

        # self.headerdf = pd.DataFrame( {"timestamp": [0, 0], "pixel": [0, 0], "evttype": ["dummy", "dummy"]})
        self.headerdf = pd.DataFrame()
# 
        # if readallsubruns:
        #     self._thisRun = Nab.DataRun(self.dirname, self.runno)
        # else:
        #     self._thisRun = Nab.File(self.filename)

        self._thisRun = Nab.File(self.filename)
        self.fileData = self._thisRun.noiseWaves().headers()

        self.get_data_summary()

        for i in self._detector:
            for j in self._eventType:
                # print(i,j)
                try:
                    self.subrundata[i][j] = self._thisRun.plotHitLocations(j, det=i)
                    self.rundata[i][j] = self.rundata[i][j] + self.subrundata[i][j]
                except:
                    self.subrundata[i][j] = np.zeros(127)
                    self.rundata[i][j] = self.rundata[i][j] + self.subrundata[i][j]

                self.rundata[i][j][self.rundata[i][j] <= 0] = 0.01
                self.subrundata[i][j][self.subrundata[i][j] <= 0] = 0.01

        tdf = self._thisRun.singleWaves().headers()
        if tdf is not None:
            self.clean_and_append_df(tdf, "single")
            del tdf
        tdf = self._thisRun.coincWaves().headers()
        if tdf is not None:
            self.clean_and_append_df(tdf, "coincidence")
            del tdf
        tdf = self._thisRun.pulsrWaves().headers()
        if tdf is not None:
            self.clean_and_append_df(tdf, "pulser")
            del tdf
        tdf = self._thisRun.noiseWaves().headers()
        if tdf is not None:
            self.clean_and_append_df(tdf, "noise")
            del tdf
        # print(self.headerdf.shape)

        self.get_eventarray()
        self.coinEventdf = pd.concat([self.coinEventdf, self.get_coinc_df()])

    def clean_and_append_df(self, df, evttype):
        df = df.drop(
            columns=[
                "result",
                "bc",
                "req",
                "event type",
                "hit type",
                "blank",
                "eventid",
                "checksum",
                "board",
                "channel",
                "unix timestamp",
            ]
        )
        df["evttype"] = evttype
        self.headerdf = pd.concat([self.headerdf, df])

    def getDetPixData(self, eventType, det="top"):
        self.eventType = eventType
        try:
            self.pixhist = self._thisRun.plotHitLocations(self.eventType, det=det)
        except:
            self.pixhist = np.zeros(127)
        return self.pixhist

    # YOU NEED TO FIGURE THIS OUT :,)
    def get_data_summary(self):
        self.subrunstats["Trigger"] = self._thisRun.triggers().numtrigs
        self.runstats["Trigger"] = (
            self.runstats["Trigger"] + self.subrunstats["Trigger"]
        )

        self.subrunstats["Single"] = self._thisRun.singleWaves().numWaves
        self.runstats["Single"] = self.runstats["Single"] + self.subrunstats["Single"]

        self.subrunstats["Coincidence"] = self._thisRun.coincWaves().numWaves
        self.runstats["Coincidence"] = (
            self.runstats["Coincidence"] + self.subrunstats["Coincidence"]
        )

        self.subrunstats["Noise"] = self._thisRun.noiseWaves().numWaves
        self.runstats["Noise"] = self.runstats["Noise"] + self.subrunstats["Noise"]

        self.subrunstats["Pulser"] = self._thisRun.pulsrWaves().numWaves
        self.runstats["Pulser"] = self.runstats["Pulser"] + self.subrunstats["Pulser"]

        # return(self.strTrig, self.strSingles, self.strCoincs, self.strNoise, self.strPulse)
        # print(type(self.strTrig))

        # print('Triggers: ', self._thisRun.triggers().numtrigs)
        # print('Singles: ', self._thisRun.singleWaves().numWaves)
        # print('Coincidences: ', self._thisRun.coincWaves().numWaves)
        # print('Baseline Traces: ', self._thisRun.noiseWaves().numWaves)
        # print('Pulsers: ', self._thisRun.pulsrWaves().numWaves)

    def updatepixplot(self, pixdata, afig, aaxis, acbar, norm, cmap):
        detfig = Nab.nplt.detectorFigure()
        detfig.logNorm = norm
        detfig.fig = afig
        detfig.ax = aaxis
        detfig.cbar = acbar
        detfig.cmap = cmap
        afig, aaxis, acbar = detfig.createFigure(pixdata)
        # preampLabels = Nab.nplt.returnPreampLabels(detfig.parameterFile.BoardChannelPixelMap[:128]) # Create the preamp labels
        # pLabels = [f'{i}\n{j}' for i,j in zip(np.arange(1,128),preampLabels)] # Otherwise, it will default to pixel number and preamp channel.
        # pLabels = [f'{i}\n{j}' for i,j in zip(np.arange(1,128),preampLabels)] # Otherwise, it will default to pixel number and preamp channel.
        # scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=self.customcmap)
        pLabels = [
            f"{i}\n{j}" for i, j in zip(np.arange(1, 128), pixdata)
        ]  # Add the values to the labels
        detfig.setPixelLabels(aaxis, pLabels)
        afig.set_tight_layout(tight=True)
        aaxis.set_axis_off()
        try:
            acbar.formatter.set_powerlimits((0, 0))
        except:
            pass

        return (afig, aaxis, acbar)

    def getpulsedata_old(self, eventType="noise", eventno=0, len=1):
        try:
            if eventType == "noise":
                self.pulsedata = (
                    self._thisRun.noiseWaves()
                    .waves()[eventno : eventno + len]
                    .compute()
                )
            elif eventType == "single":
                self.pulsedata = (
                    self._thisRun.singleWaves()
                    .waves()[eventno : eventno + len]
                    .compute()
                )
            elif eventType == "coincidence":
                self.pulsedata = (
                    self._thisRun.coincWaves()
                    .waves()[eventno : eventno + len]
                    .compute()
                )
            elif eventType == "pulser":
                self.pulsedata = (
                    self._thisRun.pulsrWaves()
                    .waves()[eventno : eventno + len]
                    .compute()
                )
            elif eventType == "trigger":
                self.pulsedata = (
                    self._thisRun.singleWaves()
                    .waves()[eventno : eventno + len]
                    .compute()
                )

        except:
            self.pulsedata = np.random.normal(size=(len, 10))

        if len == 1:
            self.pulsedata = self.pulsedata[0]

    def getpulsedata(self, eventType="noise", eventno=0, len=1):
        try:
            if eventType == "noise":
                self.pulsedata = self._thisRun.noiseWaves().waves()[eventno].compute()
            elif eventType == "single":
                self.pulsedata = self._thisRun.singleWaves().waves()[eventno].compute()
            elif eventType == "coincidence":
                self.pulsedata = self._thisRun.coincWaves().waves()[eventno].compute()
            elif eventType == "pulser":
                self.pulsedata = self._thisRun.pulsrWaves().waves()[eventno].compute()
            elif eventType == "trigger":
                self.pulsedata = self._thisRun.singleWaves().waves()[eventno].compute()

        except:
            self.pulsedata = np.random.normal(size=(len, 10))

        # if len == 1:
        # self.pulsedata = self.pulsedata[0]

    def getsingleeventdata(self, eventType="noise", eventno=0, chan=0):
        self.getpulsedata(eventType=eventType, eventno=eventno)
        self.timeaxis = np.arange(len(self.pulsedata)) * 4e-9

        return (self.timeaxis, self.pulsedata)

    def getmultipleeventdata(self, eventType="noise", events=0):
        self.getpulsedata(eventType=eventType, eventno=events, len=200)
        self.timeaxis = np.arange(len(self.pulsedata)) * 4e-9

        print(self.pulsedata.ndim)

        xbins = np.arange(len(self.pulsedata[0])) * 4e-9
        self.timeaxis = np.tile(xbins, len(self.pulsedata))
        xbins = len(xbins)
        self.timeaxis = self.timeaxis.flatten()
        self.pulsedata = self.pulsedata.flatten()
        ybins = 200
        H, xbin, ybin = np.histogram2d(
            self.timeaxis, self.pulsedata, bins=(xbins, ybins)
        )
        return (H, xbin, ybin)

    # *******************Attempt 2 extracting energies*********************
    ##Generating a list of all energies for each event
    # def getenergyhistogram(self):
    ##Extracting nested array
    # self.newhdFile = hd.File("../datafiles/hdf5files/Run1612_0.h5", "r")
    # self.evdata = np.array(self.newhdFile['events']) #Not sure if this line will work... might need to chnage data read-in
    # self.energyExtract = np.array([i[6] for i in self.evdata])
    ##Isolating energies
    # self.energy_list = []
    # self.energyList = []
    # for j in range (len(self.energyExtract)):
    # self.energy_list.append([x[2] for x in self.energyExtract[j]])
    # for i in range (len(self.energy_list)):
    # self.energyList.append(float(self.energy_list[:][i][0]))
    # self.updateEnList = np.asarray(self.energyList)
    # print(self.updateEnList.dtype)
    # print(self.updateEnList)
    # self.hy,self.hx = np.histogram(self.updateEnList)
    # self.hyNew=float(self.hy)
    # self.hxNew=float(self.hx)
    # return(self.hyNew, self.hxNew)

    # *******************Attempt 2 extracting energies*********************
    ##Generating a list of all energies for each event
    def getenergyhistogram(self, bins=10, channel=27182):
        self.bins = bins
        self.trigs = self._thisRun.triggers().triggers()
        if (
            channel == 27182
        ):  # this number is natural log, chosed to represent all pixels in lower detector
            self.energy = self.trigs.query("pixel<128").energy.to_numpy()
        elif (
            channel == 31415
        ):  # this number is pi, chosed to represent all pixels in upper detector
            self.energy = self.trigs.query("pixel>128").energy.to_numpy()
        else:
            self.energy = self.trigs.query("pixel == @channel").energy.to_numpy()

        self.counts, self.bins = np.histogram(self.energy, self.bins)

        return (
            self.counts,
            self.bins,
        )  # maybe instead do self.enerG?? So we can do query in top/bottom detector??

    def getbcpixmap(self):
        bctopixmap = self._thisRun.parameterFile().BoardChannelPixelMap
        self.bcpixmap = {}
        for i in bctopixmap:
            self.bcpixmap[int(i[0])] = int(i[1])
        self.vectorized_map = np.vectorize(self.bcpixmap.get)

    def make_event_array(self, ele):
        tstamp = ele[7][0]
        ptof = (ele[7][0] - ele[8][0]) * 4e-9 / 1e-6  # in microseconds
        pener = ele[7][2]
        evttype = ele[1]
        numtrig = ele[4]
        ppix = ele[7][1]
        epix = ele[8][1]
        eener = ele[8][2] + ele[9][2] + ele[10][2] + ele[11][2] + ele[12][2]
        return np.array([evttype, numtrig, ptof, pener, ppix, eener, epix, tstamp])

    def get_eventarray(self):
        self.getbcpixmap()
        self.events = self._thisRun.eventFile().getevents()
        self.evtarr = np.array(list(map(self.make_event_array, self.events)))
        self.evtarr[:, 4] = self.vectorized_map(self.evtarr[:, 4])
        self.evtarr[:, 6] = self.vectorized_map(self.evtarr[:, 6])
        return self.evtarr

    def get_coinc_df(self):
        evtarr = self.evtarr[self.evtarr[:, 0] == 1]
        evtdf = pd.DataFrame(evtarr)
        evtdf.columns = [
            "evttype",
            "numtrig",
            "ptof",
            "pener",
            "ppix",
            "eener",
            "epix",
            "tstamp",
        ]
        # evtdf['time'] = (evtdf.tstamp - evtdf.tstamp.min())*4e-9
        return evtdf
    
    def get_energycut_pixhits(self, det = 'top',eventType = 'single', energylow = -np.inf, energyhigh = np.inf):
        if eventType == "single":
            evttype = 0
        if eventType == "trigger":
            evttype = 0
        if eventType == "coincidence":
            evttype = 1
        if eventType == "pulser":
            evttype = 2
        if eventType == "noise":
            evttype = 3
        
        if det == 'top' or det == 'up' or det == 'upper':
            pixelOffset = 1
        elif det == 'bottom' or det == 'low' or det == 'lower':
            pixelOffset = 1001
        
        numPixels = 127
        
        bins = np.arange(pixelOffset, pixelOffset+numPixels+1)
        enerindx = 3
        pixindx = 4
        if evttype == 1 and det == 'bottom':
            enerindx = 5
            pixindx = 6
        pixels = self.evtarr[self.evtarr[:,0] == evttype]
        pixels = pixels[pixels[:,enerindx]>energylow]
        pixels = pixels[pixels[:,enerindx]<energyhigh]
        pixels = pixels[:,pixindx]
        
        hist = np.histogram(pixels, bins = bins)[0]
        return(hist)