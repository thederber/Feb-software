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

from System import System
from EventReader import EventReader
from ScanTest import ScanTest
from Hist_Plotter import Hist_Plotter
from Frame_data import *
from Hitmap_Plotter import Hitmap_Plotter
from ChessControl import ChessControl
np.set_printoptions(threshold=np.inf)

# Add data stream to file as channel 1 File writer
dataWriter = pyrogue.utilities.fileio.StreamWriter(name='dataWriter')
cmd = rogue.protocols.srp.Cmd()
# Create and Connect SRP to VC1 to send commands
srp = rogue.protocols.srp.SrpV3()

# Set base, make it visible for interactive mode
appTop = PyQt4.QtGui.QApplication(sys.argv)
guiTop = pyrogue.gui.GuiTop(group='PyRogueGui')
system = System(guiTop, cmd, dataWriter, srp)
chess_control = ChessControl()

def gui(ip = "192.168.2.101", configFile = "../config/defaultR2_test.yml" ):

    hists = []

    #################################################################
    # Check for PGP link
    if (ip == 'PGP'):
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
        #srp = rogue.protocols.srp.SrpV0()
        pyrogue.streamConnectBiDir(pgpVc1,srp)
        
        # Add data stream to file as channel 1
        pyrogue.streamConnect(pgpVc0,dataWriter.getChannel(0x1))

    else: # Else it's Ethernet based
        # Create the ETH interface @ IP Address = ip
        ethLink = pyrogue.protocols.UdpRssiPack(host=ip,port=8192,size=1400)    
    
        #connect commands to  VC0
        pyrogue.streamConnect(cmd, ethLink.application(0))
        # Create and Connect SRPv0 to AxiStream.tDest = 0x0
        pyrogue.streamConnectBiDir(srp,ethLink.application(0))

        # Add data stream to file as channel 1 to tDest = 0x1
        eventReader = EventReader()
        pyrogue.streamConnect(ethLink.application(1),eventReader)

        #old version in below 2 lines
        #fileReader = dataWriter.getChannel(0x1)
        #pyrogue.streamConnect(ethLink.application(1),dataWriter.getChannel(0x1))
    system.start(pollEn=True, pyroGroup=None, pyroHost=None)
    guiTop.addTree(system)
    guiTop.resize(800,1000)
    system.root.ReadConfig(configFile)
    print("Loading config file")

    """ Performs a test on a 1x8 block of pixels, swing th"""
    start = 720
    end = 900#0x7d0 = 2000
    step = 1#int((end-start)/nsteps)
    thresholds = range(start, end+1, step)
    ifbs = range(0,0x1F)
    baselines = range(start,end+1,step)
    #system.feb.dac.dacPIXTHRaw.set(0x3e8)

    #Setting new value based on ibf scans
    #system.feb.Chess2Ctrl1.VNLogicatt.set(22)
    
    #TODO check that pktWordSize is the nb of 64b frame received
    system.feb.sysReg.pktWordSize.set(255)
    system.feb.sysReg.timingMode.set(0x3) #reserved
    val_fields = ["VPFBatt","VNLogicatt","VNSFatt","VNatt","VPLoadatt","VPTrimatt"]
    val_ranges = [range(0,0x1F) for i in range(len(val_fields))]
    for val_ind in range(len(val_fields)):
        val_field = val_fields[val_ind]
        #disable all pixels
        print("Disable all pixels")
        chess_control.disable_all_pixels(system,all_matrices=True)
        #disable data stream
        system.feb.sysReg.timingMode.set(0x3) #reserved	

        scan_test = ScanTest()
        scan_test.set_matrix(1)
        scan_test.set_feb_field("Chess2Ctrl1")
        scan_test.set_val_field(val_field)
    	#--> scanning system.feb.Chess2Ctrl1.<val_field>
        scan_test.set_val_range(val_ranges[val_ind]) #range for VPFBatt
        
        #scan_test.set_shape((8,1)) #block of 8 rows by 1 column
        scan_test.set_shape((8,1))
        
        scan_test.set_topleft((112,31)) #128 rows,32 cols
        scan_test.set_ntrigs(5) #number of readout trigs separated by sleeptime
        scan_test.set_sleeptime(10) #ms
        scan_test.set_pulserStatus("OFF") #just to inform filename

        print("Enabling matrix 1")
        scan_test.enable_block(system,chess_control)
        #chess_control.enable_block(system,topleft=(112,31),shape=(8,1),which_matrix=1,all_matrices=False)
        #chess_control.enable_all_pixels(system,all_matrices=True)
        #time.sleep(1)



        scan_test.set_scan_type("threshold_scan")
        scan_test.set_thresholds(thresholds)
        scan_test.set_fixed_baseline(744)
        #scan_test.set_scan_type("baseline_scan")
        #scan_test.set_fixed_threshold(fixed_threshold)
        
        eventReader.hitmap_show()
        #scan through each val while keeping all other vals at config specs
        system.root.ReadConfig(configFile)
        print("Loading config file")
        scan_test.scan(system,eventReader,val_fields)
	
    # Run gui
    appTop.exec_()

    # Stop mesh after gui exits
    system.stop()
    
    return hists

if __name__ == '__main__':
    rogue.Logging.setFilter('pyrogue.SrpV3', rogue.Logging.Debug)
    if len(sys.argv) == 1:
        c2_hists = gui()
    elif len(sys.argv) == 3:
        #allow ip and configFile to be overwritten via commandline args
        c2_hists = gui(ip = sys.argv[1],configFile = sys.argv[2]) 
    else:
        raise("USAGE: python3 FebScriptTest_testing.py <board ip> <configFile>")
