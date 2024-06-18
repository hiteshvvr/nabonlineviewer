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

class MData():
    def __init__(self) -> None:
        self.data = None
        self.dirname = None
        self.filename = None
        self.runno= None
        # self.eventsig = 0xaa55f154
        self.mdata = None
        self.headerinfo = 1
        self.totalevents = 0
        self.dataarea = 0
        self.timebinwidth = 320e-6
        self.bins = 100
        self.headerdf = pd.DataFrame({'timestamp':[0,0], 'pixel':[0,0], 'evttype':['dummy','dummy']})
        
        self.rundata = {
            "top":{
                "trigger": np.random.randint(100, size=127),
                "single": np.random.randint(100, size=127),
                "coincidence": np.random.randint(100, size=127),
                "pulser": np.random.randint(100, size=127),
                "noise": np.random.randint(100, size=127),
            },
            
            "bottom":{
                "trigger": np.random.randint(100, size=127),
                "single": np.random.randint(100, size=127),
                "coincidence": np.random.randint(100, size=127),
                "pulser": np.random.randint(100, size=127),
                "noise": np.random.randint(100, size=127),
            },
        }

    def geteventdataframe(self):
        self.rawdata = hd.File(self.fname,'r')
        self.eventsdata = self.rawdata['events'][()]
        teventlist = []
        for i in range(len(self.eventsdata)):
            evtstr = {
                    'event_id':self.eventsdata[i][0],
                    'event_type':self.eventsdata[i][1],
                    'nu_waveforms':self.eventsdata[i][2],
                    'wave_len':self.eventsdata[i][3],
                    'base_tmstamp':self.eventsdata[i][4],
                    'nu_trigs':self.eventsdata[i][5],
                    'triggers':self.eventsdata[i][6][0]
            }
            teventlist.append(evtstr)
        self.eventsdf = pd.DataFrame(teventlist)
        print(self.eventsdf.shape)

        return(self.eventsdf)

    def getdatafromfile(self, readallsubruns = False):
        """
        Load various datas in the current viewer 
        """
        if readallsubruns:
            self.hdFile = Nab.DataRun(self.dirname, self.runno) 
        else:
            self.hdFile = Nab.File(self.filename) 
        self.fileData = self.hdFile.noiseWaves().headers()
        
        tdf = self.hdFile.singleWaves().headers()
        if tdf is not None:
            self.clean_and_append_df(tdf, 'single')
            del tdf
        tdf = self.hdFile.coincWaves().headers()
        if tdf is not None:
            self.clean_and_append_df(tdf, 'coincidence')
            del tdf
        tdf = self.hdFile.pulsrWaves().headers()
        if tdf is not None:
            self.clean_and_append_df(tdf, 'pulser')
            del tdf
        tdf = self.hdFile.noiseWaves().headers()
        if tdf is not None:
            self.clean_and_append_df(tdf, 'noise')
            del tdf
        print(self.headerdf.shape)
    
    def clean_and_append_df(self, df, evttype):
        df = df.drop(columns=['result', 'bc', 'req', 'event type', 'hit type', 'blank', 'eventid', 'checksum', 'board', 'channel', 'unix timestamp'])
        df['evttype'] = evttype
        self.headerdf = pd.concat([self.headerdf,df])
        
        
    def getDetPixData(self,eventType, det = 'top'):
        self.eventType = eventType
        try:
            self.pixhist = self.hdFile.plotHitLocations(self.eventType, det = det)
        except:
            self.pixhist = np.zeros(127)
        return(self.pixhist)

    #YOU NEED TO FIGURE THIS OUT :,)
    def getDataSummary(self):
        summary = {}
        self.trigger = 0
        self.trigger = self.hdFile.triggers().numtrigs
        # summary["Triggers"] = self.trigger
        self.singles = self.hdFile.singleWaves().numWaves
        summary["Singles"] = self.singles
        self.coincs = self.hdFile.coincWaves().numWaves
        summary["Coincences"] = self.coincs
        self.noise = self.hdFile.noiseWaves().numWaves
        summary["Noise"] = self.noise
        self.pulse = self.hdFile.pulsrWaves().numWaves
        summary["Pulser"] = self.pulse

        # return(str(summary))
        return(self.trigger, summary)

        # return(self.strTrig, self.strSingles, self.strCoincs, self.strNoise, self.strPulse) 
        #print(type(self.strTrig))

        #print('Triggers: ', self.hdFile.triggers().numtrigs)
        #print('Singles: ', self.hdFile.singleWaves().numWaves)
        #print('Coincidences: ', self.hdFile.coincWaves().numWaves)
        #print('Baseline Traces: ', self.hdFile.noiseWaves().numWaves)
        #print('Pulsers: ', self.hdFile.pulsrWaves().numWaves)
    

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
        # preampLabels = Nab.nplt.returnPreampLabels(detfig.parameterFile.BoardChannelPixelMap[:128]) # Create the preamp labels
        # pLabels = [f'{i}\n{j}' for i,j in zip(np.arange(1,128),preampLabels)] # Otherwise, it will default to pixel number and preamp channel.
        # pLabels = [f'{i}\n{j}' for i,j in zip(np.arange(1,128),preampLabels)] # Otherwise, it will default to pixel number and preamp channel.
        # scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=self.customcmap)
        pLabels = [f'{i}\n{j}' for i,j in zip(np.arange(1,128),pixdata)] # Add the values to the labels
        detfig.setPixelLabels(aaxis, pLabels)
        afig.set_tight_layout(tight=True)
        aaxis.set_axis_off()
        try:
            acbar.formatter.set_powerlimits((0,0))
        except:
            pass
        
        return(afig, aaxis, acbar)
        
    def getpixelhistogram(self): 
        self.pixdata = np.array(self.fileData.iloc[:,11]) #This is code from SRW jupyter notebook
        # print(len(self.pixdata))
        self.hy,self.hx = np.histogram(self.pixdata)
        # print(self.hx, self.hy)
        # print("getpixelhistogram ran successfully")
        return(self.hy,self.hx)
   
    def getpulsedata_old(self, eventType = 'noise', eventno = 0, len = 1):
        try:
            if eventType == 'noise':
                self.pulsedata = self.hdFile.noiseWaves().waves()[eventno:eventno+len].compute()
            elif eventType == 'single':
                self.pulsedata = self.hdFile.singleWaves().waves()[eventno:eventno+len].compute()
            elif eventType == 'coincidence':
                self.pulsedata = self.hdFile.coincWaves().waves()[eventno:eventno+len].compute()
            elif eventType == 'pulser':
                self.pulsedata = self.hdFile.pulsrWaves().waves()[eventno:eventno+len].compute()
            elif eventType == 'trigger':
                self.pulsedata = self.hdFile.singleWaves().waves()[eventno:eventno+len].compute()
            
        except:
            self.pulsedata = np.random.normal(size = (len,10))
            
        if len == 1:
            self.pulsedata = self.pulsedata[0]  
   
    
    def getpulsedata(self, eventType = 'noise', eventno = 0, len = 1):
        try:
            if eventType == 'noise':
                self.pulsedata = self.hdFile.noiseWaves().waves()[eventno].compute()
            elif eventType == 'single':
                self.pulsedata = self.hdFile.singleWaves().waves()[eventno].compute()
            elif eventType == 'coincidence':
                self.pulsedata = self.hdFile.coincWaves().waves()[eventno].compute()
            elif eventType == 'pulser':
                self.pulsedata = self.hdFile.pulsrWaves().waves()[eventno].compute()
            elif eventType == 'trigger':
                self.pulsedata = self.hdFile.singleWaves().waves()[eventno].compute()
            
        except:
            self.pulsedata = np.random.normal(size = (len,10))
            
        # if len == 1:
            # self.pulsedata = self.pulsedata[0]

    def getsingleeventdata(self,eventType='noise',eventno=0, chan = 0):
        self.getpulsedata(eventType=eventType, eventno=eventno)
        self.timeaxis = np.arange(len(self.pulsedata)) * 4e-9

        return(self.timeaxis,self.pulsedata)
    
    
    def getmultipleeventdata(self,eventType='noise',events=0):
        self.getpulsedata(eventType=eventType, eventno=events, len=200)
        self.timeaxis = np.arange(len(self.pulsedata)) * 4e-9
        
        print(self.pulsedata.ndim)
            
        xbins = np.arange(len(self.pulsedata[0])) * 4e-9
        self.timeaxis = np.tile(xbins, len(self.pulsedata))
        xbins = len(xbins)
        self.timeaxis = self.timeaxis.flatten()
        self.pulsedata = self.pulsedata.flatten()
        ybins = 200
        H, xbin, ybin = np.histogram2d(self.timeaxis, self.pulsedata, bins = (xbins, ybins))
        return(H, xbin, ybin)

    #*******************Attempt 2 extracting energies*********************
    ##Generating a list of all energies for each event 
    #def getenergyhistogram(self): 
        ##Extracting nested array
        #self.newhdFile = hd.File("../datafiles/hdf5files/Run1612_0.h5", "r")
        #self.evdata = np.array(self.newhdFile['events']) #Not sure if this line will work... might need to chnage data read-in
        #self.energyExtract = np.array([i[6] for i in self.evdata])
        ##Isolating energies
        #self.energy_list = []  
        #self.energyList = []
        #for j in range (len(self.energyExtract)):
            #self.energy_list.append([x[2] for x in self.energyExtract[j]])
        #for i in range (len(self.energy_list)):
            #self.energyList.append(float(self.energy_list[:][i][0]))
        #self.updateEnList = np.asarray(self.energyList)
        #print(self.updateEnList.dtype)
        #print(self.updateEnList)
        #self.hy,self.hx = np.histogram(self.updateEnList)
        #self.hyNew=float(self.hy)
        #self.hxNew=float(self.hx)
        #return(self.hyNew, self.hxNew) 

    #*******************Attempt 2 extracting energies*********************
    ##Generating a list of all energies for each event 
    def getenergyhistogram(self,bins=10,channel=27182):
        self.bins = bins
        self.trigs = self.hdFile.triggers().triggers()
        if channel == 27182:                               # this number is natural log, chosed to represent all pixels in lower detector
            self.energy = self.trigs.query("pixel<128").energy.to_numpy()
        elif channel == 31415:                               # this number is pi, chosed to represent all pixels in upper detector
            self.energy = self.trigs.query("pixel>128").energy.to_numpy()
        else:
            self.energy = self.trigs.query("pixel == @channel").energy.to_numpy()
        
            
        self.counts ,self.bins = np.histogram(self.energy, self.bins)
        
        return(self.counts, self.bins) #maybe instead do self.enerG?? So we can do query in top/bottom detector??
