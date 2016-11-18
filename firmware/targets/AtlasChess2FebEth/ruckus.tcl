# Load RUCKUS environment and library
source -quiet $::env(RUCKUS_DIR)/vivado_proc.tcl

# Load common and sub-module ruckus.tcl files
loadRuckusTcl $::env(PROJ_DIR)/../../submodules/surf
loadRuckusTcl $::env(PROJ_DIR)/../../common/AtlasChess2Feb

# Load local source Code
loadSource -dir  "$::DIR_PATH/hdl/"
loadSource -path "$::DIR_PATH/Version.vhd"

# Load Constraints
loadConstraints -path "$::DIR_PATH/../../common/AtlasChess2Feb/xdc/AtlasChess2Feb.xdc"
loadConstraints -path "$::DIR_PATH/../../common/AtlasChess2Feb/xdc/AtlasChess2FebEth.xdc"
