from matplotlib.pyplot import axis
import numpy as np
import h5py as hd
import pandas as pd


class MData():
    def __init__(self) -> None:
        self.data = None
        self.fname = None
        # self.eventsig = 0xaa55f154
        self.mdata = None
        self.headerinfo = 1
        self.totalevents = 0
        self.dataarea = 0
        self.timebinwidth = 320e-6
        self.bins = 100

    def geteventdataframe(self):
        rawdata = hd.File(self.fname,'r')
        self.eventsdata = rawdata['events'][()]
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

    def getdatafromfile(self):
        """
        Load various datas in the current viewer 
        """
        self.geteventdataframe()
    
    def getsinglesdata(self):
        """
        Get dataframe for singles data
        """