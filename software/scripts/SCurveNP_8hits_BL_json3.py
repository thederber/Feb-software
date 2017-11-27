####import ROOT as R
import numpy as np
import matplotlib #.pyplot as plt
import sys
import time
import re
import logging
import pickle
import json
#import cPickle as pickle
import scipy.io as sio
# Generating log file
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

#transfer the data
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
def get_pixels(filename):
    file_data=open(filename,'r')
    pixels=[]
    for line in file_data.readlines():
        a=re.findall('"pixel":..........',line)
        #a=re.findall('"pixel"',line)
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
        print(pixels)
    return pixels
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
        system.readAll()
        for cnt in range(nCounts):
          #time.sleep(0.1)
          # start charge injection
          system.feb.memReg.chargInjStartEventReg.set(0)
          time.sleep(0.1)
          #system.feb.chargeInj.calPulseVar.set(1)
          system.readAll()
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




def makeCalibCurve4(system,nCounts,thresholdCuts,pixels=None,histFileName="scurve.root", deltaBLToBLR = 608, chargeInjectionEnbled = 0, BL=0x26c):

    logging.info("Using makeCalibCurve4......")
    #ASIC specific configuration selected depending on the test being run

    pixEnable = 1
    chargeInj1 = not chargeInjectionEnbled  # 0 - enable / 1 - disabled
    trim = 7

    #system.feb.chargeInj.pulseWidthRaw.set(0x7fff)
    system.feb.chargeInj.calPulseInh.set(chargeInj1)

    print("Disable all pixels")
    system.feb.Chess2Ctrl0.writeAllPixels(enable= 0,chargeInj= 1,trimI= trim)
    system.feb.Chess2Ctrl1.writeAllPixels(enable= 0,chargeInj= 1,trimI= trim)
    system.feb.Chess2Ctrl2.writeAllPixels(enable= 0,chargeInj= 1,trimI= trim)
    print("Trim, pixEnable, chargeInj: (%i,%i,%i)"%(trim, pixEnable, chargeInj1))
    if pixels==None:
        hitmap0,hitmap1,hitmap2,hists = makeCalibCurveLoopBLx_hitmap(system,nCounts,thresholdCuts,pixels,histFileName, pixEnableLogic = pixEnable, chargeInjLogic = chargeInj1, pixTrimI = trim, deltaBLToBLR = deltaBLToBLR,pixth=Pixth)
    else:
        hists = makeCalibCurveLoopBLx_8hits(system,nCounts,thresholdCuts,pixels,histFileName, pixEnableLogic = pixEnable, chargeInjLogic = chargeInj1, pixTrimI = trim, deltaBLToBLR = deltaBLToBLR,BL_v=BL)
    if pixels==None:
        return hitmap0,hitmap1,hitmap2,allHists
    else:
        return hists

def makeCalibCurveLoop(system,nCounts,thresholdCuts,pixels=None,histFileName="scurve.root", pixEnableLogic = 1, chargeInjLogic = 0, pixTrimI = 0):
    nColumns      = 32
    nRows         = 128
    allHists = []
    logging.info("Using makeCalibCurveLoop......")


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
#        system.feb.dac.dacPIXTHRaw.set(threshold)
        #system.feb.dac.dacBLRaw.set(threshold+608)
        #print("Thresholds (system.feb.dac.dacBLRRaw): ",  hex(threshold))
        #system.feb.dac.dacBLRRaw.set(threshold)
        print("Thresholds (system.feb.dac.dacBLRaw): ",  hex(threshold))
        system.feb.dac.dacBLRaw.set(threshold)
        # this delay seems to be very important to enable the comparitor inside the asic to settle. (smaller values tend to make this 
        # tests to report wrong times
        time.sleep(2.0)
        system.readAll()
        for cnt in range(nCounts):
          #time.sleep(0.1)
          # start charge injection
          #system.feb.memReg.chargInjStartEventReg.set(0)
          system.feb.chargeInj.calPulseVar.set(1)
          time.sleep(0.1)          
          system.readAll()
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
                    system.readAll()
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
                    system.readAll()
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
                    system.readAll()
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
            system.readAll()
            ####hists = [ R.TH1F("deltaT_%i_%i_%i_%s"%(i_asic,row,col,hex(threshold)),"",100,0,1000) for i_asic in range(3) ] # deltaT in ns
            for cnt in range(nCounts):
                #time.sleep(1.0)
                #system.readAll()
          #system.feb.memReg.chargInjStartEventReg.set(0)
                system.feb.chargeInj.calPulseVar.set(1)
                time.sleep(0.05)          
                system.readAll()
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
        
