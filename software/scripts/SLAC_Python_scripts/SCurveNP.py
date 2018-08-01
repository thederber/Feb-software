####import ROOT as R
import numpy as np
import ctypes
import matplotlib #.pyplot as plt
import sys
import time
import re
import logging
import copy
#import PyQt4.QtGui 
#import PyQt4.QtCore 
import json
import random
from matplotlib import pyplot as plt
import pylab as pl
#import matplotlib.animation as animation
from matplotlib.colors import LogNorm
from matplotlib import cm
from matplotlib import ticker
from matplotlib import patches as patches
#import cPickle as pickle
import scipy.io as sio
# Generating log file
def decode_header(frame_rawHeader):
    timestamp=np.uint64()
    frame_size=np.uint32()
    if len(frame_rawHeader)==20:
        for i in range(len(frame_rawHeader)):
            #print ("frame header----: ",bin(frame_rawHeader[i])[2:].rjust(16,"0"))
            if i==0: 
                Virtual_Channel=frame_rawHeader[i]& 0x1
                Destination_ID_Lane_Z=(frame_rawHeader[i]& 0x7e)>>1
                Transaction_ID_1part=(frame_rawHeader[i]&0xff80)>>7
            if i==1:
                Transaction_ID_2part=frame_rawHeader[i] &0xffff
            if i==2:
                Acquire_Counter=frame_rawHeader[i]&0xffff
            if i==3:
                OP_Code=frame_rawHeader[i] & 0xff
                Element_ID=frame_rawHeader[i] & 0xf00
                Destination_ID_Z=frame_rawHeader[i] & 0xf000
            if i==4:
                Frame_Number_1part=frame_rawHeader[i] & 0xffff
            if i==5:
                Frame_Number_2part=frame_rawHeader[i] & 0xffff
            if i==6:
                Ticks_1part=frame_rawHeader[i] & 0xffff
                timestamp+=Ticks_1part
            if i==7:
                Ticks_2part=frame_rawHeader[i]&0xffff
                timestamp+=Ticks_2part<<16
            if i==8:
                Fiducials_1part=frame_rawHeader[i]&0xffff
                timestamp+=Fiducials_1part<<32
            if i==9:
                Fiducials_2part=frame_rawHeader[i]&0xffff
                timestamp+=Fiducials_2part<<48
            if i==10:
                sbtemp_0=frame_rawHeader[i]&0xffff
            if i==11:
                sbtemp_1=frame_rawHeader[i]&0xffff
            if i==12:
                sbtemp_2=frame_rawHeader[i]&0xffff
            if i==13:
                sbtemp_3=frame_rawHeader[i]&0xffff
            if i==14:
                Frame_Type_1part=frame_rawHeader[i]&0xffff
            if i==15:
                Frame_Type_2part=frame_rawHeader[i]&0xffff

            if i==16:
                frame_size+=(frame_rawHeader[i])<<16
            if i==17:
                frame_size+=frame_rawHeader[i]

        frameSize=int((frame_size)/2)-2
    return timestamp,frameSize
 
def decode(TypeOfData,data_temp,frameIndex):
    dvflag_M0,mhflag_M0,col_M0,row_M0,dvflag_M1,mhflag_M1,col_M1,row_M1,dvflag_M2,mhflag_M2,col_M2,row_M2= 0,0,0,0,0,0,0,0,0,0,0,0
    if TypeOfData=="buffer":
        if frameIndex%4==0:
        #if frameIndex%4==0 or frameIndex==0:
            dvflag_M0, mhflag_M0, col_M0, row_M0 = int((data_temp & 0x2000)>0), int((data_temp & 0x1000)>0), (data_temp & 0x0f80)>>7, data_temp & 0x007F # data_temp[13],data_temp[12],[11:7],[6:0]
        if frameIndex%4==1:
            dvflag_M1, mhflag_M1, col_M1, row_M1 = int((data_temp & 0x2000)>0), int((data_temp & 0x1000)>0), (data_temp & 0x0f80)>>7, data_temp & 0x007F # data_temp[13],data_temp[12],[11:7],[6:0]
        if frameIndex%4==2:
            dvflag_M2, mhflag_M2, col_M2, row_M2 = int((data_temp & 0x2000)>0), int((data_temp & 0x1000)>0), (data_temp & 0x0f80)>>7, data_temp & 0x007F # data_temp[13],data_temp[12],[11:7],[6:0]

    return dvflag_M0,mhflag_M0,col_M0,row_M0,dvflag_M1,mhflag_M1,col_M1,row_M1,dvflag_M2,mhflag_M2,col_M2,row_M2     


class frame_data:
    def __init__(self):
        self.dvflag_M0=[]
        self.mhflag_M0=[]
        self.col_M0=[]
        self.row_M0=[]
    
        self.dvflag_M1=[]
        self.mhflag_M1=[]
        self.col_M1=[]
        self.row_M1=[]

        self.dvflag_M2=[]
        self.mhflag_M2=[]
        self.col_M2=[]
        self.row_M2=[]
       
        self.hitmap_t0=np.zeros((128,32))
        self.hitmap_t1=np.zeros((128,32))
        self.hitmap_t2=np.zeros((128,32))

    def add_data(self,TypeOfData,data_temp,frameIndex):
        dvflag_M0_t, mhflag_M0_t, col_M0_t, row_M0_t, dvflag_M1_t, mhflag_M1_t, col_M1_t, row_M1_t, dvflag_M2_t, mhflag_M2_t, col_M2_t,row_M2_t=decode(TypeOfData,data_temp,frameIndex)     
        self.dvflag_M0.append(dvflag_M0_t)
        self.mhflag_M0.append(mhflag_M0_t)
        self.col_M0.append(col_M0_t)
        self.row_M0.append(row_M0_t)
        
        self.dvflag_M1.append(dvflag_M1_t)
        self.mhflag_M1.append(mhflag_M1_t)
        self.col_M1.append(col_M1_t)
        self.row_M1.append(row_M1_t)

        self.dvflag_M2.append(dvflag_M2_t)
        self.mhflag_M2.append(mhflag_M2_t)
        self.col_M2.append(col_M2_t)
        self.row_M2.append(row_M2_t)
        if dvflag_M0_t:
            self.hitmap_t0[row_M0_t][col_M0_t]+=1
        if dvflag_M1_t:
            self.hitmap_t1[row_M1_t][col_M1_t]+=1
        if dvflag_M2_t:
            self.hitmap_t2[row_M2_t][col_M2_t]+=1

def get_frame_header(file_o):
    file_header=np.fromfile(file_o,dtype='uint32',count=2)
    return file_header

# help to check the stream readout speed
def check_SR_file(file_o):
    frame_num=-1
    file_finished=1
    time_stamp_all=[]
    while(file_finished):
        file_header=get_frame_header(file_o)
        frame_num+=1
        if len(file_header)==0:
            file_finished=0
            break
        frame_Size = int(file_header[0]/2)-2
        frame_rawData,frame_rawHeader,frame_all,time_stamp=get_frame(file_o,frame_Size)
        time_stamp_all.append(time_stamp)

    #for i in range(len(time_stamp_all)-1):
    #    print("time diff: ",time_stamp_all[i+1]-time_stamp_all[i])
    return frame_num,time_stamp_all

def get_frame(file_o,frame_size,debug=0):
    
    PayLoad=np.fromfile(file_o,dtype='uint16',count=frame_size)
    frame_rawHeader=PayLoad[0:16].copy()
    frame_rawData=PayLoad[16:].copy()
    frame_all=PayLoad.copy()
  #  print("len(header):", len(frame_rawHeader))
    timestamp=np.uint64()
    for i in range(len(frame_rawHeader)):
        #print ("frame header: ",bin(i)[2:].rjust(16,"0"))
        if debug:
            print ("frame header----: ",bin(frame_rawHeader[i])[2:].rjust(16,"0"))
        if i==0: 
            if debug:
                print("Virtual Channel: ",(frame_rawHeader[i]& 0x1))
                print("Destination ID (Lane +Z): ",(frame_rawHeader[i]& 0x7e)>>1)
                print("Transaction ID 1part: ",(frame_rawHeader[i]&0xff80)>>7)
        if i==1:
            if debug:
                print("Transaction ID 2part: ",frame_rawHeader[i] &0xffff)
        if i==2:
            if debug:
                print("Acquire Counter: ",frame_rawHeader[i]&0xffff)
        if i==3:
            if debug:
                print("OP Code: ",frame_rawHeader[i] & 0xff)
                print("Element ID: ",frame_rawHeader[i] & 0xf00)
                print("Destination ID (Z only): ",frame_rawHeader[i] & 0xf000)     
        if i==4:
            if debug:
                print("Frame Number 1part: ",frame_rawHeader[i] & 0xffff)
        if i==5:
            if debug:
                print("Frame Number 2part: ",frame_rawHeader[i] & 0xffff)
        if i==6:
            if debug:
                print("Ticks 1part: ",frame_rawHeader[i] & 0xffff)
            timing_1=frame_rawHeader[i] & 0xffff
            timestamp+=timing_1
        if i==7:
            if debug:
                print("Ticks 2part: ",frame_rawHeader[i]&0xffff)
            timing_2=frame_rawHeader[i] & 0xffff
            timestamp+=timing_2<<16
        if i==8:
            if debug:
                print("Fiducials 1part: ",frame_rawHeader[i]&0xffff)
            timing_3=frame_rawHeader[i] & 0xffff
            timestamp+=timing_3<<32
        if i==9:
            if debug:
                print("Fiducials 2part: ",frame_rawHeader[i]&0xffff)
            timing_4=frame_rawHeader[i] & 0xffff
            timestamp+=timing_4<<48
        if i==10:
            if debug:
                print("sbtemp[0]: ",frame_rawHeader[i]&0xffff)
        if i==11:
            if debug:
                print("sbtemp[1]: ",frame_rawHeader[i]&0xffff)
        if i==12:
            if debug:
                print("sbtemp[2]: ",frame_rawHeader[i]&0xffff)
        if i==13:
            if debug:
                print("sbtemp[3]: ",frame_rawHeader[i]&0xffff)
        if i==14:
            if debug:
                print("Frame Type 1part: ",frame_rawHeader[i]&0xffff)
        if i==15:
            if debug:
                print("Frame Type 2part: ",frame_rawHeader[i]&0xffff)
    if debug:
        print("timestamp: ",timestamp)
    return frame_rawData,frame_rawHeader,frame_all,timestamp


class timep:
    def __init__(self,pixel1,matrix1,index1,threshold1,time1):
        self.pixel=pixel1
        self.matrix=matrix1
        self.index=index1
        self.threshold=threshold1
        self.time=time1

def logfile(logfilename):
    logger=logging.getLogger()
    LOG_FILE=logfilename
    LOG_FORMAT="%(asctime)s : %(funcName)s: %(message)s"
    logging.basicConfig(filename=LOG_FILE,level=logging.DEBUG, format=LOG_FORMAT)
    return logger

class Hist1d(object):
    
    def __init__(self,bins_i,x_l,x_h):
        self.bins_i=bins_i
        self.x_l=x_l
        self.x_h=x_h
        self.data=[]
        print(type(self.data),type(self.bins_i))
        self.n,self.bins_i,self.patches=plt.hist(self.data,bins=int(len(self.bins_i)),normed=0)
        #self.hist,self_edges=plt.hist(self.data,bins=int(nbins), range=(x_l,x_h))
        print(self.bins_i,self.patches)
        #return self.hist,self.edges
    def fill(self,arr):
        self.data.append(arr)
       # self.n, _ =np.histogram(self.data,bins=int(len(self.bins_i)),normed=False)
       # for rect,h in zip(self.patches,self.n):
       #      rect.set_height(h)
       # print("********************************",type(self.patches))
        return self.data
        #hist, edges=np.histogram(self.data,bins=int(self.bins_i),range=self.ranges)
        #self.hist += hist
         
class Hist2d(object):
    def __init__(self,nxbins,x_l,x_h,nybins,y_l,y_h):
        self.nxbins = nxbins
        self.x_h = x_h
        self.x_l = x_l

        self.nybins = nybins
        self.y_h = y_h
        self.y_l = y_l
        self.nbins  = (nxbins, nybins)
        self.ranges = ((x_l, x_h), (y_l, y_h))

        self.hist= np.histogram2d([],[], bins=self.nbins, range=self.ranges)

    def fill(self, xarr, yarr):
        hist,_,_= np.histogram2d(xarr, yarr, bins=self.nbins, range=self.ranges)
        self.hist += hist
        
    def data(self):
        return self.nxbins,self.nybins,self.hist 

def binRep(num):
    #binNum = bin(ctypes.c_uint.from_buffer(ctypes.c_float(num)).value)
    binNum = bin(ctypes.c_uint.from_buffer(ctypes.c_float(num)).value)[2:]
    print("bits: " + binNum.rjust(32,"0"))
    return binNum.rjust(32,"0")
   # mantissa = "1" + binNum[-23:]
   # print("sig (bin): " + mantissa.rjust(24))
   # mantInt = int(mantissa,2)/2**23
   # print("sig (float): " + str(mantInt))
   # base = int(binNum[-31:-23],2)-127
   # print("base:" + str(base))
   # sign = 1-2*("1"==binNum[-32:-31].rjust(1,"0"))
   # print("sign:" + str(sign))
   # print("recreate:" + str(sign*mantInt*(2**base)))

def load_chess2_data(filename):
    for i in [2]:
        file_data=open(filename,'r')
        for line in file_data.readlines():
            if ('Shape' in line):
                shape_hist=re.findall('\d+',line)
               # print(len(shape_hist))
                break
        data_1d=np.loadtxt(sys.argv[1])
        hists=data_1d.reshape(int(shape_hist[0]),int(shape_hist[1]),int(shape_hist[2]),int(shape_hist[3]))	
    return hists
