##############################################################################
## This file is part of 'ATLAS CHESS2 DEV'.
## It is subject to the license terms in the LICENSE.txt file found in the 
## top-level directory of this distribution and at: 
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html. 
## No part of 'ATLAS CHESS2 DEV', including this file, 
## may be copied, modified, propagated, or distributed except according to 
## the terms contained in the LICENSE.txt file.
##############################################################################

create_generated_clock -name axilClk         [get_pins {U_Core/Eth_Config.U_ETH/U_MMCM/MmcmGen.U_Mmcm/CLKOUT0}]
create_generated_clock -name axilClkDiv2     [get_pins {U_Core/Eth_Config.U_ETH/U_MMCM/MmcmGen.U_Mmcm/CLKOUT1}]
create_generated_clock -name refClk200MHz    [get_pins {U_Core/Eth_Config.U_ETH/U_MMCM/MmcmGen.U_Mmcm/CLKOUT2}] 
create_generated_clock -name dnaClk          [get_pins {U_Core/U_Sys/U_AxiVersion/GEN_DEVICE_DNA.DeviceDna_1/GEN_7SERIES.DeviceDna7Series_Inst/BUFR_Inst/O}]
create_generated_clock -name progClk         [get_pins {U_Core/U_Sys/U_AxiVersion/GEN_ICAP.Iprog_1/GEN_7SERIES.Iprog7Series_Inst/DIVCLK_GEN.BUFR_ICPAPE2/O}]  
create_generated_clock -name refClk156MHz    [get_pins {U_Core/Eth_Config.U_ETH/U_IBUFDS_GTE2/ODIV2}]  
create_generated_clock -name evrClk          [get_pins {U_Core/U_Timing/U_EVR/U_GTX/IBUFDS_GTE2_Inst/ODIV2}]  

create_generated_clock -name timingClk320MHz [get_pins {U_Core/U_Clk/U_MMCM/MmcmGen.U_Mmcm/CLKOUT0}] 
create_generated_clock -name timingClk40MHz  [get_pins {U_Core/U_Clk/U_MMCM/MmcmGen.U_Mmcm/CLKOUT1}] 

set_clock_groups -asynchronous -group [get_clocks {axilClk}] -group [get_clocks {dnaClk}]
set_clock_groups -asynchronous -group [get_clocks {axilClk}] -group [get_clocks {progClk}]
set_clock_groups -asynchronous -group [get_clocks {axilClk}] -group [get_clocks {refClk200MHz}]
set_clock_groups -asynchronous -group [get_clocks {axilClk}] -group [get_clocks {locClk40MHz}]
set_clock_groups -asynchronous -group [get_clocks {axilClk}] -group [get_clocks {extClk40MHz}]
set_clock_groups -asynchronous -group [get_clocks {axilClk}] -group [get_clocks {evrRecClk}]
set_clock_groups -asynchronous -group [get_clocks {axilClk}] -group [get_clocks {evrClk}]
set_clock_groups -asynchronous -group [get_clocks {axilClk}] -group [get_clocks {timingClk320MHz}]
set_clock_groups -asynchronous -group [get_clocks {axilClk}] -group [get_clocks {refClk156MHz}]

set_clock_groups -asynchronous -group [get_clocks {timingClk320MHz}] -group [get_clocks {evrRecClk}]

set_clock_groups -asynchronous -group [get_clocks {locClk40MHz}] -group [get_clocks {extClk40MHz}]

set_clock_groups -asynchronous -group [get_clocks {refClk200MHz}] -group [get_clocks {timingClk320MHz}]