def makeCalibCurveLoopBLx_8hits(system,nCounts,thresholdCuts,pixels=None,histFileName="scurve.root",pixEnableLogic=1,chargeInjLogic=0,pixTrimI=0,deltaBLToBLR=608,BL_v=0x800):
    nColumns      = 32
    nRows         = 128
    logging.info(" Using makeCalibCurveLoopBLx_8hits......")
    matrix=[0,1,2]
    hits=[0,1,2,3,4,5,6,7]
    allHists=get_allHists(pixels,matrix,hits,thresholdCuts)
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
        #a=thresholdCuts[1]
    for threshold in thresholdCuts:
        #threshold=a
        print("Thresholds (system.feb.dac.dacPIXTHRaw): ",  hex(threshold))
        system.feb.dac.dacPIXTHRaw.set(threshold)
        time.sleep(1.0)
        system.readAll()
        for cnt in range(nCounts):
            system.feb.chargeInj.calPulseVar.set(1)
            time.sleep(0.05)
            system.readAll()
            for n in [1]:
                for hit in hits:
                    matrix_i=0
                    if eval(get_funct('Valid',matrix_i,hit)):
                        row_det = int(eval(get_funct('row_det',matrix_i,hit)))
                        col_det = int(eval(get_funct('col_det',matrix_i,hit)))
                        if (row_det,col_det) in pixels:
                            allHists[(row_det,col_det)][matrix_i][hit][threshold].append(float(eval(get_funct('time_det',matrix_i,hit))))
                            print("row_det: ",row_det, "col_det:", col_det, "system.feb.chargeInj.hitDetTime"+str(matrix_i)+"_"+str(hit)+":", float(eval(get_funct('time_det',matrix_i,hit))))
                    matrix_i=1
                    if eval(get_funct('Valid',matrix_i,hit)):
                        row_det = int(eval(get_funct('row_det',matrix_i,hit)))
                        col_det = int(eval(get_funct('col_det',matrix_i,hit)))
                        if (row_det,col_det) in pixels:
                            allHists[(row_det,col_det)][matrix_i][hit][threshold].append(float(eval(get_funct('time_det',matrix_i,hit))))
                            print("row_det: ",row_det, "col_det:", col_det, "system.feb.chargeInj.hitDetTime"+str(matrix_i)+"_"+str(hit)+":", float(eval(get_funct('time_det',matrix_i,hit))))
                    matrix_i=2
                    if eval(get_funct('Valid',matrix_i,hit)):
                        row_det = int(eval(get_funct('row_det',matrix_i,hit)))
                        col_det = int(eval(get_funct('col_det',matrix_i,hit)))
                        if (row_det,col_det) in pixels:
                            allHists[(row_det,col_det)][matrix_i][hit][threshold].append(float(eval(get_funct('time_det',matrix_i,hit))))
                            print("row_det: ",row_det, "col_det:", col_det, "system.feb.chargeInj.hitDetTime"+str(matrix_i)+"_"+str(hit)+":", float(eval(get_funct('time_det',matrix_i,hit))))
    allhist=save_timep(allHists)
    return allhist

