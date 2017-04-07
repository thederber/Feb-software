import ROOT as R

import time

def makeSCurve(system,nCounts,thresholdCuts,pixels=None,histFileName="scurve.root"):
    nColumns      = 32
    nRows         = 128
    R.TH1.AddDirectory(R.kFALSE)
#    thresholdCuts = [0x7ce]
    # system.root.readConfig("chess2_config.yml") --- should be in the driver script
    tf = R.TFile(histFileName, "recreate")
    # Turn on one pixel at a time
    print("Disable all pixels")
    system.feb.Chess2Ctrl0.writeAllPixels(enable=0,chargeInj=0)
    system.feb.Chess2Ctrl1.writeAllPixels(enable=0,chargeInj=0)
    system.feb.Chess2Ctrl2.writeAllPixels(enable=0,chargeInj=0)
    pixels = pixels if (pixels!=None) else [ (row,col) for row in range(nRows) for col in range(nColumns) ]
    for (row,col) in pixels:
      print("Pixel: (%i,%i)"%(row,col))
      system.feb.Chess2Ctrl0.writePixel(enable=1, chargeInj=1, col=col, row=row)
      system.feb.Chess2Ctrl1.writePixel(enable=1, chargeInj=1, col=col, row=row)
      system.feb.Chess2Ctrl2.writePixel(enable=1, chargeInj=1, col=col, row=row)
      hists_row = [ R.TH1F("row_%i_%i_%i"%(i_asic,row,col),"",128,0,128) for i_asic in range(3) ]
      hists_col = [ R.TH1F("col_%i_%i_%i"%(i_asic,row,col),"",32,0,32) for i_asic in range(3) ]
      for threshold in thresholdCuts:
        hists = [ R.TH1F("deltaT_%i_%i_%i_%s"%(i_asic,row,col,hex(threshold)),"",100,0,1000) for i_asic in range(3) ] # deltaT in ns
        system.feb.dac.dacPIXTHRaw.set(threshold)
        system.feb.dac.dacBLRaw.set(threshold+608)
        system.feb.dac.dacBLRRaw.set(threshold-12)
        system.readAll()
        for cnt in range(nCounts):
          time.sleep(0.1)
          # start charge injection
          system.feb.memReg.chargInjStartEventReg.set(0)
          #system.feb.chargeInj.calPulseVar.set(1)
          system.readAll()
          if system.feb.chargeInj.hitDetValid0._rawGet():
            row_det = int(system.feb.chargeInj.hitDetRow0._rawGet())
            col_det = int(system.feb.chargeInj.hitDetCol0._rawGet())
            hists_row[0].Fill(row_det)
            hists_col[0].Fill(col_det)
            if (row == row_det) and (col == col_det):
              hists[0].Fill(float(system.feb.chargeInj.hitDetTime0._rawGet()))
          if system.feb.chargeInj.hitDetValid1._rawGet():
            row_det = int(system.feb.chargeInj.hitDetRow1._rawGet())
            col_det = int(system.feb.chargeInj.hitDetCol1._rawGet())
            hists_row[1].Fill(row_det)
            hists_col[1].Fill(col_det)
            if (row == row_det) and (col == col_det):
              hists[1].Fill(float(system.feb.chargeInj.hitDetTime1._rawGet()))
          if system.feb.chargeInj.hitDetValid2._rawGet():
            row_det = int(system.feb.chargeInj.hitDetRow2._rawGet())
            col_det = int(system.feb.chargeInj.hitDetCol2._rawGet())
            hists_row[2].Fill(row_det)
            hists_col[2].Fill(col_det)
            if (row == row_det) and (col == col_det):
              hists[2].Fill(float(system.feb.chargeInj.hitDetTime2._rawGet()))
        [ hist.Write() for hist in hists ]
        [ print("... ASIC%i %f"%(i_h,hist.GetEntries())) for (i_h,hist) in enumerate(hists) ]
      [ hist.Write() for hist in hists_row ]
      [ hist.Write() for hist in hists_col ]
      system.feb.Chess2Ctrl0.writePixel(enable=0, chargeInj=0, col=col, row=row)  
      system.feb.Chess2Ctrl1.writePixel(enable=0, chargeInj=0, col=col, row=row)  
      system.feb.Chess2Ctrl2.writePixel(enable=0, chargeInj=0, col=col, row=row)

    tf.Close()
