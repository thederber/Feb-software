#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Title      : PyRogue feb Module
#-----------------------------------------------------------------------------
# File       : feb.py
# Author     : Larry Ruckman <ruckman@slac.stanford.edu>
# Created    : 2016-11-09
# Last update: 2016-11-09
#-----------------------------------------------------------------------------
# Description:
# PyRogue feb Module
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

import surf
import surf.AxiVersion
import surf.AxiXadc
import surf.AxiMicronN25Q

import AtlasChess2Feb
import AtlasChess2Feb.SysReg
import AtlasChess2Feb.Dac
import AtlasChess2Feb.AsicRxReg
import AtlasChess2Feb.Saci
import AtlasChess2Feb.SaciTest

def create(name='feb', offset=0, memBase=None, hidden=False):

    dev = pyrogue.Device(name=name,memBase=memBase,offset=offset,
                         hidden=hidden,size=0x02000000,
                         description='feb')

    dev.add(surf.AxiVersion.create(      offset=0x00000000))
    dev.add(surf.AxiXadc.create(         offset=0x00010000))
    dev.add(surf.AxiMicronN25Q.create(   offset=0x00020000))
    dev.add(AtlasChess2Feb.SysReg.create(offset=0x00030000))   
    dev.add(AtlasChess2Feb.Dac.create(   offset=0x00100000))
    dev.add(surf.Pgp2bAxi(               offset=0x00200000))
    
    for i in range(0,3):
        dev.add(AtlasChess2Feb.AsicRxReg.create( 
            name='AtlasChess2Feb.AsicRxReg_%01i'%(i),
            offset=(0x00300000 + i*0x10000)))
    # # for i in range(0,2):
        # # dev.add(AtlasChess2Feb.Saci.create( 
            # # name='AtlasChess2Feb.Saci_%01i'%(i),
            # # offset=(0x01000000 + i*0x400000)))            
    # dev.add(AtlasChess2Feb.SaciTest.create(     offset=0x01C00000))
                               
    return dev
