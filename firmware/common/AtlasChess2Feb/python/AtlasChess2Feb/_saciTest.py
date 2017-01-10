#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Title      : PyRogue _saciTest Module
#-----------------------------------------------------------------------------
# File       : _saciTest.py
# Author     : Larry Ruckman <ruckman@slac.stanford.edu>
# Created    : 2016-11-09
# Last update: 2016-11-09
#-----------------------------------------------------------------------------
# Description:
# PyRogue _saciTest Module
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

class saciTest(pr.Device):
    def __init__(self, name="saciTest", memBase=None, offset=0, hidden=False):
        super(self.__class__, self).__init__(name, "CHESS2 SACI Test structure Interface",
                                             memBase, offset, hidden)
        #################################################################################################
        # Using the atlas-chess2/firmware/submodules/surf/protocols/saci/rtl/AxiLiteSaciMaster.vhd module
        # AXI_Lite_Address[31:24] = Ignored
        # AXI_Lite_Address[23:22] = SACI Chip Select [1:0]
        # AXI_Lite_Address[21]    = Ignored
        # AXI_Lite_Address[20:14] = SACI command [6:0]
        # AXI_Lite_Address[13:2]  = SACI address [11:0]
        # AXI_Lite_Address[1:0]   = Ignored
        # AXI_Lite_Data[31:0]     = SACI data [31:0]
        #################################################################################################
        
        # Define the command bit mask                                     
        cmd0x1  = (0x1 << 14)                                             
                             
        # Define the row and col bit size
        rowBitSize = 7
        colBitSize = 5                             
                             
        # Define all the global registers                               
        self.add(pr.Variable(name='RowPointer',description='Row Pointer',
            offset=(cmd0x1|(4*0x1)), bitSize=rowBitSize, bitOffset=0, base='hex', mode='RW')) 
                                 
        self.add(pr.Variable(name='ColPointer',description='Column Pointer',
            offset=(cmd0x1|(4*0x3)), bitSize=colBitSize, bitOffset=0, base='hex', mode='RW'))  

        self.add(pr.Variable(name='Casc',description='Casc',
            offset=(cmd0x1|(4*0x5)), bitSize=10, bitOffset=0, base='hex', mode='RW'))  
                                 
        self.add(pr.Variable(name='ColMux',description='ColMux',
            offset=(cmd0x1|(4*0x5)), bitSize=5, bitOffset=10, base='hex', mode='RW'))  
                           
        self.add(pr.Variable(name='BL',description='BL',
            offset=(cmd0x1|(4*0x6)), bitSize=10, bitOffset=0, base='hex', mode='RW'))  
                                 
        self.add(pr.Variable(name='CascPD',description='CascPD',
            offset=(cmd0x1|(4*0x6)), bitSize=1, bitOffset=10, base='bool', mode='RW'))  
                                 
        self.add(pr.Variable(name='BLPD',description='BLPD',
            offset=(cmd0x1|(4*0x6)), bitSize=1, bitOffset=11, base='bool', mode='RW'))      
                                 
        self.add(pr.Variable(name='PixPD',description='PixPD',
            offset=(cmd0x1|(4*0x6)), bitSize=1, bitOffset=12, base='bool', mode='RW'))  
                                 
        self.add(pr.Variable(name='BLRPD',description='BLRPD',
            offset=(cmd0x1|(4*0x6)), bitSize=1, bitOffset=13, base='bool', mode='RW'))                               
                           
        self.add(pr.Variable(name='Pix',description='Pix',
            offset=(cmd0x1|(4*0x7)), bitSize=10, bitOffset=0, base='hex', mode='RW'))   
                           
        self.add(pr.Variable(name='BLR',description='BLR',
            offset=(cmd0x1|(4*0x8)), bitSize=10, bitOffset=0, base='hex', mode='RW'))                                