def get_pixelsandthresholds(filename):
    file_data=open(filename,'r')
    pixels=[]
    for line in file_data.readlines():
        a=re.findall('"pixel":..........',line)
        threshold=re.findall('"threshold":.........',line)
        #a=re.findall('"pixel"',line)
        thresholds=[]
        for j in range(len(threshold)):
            threshold_i=re.findall(r"\d+\:?\d*",threshold[j])
            threshold_t=int(threshold_i[0])
            if (threshold_t in thresholds):
                continue
            thresholds.append(threshold_t)
        thresholds.sort()
        b=len(a)
        a1_i=0
        a1=[]
        for b_i in range(b):
            if b_i==0:
                a1.append(a[b_i])
            else:
                if a[b_i]!=a1[-1]:
                    a1.append(a[b_i])
        for i in range(len(a1)):
            pixel_i=re.findall(r"\d+\:?\d*",a1[i])
            p_2=(int(pixel_i[0]),int(pixel_i[1]))
            pixels.append(p_2)
    return pixels,thresholds
def get_values(filename):
    file_data=open(sys.argv[1],'r')
    line_count=0
    start=False
    for line in file_data.readlines():
        line_count+=1
        if ('thresholds (raw)' in line):
            thresholds=re.findall('\d+',line)
            start_line=line_count
            start=True
        if (start):
            if (line_count>start_line):
                if (not (']' in line)):
                    thresholds1=re.findall('\d+',line)
                    thresholds.extend(thresholds1)
                else: 
                    thresholds1=re.findall('\d+',line)
                    thresholds.extend(thresholds1)
                    break
    file_data=open(sys.argv[1],'r')
    for line in file_data.readlines():
        if ('PulseDelay:' in line):
            PulseDelay=re.findall('\d+',line)
            break
    file_data=open(sys.argv[1],'r')
    for line in file_data.readlines():
        if ('PulseWidth:' in line):
            PulseWidth=re.findall('\d+',line)
            break
    return thresholds,PulseDelay[0],PulseWidth[0]
       
def makeSCurve(system,nCounts,thresholdCuts,pixels=None,histFileName="scurve.root"):
    nColumns      = 32
    nRows         = 128
    allHists = []
    logging.info("Using makeCurve......")
    ####R.TH1.AddDirectory(R.kFALSE)
#    thresholdCuts = [0x7ce]
    # system.root.readConfig("chess2_config.yml") --- should be in the driver script
    #####tf = R.TFile(histFileName, "recreate")
    # Turn on one pixel at a time
    print("Disable all pixels")
    system.feb.Chess2Ctrl0.writeAllPixels(enable=0,chargeInj=0) #chargeInj should be 1 in this line and following 2 lines
    system.feb.Chess2Ctrl1.writeAllPixels(enable=0,chargeInj=0)
    system.feb.Chess2Ctrl2.writeAllPixels(enable=0,chargeInj=0)
    pixels = pixels if (pixels!=None) else [ (row,col) for row in range(nRows) for col in range(nColumns) ]
    for (row,col) in pixels:
      print("Pixel: (%i,%i)"%(row,col))
      system.feb.Chess2Ctrl0.writePixel(enable=1, chargeInj=1, col=col, row=row, trimI= 15) #chargeInj should be 0 in these 3 lines
      system.feb.Chess2Ctrl1.writePixel(enable=1, chargeInj=1, col=col, row=row, trimI= 15)
      system.feb.Chess2Ctrl2.writePixel(enable=1, chargeInj=1, col=col, row=row, trimI= 15)
      ####hists_row = [ R.TH1F("row_%i_%i_%i"%(i_asic,row,col),"",128,0,128) for i_asic in range(3) ]
      ####hists_col = [ R.TH1F("col_%i_%i_%i"%(i_asic,row,col),"",32,0,32) for i_asic in range(3) ]
      hists_row = [[], [], []]
      hists_col = [[], [], []]
      for threshold in thresholdCuts:
        ####hists = [ R.TH1F("deltaT_%i_%i_%i_%s"%(i_asic,row,col,hex(threshold)),"",100,0,1000) for i_asic in range(3) ] # deltaT in ns
        print("Thresholds (system.feb.dac.dacBLRRaw): ",  hex(threshold))
        hists = [[], [], []]
#        system.feb.dac.dacPIXTHRaw.set(threshold)
        #system.feb.dac.dacBLRaw.set(threshold+608)
        system.feb.dac.dacBLRRaw.set(threshold)
        #system.feb.dac.dacBLRaw.set(threshold)
        # this delay seems to be very important to enable the comparitor inside the asic to settle. (smaller values tend to make this 
        # tests to report wrong times
        time.sleep(2.0)
        system.ReadAll()
        for cnt in range(nCounts):
          #time.sleep(0.1)
          # start charge injection
          system.feb.memReg.chargInjStartEventReg.set(0)
          time.sleep(0.1)
          #system.feb.chargeInj.calPulseVar.set(1)
          system.ReadAll()
          if system.feb.chargeInj.hitDetValid0._rawGet():
            row_det = int(system.feb.chargeInj.hitDetRow0._rawGet())
            col_det = int(system.feb.chargeInj.hitDetCol0._rawGet())
            ####hists_row[0].Fill(row_det)
            ####hists_col[0].Fill(col_det)
            hists_row[0].append(row_det)
            hists_col[0].append(col_det)
            #if (row == row_det) and (col == col_det):
              ####hists[0].Fill(float(system.feb.chargeInj.hitDetTime0._rawGet()))
            hists[0].append(float(system.feb.chargeInj.hitDetTime0._rawGet()))
            print("row_det: ",row_det, "col_det", col_det, "system.feb.chargeInj.hitDetTime0: ", float(system.feb.chargeInj.hitDetTime0._rawGet()))
          else:
            hists[0].append(-1.0)
          if system.feb.chargeInj.hitDetValid1._rawGet():
            row_det = int(system.feb.chargeInj.hitDetRow1._rawGet())
            col_det = int(system.feb.chargeInj.hitDetCol1._rawGet())
            ####hists_row[1].Fill(row_det)
            ####hists_col[1].Fill(col_det)
            hists_row[1].append(row_det)
            hists_col[1].append(col_det)
            #if (row == row_det) and (col == col_det):
              ####hists[1].Fill(float(system.feb.chargeInj.hitDetTime1._rawGet()))
            hists[1].append(float(system.feb.chargeInj.hitDetTime1._rawGet()))
            print("row_det: ",row_det, "col_det", col_det, "system.feb.chargeInj.hitDetTime1: ", float(system.feb.chargeInj.hitDetTime1._rawGet()))
          else:
            hists[1].append(-1.0)
          if system.feb.chargeInj.hitDetValid2._rawGet():
            row_det = int(system.feb.chargeInj.hitDetRow2._rawGet())
            col_det = int(system.feb.chargeInj.hitDetCol2._rawGet())
            ####hists_row[2].Fill(row_det)
            ####hists_col[2].Fill(col_det)
            hists_row[2].append(row_det)
            hists_col[2].append(col_det)
            #if (row == row_det) and (col == col_det):
              ####hists[2].Fill(float(system.feb.chargeInj.hitDetTime2._rawGet()))
            hists[2].append(float(system.feb.chargeInj.hitDetTime2._rawGet()))
            print("row_det: ",row_det, "col_det", col_det, "system.feb.chargeInj.hitDetTime2: ", float(system.feb.chargeInj.hitDetTime2._rawGet()))
          else:
            hists[2].append(-1.0)
        allHists.append(hists)
        ####[ hist.Write() for hist in hists ]
#        for i in range(3):
#            fig = matplotlib.figure()
#            ax = fig.add_subplot(1, 1, 1)
#            n, bins, patches = ax.hist(hists[i], bins=100, range=(0, 1000))
#            ax.set_xlabel('Delta T in ns')
#            ax.set_ylabel('Frequency')
#            fig.savefig("plotDir/deltaT_%i_%i_%i_%s"%(i,row,col,hex(threshold)))
#            fig.clf()
        ####[ print("... ASIC%i %f"%(i_h,hist.GetEntries())) for (i_h,hist) in enumerate(hists) ]
#        [ print("... ASIC%i %f"%(i_h,len(hist))) for (i_h,hist) in enumerate(hists) ]


      ####[ hist.Write() for hist in hists_row ]
      ####[ hist.Write() for hist in hists_col ]
#      for i in range(3):
#          fig = matplotlib.figure()
#          ax1 = fig.add_subplot(2, 1, 1)
#          ax2 = fig.add_subplot(2, 1, 2)
#          n, bins, patches = ax1.hist(hists_row[i], bins=128, range=(0, 128))
#          ax1.set_xlabel('Row')
#          ax1.set_ylabel('Frequency')
#          n, bins, patches = ax2.hist(hists_col[i], bins=32, range=(0,32))
#          ax2.set_xlabel('Column')
#          ax2.set_ylabel('Frequency')
#          fig.savefig("plotDir/asic_row_col_%i_%i_%i.png"%(i,row,col))
#          fig.clf()

#      system.feb.Chess2Ctrl0.writePixel(enable=0, chargeInj=0, col=col, row=row)  
#      system.feb.Chess2Ctrl1.writePixel(enable=0, chargeInj=0, col=col, row=row)  
#      system.feb.Chess2Ctrl2.writePixel(enable=0, chargeInj=0, col=col, row=row)

      return allHists

#    tf.Close()
""" The following test enables to test a set of pixels for all trim values. 
    The  makeCalibCurveLoop function is called to implement the inner loops
    for the set of pixels and for the thresholdCuts"""
def makeCalibCurve(system,nCounts,thresholdCuts,pixels=None,histFileName="scurve.root"):
    allHists = []

    pixEnableLogic = 1
    chargeInjLogic = 0
    logging.info("Using makeCalibCurve......")
    print("Disable all pixels")
    system.feb.Chess2Ctrl0.writeAllPixels(enable= not pixEnableLogic,chargeInj= not chargeInjLogic)
    system.feb.Chess2Ctrl1.writeAllPixels(enable= not pixEnableLogic,chargeInj= not chargeInjLogic)
    system.feb.Chess2Ctrl2.writeAllPixels(enable= not pixEnableLogic,chargeInj= not chargeInjLogic)

    #for trim in range(0,16,2):
    for trim in range(7,8):
#        pixEnableLogic = 1
#        chargeInjLogic = 1
#        print("Trim, pixEnableLogic, chargeInjLogic: (%i,%i, %i)"%(trim, pixEnableLogic, chargeInjLogic))
#        hists = makeCalibCurveLoop(system,nCounts,thresholdCuts,pixels,histFileName, pixEnableLogic = pixEnableLogic, chargeInjLogic = chargeInjLogic, pixTrimI = trim)
#        allHists.append(hists)

        pixEnableLogic = 1
        chargeInjLogic = 0
        print("Trim, pixEnableLogic, chargeInjLogic: (%i,%i,%i)"%(trim, pixEnableLogic, chargeInjLogic))
        hists = makeCalibCurveLoop(system,nCounts,thresholdCuts,pixels,histFileName, pixEnableLogic = pixEnableLogic, chargeInjLogic = chargeInjLogic, pixTrimI = trim)
        allHists.append(hists)

#        pixEnableLogic = 0
#        chargeInjLogic = 1
#        print("Trim, pixEnableLogic, chargeInjLogic: (%i,%i, %i)"%(trim, pixEnableLogic, chargeInjLogic))
#        hists = makeCalibCurveLoop(system,nCounts,thresholdCuts,pixels,histFileName, pixEnableLogic = pixEnableLogic, chargeInjLogic = chargeInjLogic, pixTrimI = trim)
#        allHists.append(hists)

#        pixEnableLogic = 0
#        chargeInjLogic = 0
#        print("Trim, pixEnableLogic, chargeInjLogic: (%i,%i, %i)"%(trim, pixEnableLogic, chargeInjLogic))
#        hists = makeCalibCurveLoop(system,nCounts,thresholdCuts,pixels,histFileName, pixEnableLogic = pixEnableLogic, chargeInjLogic = chargeInjLogic, pixTrimI = trim)
#        allHists.append(hists)
    return allHists

""" The following test specifies a single pixel memory configuration (pixEnableLogic,
    chargeInjLogic and trim). The  makeCalibCurveLoop function is called to implement 
    the inner loops for the set of pixels and for the thresholdCuts"""

def makeCalibCurve2(system,nCounts,thresholdCuts,pixels=None,histFileName="scurve.root"):
    allHists = []
    logging.info("Using makeCalibCurve2......")

    pixEnableLogic = 1
    chargeInjLogic = 0
    trim = 15

    print("Disable all pixels")
    system.feb.Chess2Ctrl0.writeAllPixels(enable= not pixEnableLogic,chargeInj= not chargeInjLogic)
    system.feb.Chess2Ctrl1.writeAllPixels(enable= not pixEnableLogic,chargeInj= not chargeInjLogic)
    system.feb.Chess2Ctrl2.writeAllPixels(enable= not pixEnableLogic,chargeInj= not chargeInjLogic)


    print("Trim, pixEnableLogic, chargeInjLogic: (%i,%i,%i)"%(trim, pixEnableLogic, chargeInjLogic))
    hists = makeCalibCurveLoop(system,nCounts,thresholdCuts,pixels,histFileName, pixEnableLogic = pixEnableLogic, chargeInjLogic = chargeInjLogic, pixTrimI = trim)
    allHists.append(hists)