def get_funct(name,matrix,hit):
    name_d={'Valid':'system.feb.chargeInj.hitDetValid'+str(matrix)+'_'+str(hit)+'._rawGet','row_det':'system.feb.chargeInj.hitDetRow'+str(matrix)+'_'+str(hit)+'._rawGet()','col_det':'system.feb.chargeInj.hitDetCol'+str(matrix)+'_'+str(hit)+'._rawGet()','time_det':'system.feb.chargeInj.hitDetTime'+str(matrix)+'_'+str(hit)+'._rawGet()'}
    return name_d[name]




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
        system.readAll()
        for cnt in range(nCounts):
          #time.sleep(0.1)
          # start charge injection
          #system.feb.memReg.chargInjStartEventReg.set(0)
          system.feb.chargeInj.calPulseVar.set(1)
          time.sleep(0.1)          
          system.readAll()
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
    nColumns      = 32
    nRows         = 128
    allHists = []
    logging.info("Using SwingThLoopBLx......")

    pixels = pixels if (pixels!=None) else [ (row,col) for row in range(nRows) for col in range(nColumns) ]
    for (row,col) in pixels:
      print("Pixel: (%i,%i)"%(row,col))
      system.feb.Chess2Ctrl0.writePixel(enable=pixEnableLogic, chargeInj=chargeInjLogic, col=col, row=row, trimI= pixTrimI)
      system.feb.Chess2Ctrl1.writePixel(enable=pixEnableLogic, chargeInj=chargeInjLogic, col=col, row=row, trimI= pixTrimI)
      system.feb.Chess2Ctrl2.writePixel(enable=pixEnableLogic, chargeInj=chargeInjLogic, col=col, row=row, trimI= pixTrimI)

      hists_row = [[], [], []]
      hists_col = [[], [], []]
      for threshold in thresholdCuts:
        ####hists = [ R.TH1F("deltaT_%i_%i_%i_%s"%(i_asic,row,col,hex(threshold)),"",100,0,1000) for i_asic in range(3) ] # deltaT in ns
        hists = [[], [], []]
        #print("Thresholds (system.feb.dac.dacPIXTHRaw): ",  hex(threshold))
        #system.feb.dac.dacPIXTHRaw.set(threshold)
        #system.feb.dac.dacBLRaw.set(threshold+608)
        if (vs == 'BL'):
            system.feb.dac.dacBLRaw.set(threshold)
            print("Thresholds (system.feb.dac.dacBLRaw): ",  hex(threshold), ':system.feb.dac.dacBL:', system.feb.dac.dacBL._rawGet())

        else:
            print("Thresholds (system.feb.dac.dacBLRRaw): ",  hex(threshold), ':system.feb.dac.dacBLR:', system.feb.dac.dacBLR._rawGet())
            system.feb.dac.dacBLRRaw.set(threshold)

        # this delay seems to be very important to enable the comparitor inside the asic to settle. (smaller values tend to make this 
        # tests to report wrong times
        time.sleep(2.0)
        system.readAll()
        for cnt in range(nCounts):
          #time.sleep(0.1)
          # start charge injection
          system.feb.memReg.chargInjStartEventReg.set(0)
          #system.feb.chargeInj.calPulseVar.set(1)
          time.sleep(0.1)          
          system.readAll()
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
            print("row_det: ",row_det, ":col_det:", col_det, ":system.feb.chargeInj.hitDetTime0: ", float(system.feb.chargeInj.hitDetTime0._rawGet()))
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
            print("row_det: ",row_det, ":col_det:", col_det, ":system.feb.chargeInj.hitDetTime1: ", float(system.feb.chargeInj.hitDetTime1._rawGet()))
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
            print("row_det: ",row_det, ":col_det:", col_det, ":system.feb.chargeInj.hitDetTime2: ", float(system.feb.chargeInj.hitDetTime2._rawGet()))
          else:
            hists[2].append(-1.0)
            print("row_det: ",-1, ":col_det:", -1, ":system.feb.chargeInj.hitDetTime2: ", float(-1))

        allHists.append(hists)
    
    return allHists

