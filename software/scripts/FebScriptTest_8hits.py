#!/usr/bin/env python3
#-----------------------------------------------------------------------------
# Title      : PyRogue febBoard Module
#-----------------------------------------------------------------------------
# File       : febBoard.py
# Author     : Larry Ruckman <ruckman@slac.stanford.edu>
# Created    : 2016-11-09
# Last update: 2016-11-09
#-----------------------------------------------------------------------------
# Description:
# Rogue interface to FEB board
#-----------------------------------------------------------------------------
# This file is part of the ATLAS CHESS2 DEV. It is subject to 
# the license terms in the LICENSE.txt file found in the top-level directory 
# of this distribution and at: 
#    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html. 
# No part of the ATLAS CHESS2 DEV, including this file, may be 
# copied, modified, propagated, or distributed except according to the terms 
# contained in the LICENSE.txt file.
#-----------------------------------------------------------------------------
import rogue.hardware.pgp
import pyrogue.utilities.fileio
import pyrogue.gui
import pyrogue.protocols
import AtlasChess2Feb
import threading
import signal
import atexit
import yaml
import time
import sys
import PyQt4.QtGui
import numpy as np
import datetime
import json
import csv
import copyreg
#from SCurveNP import makeSCurve
from SCurveNP_8hits_BL_json3 import *
from AtlasChess2_testRoutines import *
#from csv_newplotter_h_8hit import *
MAKE_S_CURVE = True
MAKE_TIME_DELAY_CURVE = False

c2_hists = []

# Custom run control
class MyRunControl(pyrogue.RunControl):
   def __init__(self,name):
      pyrogue.RunControl.__init__(self,name,'Run Controller')
      self._thread = None

      self.runRate.enum = {1:'1 Hz', 10:'10 Hz', 100:'100 Hz'}

   def _setRunState(self,dev,var,value):
      if self._runState != value:
         self._runState = value

         if self._runState == 'Running':
            self._thread = threading.Thread(target=self._run)
            self._thread.start()
         else:
            self._thread.join()
            self._thread = None

   def _run(self):
      self._runCount = 0
      self._last = int(time.time())


      while (self._runState == 'Running'):
         delay = 1.0 / ({value:key for key,value in self.runRate.enum.items()}[self._runRate])
         time.sleep(delay)
         self._root.feb.sysReg.softTrig()

         self._runCount += 1
         if self._last != int(time.time()):
             self._last = int(time.time())
             self.runCount._updated()

def gui(arg = "192.168.3.28", configFile = "default.yml" ):

    hists = []
    #logfile()
    # Set base
    system = pyrogue.Root('System','Front End Board')

    # Run control
    system.add(MyRunControl('runControl'))

    # File writer
    dataWriter = pyrogue.utilities.fileio.StreamWriter('dataWriter')
    system.add(dataWriter)

    #################################################################
    # Check for PGP link
    if (arg == 'PGP'):
        # Create the PGP interfaces
        pgpVc0 = rogue.hardware.pgp.PgpCard('/dev/pgpcard_0',0,0) # Data
        pgpVc1 = rogue.hardware.pgp.PgpCard('/dev/pgpcard_0',0,1) # Registers

        # Display PGP card's firmware version
        print("")
        print("PGP Card Version: %x" % (pgpVc0.getInfo().version))
        print("")

        # Create and Connect SRPv0 to VC1
        srp = rogue.protocols.srp.SrpV0()
        pyrogue.streamConnectBiDir(pgpVc1,srp)
        
        # Add data stream to file as channel 1
        pyrogue.streamConnect(pgpVc0,dataWriter.getChannel(0x1))
    #################################################################
    # Else it's Ethernet based
    else:
        # Create the ETH interface @ IP Address = arg
        ethLink = pyrogue.protocols.UdpRssiPack(host=arg,port=8192,size=1400)    
    
        # Create and Connect SRPv0 to AxiStream.tDest = 0x0
        srp = rogue.protocols.srp.SrpV0()  
        pyrogue.streamConnectBiDir(srp,ethLink.application(0))

        # Add data stream to file as channel 1 to tDest = 0x1
        pyrogue.streamConnect(ethLink.application(1),dataWriter.getChannel(0x1))
    #################################################################
             
    # Add registers
    system.add(AtlasChess2Feb.feb(memBase=srp))
    
    # Get the updated variables