def makeCalibCurve3(system,nCounts,thresholdCuts,pixels=None,histFileName="scurve.root"):
    allHists = []

    pixEnable = 1
    chargeInj = 0 # 0 - enable / 1 - disabled
    trim = 7

    #system.feb.chargeInj.pulseWidthRaw.set(0x7fff)

    print("Disable all pixels")
    system.feb.Chess2Ctrl0.writeAllPixels(enable= 0,chargeInj= 1)
    system.feb.Chess2Ctrl1.writeAllPixels(enable= 0,chargeInj= 1)
    system.feb.Chess2Ctrl2.writeAllPixels(enable= 0,chargeInj= 1)


    print("Trim, pixEnable, chargeInj: (%i,%i,%i)"%(trim, pixEnable, chargeInj))
    hists = makeCalibCurveLoopTH(system,nCounts,thresholdCuts,pixels,histFileName, pixEnableLogic = pixEnable, chargeInjLogic = chargeInj, pixTrimI = trim)
    allHists.append(hists)

    return allHists


def configAsicsPreampTest(system = []):
    system.feb.Chess2Ctrl0.VNatt.set(0x1e)                                            
    system.feb.Chess2Ctrl0.VNres.set(0x1)
    system.feb.Chess2Ctrl0.VPLoadatt.set(0x1c)                                        
    system.feb.Chess2Ctrl0.VPLoadres.set(0x2)                                         
    system.feb.Chess2Ctrl0.VNSFatt.set(0x1f)                                          
    system.feb.Chess2Ctrl0.VNSFres.set(0x3)
    
    system.feb.Chess2Ctrl1.VNatt.set(0x1e)
    system.feb.Chess2Ctrl1.VNres.set(0x1)
    system.feb.Chess2Ctrl1.VPLoadatt.set(0x1c)                                        
    system.feb.Chess2Ctrl1.VPLoadres.set(0x2)                                         
    system.feb.Chess2Ctrl1.VNSFatt.set(0x1f)                                          
    system.feb.Chess2Ctrl1.VNSFres.set(0x3)
    
    system.feb.Chess2Ctrl2.VNatt.set(0x1e)
    system.feb.Chess2Ctrl2.VNres.set(0x1)
    system.feb.Chess2Ctrl2.VPLoadatt.set(0x1c)                                        
    system.feb.Chess2Ctrl2.VPLoadres.set(0x2)                                         
    system.feb.Chess2Ctrl2.VNSFatt.set(0x1f)                                          
    system.feb.Chess2Ctrl2.VNSFres.set(0x3)

def configAsicsPreampTestRestoreDefaultValues(system = []):
    system.feb.Chess2Ctrl0.VNatt.set(0x1F)                                            
    system.feb.Chess2Ctrl0.VNres.set(0x0)
    system.feb.Chess2Ctrl0.VPLoadatt.set(0x1e)                                        
    system.feb.Chess2Ctrl0.VPLoadres.set(0x1)                                         
    system.feb.Chess2Ctrl0.VNSFatt.set(0x1b)                                          
    system.feb.Chess2Ctrl0.VNSFres.set(0x0)
    
    system.feb.Chess2Ctrl1.VNatt.set(0x1F)
    system.feb.Chess2Ctrl1.VNres.set(0x0)
    system.feb.Chess2Ctrl1.VPLoadatt.set(0x1e) 
    system.feb.Chess2Ctrl1.VPLoadres.set(0x1)                                         
    system.feb.Chess2Ctrl1.VNSFatt.set(0x1b)                                          
    system.feb.Chess2Ctrl1.VNSFres.set(0x0)
    
    system.feb.Chess2Ctrl2.VNatt.set(0x1F)
    system.feb.Chess2Ctrl2.VNres.set(0x0)
    system.feb.Chess2Ctrl2.VPLoadatt.set(0x1e) 
    system.feb.Chess2Ctrl2.VPLoadres.set(0x1)                                         
    system.feb.Chess2Ctrl2.VNSFatt.set(0x1b)                                          
    system.feb.Chess2Ctrl2.VNSFres.set(0x0)




def makeCalibCurve4(system,nCounts,thresholdCuts,pixels=None,histFileName="scurve.root", deltaBLToBLR = 608, chargeInjectionEnbled = 0, BL=0x26c,Reading_all_pixel_together= False,mode=0):
    logging.info("Using makeCalibCurve4......")
    #ASIC specific configuration selected depending on the test being run
    pixEnable = 1
    chargeInj1 = not chargeInjectionEnbled  # 0 - enable / 1 - disabled
    trim = 7
    #system.feb.chargeInj.pulseWidthRaw.set(0x7fff)
    system.feb.chargeInj.calPulseInh.set(chargeInj1)
    print("Disable all pixels")
    logging.info("Disable all pixels, eg:system.feb.Chess2Ctrl0.writeAllPixels(enable= 0,chargeInj= 1,trimI= trim)")
    system.feb.Chess2Ctrl0.writeAllPixels(enable= 0,chargeInj= 1,trimI= trim)
    system.feb.Chess2Ctrl1.writeAllPixels(enable= 0,chargeInj= 1,trimI= trim)
    system.feb.Chess2Ctrl2.writeAllPixels(enable= 0,chargeInj= 1,trimI= trim)
    print("Trim, pixEnable, chargeInj: (%i,%i,%i)"%(trim, pixEnable, chargeInj1))
    if Reading_all_pixel_together:
        print("reading all together")
        hists = makeCalibCurveLoopBLx_8hits(system,nCounts,thresholdCuts,pixels,histFileName, pixEnableLogic = pixEnable, chargeInjLogic = chargeInj1, pixTrimI = trim, deltaBLToBLR = deltaBLToBLR,BL_v=BL,mode=mode)
    else:
        print("generating hitmap")
        hists = makeCalibCurveLoopBLx_8hits_hitmap(system,nCounts,thresholdCuts,pixels,histFileName, pixEnableLogic = pixEnable, chargeInjLogic = chargeInj1, pixTrimI = trim, deltaBLToBLR = deltaBLToBLR,BL_v=BL)
        
    return hists

def makeCalibCurve4_simu(R,nCounts,thresholdCuts,pixels=None,histFileName="scurve.root", deltaBLToBLR = 608, chargeInjectionEnbled = 0, BL=0x26c):
    #ASIC specific configuration selected depending on the test being run
    pixEnable = 1
    chargeInj1 = not chargeInjectionEnbled  # 0 - enable / 1 - disabled
    trim = 7
    print(thresholdCuts)
    #system.feb.chargeInj.pulseWidthRaw.set(0x7fff)
    hists = makeCalibCurveLoopBLx_simu(R,nCounts,thresholdCuts,pixels,histFileName, pixEnableLogic = pixEnable, chargeInjLogic = chargeInj1, pixTrimI = trim, deltaBLToBLR = deltaBLToBLR,BL_v=BL)
    return hists
def makeCalibCurveLoop(system,nCounts,thresholdCuts,pixels=None,histFileName="scurve.root", pixEnableLogic = 1, chargeInjLogic = 0, pixTrimI = 0):
    nColumns      = 32
    nRows         = 128
    allHists = []
    logging.info("Using makeCalibCurveLoop......")
    pixels = pixels if (pixels!=None) else [ (row,col) for row in range(nRows) for col in range(nColumns) ]
    for (row,col) in pixels:
      print("Pixel: (%i,%i)"%(row,col))
      system.feb.Chess2Ctrl0.writePixel(enable=pixEnableLogic, chargeInj=chargeInjLogic, col=col, row=row, trimI= pixTrimI)
      system.feb.Chess2Ctrl1.writePixel(enable=pixEnableLogic, chargeInj=chargeInjLogic, col=col, row=row, trimI= pixTrimI)
      system.feb.Chess2Ctrl2.writePixel(enable=pixEnableLogic, chargeInj=chargeInjLogic, col=col, row=row, trimI= pixTrimI)
      hists_row = [[], [], []]
      hists_col = [[], [], []]
      for threshold in thresholdCuts:
        hists = [[], [], []]
        print("Thresholds (system.feb.dac.dacBLRaw): ",  hex(threshold))
        system.feb.dac.dacBLRaw.set(threshold)
        # this delay seems to be very important to enable the comparitor inside the asic to settle. (smaller values tend to make this 
        # tests to report wrong times
        time.sleep(2.0)
        system.ReadAll()
        for cnt in range(nCounts):
          #time.sleep(0.1)
          # start charge injection
          #system.feb.memReg.chargInjStartEventReg.set(0)
          system.feb.chargeInj.calPulseVar.set(1)
          time.sleep(0.1)          
          system.ReadAll()
          if system.feb.chargeInj.hitDetValid0._rawGet():
            row_det = int(system.feb.chargeInj.hitDetRow0._rawGet())
            col_det = int(system.feb.chargeInj.hitDetCol0._rawGet())
            ####hists_row[0].Fill(row_det)
            ####hists_col[0].Fill(col_det)
            hists_row[0].append(row_det)
            hists_col[0].append(col_det)
            #if (row == row_det) and (col == col_det):
              ####hists[0].Fill(float(system.feb.chargeInj.hitDetTime0._rawGet()))
            hists[0].append(float(system.feb.chargeInj.hitDetTime0._rawGet()))
            print("row_det: ",row_det, "col_det", col_det, "system.feb.chargeInj.hitDetTime0: ", float(system.feb.chargeInj.hitDetTime0._rawGet()))
          else:
            hists[0].append(-1.0)
          if system.feb.chargeInj.hitDetValid1._rawGet():
            row_det = int(system.feb.chargeInj.hitDetRow1._rawGet())
            col_det = int(system.feb.chargeInj.hitDetCol1._rawGet())
            ####hists_row[1].Fill(row_det)
            ####hists_col[1].Fill(col_det)
            hists_row[1].append(row_det)
            hists_col[1].append(col_det)
            #if (row == row_det) and (col == col_det):
              ####hists[1].Fill(float(system.feb.chargeInj.hitDetTime1._rawGet()))
            hists[1].append(float(system.feb.chargeInj.hitDetTime1._rawGet()))
            print("row_det: ",row_det, "col_det", col_det, "system.feb.chargeInj.hitDetTime1: ", float(system.feb.chargeInj.hitDetTime1._rawGet()))
          else:
            hists[1].append(-1.0)
          if system.feb.chargeInj.hitDetValid2._rawGet():
            row_det = int(system.feb.chargeInj.hitDetRow2._rawGet())
            col_det = int(system.feb.chargeInj.hitDetCol2._rawGet())
            ####hists_row[2].Fill(row_det)
            ####hists_col[2].Fill(col_det)
            hists_row[2].append(row_det)
            hists_col[2].append(col_det)
            #if (row == row_det) and (col == col_det):
              ####hists[2].Fill(float(system.feb.chargeInj.hitDetTime2._rawGet()))
            hists[2].append(float(system.feb.chargeInj.hitDetTime2._rawGet()))
            print("row_det: ",row_det, "col_det", col_det, "system.feb.chargeInj.hitDetTime2: ", float(system.feb.chargeInj.hitDetTime2._rawGet()))
          else:
            hists[2].append(-1.0)
        allHists.append(hists)
    
    return allHists

