#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Title      : PyRogue _sysreg Module
#-----------------------------------------------------------------------------
# File       : _sysreg.py
# Author     : Larry Ruckman <ruckman@slac.stanford.edu>
# Created    : 2016-11-09
# Last update: 2016-11-09
#-----------------------------------------------------------------------------
# Description:
# PyRogue _sysreg Module
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

class memReg(pr.Device):
    def __init__(self, name="memReg", memBase=None, offset=0, hidden=False, expand=True):
        super(self.__class__, self).__init__(name, "Memory Register Module",
                        memBase=memBase, offset=offset, hidden=hidden, expand=expand)

#        dev.add(pyrogue.Variable(name='ssiPrintf', description='Retrieve data printed on the microblaze',
#                             offset=0x00040004, bitSize=1024*4, bitOffset=0, base='string', mode='RO'))

        self.add(pr.Variable(name='chargInjStartEventReg',description='Write to this register to invoque a irq to start the test', offset=0x000, bitSize=32, bitOffset=0, base='hex', mode='RW'))                       
        self.add(pr.Variable(name='chargInjHeartBeatReg', description='Write to this register to invoque a irq to start the test', offset=0x004, bitSize=32, bitOffset=0, base='hex', mode='RO', pollInterval=1))                       
        self.add(pr.Variable(name='chargInjNumEventsReg', description='Write to this register to invoque a irq to start the test', offset=0x008, bitSize=32, bitOffset=0, base='hex', mode='RO', pollInterval=1))                       
        self.add(pr.Variable(name='initValueReg',         description='Dac value at the start of the test',                        offset=0x00C, bitSize=12, bitOffset=0, base='hex', mode='RW'))
        self.add(pr.Variable(name='endValueReg',          description='Dac value at the end of the test',                          offset=0x010, bitSize=12, bitOffset=0, base='hex', mode='RW'))
        self.add(pr.Variable(name='delayValueReg',        description='Delay values use to settle DAC before and after the test',  offset=0x014, bitSize=32, bitOffset=0, base='hex', mode='RW'))


        self.add(pr.Variable(name='ssiPrintf',description='Retrieve data printed on the microblaze', offset=0x100, bitSize=1024*4, bitOffset=0, base='string', mode='RO'))                                         
                                             
 
                                 

