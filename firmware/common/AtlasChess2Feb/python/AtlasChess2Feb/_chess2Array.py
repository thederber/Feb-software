#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Title      : PyRogue _chess2Array Module
#-----------------------------------------------------------------------------
# File       : _chess2Array.py
# Author     : Larry Ruckman <ruckman@slac.stanford.edu>
# Created    : 2016-11-09
# Last update: 2016-11-09
#-----------------------------------------------------------------------------
# Description:
# PyRogue _chess2Array Module
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
                
class matrix(pr.Device):
    def __init__(self, name="matrix"):
        super(self.__class__, self).__init__(name, "CHESS2 Matrix Data",
                        memBase=None, hidden=True, expand=False)
        # Init the variables to all ones (Note: all config bits are active LOW)
        self._pixel     = [[0x3F for row in range(128)] for col in range(32)]
        
        # Create the PyRogue software variables
        for col in range(32):
            for row in range(128):
                # Common string
                pixel = 'col%02irow%03i'%(col,row)
                # Add the software variables
                self.add(pr.Variable(name=(pixel), 
                        description='Pixel Configuration',
                        base='hex', mode='RW',bitSize=6,
                        setFunction='dev._pixel[%d][%d] = value'%(col,row),
                        getFunction='value = dev._pixel[%d][%d]'%(col,row)))
                        