def makeCalibCurveLoopBLx_hitmap(system,nCounts,thresholdCuts,pixels=None,histFileName="scurve.root", pixEnableLogic = 1, chargeInjLogic = 0, pixTrimI = 0, deltaBLToBLR = 608, pixth=0x800):
    nColumns      = 32
    nRows         = 128
    logging.info(" Using makeCalibCurveLoopBLx_hitmap......")
    hitmap_mat0=[[0 for i in range(nColumns)] for j in range(nRows)]
    hitmap_mat1=[[0 for i in range(nColumns)] for j in range(nRows)]
    hitmap_mat2=[[0 for i in range(nColumns)] for j in range(nRows)]
    hist=[[],[],[]] 
    pixels = pixels if (pixels!=None) else [ (row,col) for row in range(nRows) for col in range(nColumns) ]
    delt_Bl=[0x10,0x8,0x1] 
    print("Thresholds (system.feb.dac.dacPIXTHRaw): ",  hex(pixth))
    system.feb.dac.dacPIXTHRaw.set(pixth)
    for (row,col) in pixels:
        BL_up=0x800
        BL_bot=0x0
        act_pixel0=0
        act_pixel1=0
        act_pixel2=0
        print("Matrix0 -Pixel: (%i,%i)"%(row,col))
        for Delt_BL in delt_Bl:
            if act_pixel0==2:
                break
            print("delt_BL is : ",Delt_BL)
            thresholdCuts= np.arange(BL_bot,BL_up,Delt_BL)
            for threshold in thresholdCuts:
                BLRValue  = threshold + deltaBLToBLR
                system.feb.dac.dacBLRRaw.set(BLRValue)
                #print("Thresholds (system.feb.dac.dacBLRRaw): ",  hex(BLRValue))
                system.feb.dac.dacBLRaw.set(threshold)
                print("Thresholds (system.feb.dac.dacBLRaw): ",  hex(threshold))
                system.feb.Chess2Ctrl0.writePixel(enable=pixEnableLogic, chargeInj=chargeInjLogic, col=col, row=row, trimI= pixTrimI)
                hit_num=0
                for cnt in range(nCounts):
                    #time.sleep(1.0)
                    system.feb.chargeInj.calPulseVar.set(1)
                    #time.sleep(0.05)          
                    system.ReadAll()
                    if system.feb.chargeInj.hitDetValid0._rawGet():
                        row_det = int(system.feb.chargeInj.hitDetRow0._rawGet())
                        col_det = int(system.feb.chargeInj.hitDetCol0._rawGet())
                        if (row_det==row and col_det==col):
                            print("row_det: ",row_det, "col_det", col_det, "system.feb.chargeInj.hitDetTime0: ", float(system.feb.chargeInj.hitDetTime0._rawGet()))
                            hit_num+=1
                print("hit number:",hit_num)
                if (hit_num>=0.5*nCounts):
                    BL_bot=threshold-Delt_BL
                    BL_up=threshold 
                    act_pixel0=1
                    print("BL_bottom:",BL_bot,"_up:",BL_up)       
                    #break
                    break
                    #continue
                #else: 
                if (act_pixel0==0 and threshold==thresholdCuts[-1]):
                    act_pixel0=2
                    print("dead pixel")
        hitmap_mat0[row][col]=BL_up
        hist[0].append(BL_up)
        print("The thresholds of Matrix0 (",row,col,"):",BL_up)   
        system.feb.Chess2Ctrl0.writePixel(enable=not pixEnableLogic, chargeInj=1, col=col, row=row)
        BL_up=0x800
        BL_bot=0x0
        print("Matrix1 -Pixel: (%i,%i)"%(row,col))
        for Delt_BL in delt_Bl:
            if act_pixel1==2:
                break
            print("delt_BL: ",Delt_BL)
            thresholdCuts= np.arange(BL_bot,BL_up,Delt_BL)
            for threshold in thresholdCuts:
                BLRValue  = threshold + deltaBLToBLR
                system.feb.dac.dacBLRRaw.set(BLRValue)
                #print("Thresholds (system.feb.dac.dacBLRRaw): ",  hex(BLRValue))
                system.feb.dac.dacBLRaw.set(threshold)
                print("Thresholds (system.feb.dac.dacBLRaw): ",  hex(threshold))
                system.feb.Chess2Ctrl1.writePixel(enable=pixEnableLogic, chargeInj=chargeInjLogic, col=col, row=row, trimI= pixTrimI)
                hit_num=0
                for cnt in range(nCounts):
                    #time.sleep(1.0)
                    system.feb.chargeInj.calPulseVar.set(1)
                    #time.sleep(0.05)          
                    system.ReadAll()
                    if system.feb.chargeInj.hitDetValid1._rawGet():
                        row_det = int(system.feb.chargeInj.hitDetRow1._rawGet())
                        col_det = int(system.feb.chargeInj.hitDetCol1._rawGet())
                        if (row_det==row and col_det==col):
                            print("row_det: ",row_det, "col_det", col_det, "system.feb.chargeInj.hitDetTime1: ", float(system.feb.chargeInj.hitDetTime0._rawGet()))
                            hit_num+=1
                print("hit number:",hit_num)
                if (hit_num>=0.5*nCounts):
                    BL_bot=threshold-Delt_BL
                    BL_up=threshold
                    act_pixel1=1        
                    print("BL_bottom:",BL_bot,"_up:",BL_up)       
                    #break
                    break
                if (act_pixel1==0 and threshold==thresholdCuts[-1]):
                    act_pixel1=2        
                    print("dead pixel")
                    break
                    

        hitmap_mat1[row][col]=BL_up
        hist[1].append(BL_up)
        print("find the thresholds of Matrix1 (",row,col,"):",BL_up)   
        system.feb.Chess2Ctrl1.writePixel(enable=not pixEnableLogic, chargeInj=1, col=col, row=row)
        BL_up=0x800
        BL_bot=0x0
        print("Matrix2 -Pixel: (%i,%i)"%(row,col))
        for Delt_BL in delt_Bl:
            if act_pixel2==2:
                break
            print("delt_BL: ",Delt_BL)
            thresholdCuts= np.arange(BL_bot,BL_up,Delt_BL)
            for threshold in thresholdCuts:
                BLRValue  = threshold + deltaBLToBLR
                system.feb.dac.dacBLRRaw.set(BLRValue)
                #print("Thresholds (system.feb.dac.dacBLRRaw): ",  hex(BLRValue))
                system.feb.dac.dacBLRaw.set(threshold)
                print("Thresholds (system.feb.dac.dacBLRaw): ",  hex(threshold))
                system.feb.Chess2Ctrl2.writePixel(enable=pixEnableLogic, chargeInj=chargeInjLogic, col=col, row=row, trimI= pixTrimI)
                hit_num=0
                for cnt in range(nCounts):
                    #time.sleep(1.0)
                    system.feb.chargeInj.calPulseVar.set(1)
                    #time.sleep(0.05)          
                    system.ReadAll()
                    if system.feb.chargeInj.hitDetValid2._rawGet():
                        row_det = int(system.feb.chargeInj.hitDetRow2._rawGet())
                        col_det = int(system.feb.chargeInj.hitDetCol2._rawGet())
                        if (row_det==row and col_det==col):
                            print("row_det: ",row_det, "col_det", col_det, "system.feb.chargeInj.hitDetTime2: ", float(system.feb.chargeInj.hitDetTime0._rawGet()))
                            hit_num+=1
                print("hit number:",hit_num)
                if (hit_num>=0.5*nCounts):
                    BL_bot=threshold-Delt_BL
                    BL_up=threshold        
                    act_pixel2=1        
                    print("BL_bottom:",BL_bot,"_up:",BL_up)       
                    #break
                    break
                if (act_pixel2==0 and threshold==thresholdCuts[-1]):
                    print("dead pixel")
                    act_pixel2=2
                    break
                    break

        hitmap_mat2[row][col]=BL_up
        hist[2].append(BL_up)
        print("find the thresholds of Matrix2 (",row,col,"):",BL_up)   
        system.feb.Chess2Ctrl2.writePixel(enable=not pixEnableLogic, chargeInj=1, col=col, row=row)
        
    allHists.append(hists)
    return hitmap_mat0,hitmap_mat1,hitmap_mat2,allHists


def makeCalibCurveLoopBLx(system,nCounts,thresholdCuts,pixels=None,histFileName="scurve.root", pixEnableLogic = 1, chargeInjLogic = 0, pixTrimI = 0, deltaBLToBLR = 608, BL_v=0x800):
    nColumns      = 32
    nRows         = 128
    allHists = []
    logging.info(" Using makeCalibCurveLoopBLx......")
    if pixels==None:
        hitmap_get=True
        hitmap_mat0=[[0 for i in range(nColumns)] for j in range(nRows)]
        hitmap_mat1=[[0 for i in range(nColumns)] for j in range(nRows)]
        hitmap_mat2=[[0 for i in range(nColumns)] for j in range(nRows)]
        print("hitmap_get: ",hitmap_get)
    else: 
        hitmap_get=False
    pixels = pixels if (pixels!=None) else [ (row,col) for row in range(nRows) for col in range(nColumns) ]
    BLRValue  = BL_v + deltaBLToBLR
    system.feb.dac.dacBLRRaw.set(BLRValue)
    print("Thresholds (system.feb.dac.dacBLRRaw): ",  hex(BLRValue))
    system.feb.dac.dacBLRaw.set(BL_v)
    print("Thresholds (system.feb.dac.dacBLRaw): ",  hex(BL_v))
    for (row,col) in pixels:
        system.feb.Chess2Ctrl0.writePixel(enable=pixEnableLogic, chargeInj=chargeInjLogic, col=col, row=row, trimI= pixTrimI)
        system.feb.Chess2Ctrl1.writePixel(enable=pixEnableLogic, chargeInj=chargeInjLogic, col=col, row=row, trimI= pixTrimI)
        system.feb.Chess2Ctrl2.writePixel(enable=pixEnableLogic, chargeInj=chargeInjLogic, col=col, row=row, trimI= pixTrimI)
        print("enable Pixel: (%i,%i)"%(row,col))
        hists_row = [[], [], []]
        hists_col = [[], [], []]
        for threshold in thresholdCuts:
            print("Thresholds (system.feb.dac.dacPIXTHRaw): ",  hex(threshold))
            system.feb.dac.dacPIXTHRaw.set(threshold)
            hists=[[],[],[]]
            time.sleep(1.0)
            system.ReadAll()
            ####hists = [ R.TH1F("deltaT_%i_%i_%i_%s"%(i_asic,row,col,hex(threshold)),"",100,0,1000) for i_asic in range(3) ] # deltaT in ns
            for cnt in range(nCounts):
                #time.sleep(1.0)
                #system.ReadAll()
          #system.feb.memReg.chargInjStartEventReg.set(0)
                system.feb.chargeInj.calPulseVar.set(1)
                time.sleep(0.05)          
                system.ReadAll()
                if system.feb.chargeInj.hitDetValid0_0._rawGet():
                    row_det = int(system.feb.chargeInj.hitDetRow0_0._rawGet())
                    col_det = int(system.feb.chargeInj.hitDetCol0_0._rawGet())
                    if hitmap_get:
                        hitmap_mat0[row_det][col_det]+=1   
                    if (row_det==row and col_det==col):
                        hists_row[0].append(row_det)
                        hists_col[0].append(col_det)
                        hists[0].append(float(system.feb.chargeInj.hitDetTime0_0._rawGet()))
                        print("row_det: ",row_det, "col_det", col_det, "system.feb.chargeInj.hitDetTime0: ", float(system.feb.chargeInj.hitDetTime0_0._rawGet()))
                    else:
                        hists[0].append(-2.0)
                        print("row_det: ",row_det, ":col_det:", col_det, ":system.feb.chargeInj.hitDetTime0: ", float(-2)," is",float(system.feb.chargeInj.hitDetTime0_0._rawGet()))
                else:
                    hists[0].append(-1.0)
                    print("row_det: ",-1, ":col_det:", -1, ":system.feb.chargeInj.hitDetTime0: ", float(-1))
                if system.feb.chargeInj.hitDetValid1_0._rawGet():
                    row_det = int(system.feb.chargeInj.hitDetRow1_0._rawGet())
                    col_det = int(system.feb.chargeInj.hitDetCol1_0._rawGet())
                    if hitmap_get: 
                        hitmap_mat1[row_det][col_det]+=1    
                    if (row_det==row and col_det==col):
                        hists_row[1].append(row_det)
                        hists_col[1].append(col_det)
                        hists[1].append(float(system.feb.chargeInj.hitDetTime1_0._rawGet()))
                        print("row_det: ",row_det, "col_det", col_det, "system.feb.chargeInj.hitDetTime1: ", float(system.feb.chargeInj.hitDetTime1_0._rawGet()))
                    else:
                        hists[1].append(-2.0)
                        print("row_det: ",row_det, ":col_det:", col_det, ":system.feb.chargeInj.hitDetTime1: ", float(-2)," is",float(system.feb.chargeInj.hitDetTime1_0._rawGet()))
                else:
                    hists[1].append(-1.0)
                    print("row_det: ",-1, ":col_det:", -1, ":system.feb.chargeInj.hitDetTime1: ", float(-1))
                if system.feb.chargeInj.hitDetValid2_0._rawGet():
                    row_det = int(system.feb.chargeInj.hitDetRow2_0._rawGet())
                    col_det = int(system.feb.chargeInj.hitDetCol2_0._rawGet())
                    if hitmap_get:
                        hitmap_mat2[row_det][col_det]+=1     
                    if (row_det==row and col_det==col):
                        hists_row[2].append(row_det)
                        hists_col[2].append(col_det)
                        hists[2].append(float(system.feb.chargeInj.hitDetTime2_0._rawGet()))
                        print("row_det: ",row_det, "col_det", col_det, "system.feb.chargeInj.hitDetTime2: ", float(system.feb.chargeInj.hitDetTime2_0._rawGet()))
                    else:
                        hists[2].append(-2.0)
                        print("row_det: ",row_det, ":col_det:", col_det, ":system.feb.chargeInj.hitDetTime2: ", float(-2)," is",float(system.feb.chargeInj.hitDetTime2_0._rawGet()))
                else:
                    hists[2].append(-1.0)
                    print("row_det: ",-1, ":col_det:", -1, ":system.feb.chargeInj.hitDetTime2: ", float(-1))
            allHists.append(hists)
        if (hitmap_get):
            system.feb.Chess2Ctrl0.writePixel(enable=not pixEnableLogic, chargeInj=1, col=col, row=row)
            system.feb.Chess2Ctrl1.writePixel(enable=not pixEnableLogic, chargeInj=1, col=col, row=row)
            system.feb.Chess2Ctrl2.writePixel(enable=not pixEnableLogic, chargeInj=1, col=col, row=row)
            print("disabling pixel:",row,col)
    if hitmap_get:
        return hitmap_mat0,hitmap_mat1,hitmap_mat2,allHists
    else:
        return allHists

def get_allHists(pixels,matrix,indexs,thresholdCuts):
    allHist={}.fromkeys(pixels)
    for pixel in pixels:
        allHist[pixel]={}.fromkeys(matrix)
        for matri in matrix:
            allHist[pixel][matri]={}.fromkeys(indexs)
            for index in indexs:
                allHist[pixel][matri][index]={}.fromkeys(thresholdCuts)
                for threshold in thresholdCuts:
                    allHist[pixel][matri][index][threshold]=[]
    return allHist

def save_f(file_name,hists):
    with open(file_name,"w") as save_file:
        for key in hists:
            for key1 in hists[key]:
                for key2 in hists[key][key1]:
                    if hists[key][key1][key2]:
                        save_file.writelines("pixel:{0}\nmatrix:{1}\nthreshold:{2}\nhit_time:{3}\n".format(key,key1,key2,hists[key][key1][key2]))
    save_file.close()

def save_f_pickle(file_name,hists):
    file_pickle=open(file_name,'wb')
    pickle.dump(hists,file_pickle,protocol=1)
    file_pickle.close()    

def dic2timep(dic):
    return timep(dic['pixel'],dic['matrix'],dic['index'],dic['threshold'],dic['time'])

def timep2dic(timep):
    return {'pixel':timep.pixel,'matrix':timep.matrix,'index':timep.index,'threshold':timep.threshold,'time':timep.time}

