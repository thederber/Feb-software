#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Title      : PyRogue AtlasChess2SaciTest Module
#-----------------------------------------------------------------------------
# File       : AtlasChess2SaciTest.py
# Author     : Larry Ruckman <ruckman@slac.stanford.edu>
# Created    : 2016-11-09
# Last update: 2016-11-09
#-----------------------------------------------------------------------------
# Description:
# PyRogue AtlasChess2SaciTest Module
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

def create(name='AtlasChess2SaciTest', offset=0, memBase=None, hidden=False):

    dev = pyrogue.Device(name=name,memBase=memBase,offset=offset,
                         hidden=hidden,size=0x40,
                         description='AtlasChess2SaciTest')
                         
    dev.add(pyrogue.Variable(name='RowPointer',
                             description='Row Pointer',
                             hidden=False, enum=None, offset=0x04, bitSize=5, bitOffset=0, base='uint', mode='RW')) 
                             
    dev.add(pyrogue.Variable(name='ColPointer',
                             description='Column Pointer',
                             hidden=False, enum=None, offset=0x0C, bitSize=7, bitOffset=0, base='uint', mode='RW'))  

    dev.add(pyrogue.Variable(name='Casc',
                             description='Casc',
                             hidden=False, enum=None, offset=0x14, bitSize=10, bitOffset=0, base='uint', mode='RW'))  
                             
    dev.add(pyrogue.Variable(name='ColMux',
                             description='ColMux',
                             hidden=False, enum=None, offset=0x14, bitSize=5, bitOffset=10, base='uint', mode='RW'))  
                       
    dev.add(pyrogue.Variable(name='BL',
                             description='BL',
                             hidden=False, enum=None, offset=0x18, bitSize=10, bitOffset=0, base='uint', mode='RW'))  
                             
    dev.add(pyrogue.Variable(name='CascPD',
                             description='CascPD',
                             hidden=False, enum=None, offset=0x18, bitSize=1, bitOffset=10, base='uint', mode='RW'))  
                             
    dev.add(pyrogue.Variable(name='BLPD',
                             description='BLPD',
                             hidden=False, enum=None, offset=0x18, bitSize=1, bitOffset=11, base='uint', mode='RW'))      
                             
    dev.add(pyrogue.Variable(name='PixPD',
                             description='PixPD',
                             hidden=False, enum=None, offset=0x18, bitSize=1, bitOffset=12, base='uint', mode='RW'))  
                             
    dev.add(pyrogue.Variable(name='BLRPD',
                             description='BLRPD',
                             hidden=False, enum=None, offset=0x18, bitSize=1, bitOffset=13, base='uint', mode='RW'))                               
                       
    dev.add(pyrogue.Variable(name='Pix',
                             description='Pix',
                             hidden=False, enum=None, offset=0x1C, bitSize=10, bitOffset=0, base='uint', mode='RW'))   
                       
    dev.add(pyrogue.Variable(name='BLR',
                             description='BLR',
                             hidden=False, enum=None, offset=0x20, bitSize=10, bitOffset=0, base='uint', mode='RW'))                                
    return dev
