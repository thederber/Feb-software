#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Title      : PyRogue _saci Module
#-----------------------------------------------------------------------------
# File       : _saci.py
# Author     : Larry Ruckman <ruckman@slac.stanford.edu>
# Created    : 2016-11-09
# Last update: 2016-11-09
#-----------------------------------------------------------------------------
# Description:
# PyRogue _saci Module
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

class saci(pr.Device):
    def __init__(self, name="saci", memBase=None, offset=0, hidden=False):
        super(self.__class__, self).__init__(name, "CHESS2 SACI Interface",
                                             memBase, offset, hidden)
                                             
        self.add(pr.Variable(name='RowPointer',
                                 description='Row Pointer',
                                 hidden=False, enum=None, offset=0x04, bitSize=5, bitOffset=0, base='hex', mode='RW')) 
                                 
        self.add(pr.Variable(name='ColPointer',
                                 description='Column Pointer',
                                 hidden=False, enum=None, offset=0x0C, bitSize=7, bitOffset=0, base='hex', mode='RW'))  

        self.add(pr.Variable(name='VNLogicatt',
                                 description='VNLogicatt',
                                 hidden=False, enum=None, offset=0x14, bitSize=5, bitOffset=0, base='hex', mode='RW'))  
                                 
        self.add(pr.Variable(name='VNLogicres',
                                 description='VNLogicres',
                                 hidden=False, enum=None, offset=0x14, bitSize=2, bitOffset=5, base='hex', mode='RW'))  
                                 
        self.add(pr.Variable(name='VNSFatt',
                                 description='VNSFatt',
                                 hidden=False, enum=None, offset=0x14, bitSize=5, bitOffset=7, base='hex', mode='RW')) 
                                 
        self.add(pr.Variable(name='VNSFres',
                                 description='VNSFres',
                                 hidden=False, enum=None, offset=0x14, bitSize=2, bitOffset=12, base='hex', mode='RW'))                              

        self.add(pr.Variable(name='VNatt',
                                 description='VNatt',
                                 hidden=False, enum=None, offset=0x18, bitSize=5, bitOffset=0, base='hex', mode='RW'))  
                                 
        self.add(pr.Variable(name='VNres',
                                 description='VNres',
                                 hidden=False, enum=None, offset=0x18, bitSize=2, bitOffset=5, base='hex', mode='RW'))  
                                 
        self.add(pr.Variable(name='VPFBatt',
                                 description='VPFBatt',
                                 hidden=False, enum=None, offset=0x18, bitSize=5, bitOffset=7, base='hex', mode='RW')) 
                                 
        self.add(pr.Variable(name='VPFBres',
                                 description='VPFBres',
                                 hidden=False, enum=None, offset=0x18, bitSize=2, bitOffset=12, base='hex', mode='RW'))                              

        self.add(pr.Variable(name='VPLoadatt',
                                 description='VPLoadatt',
                                 hidden=False, enum=None, offset=0x1C, bitSize=5, bitOffset=0, base='hex', mode='RW'))  
                                 
        self.add(pr.Variable(name='VPLoadres',
                                 description='VPLoadres',
                                 hidden=False, enum=None, offset=0x1C, bitSize=2, bitOffset=5, base='hex', mode='RW'))  
                                 
        self.add(pr.Variable(name='VPTrimatt',
                                 description='VPTrimatt',
                                 hidden=False, enum=None, offset=0x1C, bitSize=5, bitOffset=7, base='hex', mode='RW')) 
                                 
        self.add(pr.Variable(name='VPTrimres',
                                 description='VPTrimres',
                                 hidden=False, enum=None, offset=0x1C, bitSize=2, bitOffset=12, base='hex', mode='RW'))                                

        self.add(pr.Variable(name='CLK_bit_sel',
                                 description='CLK_bit_sel',
                                 hidden=False, enum=None, offset=0x20, bitSize=1, bitOffset=0, base='hex', mode='RW'))  

        self.add(pr.Variable(name='clk_dly',
                                 description='clk_dly',
                                 hidden=False, enum=None, offset=0x20, bitSize=4, bitOffset=1, base='hex', mode='RW'))   

        self.add(pr.Variable(name='DAC6',
                                 description='DAC6',
                                 hidden=False, enum=None, offset=0x20, bitSize=1, bitOffset=5, base='hex', mode='RW'))  

        self.add(pr.Variable(name='DAC7',
                                 description='DAC7',
                                 hidden=False, enum=None, offset=0x20, bitSize=6, bitOffset=6, base='hex', mode='RW'))                               

        self.add(pr.Variable(name='rd_1',
                                 description='rd_1',
                                 hidden=False, enum=None, offset=0x24, bitSize=3, bitOffset=0, base='hex', mode='RW'))    

        self.add(pr.Variable(name='rlt_1',
                                 description='rlt_1',
                                 hidden=False, enum=None, offset=0x24, bitSize=3, bitOffset=3, base='hex', mode='RW'))  

        self.add(pr.Variable(name='wrd_1',
                                 description='wrd_1',
                                 hidden=False, enum=None, offset=0x24, bitSize=3, bitOffset=6, base='hex', mode='RW'))  

        self.add(pr.Variable(name='DigiMux',
                                 description='DigiMux',
                                 hidden=False, enum=None, offset=0x24, bitSize=3, bitOffset=9, base='hex', mode='RW'))                               

        self.add(pr.Variable(name='wrd_2',
                                 description='wrd_2',
                                 hidden=False, enum=None, offset=0x28, bitSize=3, bitOffset=0, base='hex', mode='RW'))                                

        self.add(pr.Variable(name='rd_2',
                                 description='rd_2',
                                 hidden=False, enum=None, offset=0x28, bitSize=3, bitOffset=3, base='hex', mode='RW'))  

        self.add(pr.Variable(name='rlt_2',
                                 description='rlt_2',
                                 hidden=False, enum=None, offset=0x28, bitSize=3, bitOffset=6, base='hex', mode='RW'))   

        self.add(pr.Variable(name='DelEXEC',
                                 description='DelEXEC',
                                 hidden=False, enum=None, offset=0x28, bitSize=1, bitOffset=9, base='hex', mode='RW'))  

        self.add(pr.Variable(name='DelCCKreg',
                                 description='DelCCKreg',
                                 hidden=False, enum=None, offset=0x28, bitSize=1, bitOffset=10, base='hex', mode='RW'))   

        self.add(pr.Variable(name='LVDS_TX_Current',
                                 description='LVDS_TX_Current',
                                 hidden=False, enum=None, offset=0x28, bitSize=1, bitOffset=11, base='hex', mode='RW'))     

        self.add(pr.Variable(name='LVDS_RX_AC_Mode',
                                 description='LVDS_RX_AC_Mode',
                                 hidden=False, enum=None, offset=0x28, bitSize=1, bitOffset=12, base='hex', mode='RW'))    

        self.add(pr.Variable(name='LVDS_RX_InputImpedance_100',
                                 description='LVDS_RX_InputImpedance_100',
                                 hidden=False, enum=None, offset=0x28, bitSize=1, bitOffset=13, base='hex', mode='RW'))

        self.add(pr.Variable(name='LVDS_RX_InputImpedance_300',
                                 description='LVDS_RX_InputImpedance_300',
                                 hidden=False, enum=None, offset=0x28, bitSize=1, bitOffset=14, base='hex', mode='RW'))         

        self.add(pr.Variable(name='TM',
                                 description='TM',
                                 hidden=False, enum=None, offset=0x28, bitSize=1, bitOffset=15, base='hex', mode='RW'))                                      
                                 