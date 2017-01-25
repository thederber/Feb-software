#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Title      : PyRogue _chargeInj Module
#-----------------------------------------------------------------------------
# File       : _chargeInj.py
# Author     : Larry Ruckman <ruckman@slac.stanford.edu>
# Created    : 2016-11-17
# Last update: 2016-11-17
#-----------------------------------------------------------------------------
# Description:
# PyRogue _chargeInj Module
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

class chargeInj(pr.Device):
    def __init__(self, name="chargeInj", memBase=None, offset=0, hidden=False):
        super(self.__class__, self).__init__(name, "Charge Injection Module",
                                             memBase, offset, hidden)
        for i in range(3):
            self.add(pr.Variable(
                    name='hitDet%01i'%(i), description=' ',
                    offset=(4*i), bitSize=14, bitOffset=0, base='hex', mode='RO')) 
            self.add(pr.Variable(
                    name='hitTime%01i'%(i),description=' ',
                    offset=(4*i), bitSize=8, bitOffset=16, base='hex', mode='RO')) 
                
        self.add(pr.Variable(name = "calPulseVar", description = "Calibration Pulse",
                offset=0x10, bitSize=1, bitOffset=0, base='bool', mode='SL', hidden=True)) 
        self.add(pr.Command(name='calPulse',description='Calibration Pulse',base='None',
                function="""\
                        dev.calPulseVar.set(1)
                        """))       
                        
        self.add(pr.Variable(name='pulseWidth',description='pulse width minus one (in units of 4ns)',
                offset=0x14, bitSize=15, bitOffset=0, base='hex', mode='RW')) 

        self.add(pr.Variable(name='invPulse',description='Invert the pulse',
                offset=0x18, bitSize=1, bitOffset=0, base='bool', mode='RW'))                 
                