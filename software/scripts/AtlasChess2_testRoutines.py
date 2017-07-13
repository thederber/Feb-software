####import ROOT as R
import numpy as np
import matplotlib #.pyplot as plt
import time


def makeDelayVsHitDetectTime(system,nCounts,thresholdCuts,pixels=None,histFileName="scurve.root", deltaBLToBLR = 608, chargeInjectionEnbled = 0):

    allHists = []

    pixEnable = 1
    chargeInj = not chargeInjectionEnbled  # 0 - enable / 1 - disabled
    trim = 7

    print("Disable all pixels")
    system.feb.Chess2Ctrl0.writeAllPixels(enable= 0,chargeInj= 1)
    system.feb.Chess2Ctrl1.writeAllPixels(enable= 0,chargeInj= 1)
    system.feb.Chess2Ctrl2.writeAllPixels(enable= 0,chargeInj= 1)


    print("Trim, pixEnable, chargeInj: (%i,%i,%i)"%(trim, pixEnable, chargeInj))
    hists = makeDelayVsHitDetectTimeLoop(system,nCounts,thresholdCuts,pixels,histFileName, pixEnableLogic = pixEnable, chargeInjLogic = chargeInj, pixTrimI = trim, deltaBLToBLR = deltaBLToBLR)
    allHists.append(hists)

    return allHists



def makeDelayVsHitDetectTimeLoop(system,nCounts,thresholdCuts,pixels=None,histFileName="scurve.root", pixEnableLogic = 1, chargeInjLogic = 0, pixTrimI = 0, deltaBLToBLR = 608):
    nColumns      = 32
    nRows         = 128
    allHists = []

    BLValue  = 0x572
    BLRValue  = BLValue + deltaBLToBLR
    #print("Thresholds (system.feb.dac.dacPIXTHRaw): ",  hex(threshold))
    #system.feb.dac.dacPIXTHRaw.set(threshold)
    system.feb.dac.dacBLRRaw.set(BLRValue)
    print("Thresholds (system.feb.dac.dacBLRRaw): ",  hex(BLRValue))
    system.feb.dac.dacBLRaw.set(BLValue)
    print("Thresholds (system.feb.dac.dacBLRaw): ",  hex(BLValue))
#        system.feb.dac.dacBLRaw.set(threshold)
    
    system.feb.chargeInj.invPulse.set(False)

    system.readAll()
    # this delay seems to be very important to enable the comparitor inside the asic to settle. (smaller values tend to make this 
    # tests to report wrong times  
    time.sleep(1.0)

    # Turn on one pixel at a time
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
        
        hists = [[], [], []]

        
        #set the delay
        system.feb.chargeInj.pulseWidthRaw.set(threshold)
    
        
        for cnt in range(nCounts):
          #time.sleep(0.1)
          # start charge injection
          #system.feb.memReg.chargInjStartEventReg.set(0)
          system.feb.chargeInj.calPulseVar.set(1)
          time.sleep(0.05)          
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


