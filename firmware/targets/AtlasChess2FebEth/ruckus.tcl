# Load RUCKUS environment and library
source -quiet $::env(RUCKUS_DIR)/vivado_proc.tcl

# Load Source Code
loadSource -path "$::DIR_PATH/Version.vhd"
loadSource -path "$::DIR_PATH/hdl/AtlasChess2FebEth.vhd"

# Load Constraints
loadConstraints -path "$::DIR_PATH/../../common/AtlasChess2Feb/xdc/AtlasChess2Feb.xdc"
loadConstraints -path "$::DIR_PATH/../../common/AtlasChess2Feb/xdc/AtlasChess2FebEth.xdc"
