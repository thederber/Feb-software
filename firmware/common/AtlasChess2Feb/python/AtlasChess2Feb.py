#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Title      : PyRogue AtlasChess2Feb Module
#-----------------------------------------------------------------------------
# File       : AtlasChess2Feb.py
# Author     : Larry Ruckman <ruckman@slac.stanford.edu>
# Created    : 2016-11-09
# Last update: 2016-11-09
#-----------------------------------------------------------------------------
# Description:
# PyRogue AtlasChess2Feb Module
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
# import surf.AxiXadc
# import surf.AxiMicronN25Q
import AtlasChess2FebSysReg
# import surf.GenericMemory
# import AtlasChess2FebPwrMon
import AtlasChess2FebDac
# import surf.AxiPgp2bMon
# import AtlasChess2FebEvr
import AtlasChess2FebAsicRxReg
import AtlasChess2Saci
import AtlasChess2SaciTest

def create(name='AtlasChess2Feb', offset=0, memBase=None, hidden=False):

    dev = pyrogue.Device(name=name,memBase=memBase,offset=offset,
                         hidden=hidden,size=0x02000000,
                         description='AtlasChess2Feb')

    dev.add(surf.AxiVersion.create(         offset=0x00000000))
    # dev.add(surf.AxiXadc.create(          offset=0x00010000))
    # dev.add(surf.AxiMicronN25Q.create(    offset=0x00020000))
    dev.add(AtlasChess2FebSysReg.create(    offset=0x00030000))
    # dev.add(GenericMemory.create(         offset=0x00040000))
    # dev.add(AtlasChess2FebPwrMon.create(  offset=0x00050000))
    # dev.add(GenericMemory.create(         offset=0x00060000))
    dev.add(AtlasChess2FebDac.create(       offset=0x00100000))
    # dev.add(AxiPgp2bMon.create(           offset=0x00200000))
    # dev.add(AtlasChess2FebEvr.create(     offset=0x00210000))
    for i in range(0,2):
        dev.add(AtlasChess2FebAsicRxReg.create( 
            name='AtlasChess2FebAsicRxReg_%02i'%(i),
            offset=(0x00300000 + i*0x10000)))
    for i in range(0,2):
        dev.add(AtlasChess2Saci.create( 
            name='AtlasChess2Saci_%02i'%(i),
            offset=(0x01000000 + i*0x400000)))            
    dev.add(AtlasChess2SaciTest.create(     offset=0x01C00000))
                               
    return dev