def save_f_json(file_name,hists):
    with open(file_name+'.json','w',encoding='utf-8') as f:
        json.dump(hists,f,default=timep2dic)

def save_timep(hists):
    allhist=[]
    for key in hists: #pixel
        print(key)
        for key1 in hists[key]: #matrix
            for key2 in hists[key][key1]: #index
                for key3 in hists[key][key1][key2]: #threshold
                    #if hists[key][key1][key2][key3]: 
                    one=timep(key,key1,key2,key3,hists[key][key1][key2][key3])
                    allhist.append(one)
    return allhist

def print_f(file_name):
    with open(file_name,"r") as print_file:
        for line in print_file.readlines():
            print(line)
def makeCalibCurveLoopBLx_8hits(system,nCounts,thresholdCuts,pixels=None,histFileName="scurve.root",pixEnableLogic=1,chargeInjLogic=0,pixTrimI=0,deltaBLToBLR=608,BL_v=0x800,mode=0):
    nColumns      = 32
    nRows         = 128
    logging.info(" Using makeCalibCurveLoopBLx_8hits......")
    real_data=mode #1: real size display, 2 hitmap display
    matrix=[0,1,2]
    hits=[0,1,2,3,4,5,6,7]
    pixels = pixels if (pixels!=None) else [ (row,col) for row in range(1,128,1) for col in range(1,32,1) ]
    eventdump=False
    if len(thresholdCuts)==1:
        eventdump=True
    #i=21
    #pixels = pixels if (pixels!=None) else [ (row,col) for row in range(10,70,1) for col in range(i,i+1,1) ]
    #pixels = pixels if (pixels!=None) else [ (row,col) for row in range(1,128,1) for col in range(1,32,1) ]
    #pixels = pixels if (pixels!=None) else [ (row,col) for row in range(10,128,1) for col in range(15,31,1) ]
    allHists=get_allHists(pixels,matrix,hits,thresholdCuts)
    BLRValue  = BL_v + deltaBLToBLR
    #BLRValue=0x672
    system.feb.dac.dacBLRRaw.set(BLRValue)
    print("Thresholds (system.feb.dac.dacBLRRaw): ",  hex(BLRValue))
    system.feb.dac.dacBLRaw.set(BL_v)
    print("Thresholds (system.feb.dac.dacBLRaw): ",  hex(BL_v))
    time_h=200000
    time_reso=1000
    time_bin=range(0,time_h,time_reso)
    d_time=0
    d_time_2=time_h
    #a=thresholdCuts[1]
    #print("Thresholds (system.feb.dac.dacPIXTHRaw): ",  hex(a))
    #system.feb.dac.dacPIXTHRaw.set(a)
    time.sleep(2.0)
    if real_data==2:
        plt.ion()
        fig_all=plt.subplots(figsize=(11,9))
    if real_data==1:
        plt.ion()
        figure_0,ax=plt.subplots(figsize=(11,9))
        ax.set_axis_off()
        chass2_point=[(87.9,108),(20228,108),(24300,108),(24300,18517),(24300,18517),(20227,18517),(87.9,18517),(87.9,13413),(87.9,13138),(87.9,8034),(87.9,5212),(20227,5212),(20227,8034),(20227,13138),(20227,13413)]
        for i in range(9):
            ax.plot([chass2_point[i][0],chass2_point[i+1][0]],[chass2_point[i][1],chass2_point[i+1][1]],'k')
        ax.plot([chass2_point[0][0],chass2_point[9][0]],[chass2_point[0][1],chass2_point[9][1]],'k')
        ax.plot([chass2_point[1][0],chass2_point[5][0]],[chass2_point[1][1],chass2_point[5][1]],'k')
        for i in range(7,12,1):
            ax.plot([chass2_point[i][0],chass2_point[21-i][0]],[chass2_point[i][1],chass2_point[21-i][1]],'k')
        plt.show()
        plt.ion()
        figure_1,ax1=plt.subplots(figsize=(13,8))
        ax1.set_axis_off()
        #fig_all=plt.figure(figsize=(17,10))
    #fig_all=Figure(figsize=(17,10),dpi=100)
    hitmap_t0=np.zeros((nRows,nColumns))
    hitmap_t1=np.zeros((nRows,nColumns))
    hitmap_t2=np.zeros((nRows,nColumns))
    time_inde=range(0,time_h,time_reso) 
    time_t=np.zeros((4,len(time_inde)))
    time_t[0]=time_inde
 
    thre_t=np.zeros((4,len(thresholdCuts)))
    thre_t[0]=np.asarray(thresholdCuts)/1241.
    time_buffer=time_t
    thre_buffer=thre_t
    thre_index=0
    hot_pixels_m0=[(0,0),(8,15),(2,1),(1,16),(5,16),(6,1),(2,21),(3,30),(6,30),(2,31),(10,30)]
    hot_pixels_m1=[(0,0),(1,1),(3,1),(6,1),(8,24),(7,27)]
    hot_pixels_m2=[(0,0),(12,31),(1,1),(3,1),(4,1),(7,1),(1,2),(4,29),(5,30),(15,31),(127,31)]
#    hot_pixels=[(27,16),(50,15),(45,15)]
    
   # #FileNameIn_txt='dumpingData_Th_0.66V_Laser_hex.txt'
   # FileNameIn_txt='dumpingData_Th_0.66V_noLaser_hex.txt'
   # OutputFile=open(FileNameIn_txt,'w')
   # OutputFile.write("# # tests on pixel:"+str(pixels)+"\n")
   # OutputFile.write("# # threshold:"+str(thre_t[0])+"\n")
  
    for (row,col) in pixels:
        if (row,col) in hot_pixels_m0:
            print("hot pixel on Matrix 0: (%i,%i)"%(row,col))
        else:
            #print("enable Pixel: (%i,%i)"%(row,col))
            system.feb.Chess2Ctrl0.writePixel(enable=pixEnableLogic, chargeInj=chargeInjLogic, col=col, row=row, trimI= pixTrimI)
        if (row,col) in hot_pixels_m1:
            print("hot pixel on Matrix 1: (%i,%i)"%(row,col))
        else:
            system.feb.Chess2Ctrl1.writePixel(enable=pixEnableLogic, chargeInj=chargeInjLogic, col=col, row=row, trimI= pixTrimI)
        if (row,col) in hot_pixels_m2:
            print("hot pixel on Matrix 2: (%i,%i)"%(row,col))
        else:
            system.feb.Chess2Ctrl2.writePixel(enable=pixEnableLogic, chargeInj=chargeInjLogic, col=col, row=row, trimI= pixTrimI)
    for threshold in thresholdCuts:
       # time_buffer[1:4]=0             
       # thre_buffer[1:4]=0   
        print("Thresholds (system.feb.dac.dacPIXTHRaw): ",  hex(threshold))
        system.feb.dac.dacPIXTHRaw.set(threshold)
        time.sleep(2.0)
        #system.ReadAll()
        print("start taking ",nCounts," counts :", time.clock())
       # OutputFile.write("#                        Matrix 0       Matrix 1        Matrix2\n")
       # OutputFile.write("threshold at :"+str(threshold)+"\n")
        for cnt in range(nCounts):
        #    OutputFile.write("event :"+str(cnt)+"\n")
            system.feb.chargeInj.calPulse.set(1)
            #time.sleep(0.05)
            system.ReadAll()
            for n in [1]:
                for hit in hits:
         #           OutputFile.write("\tHit index :"+str(hit)+"\t")
                    matrix_i=0
                    if eval(get_funct('Valid',matrix_i,hit)):
                       # row_det_raw = eval(get_funct('row_det',matrix_i,hit))
                       # col_det_raw = eval(get_funct('col_det',matrix_i,hit))
                       # time_m0_raw=  hex(eval(get_funct('time_det_raw',matrix_i,hit)))
                        row_det = int(eval(get_funct('row_det',matrix_i,hit)))
                        col_det = int(eval(get_funct('col_det',matrix_i,hit)))
                        time_m0=  float(eval(get_funct('time_det',matrix_i,hit)))
          #              OutputFile.write("("+str(row_det_raw)+","+str(col_det_raw)+"):  ")
          #              OutputFile.write(str(time_m0_raw)+"\t")
                        #print("row_det: ",row_det, "col_det:", col_det, "system.feb.chargeInj.hitDetTime"+str(matrix_i)+"_"+str(hit)+":", time_m0)
                        if (time_m0<time_h):
                            #print("row_det: ",row_det, "col_det:", col_det, "system.feb.chargeInj.hitDetTime"+str(matrix_i)+"_"+str(hit)+":", time_m0)
                            if (row_det,col_det) in pixels:
                                print("row_det: ",row_det, "col_det:", col_det, "system.feb.chargeInj.hitDetTime"+str(matrix_i)+"_"+str(hit)+":", time_m0)
                                allHists[(row_det,col_det)][matrix_i][hit][threshold].append(float(eval(get_funct('time_det',matrix_i,hit))))
                            #else:
                               # allHists[(row_det,col_det)][matrix_i][hit][threshold].append(float(-2.0))
                                if (d_time<time_m0<d_time_2):                       
                                    time_buffer[matrix_i+1][int(time_m0/time_reso)]+=1
                                    thre_buffer[matrix_i+1][thre_index]+=1
                                    hitmap_t0[row_det][col_det]+=1
                    matrix_i=1
                    if eval(get_funct('Valid',matrix_i,hit)):
                       # row_det_raw = eval(get_funct('row_det',matrix_i,hit))
                       # col_det_raw = eval(get_funct('col_det',matrix_i,hit))
                       # time_m1_raw = hex(eval(get_funct('time_det_raw',matrix_i,hit)))
                        row_det = int(eval(get_funct('row_det',matrix_i,hit)))
                        col_det = int(eval(get_funct('col_det',matrix_i,hit)))
                        time_m1=float(eval(get_funct('time_det',matrix_i,hit)))
           #             OutputFile.write("("+str(row_det_raw)+","+str(col_det_raw)+"):  ")
           #             OutputFile.write(str(time_m1_raw)+"\t")
                        if (time_m1<time_h):
                           # print("row_det: ",row_det, "col_det:", col_det, "system.feb.chargeInj.hitDetTime"+str(matrix_i)+"_"+str(hit)+":", time_m1)
                            if (row_det,col_det) in pixels:
                                print("row_det: ",row_det, "col_det:", col_det, "system.feb.chargeInj.hitDetTime"+str(matrix_i)+"_"+str(hit)+":", time_m1)
                                allHists[(row_det,col_det)][matrix_i][hit][threshold].append(float(eval(get_funct('time_det',matrix_i,hit))))
                            #else:
                                #allHists[(row_det,col_det)][matrix_i][hit][threshold].append(float(-2.0))
                                #print("row_det: ",row_det, "col_det:", col_det, "system.feb.chargeInj.hitDetTime"+str(matrix_i)+"_"+str(hit)+":", time_m1)
                                if (d_time<time_m1<d_time_2):                       
                                    time_buffer[matrix_i+1][int(time_m1/time_reso)]+=1
                                    thre_buffer[matrix_i+1][thre_index]+=1
                                    hitmap_t1[row_det][col_det]+=1
                    matrix_i=2
                    if eval(get_funct('Valid',matrix_i,hit)):
                       # row_det_raw = eval(get_funct('row_det',matrix_i,hit))
                       # col_det_raw = eval(get_funct('col_det',matrix_i,hit))
                       # time_m2_raw = hex(eval(get_funct('time_det_raw',matrix_i,hit)))
                        row_det = int(eval(get_funct('row_det',matrix_i,hit)))
                        col_det = int(eval(get_funct('col_det',matrix_i,hit)))
                        time_m2=float(eval(get_funct('time_det',matrix_i,hit)))
            #            OutputFile.write("("+str(row_det_raw)+","+str(col_det_raw)+"):  ")
            #            OutputFile.write(str(time_m2_raw)+"\n")
                        if (time_m2<time_h):
                            #print("row_det: ",row_det, "col_det:", col_det, "system.feb.chargeInj.hitDetTime"+str(matrix_i)+"_"+str(hit)+":", time_m2)
                        #if (row_det,col_det) in (row,col):
                            if (row_det,col_det) in pixels:
                                print("row_det: ",row_det, "col_det:", col_det, "system.feb.chargeInj.hitDetTime"+str(matrix_i)+"_"+str(hit)+":", time_m2)
                                allHists[(row_det,col_det)][matrix_i][hit][threshold].append(float(eval(get_funct('time_det',matrix_i,hit))))
                            #else:
                                #allHists[(row_det,col_det)][matrix_i][hit][threshold].append(float(-2.0))
                            #    print("row_det: ",row_det, "col_det:", col_det, "system.feb.chargeInj.hitDetTime"+str(matrix_i)+"_"+str(hit)+":", time_m2)
                                if (d_time<time_m2<d_time_2):                       
                                    time_buffer[matrix_i+1][int(time_m2/time_reso)]+=1
                                    thre_buffer[matrix_i+1][thre_index]+=1
                                    hitmap_t2[row_det][col_det]+=1
        print("finishing taking ",nCounts," counts :", time.clock())
        print("updating plots :", time.clock())
        thre_index+=1
        if real_data==1:  #real_size event display
            l_size=10
            pl.figure(1)
            ax0=figure_0.add_axes([0.16,0.144,0.586,0.1955])
            ax0.clear()
            plt.imshow(hitmap_t2,aspect="auto",cmap='gray',origin='upper',vmin=0,interpolation='nearest')
            ax1=figure_0.add_axes([0.16,0.444,0.586,0.1955])
            ax1.clear()
            plt.imshow(hitmap_t1,aspect="auto",cmap='gray',origin='upper',vmin=0,interpolation='nearest')
            ax2=figure_0.add_axes([0.16,0.6485,0.586,0.1955])
            ax2.clear()
            plt.imshow(hitmap_t0,aspect="auto",cmap='gray',origin='lower',vmin=0,interpolation='nearest')
            #plt.show()
            figure_0.canvas.draw()
            figure_0.canvas.flush_events()
            pl.figure(2)
            fig_2_time=plt.subplot(2,1,1)
            fig_2_time.cla() 
            plt.plot(time_buffer[0],time_buffer[1],'b--',label='Matrix 0: time distribution')
            plt.plot(time_buffer[0],time_buffer[2],'y-.',label='Matrix 1: time distribution')
            plt.plot(time_buffer[0],time_buffer[3],'r-',label='Matrix 2: time distribution')
            plt.legend()
            plt.xlabel('Time [ns]',fontsize=l_size)
            plt.ylabel('Counts',fontsize=l_size)
            plt.gca().xaxis.get_major_formatter().set_powerlimits((0,200))
            fig_2_thre=plt.subplot(2,1,2)
            fig_2_thre.cla() 
            plt.step(thre_buffer[0],thre_buffer[1],'b--',label='Matrix 0: threshold scan')
            plt.step(thre_buffer[0],thre_buffer[2],'y-.',label='Matrix 1: threshold scan')
            plt.step(thre_buffer[0],thre_buffer[3],'r-',label='Matrix 2: threshold scan')
            plt.legend()
            plt.xlabel('Threshold [V]',fontsize=l_size)
            plt.ylabel('Counts',fontsize=l_size)
            figure_1.canvas.draw()
            figure_1.canvas.flush_events()
            
        if real_data==2:
            l_size=10
            fig_0_2d=plt.subplot(3,3,1)
            fig_0_2d.cla()
            plt.imshow(hitmap_t0,aspect="auto",cmap='rainbow',origin=[0,0],extent=[0,32,0,128],interpolation='nearest')
            plt.xlabel('Row',fontsize=l_size)
            plt.ylabel('Column',fontsize=l_size)
            fig_0_time=plt.subplot(3,3,2)
            fig_0_time.cla()
            plt.plot(time_buffer[0],time_buffer[1],'b-')
            plt.xlabel('Time [ns]',fontsize=l_size)
            plt.ylabel('Counts',fontsize=l_size)
            plt.gca().xaxis.get_major_formatter().set_powerlimits((0,200))
            fig_0_th=plt.subplot(3,3,3)
            fig_0_th.cla()
            plt.step(thre_buffer[0],thre_buffer[1],'b-')
            #plt.plot(thre_buffer[0],thre_buffer_a[1],'r-.')
            plt.xlabel('Threshold [V]',fontsize=l_size)
            plt.ylabel('Counts',fontsize=l_size)
            fig_1_2d=plt.subplot(3,3,4)
            fig_1_2d.cla()
            plt.imshow(hitmap_t1,aspect="auto",cmap='rainbow',origin=[0,0],extent=[0,32,0,128],interpolation='nearest')
            plt.xlabel('Row',fontsize=l_size)
            plt.ylabel('Column',fontsize=l_size)
            fig_1_time=plt.subplot(3,3,5)
            fig_1_time.cla()
            plt.plot(time_buffer[0],time_buffer[2],'b-')
            #plt.plot(thre_buffer_all[0],thre_buffer_all[1],'r--')
            plt.xlabel('Time [ns]',fontsize=l_size)
            plt.ylabel('Counts',fontsize=l_size)
            plt.gca().xaxis.get_major_formatter().set_powerlimits((0,200))
            fig_1_th=plt.subplot(3,3,6)
            #fig_1_th=plt.subplot(3,3,6)
            fig_1_th.cla()
            plt.step(thre_buffer[0],thre_buffer[2],'b-')
            plt.xlabel('Threshold [V]',fontsize=l_size)
            plt.ylabel('Counts',fontsize=l_size)
            fig_2_2d=plt.subplot(3,3,7)
            fig_2_2d.cla()
            plt.imshow(hitmap_t2,aspect="auto",cmap='rainbow',origin=[0,0],extent=[0,32,0,128],interpolation='nearest')
            plt.xlabel('Row',fontsize=l_size)
            plt.ylabel('Column',fontsize=l_size)
            fig_2_time=plt.subplot(3,3,8)
            fig_2_time.cla()
            plt.plot(time_buffer[0],time_buffer[3],'b-')
            plt.xlabel('Time [ns]',fontsize=l_size)
            plt.ylabel('Counts',fontsize=l_size)
            plt.gca().xaxis.get_major_formatter().set_powerlimits((0,200))
            fig_2_th=plt.subplot(3,3,9)
            fig_2_th.cla()
            plt.step(thre_buffer[0],thre_buffer[3],'b-')
            plt.xlabel('Threshold [V]',fontsize=l_size)
            plt.ylabel('Counts',fontsize=l_size)
            fig_all.canvas.draw()
            fig_all.canvas.flush_events()
            print("finish updating plots :", time.clock())
    allhist=save_timep(allHists)
  #  OutputFile.close()
    return allhist