#    system.readAll()
    
    # print ('Load the matrix')
#    system.feb.Chess2Ctrl0.loadMatrix()
#    system.feb.Chess2Ctrl1.loadMatrix()
#    system.feb.Chess2Ctrl2.loadMatrix()
    
    ######################################################################
    # Example: Enable only one pixel for charge injection or Th swing test
    ######################################################################
    #print ('Disable all pixels')
#    system.feb.Chess2Ctrl0.writeAllPixels(enable=0,chargeInj=1)
#    system.feb.Chess2Ctrl1.writeAllPixels(enable=0,chargeInj=1)
#    system.feb.Chess2Ctrl2.writeAllPixels(enable=0,chargeInj=1)
    ## Enable only one pixel for charge injection
    #print ('Enable only one pixels')
#    system.feb.Chess2Ctrl0.writePixel(enable=1, chargeInj=0, col=0, row=0, trimI= 9)
#    system.feb.Chess2Ctrl1.writePixel(enable=1, chargeInj=1, col=0, row=0, trimI= 9)
#    system.feb.Chess2Ctrl2.writePixel(enable=1, chargeInj=0, col=0, row=0, trimI= 9)

#    """ Enable only one pixel for charge injection """
#    print ('Enable only one pixel for threshold test')
#    system.feb.Chess2Ctrl0.writePixel(enable=1, chargeInj=1, col=1, row=1, trimI= 7)
#    system.feb.Chess2Ctrl1.writePixel(enable=1, chargeInj=1, col=1, row=1, trimI= 7)
#    system.feb.Chess2Ctrl2.writePixel(enable=1, chargeInj=1, col=1, row=1, trimI= 7)

    today=datetime.date.today()
    today1=today.strftime('%m%d%Y')

    # Create GUI
    appTop = PyQt4.QtGui.QApplication(sys.argv)
    guiTop = pyrogue.gui.GuiTop('PyRogueGui')
    guiTop.resize(800, 1000)
    guiTop.addTree(system)
    system.root.readConfig(sys.argv[2])
    print("Loading config file :", sys.argv[2])
    
    #system.root.writeConfig("/u1/home/hanyubo/atlas-chess2/software/scripts/preamp/yml/save_"+sys.argv[2])
    #print("Saving the config file :", sys.argv[2])
#    system.readAll()
    
#    system.feb.memReg.chargInjStartEventReg.set(0)
    #system.feb.dac.dacPIXTHRaw.set(0x6c2)
    #system.feb.dac.dacBLRRaw.set(0x602)
    #system.feb.dac.dacBLRaw.set(0x572)
#    system.readAll()
    
    #system.feb.memReg.initValueReg.set(0x0)
    #system.feb.memReg.endValueReg.set(0xfff)
    #system.feb.memReg.delayValueReg.set(0x5)

    """ Performs a test on a single pixel swing th"""
#    thresholds = [0xfc2,0xec2,0xdc2,0xcc2,0xbc2,0xac2,0x9c2,0x8c2,0x7c2,0x6c2,0x5c2,0x4c2,0x3c2,0x2c2,0x1c2,0x0c2]
#    print("\nSwing Th vs BL\n")
#    swingTHvsBL(system, nCounts=2, thresholdCuts = thresholds,pixels=[ (1,1) ],histFileName="scurve.root")
#    print("\nSwing Th vs BLR\n")    
#    swingTHvsBLR(system, nCounts=2, thresholdCuts = thresholds,pixels=[ (1,1) ],histFileName="scurve.root")

    """ Performs a test on a single pixel"""
#    thresholds = [0x7c1]#,0xec2,0xdc2,0xcc2,0xbc2,0xac2,0x9c2,0x8c2,0x7c2,0x6c2,0x5c2,0x4c2,0x3c2,0x2c2,0x1c2,0x0c2]
#    hists = makeCalibCurve2( system, nCounts=2, thresholdCuts = thresholds, pixels=[ (1,1) ], histFileName="scurve_test_sleep.root" )

    """Perform tests to identify which pixels that respond to the calib test for the given parameters"""
