#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Title      : PyRogue _idelay Module
#-----------------------------------------------------------------------------
# File       : _idelay.py
# Author     : Larry Ruckman <ruckman@slac.stanford.edu>
# Created    : 2016-11-09
# Last update: 2016-11-09
#-----------------------------------------------------------------------------
# Description:
# PyRogue _idelay Module
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

class idelay(pr.Device):
    def __init__(self, name="idelay", memBase=None, offset=0, hidden=False, expand=True):
        super(self.__class__, self).__init__(name, "Configurations the IDELAY modules",
                        memBase=memBase, offset=offset, hidden=hidden, expand=expand)

        for i in range(0,14):
            self.add(pr.Variable(name='idelay%01i'%(i),
                description='IDDR`s idelay[%01i]'%(i),
                hidden=False, enum=None, offset=(i*0x04), bitSize=5, bitOffset=0, base='hex', mode='RW'))
                                                                
        self.add(pr.Variable(name='phaseSel',
            description='IDDR`s phase select [13:0]',
            hidden=False, enum=None, offset=0x38, bitSize=14, bitOffset=0, base='hex', mode='RW'))
            
        self.add(pr.Variable(name='WriteAllIdelay',
            description='IDDR`s phase select [13:0]',
            hidden=False, enum=None, offset=0x3C, bitSize=5, bitOffset=0, base='hex', mode='WO'))            