def makeCalibCurveLoopBLx_8hits_hitmap(system,nCounts,thresholdCuts,pixels=None,histFileName="scurve.root",pixEnableLogic=1,chargeInjLogic=0,pixTrimI=0,deltaBLToBLR=608,BL_v=0x800):
    nColumns      = 32
    nRows         = 128
    logging.info(" Using makeCalibCurveLoopBLx_8hits_hitmap......")
    matrix=[0,1,2]
    hits=[0,1,2,3,4,5,6,7]
    pixels = pixels if (pixels!=None) else [ (row,col) for row in range(0,nRows,1) for col in range(0,nColumns,1) ]
    #pixels = pixels if (pixels!=None) else [ (row,col) for row in range(32,64,1) for col in range(24,32,1) ]
    #pixels = pixels if (pixels!=None) else [ (row,col) for row in range(49,76,1) for col in range(27,32,1) ]
    #pixels = pixels if (pixels!=None) else [ (row,col) for row in range(59,70,1) for col in range(26,32,1) ]
    #pixels = pixels if (pixels!=None) else [ (row,col) for row in range(96,128,1) for col in range(24,32,1) ]
    allHists=get_allHists(pixels,matrix,hits,thresholdCuts)
    BLRValue  = BL_v + deltaBLToBLR
    system.feb.dac.dacBLRRaw.set(BLRValue)
    print("Thresholds (system.feb.dac.dacBLRRaw): ",  hex(BLRValue))
    system.feb.dac.dacBLRaw.set(BL_v)
    print("Thresholds (system.feb.dac.dacBLRaw): ",  hex(BL_v))
    time_h=200000
    time_reso=1000
    d_time=0
    d_time_2=time_h
    time_bin=range(0,time_h,time_reso)
        #a=thresholdCuts[1]
    #fig_all=Figure(figsize=(17,10),dpi=100)
    hitmap_t0=np.zeros((nRows,nColumns))
    hitmap_t1=np.zeros((nRows,nColumns))
    hitmap_t2=np.zeros((nRows,nColumns))
    hitmap_t0_a=np.zeros((nRows,nColumns))
    hitmap_t1_a=np.zeros((nRows,nColumns))
    hitmap_t2_a=np.zeros((nRows,nColumns))
    time_inde=range(0,time_h,time_reso) 
    time_t=np.zeros((4,len(time_inde)))
    time_t[0]=time_inde
    #plt.ion()
    #fig_all=plt.figure(figsize=(17,10))
 
    thre_t=np.zeros((4,len(thresholdCuts)))
    thre_t[0]=np.asarray(thresholdCuts)/1241.
    time_buffer=time_t
    thre_buffer=thre_t
    hot_pixels=[(27,16),(50,15),(45,15)]
    #chargeInjLogic=1
    for (row,col) in pixels:
        if (row,col) in hot_pixels:
            print("hot pixel: (%i,%i)"%(row,col))
        else:
            print("enable Pixel: (%i,%i)"%(row,col))
            system.feb.Chess2Ctrl0.writePixel(enable=pixEnableLogic, chargeInj=chargeInjLogic, col=col, row=row, trimI= pixTrimI)
            #logging.info(" enable Pixel: Matrix0 (%i,%i)"%(row,col))
            system.feb.Chess2Ctrl1.writePixel(enable=pixEnableLogic, chargeInj=chargeInjLogic, col=col, row=row, trimI= pixTrimI)
            #logging.info(" enable Pixel: Matrix1 (%i,%i)"%(row,col))
            system.feb.Chess2Ctrl2.writePixel(enable=pixEnableLogic, chargeInj=chargeInjLogic, col=col, row=row, trimI= pixTrimI)
            #logging.info(" enable Pixel: Matrix2 (%i,%i)"%(row,col))
            thre_index=0
            
            for threshold in thresholdCuts:
               # time_buffer[1:4]=0             
               # thre_buffer[1:4]=0   
                #threshold=a
                print("Thresholds (system.feb.dac.dacPIXTHRaw): ",  hex(threshold))
                print("time start setting threshold: ", time.clock())
                system.feb.dac.dacPIXTHRaw.set(threshold)
                print("time start finishing threshold: ", time.clock())
                time.sleep(2.0)
                print("time after sleep(2.0): ", time.clock())
                system.ReadAll()
                print("time after readall(): ", time.clock())
                print("start taking ",nCounts," counts :", time.clock())
                for cnt in range(nCounts):
                    system.feb.chargeInj.calPulseVar.set(1)
                    #time.sleep(0.05)
                    system.ReadAll()
                    for n in [1]:
                        for hit in hits:
                            matrix_i=0
                            if eval(get_funct('Valid',matrix_i,hit)):
                                row_det = int(eval(get_funct('row_det',matrix_i,hit)))
                                col_det = int(eval(get_funct('col_det',matrix_i,hit)))
                                #hitmap_t0_a[row_det][col_det]+=1
                                time_m0=float(eval(get_funct('time_det',matrix_i,hit)))
                                #logging.info("row_det: "+str(row_det)+"col_det: "+str(col_det)+ "system.feb.chargeInj.hitDetTime_matrix"+str(matrix_i)+"_hit"+str(hit)+":"+str(time_m0))
                                #OutputFile.write(str(binRep(float(eval(get_funct('time_det',matrix_i,hit)))))+"\t")
                                #if (row_det,col_det) in pixels:
                                if (row_det==row and col_det==col):
                                    allHists[(row_det,col_det)][matrix_i][hit][threshold].append(float(eval(get_funct('time_det',matrix_i,hit))))
                                    #allHists[(row_det,col_det)][matrix_i][hit][threshold].append(time_m0)
                                    if (time_m0<time_h):
                                        print("row_det: ",row_det, "col_det:", col_det, "system.feb.chargeInj.hitDetTime"+str(matrix_i)+"_"+str(hit)+":", time_m0)
                                        if (d_time<time_m0<d_time_2):                       
                                            time_buffer[matrix_i+1][int(time_m0/time_reso)]+=1
                                            thre_buffer[matrix_i+1][thre_index]+=1
                                            hitmap_t0[row_det][col_det]+=1
                                else:
                                    allHists[(row,col)][matrix_i][hit][threshold].append(float(-2.0))
                            else: 
                                allHists[(row,col)][matrix_i][hit][threshold].append(float(-1.0))
                                #logging.info("row_det: "+str(row_det)+"col_det: "+str(col_det)+ "system.feb.chargeInj.hitDetTime_matrix"+str(matrix_i)+"_hit"+str(hit)+":"+str(-1.0))
                            matrix_i=1
                            if eval(get_funct('Valid',matrix_i,hit)):
                                row_det = int(eval(get_funct('row_det',matrix_i,hit)))
                                col_det = int(eval(get_funct('col_det',matrix_i,hit)))
                                #hitmap_t1_a[row_det][col_det]+=1
                                time_m1=float(eval(get_funct('time_det',matrix_i,hit)))
                                #OutputFile.write(str(binRep(float(eval(get_funct('time_det',matrix_i,hit)))))+"\t")
                                #print("row_det: ",row_det, "col_det: ", col_det, "system.feb.chargeInj.hitDetTime"+str(matrix_i)+"_"+str(hit)+":", time_m1)
                                #logging.info("row_det: "+str(row_det)+"col_det: "+str(col_det)+ "system.feb.chargeInj.hitDetTime_matrix"+str(matrix_i)+"_hit"+str(hit)+":"+str(time_m1))
                                if (row_det==row and col_det==col):
                                #if (row_det,col_det) in pixels:
				    #allHists[(row_det,col_det)][matrix_i][hit][threshold].append(float(eval(get_funct('time_det',matrix_i,hit))))
                                    allHists[(row_det,col_det)][matrix_i][hit][threshold].append(time_m1)
                                    if (time_m1<time_h):
                                        print("row_det: ",row_det, "col_det: ", col_det, "system.feb.chargeInj.hitDetTime"+str(matrix_i)+"_"+str(hit)+":", time_m1)
                                        if (d_time<time_m1<d_time_2):                       
                                            time_buffer[matrix_i+1][int(time_m1/time_reso)]+=1
                                            thre_buffer[matrix_i+1][thre_index]+=1
                                            hitmap_t1[row_det][col_det]+=1
                                else:
                                    allHists[(row,col)][matrix_i][hit][threshold].append(float(-2.0))
                            else: 
                                allHists[(row,col)][matrix_i][hit][threshold].append(float(-1.0))
                                #logging.info("row_det: "+str(row_det)+"col_det: "+str(col_det)+ "system.feb.chargeInj.hitDetTime_matrix"+str(matrix_i)+"_hit"+str(hit)+":"+str(-1.0))
                            matrix_i=2
                            if eval(get_funct('Valid',matrix_i,hit)):
                                row_det = int(eval(get_funct('row_det',matrix_i,hit)))
                                col_det = int(eval(get_funct('col_det',matrix_i,hit)))
                                #hitmap_t2_a[row_det][col_det]+=1
                                time_m2=float(eval(get_funct('time_det',matrix_i,hit)))
                                #OutputFile.write(str(binRep(float(eval(get_funct('time_det',matrix_i,hit)))))+"\n")
                                #print("row_det: ",row_det, "col_det: ", col_det, "system.feb.chargeInj.hitDetTime"+str(matrix_i)+"_"+str(hit)+":", time_m2)
                               # logging.info("row_det: "+str(row_det)+"col_det: "+str(col_det)+ "system.feb.chargeInj.hitDetTime_matrix"+str(matrix_i)+"_hit"+str(hit)+":"+str(time_m2))
                                if (row_det==row and col_det==col):
                                #if (row_det,col_det) in pixels:
                                    #allHists[(row_det,col_det)][matrix_i][hit][threshold].append(float(eval(get_funct('time_det',matrix_i,hit))))
                                    allHists[(row_det,col_det)][matrix_i][hit][threshold].append(time_m2)
                                    if (time_m2<time_h):
                                        print("row_det: ",row_det, "col_det: ", col_det, "system.feb.chargeInj.hitDetTime"+str(matrix_i)+"_"+str(hit)+":", time_m2)
                                        if (d_time<time_m2<d_time_2):                       
                                            time_buffer[matrix_i+1][int(time_m2/time_reso)]+=1
                                            thre_buffer[matrix_i+1][thre_index]+=1
                                            hitmap_t2[row_det][col_det]+=1
                                else:
                                    allHists[(row,col)][matrix_i][hit][threshold].append(float(-2.0))
                            else: 
                                allHists[(row,col)][matrix_i][hit][threshold].append(float(-1.0))
