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
        # Define the command bit mask                                     
        cmd0x0  = (0x0 << 14)
        cmd0x1  = (0x1 << 14)
        cmd0x2  = (0x2 << 14)
        cmd0x3  = (0x3 << 14)
        cmd0x4  = (0x4 << 14)
        cmd0x5  = (0x5 << 14)
        cmd0x8  = (0x8 << 14)
        
        # Define the row and col bit size
        rowBitSize = 7
        colBitSize = 5
                
        # Define all the non-global registers (A.K.A commands)
        self.add(pr.Variable(name='WriteMatrix',description='Write Matrix',
            offset=(cmd0x4), bitSize=32, bitOffset=0, base='hex', mode='WO'))  

        self.add(pr.Variable(name='ReadWritePixel',description='Read/Write Pixel',
            offset=(cmd0x5), bitSize=32, bitOffset=0, base='hex', mode='RW'))              
                
        self.add(pr.Variable(name='StartMatrixConfig',description='START Matrix Configuration',
            offset=(cmd0x8), bitSize=1, bitOffset=0, base='bool', mode='WO'))     

        self.add(pr.Variable(name='EndMatrixConfig',description='END Matrix Configuration',
            offset=(cmd0x0), bitSize=1, bitOffset=0, base='bool', mode='RO'))                 
            
        self.add(pr.Variable(name='WriteAllCol',description='Write All Columns',
            offset=(cmd0x2), bitSize=colBitSize, bitOffset=0, base='hex', mode='WO'))      

        self.add(pr.Variable(name='WriteAllRow',description='Write All Rows',
            offset=(cmd0x3), bitSize=rowBitSize, bitOffset=0, base='hex', mode='WO'))      
        
        # Define all the global registers                                     
        self.add(pr.Variable(name='RowPointer',description='Row Pointer',
            offset=(cmd0x1|(4*0x1)), bitSize=rowBitSize, bitOffset=0, base='hex', mode='RW')) 
                                 
        self.add(pr.Variable(name='ColPointer', description='Column Pointer',
            offset=(cmd0x1|(4*0x3)), bitSize=colBitSize, bitOffset=0, base='hex', mode='RW'))  

        self.add(pr.Variable(name='VNLogicatt',description='VNLogicatt',
            offset=(cmd0x1|(4*0x5)), bitSize=5, bitOffset=0, base='hex', mode='RW'))  
                                 
        self.add(pr.Variable(name='VNLogicres',description='VNLogicres',
            offset=(cmd0x1|(4*0x5)), bitSize=2, bitOffset=5, base='hex', mode='RW'))  
                                 
        self.add(pr.Variable(name='VNSFatt',description='VNSFatt',
            offset=(cmd0x1|(4*0x5)), bitSize=5, bitOffset=7, base='hex', mode='RW')) 
                                 
        self.add(pr.Variable(name='VNSFres',description='VNSFres',
            offset=(cmd0x1|(4*0x5)), bitSize=2, bitOffset=12, base='hex', mode='RW'))                              

        self.add(pr.Variable(name='VNatt',description='VNatt',
            offset=(cmd0x1|(4*0x6)), bitSize=5, bitOffset=0, base='hex', mode='RW'))  
                                 
        self.add(pr.Variable(name='VNres',description='VNres',
            offset=(cmd0x1|(4*0x6)), bitSize=2, bitOffset=5, base='hex', mode='RW'))  
                                 
        self.add(pr.Variable(name='VPFBatt',description='VPFBatt',
            offset=(cmd0x1|(4*0x6)), bitSize=5, bitOffset=7, base='hex', mode='RW')) 
                                 
        self.add(pr.Variable(name='VPFBres',description='VPFBres',
            offset=(cmd0x1|(4*0x6)), bitSize=2, bitOffset=12, base='hex', mode='RW'))                              

        self.add(pr.Variable(name='VPLoadatt',description='VPLoadatt',
            offset=(cmd0x1|(4*0x7)), bitSize=5, bitOffset=0, base='hex', mode='RW'))  
                                 
        self.add(pr.Variable(name='VPLoadres',description='VPLoadres',
            offset=(cmd0x1|(4*0x7)), bitSize=2, bitOffset=5, base='hex', mode='RW'))  
                                 
        self.add(pr.Variable(name='VPTrimatt',description='VPTrimatt',
            offset=(cmd0x1|(4*0x7)), bitSize=5, bitOffset=7, base='hex', mode='RW')) 
                                 
        self.add(pr.Variable(name='VPTrimres',description='VPTrimres',
            offset=(cmd0x1|(4*0x7)), bitSize=2, bitOffset=12, base='hex', mode='RW'))                                

        self.add(pr.Variable(name='CLK_bit_sel',
            description="""
            Hit Encoding Clock Selection:
            0 - Clock include Matrix load delay
            1 - Clock does not includes Matrix Load delay                                         
            """,        
            offset=(cmd0x1|(4*0x8)), bitSize=1, bitOffset=0, base='hex', mode='RW'))  

        self.add(pr.Variable(name='clk_dly',description='Hit Encoding Delay respect Matrix Clock',
            offset=(cmd0x1|(4*0x8)), bitSize=4, bitOffset=1, base='hex', mode='RW'))   

        self.add(pr.Variable(name='DAC6',description='DAC6',
            offset=(cmd0x1|(4*0x8)), bitSize=1, bitOffset=5, base='hex', mode='RW'))  

        self.add(pr.Variable(name='DAC7',description='DAC7',
            offset=(cmd0x1|(4*0x8)), bitSize=6, bitOffset=6, base='hex', mode='RW'))                               

        self.add(pr.Variable(name='rd_1',description='Reset Distance',
            offset=(cmd0x1|(4*0x9)), bitSize=3, bitOffset=0, base='hex', mode='RW'))    

        self.add(pr.Variable(name='rlt_1',description='Reset Low Time',
            offset=(cmd0x1|(4*0x9)), bitSize=3, bitOffset=3, base='hex', mode='RW'))  

        self.add(pr.Variable(name='wrd_1',description='Reset Write Distance',
            offset=(cmd0x1|(4*0x9)), bitSize=3, bitOffset=6, base='hex', mode='RW'))  

        self.add(pr.Variable(name='DigiMux',description='Monitor Mux Selection bits',
            offset=(cmd0x1|(4*0x9)), bitSize=3, bitOffset=9, base='hex', mode='RW'))                               

        self.add(pr.Variable(name='wrd_2',description='Reset Write Distance',
            offset=(cmd0x1|(4*0xA)), bitSize=3, bitOffset=0, base='hex', mode='RW'))                                

        self.add(pr.Variable(name='rd_2',description='Reset Distance',
            offset=(cmd0x1|(4*0xA)), bitSize=3, bitOffset=3, base='hex', mode='RW'))  

        self.add(pr.Variable(name='rlt_2',description='Reset Low Time',
            offset=(cmd0x1|(4*0xA)), bitSize=3, bitOffset=6, base='hex', mode='RW'))   

        self.add(pr.Variable(name='DelEXEC',description='Exec Delay',
            offset=(cmd0x1|(4*0xA)), bitSize=1, bitOffset=9, base='hex', mode='RW'))  

        self.add(pr.Variable(name='DelCCKreg',description='CCKreg Delay',
            offset=(cmd0x1|(4*0xA)), bitSize=1, bitOffset=10, base='hex', mode='RW'))   

        self.add(pr.Variable(name='LVDS_TX_Current',description='Standard LVDS Current',
            offset=(cmd0x1|(4*0xA)), bitSize=1, bitOffset=11, base='hex', mode='RW'))     

        self.add(pr.Variable(name='LVDS_RX_AC_Mode',description='LVDS Receiver mode',
            offset=(cmd0x1|(4*0xA)), bitSize=1, bitOffset=12, base='hex', mode='RW'))    

        self.add(pr.Variable(name='LVDS_RX_100Ohm',description='DC LVDS Receiver input impedance - 100 Ohm',
            offset=(cmd0x1|(4*0xA)), bitSize=1, bitOffset=13, base='hex', mode='RW'))

        self.add(pr.Variable(name='LVDS_RX_300Ohm',description='DC LVDS Receiver input impedance - 300 Ohm',
            offset=(cmd0x1|(4*0xA)), bitSize=1, bitOffset=14, base='hex', mode='RW'))         

        self.add(pr.Variable(name='TM',description='Hit Encoding Test Mode',
            offset=(cmd0x1|(4*0xA)), bitSize=1, bitOffset=15, base='hex', mode='RW'))                                      
 