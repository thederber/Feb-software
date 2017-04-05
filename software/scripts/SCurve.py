import ROOT as R

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
      for threshold in thresholdCuts:
        hists = [ R.TH1F("deltaT_%i_%i_%i_%s"%(i_asic,row,col,hex(threshold)),"",100,0,1000) for i_asic in range(3) ] # deltaT in ns
        system.feb.dac.dacPIXTHRaw.set(threshold)
        system.feb.dac.dacBLRaw.set(threshold+608)
        system.feb.dac.dacBLRRaw.set(threshold-12)
        system.readAll()
        for cnt in range(nCounts):
          # start charge injection
          system.feb.memReg.chargInjStartEventReg.set(0)
          system.readAll()
          if system.feb.chargeInj.hitDetValid0._rawGet():
            hists[0].Fill(float(system.feb.chargeInj.hitDetTime0._rawGet()))
          if system.feb.chargeInj.hitDetValid1._rawGet():
            hists[1].Fill(float(system.feb.chargeInj.hitDetTime1._rawGet()))
          if system.feb.chargeInj.hitDetValid2._rawGet():
            hists[2].Fill(float(system.feb.chargeInj.hitDetTime2._rawGet()))
        [ hist.Write() for hist in hists ]
        [ print("... ASIC%i %f"%(i_h,hist.GetEntries())) for (i_h,hist) in enumerate(hists) ]
      system.feb.Chess2Ctrl0.writePixel(enable=0, chargeInj=0, col=col, row=row)  
      system.feb.Chess2Ctrl1.writePixel(enable=0, chargeInj=0, col=col, row=row)  
      system.feb.Chess2Ctrl2.writePixel(enable=0, chargeInj=0, col=col, row=row)

    tf.Close()
