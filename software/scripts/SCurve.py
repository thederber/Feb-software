
def makeSCurve(system,nCounts):
    nColumns      = 256
    nRows         = 32
    thresholdCuts = ['0x7ce'] # --- Is there a straightforward way to convert this to float, or vice versa?
    # system.root.readConfig("chess2_config.yml") --- Set at some point
    # tf = TFile("oneFileForAllPixels.root")
    for x in xrange(nColumns):
      for y in xrange(nRows):
        # Turn on one pixel at a time
        system.feb.Chess2Ctrl0.writeAllPixels(enable=0,chargeInj=0)
        system.feb.Chess2Ctrl0.writePixel(enable=1, chargeInj=1, col=x, row=y)
        # hist = TH1F("scurve","scurve",len(thresholdCuts),0,hex_to_float(thresholdCuts[-1]))
        for threshold in thresholdCuts:
          nEvents = []
          system.feb.dac.dacPIXTHRaw.set(int(str(threshold),16))
          #system.feb.dac.BL.set()  --- Set baseline so TH and BL are 0.10 V apart
          #system.dataWriter.dataFile.set("dummy.dat")
          #system.dataWriter.open.set(True)
          system.runControl.runState.set('Running') # --- Collect data
          while True:
            if(system.runControl.runCount._rawGet() > nCounts):
              system.runControl.runState.set('Stopped')
              #system.dataWriter.open.set(False)
              break
	  # data = accessData() --- This will probably not be that straightforward
          # nEvents = processedData(data)
          # mean = takeMean(nEvents)
          # bin = hist.GetXaxis().FindBin(hex_to_float(threshold))
          # hist.SetBinContent(bin,mean)
          # hist.Write()
        
 
