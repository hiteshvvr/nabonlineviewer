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


    def getpixelhistogram(self): 
        self.pixdata = np.array(self.fileData.iloc[:,11]) #This is code from SRW jupyter notebook
        # print(len(self.pixdata))
        self.hy,self.hx = np.histogram(self.pixdata)
        # print(self.hx, self.hy)
        # print("getpixelhistogram ran successfully")
        return(self.hy,self.hx)

    def getnoisedata(self,eventno=0): 
        self.noisedata = self.hdFile.noiseWaves().waves()[eventno].compute()
        self.timeaxis = np.arange(len(self.noisedata)) * 4e-9
        self.noisedata = np.array(self.noisedata)
        # print(len(self.noisedata),len(self.timeaxis))
        # print(self.noisedata[:2],self.timeaxis[:2])

        return(self.timeaxis,self.noisedata)

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
    def getenergyhistogram(self):
        self.enerG = self.hdFile.triggers().triggers()
        #self.energyList = self.enerG.energy.to_numpy()
        return(self.enerG) #maybe instead do self.enerG?? So we can do query in top/bottom detector??

        