#    thresholds = [0x5c2]#[0x7c2,0x8c2,0x9c2]
#    for row in range (0, 10):
#        for col in range (0,32):
#            hists = makeCalibCurve( system, nCounts=2, thresholdCuts = thresholds, pixels=[ (row,col) ], histFileName="scurve_test_sleep.root" )

    """ Make S curve"""
    if (MAKE_S_CURVE):
        run = 1
        Qinj = [1,0]
        a1='28'
        #set VNSF=0.026#muA
        #system.feb.Chess2Ctrl0.VNSFatt.set(0x16)
        #system.feb.Chess2Ctrl0.VNSFres.set(0x2)
        #system.feb.Chess2Ctrl1.VNSFatt.set(0x16)
        #system.feb.Chess2Ctrl1.VNSFres.set(0x2)
        #system.feb.Chess2Ctrl2.VNSFatt.set(0x16)
        #system.feb.Chess2Ctrl2.VNSFres.set(0x2)
        #set VNSF=0.090#muA
        #system.feb.Chess2Ctrl0.VNSFatt.set(0x17)
        #system.feb.Chess2Ctrl0.VNSFres.set(0x3)
        #system.feb.Chess2Ctrl1.VNSFatt.set(0x17)
        #system.feb.Chess2Ctrl1.VNSFres.set(0x3)
        #system.feb.Chess2Ctrl2.VNSFatt.set(0x17)
        #system.feb.Chess2Ctrl2.VNSFres.set(0x3)
        #set VNSF=0.361#muA
        #system.feb.Chess2Ctrl0.VNSFatt.set(0x19)
        #system.feb.Chess2Ctrl0.VNSFres.set(0x3)
        #system.feb.Chess2Ctrl1.VNSFatt.set(0x19)
        #system.feb.Chess2Ctrl1.VNSFres.set(0x3)
        #system.feb.Chess2Ctrl2.VNSFatt.set(0x19)
        #system.feb.Chess2Ctrl2.VNSFres.set(0x3)
        BL_value=[0x5d1] #BL
        #BL_value=[0x8,0x136,0x1b2,0x240,0x2e8,0x364,0x3a2,0x3e1,0x45d,0x500,0x555,0x5d1] #BL
        values = [6]#, 5, 4, 3, 2, 1, 0, 7, 8, 9]
        a=sys.argv[1]
        #InvPulse=False
        InvPulse=True #origin
        PulseDelay=0x2bbf
        PulseWidth=0x12bf
        system.feb.chargeInj.pulseWidthRaw.set(PulseWidth)
        #system.feb.chargeInj.pulseDelayRaw.set(0xc7f) #10000ns`
        system.feb.chargeInj.pulseDelayRaw.set(PulseDelay) #35000ns`
        system.feb.chargeInj.invPulse.set(InvPulse) 
        #print(a1)
        logfile("chess2_scan_SCurveTest_"+today1+"_board_"+str(sys.argv[1])+"_run_" + str(run)+"_chargeInjectionEnbled_"+str(Qinj)+"_thN_"+str(values)+"_PulseDelay_"+str(PulseDelay)+"_PXTHsweep.log")
        #logfile("/u1/atlas-chess2-Asic-tests/data/data_h/log/chess2_scan_SCurveTest_"+today1+"_board_"+str(sys.argv[1])+"_run_" + str(run)+"_chargeInjectionEnbled_"+str(Qinj)+"_thN_"+str(values)+"_PulseDelay_"+str(PulseDelay)+"_PXTHsweep.log")
        #logfile("preamp/log/chess2_scan_SCurveTest_07172017_run_" + str(run)+"_chargeInjectionEnbled_"+ str(Qinj[0])+str(Qinj[1]) + "_thN_"+str(hex(values))+".log")
        for value in values:
            logging.info('Running the test with Values='+str(value))
            for chargeInjectionEnbled in Qinj:
                logging.info("Using board: "+str(sys.argv[1]))
                logging.info("Loading config file: "+str(sys.argv[2])) 
                logging.info('    Running the test with Qinj='+str(chargeInjectionEnbled))
                deltaBLToBLR = value * 120 
                #deltaBLToBLR = 0xce5 
                # define test Variables
                #thresholds = [0xfc2,0xec2,0xdc2,0xcc2,0xbc2,0xac2,0x9c2,0x8c2,0x7c2,0x6c2,0x5c2,0x4c2,0x3c2,0x2c2,0x1c2,0x0c2]
                #thresholds = [0x8c2,0x83e,0x7c2,0x73e,0x6c2,0x63e,0x5c2,0x53e,0x4c2,0x43e,0x3c2,0x33e,0x2c2,0x2c2,0x13e,0x1c2]
                #thresholds = [0xbc2,0xbc2,0xbc2,0xbc2,0xbc2,0xac2,0x9c2,0x8c2,0x7c2,0x6c2,0x6b2,0x6a2,0x692,0x682,0x672,0x662,0x652,0x642,0x632,0x622,0x612,0x602,0x5f2,0x5e2,0x5c2,0x5b2,0x5a2,0x592,0x582,0x572,0x562,0x552,0x542,0x532,0x4c2,0x3c2,0x2c2,0x1c2,0x0c2]
                thresholds =range(0x0, 0x800, 0x8)
                #thresholds = range(0x45c, 0x4d9, 0x10)
                #thresholds = np.arange(0x45c, 0x4d9, 0x10)
                #thresholds = [0x6b2]  #BL
                #pixels=[ (3,12),(9,25),(42,15),(85,10),(86,25)]
                #pixels=[(21,21),(21,20)]
                #pixels=[(20,20),(19,19),(80,2),(61,3)]
                #pixels=[(1,20),(10,2),(11,5),(61,3),(61,6)]
                #pixels=[(15,5),(20,20),(120,30),(110,3),(80,2),(11,5),(61,3),(10,2)]
                #pixels=[(19,19)]
                pixels=[(20,20)]
                #pixels=None
                if pixels!=None:
                    logging.info("    Testing Pixel "+str(pixels))
              #  for pixel_i in pixels:
                for BL_value_i in BL_value:
                    hists = makeCalibCurve4( system, nCounts=100, thresholdCuts = thresholds, pixels=pixels, histFileName="scurve_test_sleep.root", deltaBLToBLR = deltaBLToBLR, chargeInjectionEnbled = chargeInjectionEnbled, BL=BL_value_i)
                #thresholdHexList = np.arange(0x800, 0x500, -2) # for the file 'chess2_scan_QinjPulse_BLx_SCurveTest_trim7' 
                #hists = makeSCurve( system, nCounts=10, thresholdCut=thresholds, pixels=pixels, histFileName="scurve_test_sleep.root")
                    #hists1=np.asarray(hists)
                    #print(hists1.shape)
                    #print(hists1)
                # create file header
                    headerText = "\n# Test that perform the BL and BLR voltage sweep. BLR is set as BL plus a delta voltage. (Note: ASIC V1.8a set to 1.8V again). Running with default ASIC values"
                    headerText = headerText + "\n# pixels, " + str(pixels)
                    headerText = headerText + "\n# chargeInjectionEnbled, " + str(chargeInjectionEnbled)
                    headerText = headerText + "\n# deltaBLToBLR:," + str(deltaBLToBLR) 
                    headerText = headerText + "\n# system.feb.dac.dacBLRaw:," + str(system.feb.dac.dacBLRaw._rawGet()) 
                    headerText = headerText + "\n# trim, " + str(7)
                    headerText = headerText + "\n# thresholds (raw):," + str(thresholds)
                    headerText = headerText + "\n# PulseDelay:"+str(PulseDelay)
                    headerText = headerText + "\n# PulseWidth:"+str(PulseWidth)
                    headerText = headerText + "\n# invPulse:"+str(InvPulse)
                    #headerText = headerText + "\n# thresholds (volts):," + str(thresholds/1240)
                    #headerText = headerText + "\n# Shape:{0}:".format(hists1.shape)
                    #print(hists1.shape)
                        #  run test
                        #logging.info(headerText)
                        #hists = makeCalibCurve4( system, nCounts=100, thresholdCuts = thresholds, pixels=pixels, histFileName="scurve_test_sleep.root", deltaBLToBLR = deltaBLToBLR, chargeInjectionEnbled = chargeInjectionEnbled)
               
                # save file
                # new csv file output style
                    save_name="chess2_scan_SCurveTest_10132017_board_"+str(sys.argv[1])+"_run_" +str(run)+"_BL_"+str(BL_value_i)+"_chargeInjectionEnbled_"+ str(chargeInjectionEnbled) + "_thN_"+str(hex(value))+"_PulseDelay_"+str(PulseDelay)+"_PXTHsweep"
                   # save_name="/u1/atlas-chess2-Asic-tests/data/data_h/pre-ampdata-"+a1+"/chess2_scan_SCurveTest_"+today1+"_board_"+str(sys.argv[1])+"_run_" +str(run)+"_BL_"+str(BL_value_i)+"_chargeInjectionEnbled_"+ str(chargeInjectionEnbled) + "_thN_"+str(hex(value))+"_PulseDelay_"+str(PulseDelay)+"_PXTHsweep"
                    #save_f_pickle(save_name+"p",hists)
                    save_f_json(save_name,hists)
                    logging.info(headerText)
                    logging.info(save_name+".json")
                    
    
    system.root.writeConfig("/u1/home/hanyubo/atlas-chess2/software/scripts/preamp/yml/save_2"+sys.argv[2])
    if (MAKE_TIME_DELAY_CURVE):
        run = 1
        thresholds = np.arange(0x0, 0x7FFF, 0x1000)
        pixels=[ (1,1) ]
        values = [3]
        Qinj = [True, False]
        for value in values:
            deltaBLToBLR = value * 120 
            for chargeInjectionEnbled in Qinj:

                headerText = "\n# Test that perform the pulse width sweep (Note: ASIC V1.8a changed to 3.3V)"
                headerText = headerText + "\n# pixels, " + str(pixels)
                headerText = headerText + "\n# chargeInjectionEnbled, " + str(chargeInjectionEnbled)
                headerText = headerText + "\n# deltaBLToBLR:," + str(deltaBLToBLR) 
                headerText = headerText + "\n# system.feb.dac.dacPIXTHRaw:," + str(system.feb.dac.dacPIXTH._rawGet()) 
                headerText = headerText + "\n# trim, " + str(7)
                headerText = headerText + "\n# thresholds (raw):," + str(thresholds)
                # run test
                hists = makeDelayVsHitDetectTime( system, nCounts=100, thresholdCuts = thresholds, pixels=pixels, histFileName="scurve_test_sleep.root", deltaBLToBLR = deltaBLToBLR, chargeInjectionEnbled = chargeInjectionEnbled)
                # save file
                np.savetxt("chess2_scan_QinjDelay_07272017_run_" + str(run)+"_chargeInjectionEnbled_"+ str(chargeInjectionEnbled) + "_thN_"+str(hex(value))+".csv", hists, fmt = "%s",delimiter=",", header=headerText)        
    
#   values = [0xf2e, 0xe2e, 0xd2e, 0xc2e, 0xb2e, 0xa2e, 0x92e, 0x82e, 0x72e, 0x62e, 0x52e, 0x42e, 0x32e, 0x22e, 0x12e]
 #   for value in values:
 #       print("system.feb.dac.dacBLRaw", hex(value) )
 #       system.feb.dac.dacBLRaw.set(value)
        #hists = makeSCurve( system, nCounts=2, thresholdCuts = thresholds, pixels=[ (i,i) for i in range(0,1) ], histFileName="scurve_test_sleep.root" )
#        hists = makeSCurve( system, nCounts=2, thresholdCuts = thresholds, pixels=[ (127,31) ], histFileName="scurve_test_sleep.root" )
#        np.savetxt("chess2_scan_test_trim15"+str(hex(value))+".csv", np.asarray(hists,dtype=np.float32),fmt = "%s", delimiter=",", header="system.feb.dac.dacBLRaw:,"+str(hex(value)))

    # Run gui
    appTop.exec_()

    # Stop mesh after gui exits
    system.stop()
    
    return hists

if __name__ == '__main__':
    c2_hists = gui(arg = sys.argv[1], configFile = sys.argv[2] )
   
