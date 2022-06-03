from turtle import shape
from matplotlib.pyplot import axis
import numpy as np

class MData():
    def __init__(self) -> None:
        self.data = None
        self.fname = None
        self.eventsig = 0xaa55f154
        self.mdata = None
        self.headerinfo = 1
        self.totalevents = 0
        self.dataarea = 0
        self.timebinwidth = 320e-6
        self.bins = 100

    def getoffset(self):
        header_index = -1                         # -1 is reserved for indication of no header
        data = np.fromfile(self.fname, dtype=np.uint32)
        for i in range(0, len(data)):
            if(data[i] == self.eventsig):
                header_index = i
                break
        if(i == len(data) - 1):
            header_index = -1
        return(header_index)

    def getdatafromfile(self):
        """
        Get the data in the form of array of 48x40 (2d array)(48 channel column, and 40 rows which are samples)
        """
        # GET OFFSET
        # print("File: ", self.fname)
        self.offset = self.getoffset()
        # print("Header Offset: ", self.offset)
        if self.offset < 0:
            self.headerinfo = 0
            offset = 0
        else:
            offset = self.offset

        tdata = np.core.records.fromfile(
            self.fname, formats='(48)int32,(40,48)int32', names='header,data', offset=offset * 4)

        tdata = tdata['data']
        tdata = tdata.transpose(0, 2, 1)
        tdata = tdata // (2**8)
        tdata = 20 * tdata / (2**24)

        # Set Various Data Attributes
        self.mdata = tdata
        self.totalevents = len(self.mdata)
        del tdata
        return(self.headerinfo)

    def getarea(self,chan):
        if self.mdata is not None:
            talldata = self.mdata[:, chan].flatten()
            return(talldata.sum())
        else:
            return(0)
    
    def getsingle_chan_evnt(self,evtno,chan):
        if self.mdata is not None:
            ydata = self.mdata[evtno,chan]
            xdata = self.timebinwidth * np.arange(len(ydata))
            return(xdata,ydata)

    def getrangedata(self,llim,hlim,chan):
        if self.mdata is not None:
            ydata = self.mdata[llim:hlim, chan].flatten()
            xdata = np.arange(len(ydata))
            return(xdata, ydata)
    
    def gethistdistribution(self,chan):
        if self.mdata is not None:
            tdata = self.mdata[:,chan].flatten()
            counts, edges = np.histogram(tdata,bins=self.bins)
            return(edges,counts)
    
    def getstackdata(self,llim,hlim,chan):
        if self.mdata is not None:
            singlechandata = self.mdata[llim:hlim,chan]
            ydata = singlechandata.flatten()
            xdata = np.tile(np.arange(0,len(singlechandata[0])), len(singlechandata))
            xdata = xdata*self.timebinwidth
            return(xdata,ydata)
    
    def gettimemean(self,llim=0,hlim=-1,chan=0):
        if self.mdata is not None:
            if hlim == -1:
                hlim = len(self.mdata) - 1
            tmeandata = self.mdata[llim:hlim,chan].mean(axis=0)
            xdata = np.arange(0,len(tmeandata)) * self.timebinwidth
            return(xdata,tmeandata)

    def applyvcut(self, vcutval):
        if self.mdata is not None:
            pass
            # print(self.mdata.shape)
            # # self.mdata = self.mdata[self.mdata<vcutval]
            # tindx = np.any(np.any(self.mdata<vcutval, axis = 2), axis = 1)
            # self.mdata = self.mdata[~tindx]
            # # print("indexshape", tindx.shape)
            # print(~tindx[:20])
            # # self.mdata = np.where(self.mdata < vcutval, self.mdata, self.mdata)
            # print(self.mdata.shape)




