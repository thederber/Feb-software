#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Title      : PyRogue AtlasChess2FebDac Module
#-----------------------------------------------------------------------------
# File       : AtlasChess2FebDac.py
# Author     : Larry Ruckman <ruckman@slac.stanford.edu>
# Created    : 2016-11-09
# Last update: 2016-11-09
#-----------------------------------------------------------------------------
# Description:
# PyRogue AtlasChess2FebDac Module
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

def create(name='AtlasChess2FebDac', offset=0, memBase=None, hidden=False):

    dev = pyrogue.Device(name=name,memBase=memBase,offset=offset,
                         hidden=hidden,size=0x20000,
                         description='AtlasChess2FebDac')

    dev.add(pyrogue.Variable(name='dacCASC',
                             description='DAC CASC',
                             hidden=False, enum=None, offset=0x00000, bitSize=16, bitOffset=0, base='uint', mode='RW'))

    dev.add(pyrogue.Variable(name='dacPIXTH',
                             description='DAC PIXTH',
                             hidden=False, enum=None, offset=0x00004, bitSize=16, bitOffset=0, base='uint', mode='RW'))   

    dev.add(pyrogue.Variable(name='dacBLR',
                             description='DAC BLR',
                             hidden=False, enum=None, offset=0x00008, bitSize=16, bitOffset=0, base='uint', mode='RW')) 

    dev.add(pyrogue.Variable(name='dacBL',
                             description='DAC BL',
                             hidden=False, enum=None, offset=0x0000C, bitSize=16, bitOffset=0, base='uint', mode='RW'))     

    dev.add(pyrogue.Variable(name='dacLvdsVCOM',
                             description='DAC LVDS_VCOM',
                             hidden=False, enum=None, offset=0x10000, bitSize=16, bitOffset=0, base='uint', mode='RW'))

    dev.add(pyrogue.Variable(name='dacLvdsVctrl',
                             description='DAC LVDS_VCTRL',
                             hidden=False, enum=None, offset=0x10004, bitSize=16, bitOffset=0, base='uint', mode='RW'))   

    dev.add(pyrogue.Variable(name='dacRefP',
                             description='DAC REFP',
                             hidden=False, enum=None, offset=0x10008, bitSize=16, bitOffset=0, base='uint', mode='RW'))

    dev.add(pyrogue.Variable(name='dacRefN',
                             description='DAC REFN',
                             hidden=False, enum=None, offset=0x1000C, bitSize=16, bitOffset=0, base='uint', mode='RW'))                                 

    return dev
