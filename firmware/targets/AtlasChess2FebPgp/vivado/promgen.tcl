##############################################################################
## This file is part of 'ATLAS CHESS2 DEV'.
## It is subject to the license terms in the LICENSE.txt file found in the 
## top-level directory of this distribution and at: 
##    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html. 
## No part of 'ATLAS CHESS2 DEV', including this file, 
## may be copied, modified, propagated, or distributed except according to 
## the terms contained in the LICENSE.txt file.
##############################################################################
## Source the AMC Carrier Core's .TCL file
source $::env(PROJ_DIR)/../../common/AtlasChess2Feb/vivado/promgen.tcl

## Setup the .BIT file and user file configurations
set loadbit    "up ${APP_BIT} ${BIT_PATH}"
# set loaddata   "up ${APP_GZ}  ${DATA_PATH}"
