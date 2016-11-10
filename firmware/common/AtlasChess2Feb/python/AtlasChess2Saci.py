#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Title      : PyRogue AtlasChess2Saci Module
#-----------------------------------------------------------------------------
# File       : AtlasChess2Saci.py
# Author     : Larry Ruckman <ruckman@slac.stanford.edu>
# Created    : 2016-11-09
# Last update: 2016-11-09
#-----------------------------------------------------------------------------
# Description:
# PyRogue AtlasChess2Saci Module
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

def create(name='AtlasChess2Saci', offset=0, memBase=None, hidden=False):

    dev = pyrogue.Device(name=name,memBase=memBase,offset=offset,
                         hidden=hidden,size=0x40,
                         description='AtlasChess2Saci')


    dev.add(pyrogue.Variable(name='RowPointer',
                             description='Row Pointer',
                             hidden=False, enum=None, offset=0x04, bitSize=5, bitOffset=0, base='uint', mode='RW')) 
                             
    dev.add(pyrogue.Variable(name='ColPointer',
                             description='Column Pointer',
                             hidden=False, enum=None, offset=0x0C, bitSize=7, bitOffset=0, base='uint', mode='RW'))  

    dev.add(pyrogue.Variable(name='VNLogicatt',
                             description='VNLogicatt',
                             hidden=False, enum=None, offset=0x14, bitSize=5, bitOffset=0, base='uint', mode='RW'))  
                             
    dev.add(pyrogue.Variable(name='VNLogicres',
                             description='VNLogicres',
                             hidden=False, enum=None, offset=0x14, bitSize=2, bitOffset=5, base='uint', mode='RW'))  
                             
    dev.add(pyrogue.Variable(name='VNSFatt',
                             description='VNSFatt',
                             hidden=False, enum=None, offset=0x14, bitSize=5, bitOffset=7, base='uint', mode='RW')) 
                             
    dev.add(pyrogue.Variable(name='VNSFres',
                             description='VNSFres',
                             hidden=False, enum=None, offset=0x14, bitSize=2, bitOffset=12, base='uint', mode='RW'))                              

    dev.add(pyrogue.Variable(name='VNatt',
                             description='VNatt',
                             hidden=False, enum=None, offset=0x18, bitSize=5, bitOffset=0, base='uint', mode='RW'))  
                             
    dev.add(pyrogue.Variable(name='VNres',
                             description='VNres',
                             hidden=False, enum=None, offset=0x18, bitSize=2, bitOffset=5, base='uint', mode='RW'))  
                             
    dev.add(pyrogue.Variable(name='VPFBatt',
                             description='VPFBatt',
                             hidden=False, enum=None, offset=0x18, bitSize=5, bitOffset=7, base='uint', mode='RW')) 
                             
    dev.add(pyrogue.Variable(name='VPFBres',
                             description='VPFBres',
                             hidden=False, enum=None, offset=0x18, bitSize=2, bitOffset=12, base='uint', mode='RW'))                              

    dev.add(pyrogue.Variable(name='VPLoadatt',
                             description='VPLoadatt',
                             hidden=False, enum=None, offset=0x1C, bitSize=5, bitOffset=0, base='uint', mode='RW'))  
                             
    dev.add(pyrogue.Variable(name='VPLoadres',
                             description='VPLoadres',
                             hidden=False, enum=None, offset=0x1C, bitSize=2, bitOffset=5, base='uint', mode='RW'))  
                             
    dev.add(pyrogue.Variable(name='VPTrimatt',
                             description='VPTrimatt',
                             hidden=False, enum=None, offset=0x1C, bitSize=5, bitOffset=7, base='uint', mode='RW')) 
                             
    dev.add(pyrogue.Variable(name='VPTrimres',
                             description='VPTrimres',
                             hidden=False, enum=None, offset=0x1C, bitSize=2, bitOffset=12, base='uint', mode='RW'))                                

    dev.add(pyrogue.Variable(name='CLK_bit_sel',
                             description='CLK_bit_sel',
                             hidden=False, enum=None, offset=0x20, bitSize=1, bitOffset=0, base='uint', mode='RW'))  

    dev.add(pyrogue.Variable(name='clk_dly',
                             description='clk_dly',
                             hidden=False, enum=None, offset=0x20, bitSize=4, bitOffset=1, base='uint', mode='RW'))   

    dev.add(pyrogue.Variable(name='DAC6',
                             description='DAC6',
                             hidden=False, enum=None, offset=0x20, bitSize=1, bitOffset=5, base='uint', mode='RW'))  

    dev.add(pyrogue.Variable(name='DAC7',
                             description='DAC7',
                             hidden=False, enum=None, offset=0x20, bitSize=6, bitOffset=6, base='uint', mode='RW'))                               

    dev.add(pyrogue.Variable(name='rd_1',
                             description='rd_1',
                             hidden=False, enum=None, offset=0x24, bitSize=3, bitOffset=0, base='uint', mode='RW'))    

    dev.add(pyrogue.Variable(name='rlt_1',
                             description='rlt_1',
                             hidden=False, enum=None, offset=0x24, bitSize=3, bitOffset=3, base='uint', mode='RW'))  

    dev.add(pyrogue.Variable(name='wrd_1',
                             description='wrd_1',
                             hidden=False, enum=None, offset=0x24, bitSize=3, bitOffset=6, base='uint', mode='RW'))  

    dev.add(pyrogue.Variable(name='DigiMux',
                             description='DigiMux',
                             hidden=False, enum=None, offset=0x24, bitSize=3, bitOffset=9, base='uint', mode='RW'))                               

    dev.add(pyrogue.Variable(name='wrd_2',
                             description='wrd_2',
                             hidden=False, enum=None, offset=0x28, bitSize=3, bitOffset=0, base='uint', mode='RW'))                                

    dev.add(pyrogue.Variable(name='rd_2',
                             description='rd_2',
                             hidden=False, enum=None, offset=0x28, bitSize=3, bitOffset=3, base='uint', mode='RW'))  

    dev.add(pyrogue.Variable(name='rlt_2',
                             description='rlt_2',
                             hidden=False, enum=None, offset=0x28, bitSize=3, bitOffset=6, base='uint', mode='RW'))   

    dev.add(pyrogue.Variable(name='DelEXEC',
                             description='DelEXEC',
                             hidden=False, enum=None, offset=0x28, bitSize=1, bitOffset=9, base='uint', mode='RW'))  

    dev.add(pyrogue.Variable(name='DelCCKreg',
                             description='DelCCKreg',
                             hidden=False, enum=None, offset=0x28, bitSize=1, bitOffset=10, base='uint', mode='RW'))   

    dev.add(pyrogue.Variable(name='LVDS_TX_Current',
                             description='LVDS_TX_Current',
                             hidden=False, enum=None, offset=0x28, bitSize=1, bitOffset=11, base='uint', mode='RW'))     

    dev.add(pyrogue.Variable(name='LVDS_RX_AC_Mode',
                             description='LVDS_RX_AC_Mode',
                             hidden=False, enum=None, offset=0x28, bitSize=1, bitOffset=12, base='uint', mode='RW'))    

    dev.add(pyrogue.Variable(name='LVDS_RX_InputImpedance_100',
                             description='LVDS_RX_InputImpedance_100',
                             hidden=False, enum=None, offset=0x28, bitSize=1, bitOffset=13, base='uint', mode='RW'))

    dev.add(pyrogue.Variable(name='LVDS_RX_InputImpedance_300',
                             description='LVDS_RX_InputImpedance_300',
                             hidden=False, enum=None, offset=0x28, bitSize=1, bitOffset=14, base='uint', mode='RW'))         

    dev.add(pyrogue.Variable(name='TM',
                             description='TM',
                             hidden=False, enum=None, offset=0x28, bitSize=1, bitOffset=15, base='uint', mode='RW'))                                      
                             
    return dev
