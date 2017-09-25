##############################################################################
## This file is part of 'LCLS2 Common Carrier Core'.
## It is subject to the license terms in the LICENSE.txt file found in the 
## top-level directory of this distribution and at: 
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html. 
## No part of 'LCLS2 Common Carrier Core', including this file, 
## may be copied, modified, propagated, or distributed except according to 
## the terms contained in the LICENSE.txt file.
##############################################################################

##############################
# Get variables and procedures
##############################
source -quiet $::env(RUCKUS_DIR)/vivado_env_var.tcl
source -quiet $::env(RUCKUS_DIR)/vivado_proc.tcl

############################
## Open the synthesis design
############################
open_run synth_1

###############################
## Set the name of the ILA core
###############################
set ilaName u_ila_1

##################
## Create the core
##################
CreateDebugCore ${ilaName}

#######################
## Set the record depth
#######################
set_property C_DATA_DEPTH 2048 [get_debug_cores ${ilaName}]

#################################
## Set the clock for the ILA core
#################################
SetDebugCoreClk ${ilaName} {U_Core/U_Asic/U_ChargeInj/timingClk320MHz}

#######################
## Set the debug Probes
#######################

ConfigProbe ${ilaName} {U_Core/U_Asic/U_ChargeInj/hitDet[0][13:0]}
ConfigProbe ${ilaName} {U_Core/U_Asic/U_ChargeInj/hitDet[1][13:0]}
ConfigProbe ${ilaName} {U_Core/U_Asic/U_ChargeInj/hitDet[2][13:0]}
ConfigProbe ${ilaName} {U_Core/U_Asic/U_ChargeInj/hitDet[0][27:14]}
ConfigProbe ${ilaName} {U_Core/U_Asic/U_ChargeInj/hitDet[1][27:14]}
ConfigProbe ${ilaName} {U_Core/U_Asic/U_ChargeInj/hitDet[2][27:14]}
ConfigProbe ${ilaName} {U_Core/U_Asic/U_ChargeInj/hitDet[0][41:28]}
ConfigProbe ${ilaName} {U_Core/U_Asic/U_ChargeInj/hitDet[1][41:28]}
ConfigProbe ${ilaName} {U_Core/U_Asic/U_ChargeInj/hitDet[2][41:28]}
ConfigProbe ${ilaName} {U_Core/U_Asic/U_ChargeInj/dataValid[*]}
ConfigProbe ${ilaName} {U_Core/U_Asic/U_ChargeInj/timer[*]}
ConfigProbe ${ilaName} {U_Core/U_Asic/U_ChargeInj/hitDetIndex[*]}
ConfigProbe ${ilaName} {U_Core/U_Asic/U_Chess[0].U_Rx/chessDin[*]}
ConfigProbe ${ilaName} {U_Core/U_Asic/U_Chess[1].U_Rx/chessDin[*]}
ConfigProbe ${ilaName} {U_Core/U_Asic/U_Chess[2].U_Rx/chessDin[*]}


ConfigProbe ${ilaName} {U_Core/U_Asic/U_ChargeInj/calPulse}

##########################
## Write the port map file
##########################
WriteDebugProbes ${ilaName} ${PROJ_DIR}/images/debug_probes.ltx

