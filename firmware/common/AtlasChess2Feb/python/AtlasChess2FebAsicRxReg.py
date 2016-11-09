#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Title      : PyRogue AtlasChess2FebAsicRxReg Module
#-----------------------------------------------------------------------------
# File       : AtlasChess2FebAsicRxReg.py
# Author     : Larry Ruckman <ruckman@slac.stanford.edu>
# Created    : 2016-11-09
# Last update: 2016-11-09
#-----------------------------------------------------------------------------
# Description:
# PyRogue AtlasChess2FebAsicRxReg Module
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

def create(name='AtlasChess2FebAsicRxReg', offset=0, memBase=None, hidden=False):

    dev.add(pyrogue.Variable(name='idelay0',
                             description='IDDR`s idelay[0]',
                             hidden=False, enum=None, offset=0x00, bitSize=5, bitOffset=0, base='uint', mode='RW'))
                             
    dev.add(pyrogue.Variable(name='idelay1',
                             description='IDDR`s idelay[1]',
                             hidden=False, enum=None, offset=0x04, bitSize=5, bitOffset=0, base='uint', mode='RW'))                             
                             
    dev.add(pyrogue.Variable(name='idelay2',
                             description='IDDR`s idelay[2]',
                             hidden=False, enum=None, offset=0x08, bitSize=5, bitOffset=0, base='uint', mode='RW'))
                             
    dev.add(pyrogue.Variable(name='idelay3',
                             description='IDDR`s idelay[3]',
                             hidden=False, enum=None, offset=0x0C, bitSize=5, bitOffset=0, base='uint', mode='RW'))    
                             
    dev.add(pyrogue.Variable(name='idelay4',
                             description='IDDR`s idelay[4]',
                             hidden=False, enum=None, offset=0x10, bitSize=5, bitOffset=0, base='uint', mode='RW'))
                             
    dev.add(pyrogue.Variable(name='idelay5',
                             description='IDDR`s idelay[5]',
                             hidden=False, enum=None, offset=0x14, bitSize=5, bitOffset=0, base='uint', mode='RW'))                             
                             
    dev.add(pyrogue.Variable(name='idelay6',
                             description='IDDR`s idelay[6]',
                             hidden=False, enum=None, offset=0x18, bitSize=5, bitOffset=0, base='uint', mode='RW'))
                             
    dev.add(pyrogue.Variable(name='idelay7',
                             description='IDDR`s idelay[7]',
                             hidden=False, enum=None, offset=0x1C, bitSize=5, bitOffset=0, base='uint', mode='RW'))                             
                                                          
    dev.add(pyrogue.Variable(name='idelay8',
                             description='IDDR`s idelay[8]',
                             hidden=False, enum=None, offset=0x20, bitSize=5, bitOffset=0, base='uint', mode='RW'))
                             
    dev.add(pyrogue.Variable(name='idelay9',
                             description='IDDR`s idelay[9]',
                             hidden=False, enum=None, offset=0x24, bitSize=5, bitOffset=0, base='uint', mode='RW'))                             
                             
    dev.add(pyrogue.Variable(name='idelay10',
                             description='IDDR`s idelay[10]',
                             hidden=False, enum=None, offset=0x28, bitSize=5, bitOffset=0, base='uint', mode='RW'))
                             
    dev.add(pyrogue.Variable(name='idelay11',
                             description='IDDR`s idelay[11]',
                             hidden=False, enum=None, offset=0x2C, bitSize=5, bitOffset=0, base='uint', mode='RW'))    
                             
    dev.add(pyrogue.Variable(name='idelay12',
                             description='IDDR`s idelay[12]',
                             hidden=False, enum=None, offset=0x30, bitSize=5, bitOffset=0, base='uint', mode='RW'))
                             
    dev.add(pyrogue.Variable(name='idelay13',
                             description='IDDR`s idelay[13]',
                             hidden=False, enum=None, offset=0x34, bitSize=5, bitOffset=0, base='uint', mode='RW'))                                  
                             
    dev.add(pyrogue.Variable(name='phaseSel',
                             description='IDDR`s phase select [13:0]',
                             hidden=False, enum=None, offset=0x38, bitSize=14, bitOffset=0, base='uint', mode='RW'))
    return dev
