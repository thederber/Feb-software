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

##############################
# Set base
##############################
#class System(pyrogue.Root):
#   def __init__(self, guiTop, cmd, dataWriter, srp, **kwargs):
#       super().__init__(name='System',description='Front End Board', **kwargs)
#       self.add(dataWriter)
#       self.guiTop = guiTop

#       @self.command()
#       def Trigger():
#           #cmd.sendCmd(0, 0)
#           self._root.feb.sysReg.softTrig()

#       # Add registers
#       self.add(AtlasChess2Feb.feb(memBase=srp))

#       # Add run control
#       self.add(pyrogue.RunControl(name = 'runControl', description='Run Controller Chess 2', cmd=self.Trigger, rates={1:'1 Hz', 2:'2 Hz', 4:'4 Hz', 8:'8 Hz', 10:'10 Hz', 30:'30 Hz', 60:'60 Hz', 120:'120 Hz'}))


#class EventReader(rogue.interfaces.stream.Slave):
#   def __init__(self):
#       rogue.interfaces.stream.Slave.__init__(self)
#       self.plotter = Hitmap_Plotter()
#       self.counter = 0
#       self.ev_hitmap_t0 = np.zeros((128,32))
#       self.ev_hitmap_t1 = np.zeros((128,32))
#       self.ev_hitmap_t2 = np.zeros((128,32))

#   def _acceptFrame(self,frame):
#       p = bytearray(frame.getPayload())
#       frame.read(p,0)
#       f = Frame_data(p)
#       f.decode_frame()
#       self.hitmap_update(f)
#       self.counter += 1
#       print(self.counter)

#   def hitmap_update(self,frame_data):
#       self.ev_hitmap_t0 += frame_data.hitmap_t0
#       self.ev_hitmap_t1 += frame_data.hitmap_t1
#       self.ev_hitmap_t2 += frame_data.hitmap_t2

#   def hitmap_show(self):
#       self.plotter.show()

#   def hitmap_plot(self):
#       self.plotter.add_data(self.ev_hitmap_t0,
#                            self.ev_hitmap_t1,
#                            self.ev_hitmap_t2)
#       self.plotter.plot()

#   def hitmap_reset(self):
#       self.counter = 0
#       self.ev_hitmap_t0 = np.zeros((128,32))
#       self.ev_hitmap_t1 = np.zeros((128,32))
#       self.ev_hitmap_t2 = np.zeros((128,32))
#
#   def hitmap_print(self):
#       msg = str("Hitmap 0 (self.hitmap_t0):"+str(self.ev_hitmap_t0)+"\n")
#       msg += str("Hitmap 1 (self.hitmap_t1):"+str(self.ev_hitmap_t1)+"\n")
#       msg += str("Hitmap 2 (self.hitmap_t2):"+str(self.ev_hitmap_t2)+"\n")
#       print(msg)

    

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

def gui(arg = "192.168.2.101", configFile = "../config/defaultR2_test.yml" ):

    hists = []

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
        #fileReader = dataWriter.getChannel(0x1)
        eventReader = EventReader()
        pyrogue.streamConnect(ethLink.application(1),eventReader)

        #pyrogue.streamConnect(ethLink.application(1),dataWriter.getChannel(0x1))
    #################################################################
             
    today=datetime.date.today()
    today1=today.strftime('%m%d%Y')

    system.start(pollEn=True, pyroGroup=None, pyroHost=None)
    guiTop.addTree(system)
    guiTop.resize(800,1000)
    system.root.ReadConfig(configFile)
    print("Loading config file")

    """ Performs a test on a 1x8 block of pixels, swing th"""
    start = 0x0
    #end = 0x500
    end = 0x7d0
    step = 8#int((end-start)/nsteps)
    thresholds = range(start, end+1, step)
    ifbs = range(0,0x1F)   
    baselines = range(start,end+1,step)
    system.feb.dac.dacPIXTHRaw.set(0x3e8)

    #Setting new value based on ibf scans
    system.feb.Chess2Ctrl1.VNLogicatt.set(22)
    
    print("Disable all pixels")
    chess_control.disable_all_pixels(system,all_matrices=True)
    eventReader.hitmap_show()

    #print("\nSwing Th vs BL\n")
    #data_path = "../data/."

    #TODO check that pktWordSize is the nb of 64b fram received
    system.feb.sysReg.pktWordSize.set(60)
    system.feb.sysReg.timingMode.set(0x3)
    test_topleft = (112,31)
    chess_control.toggle_block_1x8(system,topleft=test_topleft,enable=1,which_matrix=1,all_matrices=False)

    #scan_test = ScanTest(matrix=1,feb_field="Chess2Ctrl1",val_field="VPFBatt")
    #scan_test.set_val_range(range(0,0x1F))
    #scan_test.set_shape((1,8))
    #scan_test.set_topleft((112,31))
    #scan_test.set_scan_type("threshold_scan")
    #scan_test.set_thresholds(thresholds)
    ##scan_test.set_scan_type("baseline_scan")
    ##scan_test.set_fixed_threshold(fixed_threshold)
    
    #scan_test.scan(system,eventReader)
    
    for ifb in ifbs:
        system.feb.Chess2Ctrl1.VPFBatt.set(ifb)
        hist_fig = Hist_Plotter((1,8),thresholds)
        hist_fig.show()
        for th in thresholds:
        #for bl in baselines:
            #print("Threshold: ",th)
            system.feb.dac.dacPIXTHRaw.set(th)
            #system.feb.dac.dacBLRaw.set(bl)
            #system.feb.dac.dacBLRRaw.set(bl+144)
            eventReader.hitmap_reset()
            system.feb.sysReg.timingMode.set(0x0)
            time.sleep(.05)
            system.feb.sysReg.timingMode.set(0x3)
            eventReader.hitmap_plot()
            hist_fig.add_data(eventReader.plotter.data1[test_topleft[0]:test_topleft[0]+8,test_topleft[1]][np.newaxis])
            hist_fig.plot()
        hist_fig.fig.savefig("/home/herve/Desktop/Chess2Data/ifbs_scan_"+str(ifb)+".png")
        hist_fig.close()
        del hist_fig

    # Run gui
    appTop.exec_()

    # Stop mesh after gui exits
    system.stop()
    
    return hists

if __name__ == '__main__':
    rogue.Logging.setFilter('pyrogue.SrpV3', rogue.Logging.Debug)
    #c2_hists = gui(arg = sys.argv[1],configFile = sys.argv[2]) 
    c2_hists = gui()
   