#                print("finishing taking ",nCounts," counts :", time.clock())
                thre_index+=1
#                print("updating plots :", time.clock())
                l_size=10
#                fig_0_2d=plt.subplot(3,3,1)
#                fig_0_2d.cla()
#                plt.imshow(hitmap_t0,aspect="auto",cmap='Reds',origin=[0,0],extent=[0,31,0,127],interpolation='nearest')
#                plt.xlabel('Row',fontsize=l_size)
#                plt.ylabel('Column',fontsize=l_size)
#                fig_0_time=plt.subplot(3,3,2)
#                fig_0_time.cla()
#                plt.plot(time_buffer[0],time_buffer[1],'b-')
#                plt.xlabel('Time [ns]',fontsize=l_size)
#                plt.ylabel('Counts',fontsize=l_size)
#                plt.gca().xaxis.get_major_formatter().set_powerlimits((0,200))
#                fig_0_th=plt.subplot(3,3,3)
#                fig_0_th.cla()
#                plt.step(thre_buffer[0],thre_buffer[1],'b-')
#                plt.xlabel('Threshold [V]',fontsize=l_size)
#                plt.ylabel('Counts',fontsize=l_size)
#                fig_1_2d=plt.subplot(3,3,4)
#                fig_1_2d.cla()
#                plt.imshow(hitmap_t1,aspect="auto",cmap='Reds',origin=[0,0],extent=[0,31,0,127],interpolation='nearest')
#                plt.xlabel('Row',fontsize=l_size)
#                plt.ylabel('Column',fontsize=l_size)
#                fig_1_time=plt.subplot(3,3,5)
#                fig_1_time.cla()
#                plt.plot(time_buffer[0],time_buffer[2],'b-')
#                plt.xlabel('Time [ns]',fontsize=l_size)
#                plt.ylabel('Counts',fontsize=l_size)
#                plt.gca().xaxis.get_major_formatter().set_powerlimits((0,200))
#                fig_1_th=plt.subplot(3,3,6)
#                fig_1_th.cla()
#                plt.step(thre_buffer[0],thre_buffer[2],'b-')
#                plt.xlabel('Threshold [V]',fontsize=l_size)
#                plt.ylabel('Counts',fontsize=l_size)
#                fig_2_2d=plt.subplot(3,3,7)
#                fig_2_2d.cla()
#                plt.imshow(hitmap_t2,aspect="auto",cmap='Reds',origin=[0,0],extent=[0,31,0,127],interpolation='nearest')
#                plt.xlabel('Row',fontsize=l_size)
#                plt.ylabel('Column',fontsize=l_size)
#                fig_2_time=plt.subplot(3,3,8)
#                fig_2_time.cla()
#                plt.plot(time_buffer[0],time_buffer[3],'b-')
#                plt.xlabel('Time [ns]',fontsize=l_size)
#                plt.ylabel('Counts',fontsize=l_size)
#                plt.gca().xaxis.get_major_formatter().set_powerlimits((0,200))
#                fig_2_th=plt.subplot(3,3,9)
#                fig_2_th.cla()
#                plt.step(thre_buffer[0],thre_buffer[3],'b-')
#                plt.xlabel('Threshold [V]',fontsize=l_size)
#                plt.ylabel('Counts',fontsize=l_size)
#                fig_all.canvas.draw()
#                fig_all.canvas.flush_events()
#                print("finish updating plots :", time.clock())
        system.feb.Chess2Ctrl0.writePixel(enable=not pixEnableLogic, chargeInj=chargeInjLogic, col=col, row=row)
        system.feb.Chess2Ctrl1.writePixel(enable=not pixEnableLogic, chargeInj=chargeInjLogic, col=col, row=row)
        system.feb.Chess2Ctrl2.writePixel(enable=not pixEnableLogic, chargeInj=chargeInjLogic, col=col, row=row)
        print("disable Pixel: (%i,%i)"%(row,col))
    find_hotpixel=False
    if find_hotpixel:
        plt.ion()
        fig_all=plt.figure(figsize=(17,8))
        fig_0_hmp=plt.subplot(3,2,1)
        plt.imshow(hitmap_t0,aspect="auto",cmap='rainbow',origin=[0,0],extent=[0,31,0,127],interpolation='nearest')
        plt.xlabel('Row',fontsize=l_size)
        plt.ylabel('Column',fontsize=l_size)
        plt.colorbar()
        fig_0_hmp_a=plt.subplot(3,2,2)
        plt.imshow(hitmap_t0_a,aspect="auto",cmap='rainbow',origin=[0,0],extent=[0,31,0,127],interpolation='nearest')
        plt.xlabel('Row',fontsize=l_size)
        plt.ylabel('Column',fontsize=l_size)
        plt.colorbar()
        fig_1_hmp=plt.subplot(3,2,3)
        plt.imshow(hitmap_t1,aspect="auto",cmap='rainbow',origin=[0,0],extent=[0,31,0,127],interpolation='nearest')
        plt.xlabel('Row',fontsize=l_size)
        plt.ylabel('Column',fontsize=l_size)
        plt.colorbar()
        fig_1_hmp_a=plt.subplot(3,2,4)
        plt.imshow(hitmap_t1_a,aspect="auto",cmap='rainbow',origin=[0,0],extent=[0,31,0,127],interpolation='nearest')
        plt.xlabel('Row',fontsize=l_size)
        plt.ylabel('Column',fontsize=l_size)
        plt.colorbar()
        fig_2_hmp=plt.subplot(3,2,5)
        plt.imshow(hitmap_t2,aspect="auto",cmap='rainbow',origin=[0,0],extent=[0,31,0,127],interpolation='nearest')
        plt.xlabel('Row',fontsize=l_size)
        plt.ylabel('Column',fontsize=l_size)
        plt.colorbar()
        fig_2_hmp_a=plt.subplot(3,2,6)
        plt.imshow(hitmap_t2_a,aspect="auto",cmap='rainbow',origin=[0,0],extent=[0,31,0,127],interpolation='nearest')
        plt.xlabel('Row',fontsize=l_size)
        plt.ylabel('Column',fontsize=l_size)
        plt.colorbar()
        fig_all.canvas.draw()
    allhist=save_timep(allHists)
    return allhist

def makeCalibCurveLoopBLx_simu(allHists,nCounts,thresholdCuts,pixels=None,histFileName="scurve.root",pixEnableLogic=1,chargeInjLogic=0,pixTrimI=0,deltaBLToBLR=608,BL_v=0x800):
    nRows         = 128
    nColumns      = 32
    global Ri 
    print(" Using makeCalibCurveLoopBLx_simu......")
    matrix=[0,1,2]
    hits=[0,1,2,3,4,5,6,7]
    pixels = pixels if (pixels!=None) else [ (row,col) for row in range(70,nRows,1) for col in range(20,nColumns,1) ]
    print(thresholdCuts)
    allHists=get_allHists(pixels,matrix,hits,thresholdCuts)
    BLRValue  = BL_v + deltaBLToBLR
    print("Thresholds (system.feb.dac.dacBLRRaw): ",  BLRValue)
    print("Thresholds (system.feb.dac.dacBLRaw): ",  BL_v)
    time_h=150000
    time_reso=1000
    time_bin=range(0,time_h,time_reso)
    plt.ion()
    fig_all=plt.figure(figsize=(17,10))
    #fig_all=Figure(figsize=(17,10),dpi=100)
    
    time_t0=[]
    th_t0=[]
    row_list0=[]
    col_list0=[]
    
    time_t1=[]
    th_t1=[]
    row_list1=[]
    col_list1=[]
    
    time_t2=[]
    th_t2=[]
    row_list2=[]
    col_list2=[]
    t1=time.clock()
    for threshold in thresholdCuts:
        time_buffer[1:4]=0             
        thre_buffer[1:4]=0   
        #threshold=a
        print("Thresholds (system.feb.dac.dacPIXTHRaw): ",  hex(threshold))
        for cnt in range(nCounts):
            for n in [1]:
                for hit in hits:
                    matrix_i=0
                    #if eval(get_funct('Valid',matrix_i,hit)):
                    if 1:
                        row_det = random.randint(0,127) 
                        col_det = random.randint(0,31)
                        if (row_det,col_det) in pixels:
                            time_m0=float(random.randint(0,150000))
                            allHists[(row_det,col_det)][matrix_i][hit][threshold].append(time_m0)
                            #allHists[(row_det,col_det)][matrix_i][hit][threshold].append(float(eval(get_funct('time_det',matrix_i,hit))))
                            print("row_det: ",row_det, "col_det:", col_det, "system.feb.chargeInj.hitDetTime"+str(matrix_i)+"_"+str(hit)+":", time_m0)
                            fig_0_2d=plt.subplot(3,3,1)
                            row_list0.append(row_det)
                            col_list0.append(col_det)
                            all_counts,x_edges,yedges,Image=plt.hist2d(np.array(col_list0),np.array(row_list0),[nColumns,nRows],range=[[0,nColumns],[0,nRows]],cmin=1,cmap=cm.jet)
                            #plt.colorbar(H[3],ax=ax0)
                            plt.title('Matrix 0: hitmap',fontsize=10,ha='left')
                            plt.xlabel('Row',fontsize=8)
                            plt.ylabel('Column',fontsize=8)
                            fig_0_time=plt.subplot(3,3,2)
                            time_t0.append(time_m0)
                            n,bins,patches=plt.hist(np.array(time_t0),int(len(time_bin)),normed=0,color='blue',range=(0,time_h),histtype='step')
                            plt.xlabel('Time [ns]',fontsize=8)
                            plt.ylabel('Hits',fontsize=8)
                            fig_0_th=plt.subplot(3,3,3)
                            th_t0.append(threshold)
                            n,bins,patches=plt.hist(np.array(th_t0),int(len(thresholdCuts)),normed=0,color='blue',range=(min(thresholdCuts),max(thresholdCuts)),histtype='stepfilled')
                            plt.xlabel('Threshold',fontsize=8)
                            plt.ylabel('Hits',fontsize=8)
                            fig_all.canvas.draw()
                            fig_all.canvas.flush_events()
                    matrix_i=1
                    if 1:
                        row_det = random.randint(0,127) 
                        col_det = random.randint(0,31)
                        if (row_det,col_det) in pixels:
                            time_m1=float(random.randint(0,150000))
                            allHists[(row_det,col_det)][matrix_i][hit][threshold].append(time_m1)
                            print("row_det: ",row_det, "col_det:", col_det, "system.feb.chargeInj.hitDetTime"+str(matrix_i)+"_"+str(hit)+":", time_m1)
                           # fig_1_2d=plt.subplot(3,3,4)
                           # row_list1.append(row_det)
                           # col_list1.append(col_det)
                           # all_counts,x_edges,yedges,Image=plt.hist2d(np.array(col_list1),np.array(row_list1),[nColumns,nRows],range=[[0,nColumns],[0,nRows]],cmin=1,cmap=cm.jet)
                           # plt.title('Matrix 1: hitmap',fontsize=10,ha='left')
                           # plt.xlabel('Row',fontsize=8)
                           # plt.ylabel('Column',fontsize=8)
                         
                           # fig_1_time=plt.subplot(3,3,5)
                           # time_t1.append(time_m1)
                           # n,bins,patches=plt.hist(np.array(time_t1),int(len(time_bin)),normed=0,color='blue',range=(0,time_h),histtype='step')
                           # plt.xlabel('Time [ns]',fontsize=8)
                           # plt.ylabel('Hits',fontsize=8)
                           # 
                           # fig_1_th=plt.subplot(3,3,6)
                           # th_t1.append(threshold)
                           # n,bins,patches=plt.hist(np.array(th_t1),int(len(thresholdCuts)),normed=0,color='blue',range=(min(thresholdCuts),max(thresholdCuts)),histtype='stepfilled')
                           # plt.xlabel('Threshold',fontsize=8)
                           # plt.ylabel('Hits',fontsize=8)
                           # fig_all.canvas.draw()
                           # fig_all.canvas.flush_events()
                    matrix_i=2
                    if 1:
                        row_det = random.randint(0,127) 
                        col_det = random.randint(0,31)
                        if (row_det,col_det) in pixels:
                            time_m2=float(random.randint(0,150000))
                            allHists[(row_det,col_det)][matrix_i][hit][threshold].append(time_m2)
                            print("row_det: ",row_det, "col_det:", col_det, "system.feb.chargeInj.hitDetTime"+str(matrix_i)+"_"+str(hit)+":", time_m2)
                           # fig_2_2d=plt.subplot(3,3,7)
                           # row_list2.append(row_det)
                           # col_list2.append(col_det)
                           # all_counts,x_edges,yedges,Image=plt.hist2d(np.array(col_list2),np.array(row_list2),[nColumns,nRows],range=[[0,nColumns],[0,nRows]],cmin=1,cmap=cm.jet)
                           # plt.title('Matrix 2: hitmap',fontsize=10,ha='left')
                           # plt.xlabel('Row',fontsize=8)
                           # plt.ylabel('Column',fontsize=8)
                         
                           # fig_2_time=plt.subplot(3,3,8)
                           # time_t2.append(time_m2)
                           # n,bins,patches=plt.hist(np.array(time_t2),int(len(time_bin)),normed=0,color='blue',range=(0,time_h),histtype='step')
                           # plt.xlabel('Time [ns]',fontsize=8)
                           # plt.ylabel('Hits',fontsize=8)
                           # 
                           # fig_2_th=plt.subplot(3,3,9)
                           # th_t2.append(threshold)
                           # n,bins,patches=plt.hist(np.array(th_t2),int(len(thresholdCuts)),normed=0,color='blue',range=(min(thresholdCuts),max(thresholdCuts)),histtype='stepfilled')
                           # plt.xlabel('Threshold',fontsize=8)
                           # plt.ylabel('Hits',fontsize=8)
                           # fig_all.canvas.draw()
                           # fig_all.canvas.flush_events()
                Ri=copy.copy(allHists)
               
    allhist=save_timep(allHists)
    return allhist
