#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Title      : PyRogue _sysreg Module
#-----------------------------------------------------------------------------
# File       : _sysreg.py
# Author     : Larry Ruckman <ruckman@slac.stanford.edu>
# Created    : 2016-11-09
# Last update: 2016-11-09
#-----------------------------------------------------------------------------
# Description:
# PyRogue _sysreg Module
#-----------------------------------------------------------------------------
# This file is part of the ATLAS CHESS2 DEV. It is subject to 
# the license terms in the LICENSE.txt file found in the top-level directory 
# of this distribution and at: 
#    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html. 
# No part of the ATLAS CHESS2 DEV, including this file, may be 
# copied, modified, propagated, or distributed except according to the terms 
# contained in the LICENSE.txt file.
#-----------------------------------------------------------------------------

import pyrogue as pr

class sysReg(pr.Device):
    def __init__(self, name="sysReg", memBase=None, offset=0, hidden=False):
        super(self.__class__, self).__init__(name, "System Register Module",
                                             memBase, offset, hidden)

        self.add(pr.Variable(name='refLockedCnt',description='Reference clock Locked Status Counter',
                offset=0x000, bitSize=32, bitOffset=0, base='hex', mode='RO'))                                         
                                             
        self.add(pr.Variable(name='refLocked',description='Reference clock Locked Status',
                offset=0x100, bitSize=1, bitOffset=0, base='bool', mode='RO'))
                                 
        self.add(pr.Variable(name='refClkFreq',description='Reference clock frequency (units of Hz)',
                offset=0x1FC, bitSize=32, bitOffset=0, base='uint', mode='RO'))
                                 
        self.add(pr.Variable(name='refSelect',description='0x0 = local 40 MHz OSC, 0x1 = external 40 MHz reference',                
                enum = {0:'LOCAL_40MHZ_OSC',1:'EXTERNAL_40MHZ_OSC'},
                offset=0x800, bitSize=1, bitOffset=0, base='enum', mode='RW'))                
                
        self.add(pr.Variable(name='timingMode',description='0x0 = LEMO Triggering, 0x1 = PGP Triggering, 0x2 = EVR Triggering',
                enum = {0:'TIMING_LEMO_TRIG_C',1:'TIMING_PGP_TRIG_C',2:'TIMING_SLAC_EVR_C',3:'TIMING_RESERVED'},
                offset=0x804, bitSize=2, bitOffset=0, base='enum', mode='RW'))
                                 
        self.add(pr.Variable(name='pllRst',description='PLL reset',
                offset=0x808, bitSize=1, bitOffset=0, base='bool', mode='WO'))
                                 
        self.add(pr.Variable(name='dlyRst',description='Delay FIFOs reset',
                offset=0x80C, bitSize=1, bitOffset=0, base='bool', mode='WO'))
                                 
        self.add(pr.Variable(name='dlyTiming',description='ASIC timingpath delay FIFO configuration (units of 1/320MHz)',
                offset=0x810, bitSize=12, bitOffset=0, base='hex', mode='RW'))
                                 
        self.add(pr.Variable(name='dlyChess',description='ASIC datapath delay FIFO configuration (units of 1/320MHz)',
                offset=0x814, bitSize=12, bitOffset=0, base='hex', mode='RW'))                             
                                 
        self.add(pr.Variable(name='destId',description='ASIC packet header DEST ID',
                offset=0x818, bitSize=6, bitOffset=0, base='hex', mode='RW'))
                                 
        self.add(pr.Variable(name='frameType',description='ASIC packet header frame type',
                offset=0x81C, bitSize=32, bitOffset=0, base='hex', mode='RW'))

        self.add(pr.Variable(name='pktWordSize',description='ASIC Packet Size (in units of 16-bits words)',
                offset=0x820, bitSize=8, bitOffset=0, base='hex', mode='RW'))                             
                                
        self.add(pr.Variable(name='chessClkOe',description='CHESS clock output enable',
                # enum = {0:'CLOCKS_DISABLED',1:'CLOCKS_ENABLED'},
                offset=0x824, bitSize=1, bitOffset=0, base='bool', mode='RW'))
                                
        self.add(pr.Variable(name='forceHardReset',description='ForceHardReset',
                offset=0x828, bitSize=1, bitOffset=0, base='bool', mode='RW'))                                
                                
        self.add(pr.Variable(name='rollOverEn',description='RollOverEn',
                offset=0xf00, bitSize=1, bitOffset=0, base='hex', mode='RW'))

        self.add(pr.Command(name='counterReset',description='CounterReset',
                            offset = 0xf10, bitSize = 1, bitOffset = 0, function=pr.Command.touch))                
                                 
        self.add(pr.Variable(name = "softTrigVar", description = "Software Trigger",
                offset=0xf14, bitSize=1, bitOffset=0, base='bool', mode='SL', hidden=True)) 
        self.add(pr.Command(name='softTrig',description='Software Trigger',base='None',
                function="""\
                        dev.softTrigVar.set(1)
                        """))                
                        
        self.add(pr.Variable(name='softReset',description='SoftReset',
                offset=0xff8, bitSize=1, bitOffset=0, base='bool', mode='SL', hidden=True))

        self.add(pr.Variable(name='hardReset',description='HardReset',
                offset=0xffc, bitSize=1, bitOffset=0, base='hex', mode='WO', hidden=False))                                                               