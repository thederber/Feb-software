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
                                             
        def addPair(name, description, offset):
            """Add a Raw ADC register variable and corresponding converted value Variable"""
            self.add(pr.Variable(name=name+"Raw", offset=offset, bitSize=12, bitOffset=0,
                                 base='hex', mode='RW', description=description))
            
            self.add(pr.Variable(name=name, mode = 'RO', base='string',
                                 getFunction=dac.convtFloat, dependencies=[self.variables[name+"Raw"]]))

        addPair(name='dacCASC',     description='DAC CASC',         offset=0x00000)
        addPair(name='dacPIXTH',    description='DAC PIXTH',        offset=0x00004)
        addPair(name='dacBLR',      description='DAC BLR',          offset=0x00008)
        addPair(name='dacBL',       description='DAC BL',           offset=0x0000C)
        addPair(name='dacLvdsVCOM', description='DAC LVDS_VCOM',    offset=0x10000)
        addPair(name='dacLvdsVctrl',description='DAC LVDS_VCTRL',   offset=0x10004)
        addPair(name='dacRefP',     description='DAC REFP',         offset=0x10008)
        addPair(name='dacRefN',     description='DAC REFN',         offset=0x1000C)        
                                
    @staticmethod
    def convtFloat(dev, var):
        value   = var.dependencies[0].get(read=False)
        fpValue = value*(3.3/4096.0)
        return '%0.3f V'%(fpValue)            