def get_funct(name,matrix,hit):
    name_d={'Valid':'system.feb.chargeInj.hitDetValid'+str(matrix)+'_'+str(hit)+'.get()','row_det':'system.feb.chargeInj.hitDetRow'+str(matrix)+'_'+str(hit)+'.get()','col_det':'system.feb.chargeInj.hitDetCol'+str(matrix)+'_'+str(hit)+'.get()','time_det':'system.feb.chargeInj.hitDetTime'+str(matrix)+'_'+str(hit)+'.get()','time_det_raw':'system.feb.chargeInj.hitDetTimeRaw'+str(matrix)+'_'+str(hit)+'.get()'}
    return name_d[name]

def data_update_Ri(Ri,t1):
    if (time.clock-t1)%100==0:
        if(Ri):
            print('updating Ri')
            return Ri


def makeCalibCurveLoopTH(system,nCounts,thresholdCuts,pixels=None,histFileName="scurve.root", pixEnableLogic = 1, chargeInjLogic = 0, pixTrimI = 0):
    nColumns      = 32
    nRows         = 128
    allHists = []
    logging.info("  Using makeCalibCurveLoopTH......")


    # Turn on one pixel at a time
#    print("Disable all pixels")
#    system.feb.Chess2Ctrl0.writeAllPixels(enable= not pixEnableLogic,chargeInj= not chargeInjLogic)
#    system.feb.Chess2Ctrl1.writeAllPixels(enable= not pixEnableLogic,chargeInj= not chargeInjLogic)
#    system.feb.Chess2Ctrl2.writeAllPixels(enable= not pixEnableLogic,chargeInj= not chargeInjLogic)
    pixels = pixels if (pixels!=None) else [ (row,col) for row in range(nRows) for col in range(nColumns) ]
    for (row,col) in pixels:
      print("Pixel: (%i,%i)"%(row,col))
      system.feb.Chess2Ctrl0.writePixel(enable=pixEnableLogic, chargeInj=chargeInjLogic, col=col, row=row, trimI= pixTrimI)
      system.feb.Chess2Ctrl1.writePixel(enable=pixEnableLogic, chargeInj=chargeInjLogic, col=col, row=row, trimI= pixTrimI)
      system.feb.Chess2Ctrl2.writePixel(enable=pixEnableLogic, chargeInj=chargeInjLogic, col=col, row=row, trimI= pixTrimI)
      ####hists_row = [ R.TH1F("row_%i_%i_%i"%(i_asic,row,col),"",128,0,128) for i_asic in range(3) ]
      ####hists_col = [ R.TH1F("col_%i_%i_%i"%(i_asic,row,col),"",32,0,32) for i_asic in range(3) ]
      hists_row = [[], [], []]
      hists_col = [[], [], []]
      for threshold in thresholdCuts:
        ####hists = [ R.TH1F("deltaT_%i_%i_%i_%s"%(i_asic,row,col,hex(threshold)),"",100,0,1000) for i_asic in range(3) ] # deltaT in ns
        hists = [[], [], []]
        print("Thresholds (system.feb.dac.dacPIXTHRaw): ",  hex(threshold))
        system.feb.dac.dacPIXTHRaw.set(threshold)
        #system.feb.dac.dacBLRaw.set(threshold+608)
        #print("Thresholds (system.feb.dac.dacBLRRaw): ",  hex(threshold))
        #system.feb.dac.dacBLRRaw.set(threshold)
#        print("Thresholds (system.feb.dac.dacBLRaw): ",  hex(threshold))
#        system.feb.dac.dacBLRaw.set(threshold)
        # this delay seems to be very important to enable the comparitor inside the asic to settle. (smaller values tend to make this 
        # tests to report wrong times
        time.sleep(2.0)
        system.ReadAll()
        for cnt in range(nCounts):
          #time.sleep(0.1)
          # start charge injection
          #system.feb.memReg.chargInjStartEventReg.set(0)
          system.feb.chargeInj.calPulseVar.set(1)
          time.sleep(0.1)          
          system.ReadAll()
          if system.feb.chargeInj.hitDetValid0._rawGet():
            row_det = int(system.feb.chargeInj.hitDetRow0._rawGet())
            col_det = int(system.feb.chargeInj.hitDetCol0._rawGet())
            ####hists_row[0].Fill(row_det)
            ####hists_col[0].Fill(col_det)
            hists_row[0].append(row_det)
            hists_col[0].append(col_det)
            #if (row == row_det) and (col == col_det):
              ####hists[0].Fill(float(system.feb.chargeInj.hitDetTime0._rawGet()))
            hists[0].append(float(system.feb.chargeInj.hitDetTime0._rawGet()))
            print("row_det: ",row_det, "col_det", col_det, "system.feb.chargeInj.hitDetTime0: ", float(system.feb.chargeInj.hitDetTime0._rawGet()))
          else:
            hists[0].append(-1.0)
            print("row_det: ",-1, ":col_det:", -1, ":system.feb.chargeInj.hitDetTime0: ", float(-1))

          if system.feb.chargeInj.hitDetValid1._rawGet():
            row_det = int(system.feb.chargeInj.hitDetRow1._rawGet())
            col_det = int(system.feb.chargeInj.hitDetCol1._rawGet())
            ####hists_row[1].Fill(row_det)
            ####hists_col[1].Fill(col_det)
            hists_row[1].append(row_det)
            hists_col[1].append(col_det)
            #if (row == row_det) and (col == col_det):
              ####hists[1].Fill(float(system.feb.chargeInj.hitDetTime1._rawGet()))
            hists[1].append(float(system.feb.chargeInj.hitDetTime1._rawGet()))
            print("row_det: ",row_det, "col_det", col_det, "system.feb.chargeInj.hitDetTime1: ", float(system.feb.chargeInj.hitDetTime1._rawGet()))
          else:
            hists[1].append(-1.0)
            print("row_det: ",-1, ":col_det:", -1, ":system.feb.chargeInj.hitDetTime1: ", float(-1))

          if system.feb.chargeInj.hitDetValid2._rawGet():
            row_det = int(system.feb.chargeInj.hitDetRow2._rawGet())
            col_det = int(system.feb.chargeInj.hitDetCol2._rawGet())
            ####hists_row[2].Fill(row_det)
            ####hists_col[2].Fill(col_det)
            hists_row[2].append(row_det)
            hists_col[2].append(col_det)
            #if (row == row_det) and (col == col_det):
              ####hists[2].Fill(float(system.feb.chargeInj.hitDetTime2._rawGet()))
            hists[2].append(float(system.feb.chargeInj.hitDetTime2._rawGet()))
            print("row_det: ",row_det, "col_det", col_det, "system.feb.chargeInj.hitDetTime2: ", float(system.feb.chargeInj.hitDetTime2._rawGet()))
          else:
            hists[2].append(-1.0)
            print("row_det: ",-1, ":col_det:", -1, ":system.feb.chargeInj.hitDetTime2: ", float(-1))

        allHists.append(hists)
    
    return allHists


def swingTHvsBL(system,nCounts,thresholdCuts,pixels=None,histFileName="scurve.root"):
    allHists = []
    logging.info("Using swingTHvsBL......")

    pixEnable = 1
    chargeInj = 1
    trim = 15

    #
    system.feb.dac.dacPIXTHRaw.set(0x9ce)
    system.feb.dac.dacBLRRaw.set(0x5c2)
    system.feb.dac.dacBLRaw.set(0x5c2)
    #  
    system.feb.memReg.initValueReg.set(0x0)
    system.feb.memReg.endValueReg.set(0xfff)
    system.feb.memReg.delayValueReg.set(0x5)

    print("Disable all pixels")
    system.feb.Chess2Ctrl0.writeAllPixels(enable= 0,chargeInj= 1)
    system.feb.Chess2Ctrl1.writeAllPixels(enable= 0,chargeInj= 1)
    system.feb.Chess2Ctrl2.writeAllPixels(enable= 0,chargeInj= 1)


    print("Trim, pixEnable, chargeInj: (%i,%i,%i)"%(trim, pixEnable, chargeInj))
    hists = SwingThLoopBLx(system,nCounts,thresholdCuts,pixels,histFileName, pixEnableLogic = pixEnable, chargeInjLogic = chargeInj, pixTrimI = trim, vs = 'BL')
    allHists.append(hists)

    return allHists


def swingTHvsBLR(system,nCounts,thresholdCuts,pixels=None,histFileName="scurve.root"):
    allHists = []

    pixEnable = 1
    chargeInj = 1
    trim = 15

    #
    system.feb.dac.dacPIXTHRaw.set(0x9ce)
    system.feb.dac.dacBLRRaw.set(0x5c2)
    system.feb.dac.dacBLRaw.set(0x5c2)
    #  
    system.feb.memReg.initValueReg.set(0x0)
    system.feb.memReg.endValueReg.set(0xfff)
    system.feb.memReg.delayValueReg.set(0x5)

    print("Disable all pixels")
    system.feb.Chess2Ctrl0.writeAllPixels(enable= 0,chargeInj= 1)
    system.feb.Chess2Ctrl1.writeAllPixels(enable= 0,chargeInj= 1)
    system.feb.Chess2Ctrl2.writeAllPixels(enable= 0,chargeInj= 1)


    print("Trim, pixEnable, chargeInj: (%i,%i,%i)"%(trim, pixEnable, chargeInj))
    hists = SwingThLoopBLx(system,nCounts,thresholdCuts,pixels,histFileName, pixEnableLogic = pixEnable, chargeInjLogic = chargeInj, pixTrimI = trim, vs = 'BLR')
    allHists.append(hists)

    return allHists

def SwingThLoopBLx(system,nCounts,thresholdCuts,pixels=None,histFileName="scurve.root", pixEnableLogic = 1, chargeInjLogic = 0, pixTrimI = 0, vs = 'BL'):
    logging.info("Using SwingThLoopBLx......")
    thresh = []
    hits = []
    plt.ion()
    fig=plt.figure()
    
    pixels = pixels if (pixels!=None) else [ (row,col) for row in range(nRows) for col in range(nColumns) ]
    for (row,col) in pixels:
      print("Pixel: (%i,%i)"%(row,col))
      system.feb.Chess2Ctrl1.writePixel(enable=pixEnableLogic, chargeInj=chargeInjLogic, col=col, row=row, trimI= pixTrimI)
      for threshold in thresholdCuts:
          print("Thresholds (system.feb.dac.dacPIXTHRaw): ",  hex(threshold))
          print(" Baseline  (system.feb.dac.dacBLRaw)", hex(system.feb.dac.dacBLRaw.get()))
          system.feb.dac.dacPIXTHRaw.set(threshold)
          time.sleep(0.5)
          print("start taking ",nCounts," counts :", time.clock())
          counts = 0.1
          for cnt in range(nCounts):
              system.feb.chargeInj.calPulse.set(1)
              time.sleep(0.01)
              system.ReadAll()
              time.sleep(0.01)
              for hit in range(0,8):
                  matrix_i=1
                  if eval(get_funct('Valid',matrix_i,hit)):
                      row_det = int(eval(get_funct('row_det',matrix_i,hit)))
                      col_det = int(eval(get_funct('col_det',matrix_i,hit)))
                      time_det=  float(eval(get_funct('time_det',matrix_i,hit)))
                      counts += 1
                      print("Row: {0}, Col: {1}, Time: {2}".format(row_det,col_det,time_det))
                           
          thresh.append(threshold)
          hits.append(counts)
          barWidth = (thresh[-1]-thresh[0])/len(thresh)
          plt.bar(thresh,hits,width=barWidth,color='b')
          fig.canvas.draw()
          fig.canvas.flush_events()
    
    return allHists

