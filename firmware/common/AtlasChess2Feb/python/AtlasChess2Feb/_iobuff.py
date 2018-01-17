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

class iobuff(pr.Device):
    def __init__(self, name="iobuff", memBase=None, offset=0, hidden=False, expand=True):
        super(self.__class__, self).__init__(name, "Configure IO buffer tristate",
                        memBase=memBase, offset=offset, hidden=hidden, expand=expand)
                                             
        """Add a bit to every buffer"""
        self.add(pr.Variable(name="IOBuffer_Disable",            offset=offset, bitSize=31, bitOffset=0,  base='hex',  mode='RW', description=""))
        self.add(pr.Variable(name="IOBuffer_testClk_Disable",    offset=offset, bitSize=1,  bitOffset=0,  base='bool', mode='RW', description=""))
        self.add(pr.Variable(name="IOBuffer_dacEnL_Disable",     offset=offset, bitSize=1,  bitOffset=1,  base='bool', mode='RW', description=""))
        self.add(pr.Variable(name="IOBuffer_term100_Disable",    offset=offset, bitSize=1,  bitOffset=2,  base='bool', mode='RW', description=""))
        self.add(pr.Variable(name="IOBuffer_term300_Disable",    offset=offset, bitSize=1,  bitOffset=3,  base='bool', mode='RW', description=""))
        self.add(pr.Variable(name="IOBuffer_lvdsTxSel_Disable",  offset=offset, bitSize=1,  bitOffset=4,  base='bool', mode='RW', description=""))
        self.add(pr.Variable(name="IOBuffer_acMode_Disable",     offset=offset, bitSize=1,  bitOffset=5,  base='bool', mode='RW', description=""))
        self.add(pr.Variable(name="IOBuffer_bitSel_Disable",     offset=offset, bitSize=1,  bitOffset=6,  base='bool', mode='RW', description=""))
        #
        self.add(pr.Variable(name="IOBuffer_saciClk_Disable",    offset=offset, bitSize=1,  bitOffset=7,  base='bool', mode='RW', description=""))
        self.add(pr.Variable(name="IOBuffer_saciCmd_Disable",    offset=offset, bitSize=1,  bitOffset=8,  base='bool', mode='RW', description=""))
        self.add(pr.Variable(name="IOBuffer_saciRstL_Disable",   offset=offset, bitSize=1,  bitOffset=9,  base='bool', mode='RW', description=""))
        self.add(pr.Variable(name="IOBuffer_saciSelL_0_Disable", offset=offset, bitSize=1,  bitOffset=10, base='bool', mode='RW', description=""))
        self.add(pr.Variable(name="IOBuffer_saciSelL_1_Disable", offset=offset, bitSize=1,  bitOffset=11, base='bool', mode='RW', description=""))
        self.add(pr.Variable(name="IOBuffer_saciSelL_2_Disable", offset=offset, bitSize=1,  bitOffset=12, base='bool', mode='RW', description=""))
        self.add(pr.Variable(name="IOBuffer_saciSelL_3_Disable", offset=offset, bitSize=1,  bitOffset=13, base='bool', mode='RW', description=""))
