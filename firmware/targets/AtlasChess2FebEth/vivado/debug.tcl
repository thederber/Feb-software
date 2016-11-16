##############################################################################
## This file is part of 'LCLS2 Common Carrier Core'.
## It is subject to the license terms in the LICENSE.txt file found in the 
## top-level directory of this distribution and at: 
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html. 
## No part of 'LCLS2 Common Carrier Core', including this file, 
## may be copied, modified, propagated, or distributed except according to 
## the terms contained in the LICENSE.txt file.
##############################################################################
set VIVADO_BUILD_DIR $::env(VIVADO_BUILD_DIR)
source -quiet ${VIVADO_BUILD_DIR}/vivado_env_var_v1.tcl
source -quiet ${VIVADO_BUILD_DIR}/vivado_proc_v1.tcl

## Open the run
open_run synth_1

## Setup configurations
set ilaName    u_ila_0

## Create the core
CreateDebugCore ${ilaName}

## Set the record depth
set_property C_DATA_DEPTH 1024 [get_debug_cores ${ilaName}]

## Set the clock for the Core

SetDebugCoreClk ${ilaName} {U_Core/U_SACI/axilClk}

## Set the Probes

ConfigProbe ${ilaName} {U_Core/U_SACI/r[chip][*]}
ConfigProbe ${ilaName} {U_Core/U_SACI/r[cmd][*]}
ConfigProbe ${ilaName} {U_Core/U_SACI/r[state][*]}
ConfigProbe ${ilaName} {U_Core/U_SACI/saciRsp[*]}
ConfigProbe ${ilaName} {U_Core/U_SACI/saciSelL[*]}

ConfigProbe ${ilaName} {U_Core/U_SACI/ack}
ConfigProbe ${ilaName} {U_Core/U_SACI/fail}
ConfigProbe ${ilaName} {U_Core/U_SACI/axilReadMaster[arvalid]}
ConfigProbe ${ilaName} {U_Core/U_SACI/axilReadMaster[rready]}
ConfigProbe ${ilaName} {U_Core/U_SACI/axilWriteMaster[awvalid]}
ConfigProbe ${ilaName} {U_Core/U_SACI/axilWriteMaster[bready]}
ConfigProbe ${ilaName} {U_Core/U_SACI/axilWriteMaster[wvalid]}
ConfigProbe ${ilaName} {U_Core/U_SACI/r[axilReadSlave][arready]}
ConfigProbe ${ilaName} {U_Core/U_SACI/r[axilReadSlave][rvalid]}
ConfigProbe ${ilaName} {U_Core/U_SACI/r[axilWriteSlave][awready]}
ConfigProbe ${ilaName} {U_Core/U_SACI/r[axilWriteSlave][bvalid]}
ConfigProbe ${ilaName} {U_Core/U_SACI/r[axilWriteSlave][wready]}
ConfigProbe ${ilaName} {U_Core/U_SACI/r[op]}
ConfigProbe ${ilaName} {U_Core/U_SACI/r[req]}
ConfigProbe ${ilaName} {U_Core/U_SACI/r[saciRst]}


## Delete the last unused port
delete_debug_port [get_debug_ports [GetCurrentProbe ${ilaName}]]

## Write the port map file
write_debug_probes -force ${PROJ_DIR}/images/debug_probes_${PRJ_VERSION}.ltx

