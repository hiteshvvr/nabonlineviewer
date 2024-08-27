from matplotlib.pyplot import axis
import numpy as np

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
        self.mdata = None
        self.headerinfo = 1
        self.totalevents = 0
        self.dataarea = 0
        self.timebinwidth = 320e-6
        self.bins = 100
        self._detector = ['top', 'bottom']
        self._eventType = ['trigger', 'single', 'coincidence', 'pulser', 'noise']
        
        self.coinEventdf = pd.DataFrame({'evttype':np.zeros(2), 'numtrig':np.zeros(2), 'ptof':np.zeros(2), 'pener':np.zeros(2), 'ppix':np.zeros(2), 'eener':np.zeros(2), 'epix':np.zeros(2)})
        

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

        self.runstats = { "Trigger": 7, "Single": 3, "Coincidence": 2, "Pulser": 1, "Noise": 1 }
        self.subrunstats = { "Trigger": 7, "Single": 3, "Coincidence": 2, "Pulser": 1, "Noise": 1 }

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
        """
        
        self.headerdf = pd.DataFrame( {"timestamp": [0, 0], "pixel": [0, 0], "evttype": ["dummy", "dummy"]})
        
    
        self._thisRun = Nab.File(self.filename)
        self.fileData = self._thisRun.noiseWaves().headers()

        self.get_data_summary()

        for i in self._detector:
            for j in self._eventType:
                try:
                    self.subrundata[i][j] = self._thisRun.plotHitLocations(j, det=i)
                    self.rundata[i][j] = self.rundata[i][j] + self.subrundata[i][j]
                except:
                    self.subrundata[i][j] = np.zeros(127)  
                    self.rundata[i][j] = self.rundata[i][j] + self.subrundata[i][j]

                self.rundata[i][j][self.rundata[i][j] <= 0 ] = 0.01
                self.subrundata[i][j][self.subrundata[i][j] <= 0 ] = 0.01

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

    def get_data_summary(self):
        self.subrunstats['Trigger'] = self._thisRun.triggers().numtrigs
        self.runstats['Trigger'] = self.runstats['Trigger'] + self.subrunstats['Trigger']

        self.subrunstats['Single'] = self._thisRun.singleWaves().numWaves
        self.runstats['Single'] = self.runstats['Single'] + self.subrunstats['Single']

        self.subrunstats["Coincidence"] = self._thisRun.coincWaves().numWaves
        self.runstats['Coincidence'] = self.runstats['Coincidence'] + self.subrunstats['Coincidence']

        self.subrunstats['Noise'] = self._thisRun.noiseWaves().numWaves
        self.runstats['Noise'] = self.runstats['Noise'] + self.subrunstats['Noise']

        self.subrunstats['Pulser'] = self._thisRun.pulsrWaves().numWaves
        self.runstats['Pulser'] = self.runstats['Pulser'] + self.subrunstats['Pulser']



    def getsinglesdata(self):
        """
        Get dataframe for singles data
        """
        print("did we get here?")

    def updatepixplot(self, pixdata, afig, aaxis, acbar, norm, cmap):
        detfig = Nab.nplt.detectorFigure()
        detfig.logNorm = norm
        detfig.fig = afig
        detfig.ax = aaxis
        detfig.cbar = acbar
        detfig.cmap = cmap
        afig, aaxis, acbar = detfig.createFigure(pixdata)
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

    def getpixelhistogram(self):
        self.pixdata = np.array(
            self.fileData.iloc[:, 11]
        )  # This is code from SRW jupyter notebook
        self.hy, self.hx = np.histogram(self.pixdata)
        return (self.hy, self.hx)

    def getpulsedata_old(self, eventType="noise", eventno=0, len=1):
        try:
            if eventType == "noise":
                self.pulsedata = (
                    self._thisRun.noiseWaves().waves()[eventno : eventno + len].compute()
                )
            elif eventType == "single":
                self.pulsedata = (
                    self._thisRun.singleWaves().waves()[eventno : eventno + len].compute()
                )
            elif eventType == "coincidence":
                self.pulsedata = (
                    self._thisRun.coincWaves().waves()[eventno : eventno + len].compute()
                )
            elif eventType == "pulser":
                self.pulsedata = (
                    self._thisRun.pulsrWaves().waves()[eventno : eventno + len].compute()
                )
            elif eventType == "trigger":
                self.pulsedata = (
                    self._thisRun.singleWaves().waves()[eventno : eventno + len].compute()
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


    def getenergyhistogram(self, bins=10, channel=27182):
        self.bins = bins
        self.trigs = self._thisRun.triggers().triggers()
        if( channel == 27182):  # this number is natural log, chosed to represent all pixels in lower detector
            self.energy = self.trigs.query("pixel<128").energy.to_numpy()
        elif( channel == 31415):  # this number is pi, chosed to represent all pixels in upper detector
            self.energy = self.trigs.query("pixel>128").energy.to_numpy()
        else:
            self.energy = self.trigs.query("pixel == @channel").energy.to_numpy()

        self.counts, self.bins = np.histogram(self.energy, self.bins)

        return( self.counts, self.bins)  # maybe instead do self.enerG?? So we can do query in top/bottom detector??

    def getbcpixmap(self):
        bctopixmap = self._thisRun.parameterFile().BoardChannelPixelMap
        self.bcpixmap = {}
        for i in bctopixmap:
            self.bcpixmap[int(i[0])] = int(i[1])
        self.vectorized_map = np.vectorize(self.bcpixmap.get) 

    def evtarr(self,ele):
        ptof = (ele[7][0] - ele[8][0]) * 4e-9 / 1e-6  # in microseconds
        pener = ele[7][2]
        evttype = ele[1]
        numtrig = ele[4]
        ppix = ele[7][1]
        epix = ele[8][1]
        eener = ele[8][2] + ele[9][2] + ele[10][2] + ele[11][2] + ele[12][2]
        return(np.array([evttype, numtrig, ptof, pener, ppix, eener, epix]))

    def get_coinc_df(self):
        self.getbcpixmap()
        self.events = self._thisRun.eventFile().getevents()
        evtarr = np.array(list(map(self.evtarr, self.events)))
        evtarr[:,4]= self.vectorized_map(evtarr[:,4])
        evtarr[:,6]= self.vectorized_map(evtarr[:,6])
        evtarr = evtarr[evtarr[:,0] == 1]
        evtdf = pd.DataFrame(evtarr)
        evtdf.columns = ['evttype', 'numtrig', 'ptof', 'pener', 'ppix', 'eener', 'epix']
        return(evtdf)   
