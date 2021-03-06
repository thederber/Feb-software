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
import pyrogue.utilities.prbs
import rogue.hardware.pgp
import rogue.hardware.data
import surf
import surf.axi
import surf.protocols.ssi
import AtlasChess2Feb
import threading
import signal
import atexit
import yaml
import time
import sys
import PyQt4.QtGui
import PyQt4.QtCore
import numpy as np
import argparse
import frameViewer as vi


#from SCurveNP import makeSCurve
from SCurveNP import *


START_VIEWER=True


c2_hists = []

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
            #self._root.feb.chargeInj.calPulseVar.set(1)
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

def gui(arg):
    
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
        pyrogue.streamConnectBiDir(pgpVc1,srp)
        
        # Add data stream to file as channel 1
        pyrogue.streamConnect(pgpVc0,dataWriter.getChannel(0x1))
    #################################################################
    # Else it's Ethernet based
    else:
        # Create the ETH interface @ IP Address = arg
        ethLink = pyrogue.protocols.UdpRssiPack(host=arg,port=8192,jumbo=1400)    

        #connect commands to  VC0
        pyrogue.streamConnect(cmd, ethLink.application(0))
    
        # Create and Connect SRPv3 to AxiStream.tDest = 0x0      
        pyrogue.streamConnectBiDir(srp,ethLink.application(0))

        # Add data stream to file as channel 1 to tDest = 0x1
        pyrogue.streamConnect(ethLink.application(1),dataWriter.getChannel(0x1))
    #################################################################
             
    
    
 
    # Create GUI
    system.start(pollEn=True, pyroGroup=None, pyroHost=None)
    #system.feb.memReg.chargInjStartEventReg.set(1)
   # system.feb.dac.dacPIXTHRaw.set(0x2ef)
   # system.feb.dac.dacBLRRaw.set(0x5b8)
   # system.feb.dac.dacBLRaw.set(0x2e8)
    guiTop.addTree(system)
    guiTop.resize(800,1000)
    system.root.ReadConfig("/u1/home/hanyubo/atlas-chess2_b2/software/config/defaultR2_test.yml")

    
    
          
    # enable the pixels 
    nRows=128
    nColumns=32
    pixels= None
    print("Disable all pixels")
    system.feb.Chess2Ctrl0.writeAllPixels(enable= 0,chargeInj= 1,trimI=7 )
    system.feb.Chess2Ctrl1.writeAllPixels(enable= 0,chargeInj= 1,trimI=7 )
    system.feb.Chess2Ctrl2.writeAllPixels(enable= 0,chargeInj= 1,trimI=7 )

    pixels = pixels if (pixels!=None) else [ (row,col) for row in range(10,nRows) for col in range(10,nColumns) ]
    print("Enable all pixels")
    for (row,col) in pixels:
        system.feb.Chess2Ctrl0.writePixel(enable=1, chargeInj=0, col=col, row=row, trimI= 7)
        system.feb.Chess2Ctrl1.writePixel(enable=1, chargeInj=0, col=col, row=row, trimI= 7)
        system.feb.Chess2Ctrl2.writePixel(enable=1, chargeInj=0, col=col, row=row, trimI= 7)
    print("finish configure the pixels")
 #   system.dataWriter.dataFile.set("test1.dat")
 #   system.dataWriter._setOpen(system.dataWriter,system.dataWriter.open,True,1)
    #system.runControl._setRunRate(system.runControl.runRate,'1 Hz',1)
    #system.runControl._setRunState(system.runControl.runState,'Running',1)
    if (START_VIEWER):
        viewer = vi.Window(system)
        viewer.eventReaderMonitoring.frameIndex = 0
        pyrogue.streamTap(ethLink.application(1), viewer.eventReaderMonitoring)
            
   # system.dataWriter._setBufferSize(system.dataWriter,system.dataWriter.bufferSize,10000)
   # system.dataWriter._setMaxFileSize(system.dataWriter,system.dataWriter.maxFileSize,100000)
   # while 1:
   #    if (system.dataWriter._getFrameCount(system.dataWriter,system.dataWriter._getFrameCount))>1000:
   #        system.feb.sysReg.timingMode.set(3)
   #        print("get 1000 frame")


    # Run gui
    appTop.exec_()

    # Stop mesh after gui exits
    system.stop()
    
    return hists

if __name__ == '__main__':
    rogue.Logging.setFilter('pyrogue.SrpV3', rogue.Logging.Debug)

    c2_hists = gui(sys.argv[1])
