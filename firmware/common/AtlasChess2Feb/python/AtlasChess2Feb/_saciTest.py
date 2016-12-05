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
                             
        self.add(pr.Variable(name='RowPointer',
                                 description='Row Pointer',
                                 hidden=False, enum=None, offset=0x04, bitSize=5, bitOffset=0, base='hex', mode='RW')) 
                                 
        self.add(pr.Variable(name='ColPointer',
                                 description='Column Pointer',
                                 hidden=False, enum=None, offset=0x0C, bitSize=7, bitOffset=0, base='hex', mode='RW'))  

        self.add(pr.Variable(name='Casc',
                                 description='Casc',
                                 hidden=False, enum=None, offset=0x14, bitSize=10, bitOffset=0, base='hex', mode='RW'))  
                                 
        self.add(pr.Variable(name='ColMux',
                                 description='ColMux',
                                 hidden=False, enum=None, offset=0x14, bitSize=5, bitOffset=10, base='hex', mode='RW'))  
                           
        self.add(pr.Variable(name='BL',
                                 description='BL',
                                 hidden=False, enum=None, offset=0x18, bitSize=10, bitOffset=0, base='hex', mode='RW'))  
                                 
        self.add(pr.Variable(name='CascPD',
                                 description='CascPD',
                                 hidden=False, enum=None, offset=0x18, bitSize=1, bitOffset=10, base='hex', mode='RW'))  
                                 
        self.add(pr.Variable(name='BLPD',
                                 description='BLPD',
                                 hidden=False, enum=None, offset=0x18, bitSize=1, bitOffset=11, base='hex', mode='RW'))      
                                 
        self.add(pr.Variable(name='PixPD',
                                 description='PixPD',
                                 hidden=False, enum=None, offset=0x18, bitSize=1, bitOffset=12, base='hex', mode='RW'))  
                                 
        self.add(pr.Variable(name='BLRPD',
                                 description='BLRPD',
                                 hidden=False, enum=None, offset=0x18, bitSize=1, bitOffset=13, base='hex', mode='RW'))                               
                           
        self.add(pr.Variable(name='Pix',
                                 description='Pix',
                                 hidden=False, enum=None, offset=0x1C, bitSize=10, bitOffset=0, base='hex', mode='RW'))   
                           
        self.add(pr.Variable(name='BLR',
                                 description='BLR',
                                 hidden=False, enum=None, offset=0x20, bitSize=10, bitOffset=0, base='hex', mode='RW'))                                
