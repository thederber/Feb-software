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


#from SCurveNP import makeSCurve
from SCurveNP import *


c2_hists = []

# Custom run control
class MyRunControl(pyrogue.RunControl):
   def __init__(self,name):
      pyrogue.RunControl.__init__(self,name, description='Run Controller',  rates={1:'1 Hz', 2:'2 Hz', 4:'4 Hz', 8:'8 Hz', 10:'10 Hz', 25:'25 Hz', 50:'50 Hz', 100:'100 Hz'})
      self._thread = None

   def _setRunState(self,dev,var,value,changed):
      if changed: 
         if self.runState.get(read=False) == 'Running': 
            self._thread = threading.Thread(target=self._run) 
            self._thread.start() 
         else: 
            self._thread.join() 
            self._thread = None 

   def _run(self):
      self.runCount.set(0)
      self._last = int(time.time())

      while (self.runState.value() == 'Running'):
         delay = 1.0 / ({value: key for key,value in self.runRate.enum.items()}[self._runRate])
         time.sleep(delay)
         self._root.feb.sysReg.softTrig()

         self._runCount += 1
         if self._last != int(time.time()):
             self._last = int(time.time())
             self.runCount._updated()


##############################
# Set base
##############################
class System(pyrogue.Root):
    def __init__(self, guiTop, cmd, dataWriter, srp, **kwargs):
        super().__init__(name='System',description='Front End Board', **kwargs)
        self.add(dataWriter)
        self.guiTop = guiTop

        @self.command()
        def Trigger():
            #cmd.sendCmd(0, 0)
            self._root.feb.sysReg.softTrig()

        # Add registers
        self.add(AtlasChess2Feb.feb(memBase=srp))


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
    guiTop.addTree(system)
    guiTop.resize(800,1000)

    # Run gui
    appTop.exec_()

    # Stop mesh after gui exits
    system.stop()
    
    return hists

if __name__ == '__main__':
    rogue.Logging.setFilter('pyrogue.SrpV3', rogue.Logging.Debug)
    c2_hists = gui(sys.argv[1])
