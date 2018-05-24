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
import rogue
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
import random
import copyreg
from SCurveNP import *
from AtlasChess2_testRoutines import *

#from csv_newplotter_h_8hit import *
MAKE_S_CURVE = True
MAKE_TIME_DELAY_CURVE = False
QUIET_BOARD=False
c2_hists = []


# Custom run control

#class MyRunControl(pyrogue.RunControl):
#   def __init__(self,name):
#      pyrogue.RunControl.__init__(self,name,'Run Controller')
#      self._thread = None
#
#      self.runRate.enum = {1:'1 Hz', 10:'10 Hz', 100:'100 Hz'}
#
#   def _setRunState(self,dev,var,value):
#      if self._runState != value:
#         self._runState = value
#
#         if self._runState == 'Running':
#            self._thread = threading.Thread(target=self._run)
#            self._thread.start()
#         else:
#            self._thread.join()
#            self._thread = None
#
#   def _run(self):
#      self._runCount = 0
#      self._last = int(time.time())
#
#
#      while (self._runState == 'Running'):
#         delay = 1.0 / ({value:key for key,value in self.runRate.enum.items()}[self._runRate])
#         time.sleep(delay)
#         self._root.feb.sysReg.softTrig()
#
#         self._runCount += 1
#         if self._last != int(time.time()):
#             self._last = int(time.time())
#             self.runCount._updated()
#
##############################
# Set base
##############################
class System(pyrogue.Root):
    def __init__(self, guiTop, cmd, dataWriter, srp, **kwargs):
        super().__init__(name='System',description='Front End Board', **kwargs)
        #self.add(MyRunControl('runControl'))
        self.add(dataWriter)
        self.guiTop = guiTop

        @self.command()
        def Trigger():
            #cmd.sendCmd(0, 0)
            self._root.feb.sysReg.softTrig()

        # Add registers
        self.add(AtlasChess2Feb.feb(memBase=srp))

        # Add run cotnrol
        self.add(pyrogue.RunControl(name = 'runControl', description='Run Controller Chess 2', cmd=self.Trigger, rates={1:'1 Hz', 2:'2 Hz', 4:'4 Hz', 8:'8 Hz', 10:'10 Hz', 30:'30 Hz', 60:'60 Hz', 120:'120 Hz'}))


# Add data stream to file as channel 1 File writer
dataWriter = pyrogue.utilities.fileio.StreamWriter(name='dataWriter')
cmd = rogue.protocols.srp.Cmd()
# Create and Connect SRP to VC1 to send commands
srp = rogue.protocols.srp.SrpV3()



# Set base, make it visible for interactive mode
appTop = PyQt4.QtGui.QApplication(sys.argv)
guiTop = pyrogue.gui.GuiTop(group='PyRogueGui')
system = System(guiTop, cmd, dataWriter, srp)


def gui(arg = "192.168.3.28", configFile = "default.yml" ):

    hists = []
    #logfile()
    # Set base
#    system = pyrogue.Root('System','Front End Board')

    # Run control
#    system.add(MyRunControl('runControl'))

    # File writer
#    dataWriter = pyrogue.utilities.fileio.StreamWriter('dataWriter')
#    system.add(dataWriter)

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
        #connect commands to  VC0
        pyrogue.streamConnect(cmd, pgpVc0)

        # Create and Connect SRPv0 to VC1
        ##srp = rogue.protocols.srp.SrpV0()
        pyrogue.streamConnectBiDir(pgpVc1,srp)
        
        # Add data stream to file as channel 1
        pyrogue.streamConnect(pgpVc0,dataWriter.getChannel(0x1))
    #################################################################
    # Else it's Ethernet based
    else:
        # Create the ETH interface @ IP Address = arg
        ethLink = pyrogue.protocols.UdpRssiPack(host=arg,port=8192,size=1400)    
    
        #connect commands to  VC0
        pyrogue.streamConnect(cmd, ethLink.application(0))
        # Create and Connect SRPv0 to AxiStream.tDest = 0x0
        ##srp = rogue.protocols.srp.SrpV0()  
        pyrogue.streamConnectBiDir(srp,ethLink.application(0))

        # Add data stream to file as channel 1 to tDest = 0x1
        pyrogue.streamConnect(ethLink.application(1),dataWriter.getChannel(0x1))
    #################################################################
             
    # Add registers