class Chess2Array(pr.Device):
    def __init__(self, name="Chess2Array", memBase=None, offset=0, hidden=False, expand=True, enabled=False):
        super(self.__class__, self).__init__(name, "CHESS2 Array Interface",
                        memBase=memBase, offset=offset, hidden=hidden, expand=expand, enabled=enabled)        
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
        
        # Create a warning message
        warningMessage="""
            The values should in principle enforce a functional front-end for CHESS2 
            and should not be modified without a consultation with the designers as 
            it could allow too much current to flow in the sensor and damage it.                                        
            """
                
        ######################################################
        # Define all the non-global registers (A.K.A commands)
        ######################################################
                        
        self.add(pr.Variable(name='StartMatrixConfig',description='START Matrix Configuration',
            offset=(cmd0x8), bitSize=32, bitOffset=0, base='bool', mode='WO', hidden=True))     

        self.add(pr.Variable(name='WritePixel',description='Write Pixel',
            offset=(cmd0x5), bitSize=6, bitOffset=0, base='hex', mode='WO', hidden=True))              
            
        self.add(pr.Variable(name='EndMatrixConfig',description='END Matrix Configuration',
            offset=(cmd0x0), bitSize=32, bitOffset=0, base='bool', mode='RO', hidden=True))                 
        
        #################################
        # Define all the global registers     
        #################################
        
        self.add(pr.Variable(name='RowPointer',description='Row Pointer',
            offset=(cmd0x1|(4*0x1)), bitSize=rowBitSize, bitOffset=0, base='hex', mode='RW')) 
                                 
        self.add(pr.Variable(name='ColPointer', description='Column Pointer',
            offset=(cmd0x1|(4*0x3)), bitSize=colBitSize, bitOffset=0, base='hex', mode='RW'))  

        self.add(pr.Variable(name='VNLogicatt', description=warningMessage,            
            offset=(cmd0x1|(4*0x5)), bitSize=5, bitOffset=0, base='hex', mode='RW'))  
                                 
        self.add(pr.Variable(name='VNLogicres', description=warningMessage,           
            offset=(cmd0x1|(4*0x5)), bitSize=2, bitOffset=5, base='hex', mode='RW'))  
                                 
        self.add(pr.Variable(name='VNSFatt', description=warningMessage,            
            offset=(cmd0x1|(4*0x5)), bitSize=5, bitOffset=7, base='hex', mode='RW')) 
                                 
        self.add(pr.Variable(name='VNSFres', description=warningMessage,        
            offset=(cmd0x1|(4*0x5)), bitSize=2, bitOffset=12, base='hex', mode='RW'))                              

        self.add(pr.Variable(name='VNatt', description=warningMessage,        
            offset=(cmd0x1|(4*0x6)), bitSize=5, bitOffset=0, base='hex', mode='RW'))  
                                 
        self.add(pr.Variable(name='VNres', description=warningMessage,   
            offset=(cmd0x1|(4*0x6)), bitSize=2, bitOffset=5, base='hex', mode='RW'))  
                                 
        self.add(pr.Variable(name='VPFBatt', description=warningMessage,   
            offset=(cmd0x1|(4*0x6)), bitSize=5, bitOffset=7, base='hex', mode='RW')) 
                                 
        self.add(pr.Variable(name='VPFBres', description=warningMessage, 
            offset=(cmd0x1|(4*0x6)), bitSize=2, bitOffset=12, base='hex', mode='RW'))                              

        self.add(pr.Variable(name='VPLoadatt', description=warningMessage,       
            offset=(cmd0x1|(4*0x7)), bitSize=5, bitOffset=0, base='hex', mode='RW'))  
                                 
        self.add(pr.Variable(name='VPLoadres', description=warningMessage, 
            offset=(cmd0x1|(4*0x7)), bitSize=2, bitOffset=5, base='hex', mode='RW'))  
                                 
        self.add(pr.Variable(name='VPTrimatt', description=warningMessage,         
            offset=(cmd0x1|(4*0x7)), bitSize=5, bitOffset=7, base='hex', mode='RW')) 
                                 
        self.add(pr.Variable(name='VPTrimres', description=warningMessage, 
            offset=(cmd0x1|(4*0x7)), bitSize=2, bitOffset=12, base='hex', mode='RW'))                                

        self.add(pr.Variable(name='CLK_bit_sel',description="""
            Hit Encoding Clock Selection:
            0 - Clock include Matrix load delay
            1 - Clock does not includes Matrix Load delay                                         
            """,        
            offset=(cmd0x1|(4*0x8)), bitSize=1, bitOffset=0, base='bool', mode='RW'))  

        self.add(pr.Variable(name='clk_dly',description='Hit Encoding Delay respect Matrix Clock',
            offset=(cmd0x1|(4*0x8)), bitSize=4, bitOffset=1, base='hex', mode='RW'))   

        self.add(pr.Variable(name='rd_1',description='Reset Distance',
            offset=(cmd0x1|(4*0x9)), bitSize=3, bitOffset=0, base='hex', mode='RW'))    

        self.add(pr.Variable(name='rlt_1',description='Reset Low Time',
            offset=(cmd0x1|(4*0x9)), bitSize=3, bitOffset=3, base='hex', mode='RW'))  

        self.add(pr.Variable(name='wrd_1',description='Reset Write Distance',
            offset=(cmd0x1|(4*0x9)), bitSize=3, bitOffset=6, base='hex', mode='RW'))  

        self.add(pr.Variable(name='DigiMux',description="""
            Multiplexer Configuration for digital output monitoring:
            0b000 = 0x0 = reset1i
            0b001 = 0x1 = writeCLK1i
            0b010 = 0x2 = reset2i
            0b011 = 0x3 = writeCLK2i
            0b000 = 0x4 = wsi
            0b001 = 0x5 = CLKi_1_40MHzi
            0b010 = 0x6 = CLKi_2_40MHzi
            0b011 = 0x7 = gndd!
            """,             
            enum = {0:'reset1i',1:'writeCLK1i',2:'reset2i',3:'writeCLK2i',
                    4:'wsi',5:'CLKi_1_40MHzi',6:'CLKi_2_40MHzi',7:'gndd'},
            offset=(cmd0x1|(4*0x9)), bitSize=3, bitOffset=9, base='enum', mode='RW'))                               

        self.add(pr.Variable(name='wrd_2',description='Reset Write Distance',
            offset=(cmd0x1|(4*0xA)), bitSize=3, bitOffset=0, base='hex', mode='RW'))                                

        self.add(pr.Variable(name='rd_2',description='Reset Distance',
            offset=(cmd0x1|(4*0xA)), bitSize=3, bitOffset=3, base='hex', mode='RW'))  

        self.add(pr.Variable(name='rlt_2',description='Reset Low Time',
            offset=(cmd0x1|(4*0xA)), bitSize=3, bitOffset=6, base='hex', mode='RW'))   

        self.add(pr.Variable(name='DelEXEC',description='Exec Delay',
            offset=(cmd0x1|(4*0xA)), bitSize=1, bitOffset=9, base='bool', mode='RW'))  

        self.add(pr.Variable(name='DelCCKreg',description='CCKreg Delay',
            offset=(cmd0x1|(4*0xA)), bitSize=1, bitOffset=10, base='bool', mode='RW'))   

        self.add(pr.Variable(name='LVDS_TX_Current',description='Standard LVDS Current',
            offset=(cmd0x1|(4*0xA)), bitSize=1, bitOffset=11, base='bool', mode='RW'))     

        self.add(pr.Variable(name='LVDS_RX_AC_Mode',description='LVDS Receiver mode',
            offset=(cmd0x1|(4*0xA)), bitSize=1, bitOffset=12, base='bool', mode='RW'))    

        self.add(pr.Variable(name='LVDS_RX_100Ohm',description='DC LVDS Receiver input impedance - 100 Ohm',
            offset=(cmd0x1|(4*0xA)), bitSize=1, bitOffset=13, base='bool', mode='RW'))

        self.add(pr.Variable(name='LVDS_RX_300Ohm',description='DC LVDS Receiver input impedance - 300 Ohm',
            offset=(cmd0x1|(4*0xA)), bitSize=1, bitOffset=14, base='bool', mode='RW'))         

        self.add(pr.Variable(name='TM',description='Hit Encoding Test Mode',
            offset=(cmd0x1|(4*0xA)), bitSize=1, bitOffset=15, base='bool', mode='RW'))        
            
        ############################    
        # Add the software variables
        ############################    
        self.add(matrix())   

    @staticmethod
    def configPixel(enable, chargeInj, trimI):
        # Default value: disable pixel, no charge injection, all trim bits disabled
        value = 0x00
        # Check if pixel is enabled
        if enable:
            value |= 0x20
        # Check if enabling charge injection
        if chargeInj:
            value |= 0x01
        # Set the trim current source
        value |= ((trimI & 0xF) << 1)
        # Return the inverted value
        return((~value)&0x3F)
    
    def setDefaults(self):
        # print ('setDefaults(self=%s)' % (self))
        # Configure for 40 MHz timing
        self.CLK_bit_sel.set(0x0)
        self.clk_dly.set(0x0)
        self.rd_1.set(0x0)
        self.rlt_1.set(0x2)
        self.wrd_1.set(0x3)
        self.wrd_2.set(0x3)
        self.rd_2.set(0x0)
        self.rlt_2.set(0x2)    
    
    def writeAllPixels(self, enable, chargeInj, trimI=0):
        # print ('writeAllPixels(self=%s,enable=%d,chargeInj=%d,trimI=%d) = 0x%x' % (self,enable,chargeInj,trimI,value))
        # Configure for 40 MHz timing
        self.setDefaults()    
        value = self.configPixel(enable, chargeInj, trimI)
        self.StartMatrixConfig.post(0)
        for row in range(128): 
            for col in range(32):        
                self.ColPointer.post(col)       
                self.RowPointer.post(row)       
                self.WritePixel.post(value)
                # Update the software variable
                self.matrix._pixel[col][row] = value
        self.EndMatrixConfig.get()       
             
    def writePixel(self, row, col, enable, chargeInj, trimI=0):
        # print ('writePixel(self=%s,row=%d,col=%d,enable=%d,chargeInj=%d,trimI=%d) = 0x%X' % (self,row,col,enable,chargeInj,trimI,value))        
        value = self.configPixel(enable, chargeInj, trimI)
        self.StartMatrixConfig.post(0)
        self.RowPointer.post(row)
        self.ColPointer.post(col)
        self.WritePixel.post(value)
        self.matrix._pixel[col][row] = value
        self.EndMatrixConfig.get()
        
    def loadMatrix(self):
        print ('loadMatrix(self=%s)' % (self))
        # Configure for 40 MHz timing
        self.setDefaults()
        # Load the matrix with the software variables
        self.StartMatrixConfig.post(0)
        for row in range(128): 
            for col in range(32):        
                self.ColPointer.post(col)       
                self.RowPointer.post(row)      
                # Load the software variable
                self.WritePixel.post(self.matrix._pixel[col][row])
        self.EndMatrixConfig.get()
        
