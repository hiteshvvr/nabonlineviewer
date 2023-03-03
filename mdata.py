from matplotlib.pyplot import axis
import numpy as np
import h5py as hd
import pandas as pd
import nabPy as Nab

class MData():
    def __init__(self) -> None:
        self.data = None
        self.foldname = None
        self.runno= None
        # self.eventsig = 0xaa55f154
        self.mdata = None
        self.headerinfo = 1
        self.totalevents = 0
        self.dataarea = 0
        self.timebinwidth = 320e-6
        self.bins = 100

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

    def getdatafromfile(self):
        """
        Load various datas in the current viewer 
        """
        # self.filePath = "../datafiles/hdf5files/"
        # self.filePath = "/Volumes/T7/Nab_Data/"
        # self.runno = 1612
        self.hdFile = Nab.DataRun(self.foldname, self.runno) #We will have to chnage this later so user can input the run number 
        # self.hdFile = Nab.DataRun(self.filePath, 2430) #We will have to chnage this later so user can input the run number 
        self.fileData = self.hdFile.noiseWaves().headers()
        # print("this ran successfully")

    def getDetPixData(self):
        self.pixhist = self.hdFile.plotHitLocations('noise', size = 1.3, rounding='int', alpha = 0.6, title='1612 File')
        return(self.pixhist)

    

    def getsinglesdata(self):
        """
        Get dataframe for singles data
        """
        print("did we get here?")


    def getpixelhistogram(self): #Commenting this block of code in for now SRW
        self.pixdata = np.array(self.fileData.iloc[:,11]) #This is code from SRW jupyter notebook
        # print(len(self.pixdata))
        self.hy,self.hx = np.histogram(self.pixdata)
        # print(self.hx, self.hy)
        # print("getpixelhistogram ran successfully")
        return(self.hy,self.hx)

    def getnoisedata(self,eventno=0): #Commenting this block of code in for now SRW
        self.noisedata = self.hdFile.noiseWaves().waves()[eventno].compute()
        self.timeaxis = np.arange(len(self.noisedata)) * 4e-9
        self.noisedata = np.array(self.noisedata)
        # print(len(self.noisedata),len(self.timeaxis))
        # print(self.noisedata[:2],self.timeaxis[:2])

        return(self.timeaxis,self.noisedata)

    #*******************Attempt 1 extracting energies*********************
    
    #We need to instead try using nabpy to extract energies! 

    #Commenting this out to push because there is an error associated with it.
    
    #def getenergyhistogram(self,bins=100):
        """For now it is giving random data, update it accordingly"""
        #self.evdata = np.array(self.hdFile['events'])
        #print("ENERGY CODE STEP 2")
        #self.nested_data = np.array([i[6] for i in (self.evdata)])
        #print("ENERGY CODE STEP 3")
        #self.energy_list = []
        #for j in range (len(self.nested_data)):
            #self.energy_list.append([x[2] for x in self.nested_data[j]])
        #print(self.energy_list)
        #return(self.energy_list)
        #print("energy CODE RAN SUCCESSFULLY")
        
        
        #self.counts, self.edges = np.histogram(np.random.random(200), bins = bins)
        #return(self.edges, self.counts)