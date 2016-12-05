#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Title      : PyRogue _dac Module
#-----------------------------------------------------------------------------
# File       : _dac.py
# Author     : Larry Ruckman <ruckman@slac.stanford.edu>
# Created    : 2016-11-09
# Last update: 2016-11-09
#-----------------------------------------------------------------------------
# Description:
# PyRogue _dac Module
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

class dac(pr.Device):
    def __init__(self, name="dac", memBase=None, offset=0, hidden=False):
        super(self.__class__, self).__init__(name, "Configurations the DAC module",
                                             memBase, offset, hidden)
                                             
        self.add(pr.Variable(name='dacCASC',
                                 description='DAC CASC',
                                 hidden=False, enum=None, offset=0x00000, bitSize=12, bitOffset=0, base='hex', mode='RW'))

        self.add(pr.Variable(name='dacPIXTH',
                                 description='DAC PIXTH',
                                 hidden=False, enum=None, offset=0x00004, bitSize=12, bitOffset=0, base='hex', mode='RW'))   

        self.add(pr.Variable(name='dacBLR',
                                 description='DAC BLR',
                                 hidden=False, enum=None, offset=0x00008, bitSize=12, bitOffset=0, base='hex', mode='RW')) 

        self.add(pr.Variable(name='dacBL',
                                 description='DAC BL',
                                 hidden=False, enum=None, offset=0x0000C, bitSize=12, bitOffset=0, base='hex', mode='RW'))     

        self.add(pr.Variable(name='dacLvdsVCOM',
                                 description='DAC LVDS_VCOM',
                                 hidden=False, enum=None, offset=0x10000, bitSize=12, bitOffset=0, base='hex', mode='RW'))

        self.add(pr.Variable(name='dacLvdsVctrl',
                                 description='DAC LVDS_VCTRL',
                                 hidden=False, enum=None, offset=0x10004, bitSize=12, bitOffset=0, base='hex', mode='RW'))   

        self.add(pr.Variable(name='dacRefP',
                                 description='DAC REFP',
                                 hidden=False, enum=None, offset=0x10008, bitSize=12, bitOffset=0, base='hex', mode='RW'))

        self.add(pr.Variable(name='dacRefN',
                                 description='DAC REFN',
                                 hidden=False, enum=None, offset=0x1000C, bitSize=12, bitOffset=0, base='hex', mode='RW'))                                 