#    system.add(AtlasChess2Feb.feb(memBase=srp))
    
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

    today=datetime.date.today()
    today1=today.strftime('%m%d%Y')

    system.start(pollEn=True, pyroGroup=None, pyroHost=None)
    guiTop.addTree(system)
    guiTop.resize(800,1000)
    system.root.ReadConfig("/u1/home/hanyubo/atlas-chess2_b2/software/config/defaultR2_test.yml")
    print("Loading config file")
    
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
#    pixel_num=12
#    pixels=[]
#    for p_num in range(pixel_num): 
#        pixels_i=()
#        prow=random.randrange(0,127,1)
#        pcol=random.randrange(0,31,1)
#        pixels_i=(prow,pcol)
#        pixels.append(pixels_i)
#    print(pixels)
    if (MAKE_S_CURVE):
        simu=False
        run = 'test'  
        Qinj = [1,0]
        a1='01'
        reading_all_together=True
        #reading_all_together=False
        Dump_event=False
        real_time=1 # 0--turn off real-time figure 1: on 
        #a1='02'
        #set VNSF=0.026#muA
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
        BL_value=[0x2e8] #BL=0.6v
        #BL_value=[0x500] #1.009v
        #BL_value=[0x364,0x3a2,0x3e1,0x45d,0x500] #BL
        #BL_value=[0x45d,0x45d,0x45d,0x45d] #BL
        #BL_value=[0x8,0x136] #BL
        values = [6]
        #values = [6]#, 5, 4, 3, 2, 1, 0, 7, 8, 9]
        a=sys.argv[1]
        InvPulse=False
        #InvPulse=True #origin
        #PulseDelay=0x2bbf #35000ns
        #PulseDelay=0x257f #30000ns
        #PulseDelay=0x18ff #20000ns
        #PulseDelay=0xc7f #10000ns
        PulseDelay=0x0 #3.15ns
        #PulseDelay=0x9f #500ns
        #PulseDelay=0x3e7f #50000ns
        #PulseDelay=0x63ff #80000ns
        PulseWidth=0x12bf  #15000ns
        system.feb.chargeInj.pulseWidthRaw.set(PulseWidth)
        #system.feb.chargeInj.pulseDelayRaw.set(0xc7f) #10000ns`
        system.feb.chargeInj.pulseDelayRaw.set(PulseDelay)
        system.feb.chargeInj.invPulse.set(InvPulse) 
        print(a1)
        print("logging...")
        #save_name="/u1/atlas-chess2-Asic-tests/data/data_h/pre-ampdata-"+a1+"/chess2_scan_SCurveTest_03032018_board_"+str(sys.argv[1])+"_run_" +str(run)+"_BL_"+str(BL_value)+"_chargeInjectionEnbled_"+ str(chargeInjectionEnbled) + "_thN_"+str(hex(value))+"withbias12v_PXTHsweep_50000ns_eventd_0.9_samepixel(00)"
        logfile("/u1/atlas-chess2-Asic-tests/data/data_h/pre-ampdata-19/rawdata/chess2_scan_SCurveTest_"+today1+"_board_"+str(sys.argv[1])+"_run_" + str(run)+"_chargeInjectionEnbled_"+str(Qinj)+"_thN_"+str(values)+"_PulseDelay_"+str(PulseDelay)+"_rawdatacheck_nobias_hitmap.log")
        #logfile("/u1/atlas-chess2-Asic-tests/data/data_h/log/chess2_scan_SCurveTest_"+today1+"_board_"+str(sys.argv[1])+"_run_" + str(run)+"_chargeInjectionEnbled_"+str(Qinj)+"_thN_"+str(values)+"_PulseDelay_"+str(PulseDelay)+"_PXTHsweep.log")
        #logfile("preamp/log/chess2_scan_SCurveTest_07172017_run_" + str(run)+"_chargeInjectionEnbled_"+ str(Qinj[0])+str(Qinj[1]) + "_thN_"+str(hex(values))+".log")
        for value in values:
            logging.info('Running the test with Values='+str(value))
            for chargeInjectionEnbled in Qinj:
                logging.info("Using board: "+str(sys.argv[1]))
                #logging.info("Loading config file: "+str(sys.argv[2])) 
                deltaBLToBLR = value * 120 
                #deltaBLToBLR = 0xce5 
                #thresholds =range(0x302,0x303,0x1) #0.62
                #thresholds =range(0x3bb,0x4bb,0x1) #0.7-0.8
                #thresholds =range(0x364,0x3dd,0x3) #0.7-0.8
                #thresholds =range(0x2f5,0x2f6,0x1) #0.61
                #thresholds =range(0x3aa,0x3ab,0x1) #0.75
                #thresholds =range(0x364,0x370,0x2) #0.71
                #thresholds =range(0x3e1,0x3e2,0x1) #0.8
                #thresholds =range(0x45d,0x45e,0x1) #0.9
                #thresholds =range(0x4d9,0x4da,0x1) #1
                #thresholds =range(0x5d1,0x5d2,0x1) #1.2
                #thresholds =range(0x555,0x556,0x1) #1.1
                #thstr='0.96'
                # define test Variables
                #thresholds =range(0x0, 0x5d1, 0x5)
                #thresholds =range(0x3e1, 0x3ee, 0x1) #0.7
                #thresholds =range(0x31a, 0x324, 0x1) #0.64
                ####thresholds =range(0x3c6, 0x3f6, 0x1)
                thresholds =range(0x200, 0x600, 0x20)
                #thresholds =range(0x45d, 0x6c9, 0x20)
                #thresholds =range(0x3a0, 0x800, 0x10)
                #thresholds =range(0x48e, 0x555, 0x20)
                #thresholds =range(0x3a0, 0x555, 0x4)
                #thresholds =range(0x501, 0x506, 0x1) #detail scan on board #02
                #thresholds =range(0x45d, 0x49b, 0x2) #detail scan on board #02
                #thresholds =range(0x45e,0x45f,0x1) #at 0.9v
                #thresholds =range(0x364, 0x517, 0x3)
                #thresholds =range(0x3ab,0x3ae,0x1)  #first hitmap
                #thresholds =range(0x364,0x365,0x1)  #0.7v
                #thresholds =range(0x3e1,0x3e2,0x1)  #0.8v
                #thresholds =range(0x45d,0x45e,0x1)  #0.9v
                #thresholds =range(0x555,0x556,0x1)  #1.1v
                #thresholds = np.arange(0x45c, 0x4d9, 0x10)
                #thresholds = [0x6b2]  #BL
                #pixels=[(50,0),(50,8),(50,16),(50,31),(110,0),(110,8),(110,16),(110,31)]
                #pixels=[(110,31)]
                #pixels=[(21,21),(21,20),(20,21),(20,20)]
                #pixels=[(20,20),(19,19),(80,2),(61,3)]
                #pixels=[(64,16),(64,8),(64,24)]
                #pixels=[(127,24)]
                #pixels=[(1,20),(10,2),(11,5),(61,3),(61,6)]
                #pixels=[(40,2),(110,2),(25,15),(70,13),(111,17),(3,24),(50,23),(100,25),(2,31),(40,31),(85,31),(123,31)]
                
                pixels=[(62,19)]
                #pixels=[(108,20)] #(99,20),(95,21),(108,20)
                #pixels=[(70,20)]  #(20,11),(20,12),(20,14))
                #pixels=None
                #for ai in range(1,2,1):
                #    pixels=[ (row,col) for row in range(1,128,1) for col in range(ai,ai+1,1) ]
                #for pixel_num in range(18,19,1):
                #    for direct in [1]:
                #        if direct==0:
                #            pixels=[(row,col) for row in range(p1[0],p1[0]+pixel_num,1) for col in range(p1[1],p1[1]+1,1)]
                #            di='ve'
                #        if direct==1:
                #            pixels=[(row,col) for row in range(p1[0],p1[0]+1,1) for col in range(p1[1],p1[1]+pixel_num,1)]
                #            di='ho'
                if 1:
                    #if pixels!=None:
                    #    print("    Testing Pixel: "+str(pixels))
                        #logging.info("    Testing Pixel: "+str(pixels))
                        #logging.info("    Testing Pixel "+str(pixels))
                    #else:
                    #    logging.info("    Testing all Pixels! ")
                    #for pixel_i in pixels:
                    if 1:
                       # pixel_j=[(pixel_i[0],pixel_i[1])]
                       # print("testing on pixel: "+str(pixel_i))
                        for BL_value_i in BL_value:
                            hists = makeCalibCurve4( system, nCounts=100, thresholdCuts = thresholds, pixels=pixels, histFileName="scurve_test_sleep.root", deltaBLToBLR = deltaBLToBLR, chargeInjectionEnbled = chargeInjectionEnbled, BL=BL_value_i,Reading_all_pixel_together=reading_all_together,mode=real_time)
                            #hists = makeCalibCurve4( system, nCounts=50, thresholdCuts = thresholds, pixels=pixels, histFileName="scurve_test_sleep.root", deltaBLToBLR = deltaBLToBLR, chargeInjectionEnbled = chargeInjectionEnbled, BL=BL_value_i,Reading_all_pixel_together=reading_all_together,Dump_event=Dump_event)
                                
                           #thresholdHexList = np.arange(0x800, 0x500, -2) # for the file 'chess2_scan_QinjPulse_BLx_SCurveTest_trim7' 
                           #hists = makeSCurve( system, nCounts=10, thresholdCut=thresholds, pixels=pixels, histFileName="scurve_test_sleep.root")
                           #hists1=np.asarray(hists)
                           #print(hists1.shape)
                           #print(hists1)
                           # create file header
                            #headerText = "\n# Test that perform the BL and BLR voltage sweep. BLR is set as BL plus a delta voltage. (Note: ASIC V1.8a set to 1.8V again). Running with default ASIC values"
                            headerText = "\n# raw data of tests"
                            headerText = headerText + "\n# pixels, " + str(pixels)
                            headerText = headerText + "\n# chargeInjectionEnbled, " + str(chargeInjectionEnbled)
                            headerText = headerText + "\n# deltaBLToBLR:," + str(deltaBLToBLR) 
                            headerText = headerText + "\n# system.feb.dac.dacBLRaw:," + str(system.feb.dac.dacBLRaw.get()) 
                            headerText = headerText + "\n# trim, " + str(7)
                            headerText = headerText + "\n# thresholds (raw):," + str(thresholds)
                            headerText = headerText + "\n# PulseDelay:"+str(PulseDelay)
                            headerText = headerText + "\n# PulseWidth:"+str(PulseWidth)
                            headerText = headerText + "\n# invPulse:"+str(InvPulse)

                            save_name="/u1/atlas-chess2-Asic-tests/data/data_h/pre-ampdata-"+a1+"/chess2_scan_SCurveTest_"+today1+"_board_"+str(sys.argv[1])+"_run_" +str(run)+"_BL_"+str(BL_value_i)+"_chargeInjectionEnbled_"+ str(chargeInjectionEnbled) + "_thN_"+str(hex(value))+"_Bias_-7_M1_1P_thscan"
                            #save_name="/u1/atlas-chess2-Asic-tests/data/data_h/pre-ampdata-"+a1+"/chess2_scan_SCurveTest_"+today1+"_board_"+str(sys.argv[1])+"_run_" +str(run)+"_BL_"+str(BL_value_i)+"_chargeInjectionEnbled_"+ str(chargeInjectionEnbled) + "_thN_"+str(hex(value))+"_Bias_-7_hitmap"

                            #save_name="/u1/atlas-chess2-Asic-tests/data/data_h/pre-ampdata-"+a1+"/chess2_scan_SCurveTest_"+today1+"_board_"+str(sys.argv[1])+"_run_" +str(run)+"_BL_"+str(BL_value_i)+"_chargeInjectionEnbled_"+ str(chargeInjectionEnbled) + "_thN_"+str(hex(value))+"withbias12_aroundtarget_2"
                            #save_name="/u1/atlas-chess2-Asic-tests/data/data_h/pre-ampdata-"+a1+"/chess2_scan_SCurveTest_"+today1+"_board_"+str(sys.argv[1])+"_run_" +str(run)+"_BL_"+str(BL_value_i)+"_chargeInjectionEnbled_"+ str(chargeInjectionEnbled) + "_thN_"+str(hex(value))+"_PulseDelay_"+str(PulseDelay)+"_PXTHsweep"
                        save_f_json(save_name,hists)
                        logging.info(headerText)
                        logging.info("The data has been saved in \n /u1/atlas-chess2-Asic-tests/data/data_h/pre-ampdata-"+a1+save_name+".json")
                        #plot(save_name+"csv",1)
                    
    
    if (QUIET_BOARD):
        system.feb.chargeInj.calPulseInh.set(1)
        print("Disable all pixels")
        trim=7
        system.feb.Chess2Ctrl0.writeAllPixels(enable= 0,chargeInj= 1,trimI= trim)
        system.feb.Chess2Ctrl1.writeAllPixels(enable= 0,chargeInj= 1,trimI= trim)
        system.feb.Chess2Ctrl2.writeAllPixels(enable= 0,chargeInj= 1,trimI= trim)
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
    rogue.Logging.setFilter('pyrogue.SrpV3', rogue.Logging.Debug)
    c2_hists = gui(arg = sys.argv[1],arg = sys.argv[2])
   
