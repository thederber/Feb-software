#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Title      : PyRogue AtlasChess2FebSysReg Module
#-----------------------------------------------------------------------------
# File       : AtlasChess2FebSysReg.py
# Author     : Larry Ruckman <ruckman@slac.stanford.edu>
# Created    : 2016-11-09
# Last update: 2016-11-09
#-----------------------------------------------------------------------------
# Description:
# PyRogue AtlasChess2FebSysReg Module
#-----------------------------------------------------------------------------
# This file is part of the ATLAS CHESS2 DEV. It is subject to 
# the license terms in the LICENSE.txt file found in the top-level directory 
# of this distribution and at: 
#    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html. 
# No part of the ATLAS CHESS2 DEV, including this file, may be 
# copied, modified, propagated, or distributed except according to the terms 
# contained in the LICENSE.txt file.
#-----------------------------------------------------------------------------
import pyrogue
import collections

def create(name='AtlasChess2FebSysReg', offset=0, memBase=None, hidden=False):

    dev.add(pyrogue.Variable(name='refLockedCnt',
                             description='Reference clock Locked Status Counter',
                             hidden=False, enum=None, offset=0x000, bitSize=32, bitOffset=0, base='uint', mode='RO'))                                         
                                         
    dev.add(pyrogue.Variable(name='refLocked',
                             description='Reference clock Locked Status',
                             hidden=False, enum=None, offset=0x100, bitSize=1, bitOffset=0, base='uint', mode='RO'))
                             
    dev.add(pyrogue.Variable(name='refClkFreq',
                             description='Reference clock frequency (units of Hz)',
                             hidden=False, enum=None, offset=0x1FC, bitSize=32, bitOffset=0, base='uint', mode='RO'))
                             
    dev.add(pyrogue.Variable(name='refSelect',
                             description='0x0 = local 40 MHz OSC, 0x1 = external 40 MHz reference',
                             hidden=False, enum=None, offset=0x800, bitSize=1, bitOffset=0, base='uint', mode='RW'))
                             
    dev.add(pyrogue.Variable(name='timingMode',
                             description='0x0 = LEMO Triggering, 0x1 = PGP Triggering, 0x2 = EVR Triggering',
                             hidden=False, enum=None, offset=0x804, bitSize=2, bitOffset=0, base='uint', mode='RW'))
                             
    dev.add(pyrogue.Variable(name='pllRst',
                             description='PLL reset',
                             hidden=False, enum=None, offset=0x808, bitSize=1, bitOffset=0, base='uint', mode='WO'))
                             
    dev.add(pyrogue.Variable(name='dlyRst',
                             description='Delay FIFOs reset',
                             hidden=False, enum=None, offset=0x80C, bitSize=1, bitOffset=0, base='uint', mode='WO'))
                             
    dev.add(pyrogue.Variable(name='dlyTiming',
                             description='ASIC timingpath delay FIFO configuration (units of 1/320MHz)',
                             hidden=False, enum=None, offset=0x810, bitSize=12, bitOffset=0, base='uint', mode='RW'))
                             
    dev.add(pyrogue.Variable(name='dlyChess',
                             description='ASIC datapath delay FIFO configuration (units of 1/320MHz)',
                             hidden=False, enum=None, offset=0x814, bitSize=12, bitOffset=0, base='uint', mode='RW'))                             
                             
    dev.add(pyrogue.Variable(name='destId',
                             description='ASIC packet header DEST ID',
                             hidden=False, enum=None, offset=0x818, bitSize=6, bitOffset=0, base='uint', mode='RW'))
                             
    dev.add(pyrogue.Variable(name='frameType',
                             description='ASIC packet header frame type',
                             hidden=False, enum=None, offset=0x81C, bitSize=32, bitOffset=0, base='uint', mode='RW'))

    dev.add(pyrogue.Variable(name='pktWordSize',
                             description='ASIC Packet Size (in units of 16-bits words)',
                             hidden=False, enum=None, offset=0x820, bitSize=8, bitOffset=0, base='uint', mode='RW'))                             
                                                    
    dev.add(pyrogue.Variable(name='rollOverEn',
                             description='RollOverEn',
                             hidden=False, enum=None, offset=0xf00, bitSize=1, bitOffset=0, base='uint', mode='RW'))

    dev.add(pyrogue.Variable(name='counterReset',
                             description='CounterReset',
                             hidden=False, enum=None, offset=0xff4, bitSize=1, bitOffset=0, base='uint', mode='WO'))

    dev.add(pyrogue.Variable(name='softReset',
                             description='SoftReset',
                             hidden=False, enum=None, offset=0xff8, bitSize=1, bitOffset=0, base='uint', mode='WO'))

    dev.add(pyrogue.Variable(name='hardReset',
                             description='HardReset',
                             hidden=False, enum=None, offset=0xffc, bitSize=1, bitOffset=0, base='uint', mode='WO'))                                                               

    return dev
