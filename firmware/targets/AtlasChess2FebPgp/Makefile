
# Define target output
target: prom

# Define target part
export PRJ_PART = XC7K70TFBG676-3

# Using a non-standard target directory structure, 
# which requires me to define the TOP_DIR path
export TOP_DIR = $(abspath $(PWD)/../..)

export MODULES = $(TOP_DIR)/submodules

# List of build core directories.
export MODULE_DIRS = $(PROJ_DIR)/../../submodules/surf/base  \
                     $(PROJ_DIR)/../../submodules/surf/axi  \
                     $(PROJ_DIR)/../../submodules/surf/xilinx/general  \
                     $(PROJ_DIR)/../../submodules/surf/xilinx/general/microblaze \
                     $(PROJ_DIR)/../../submodules/surf/xilinx/7Series/gtx7  \
                     $(PROJ_DIR)/../../submodules/surf/xilinx/7Series/general  \
                     $(PROJ_DIR)/../../submodules/surf/protocols/ssi \
                     $(PROJ_DIR)/../../submodules/surf/protocols/srp \
                     $(PROJ_DIR)/../../submodules/surf/protocols/pgp/pgp2b/core \
                     $(PROJ_DIR)/../../submodules/surf/protocols/pgp/pgp2b/gtx7 \
                     $(PROJ_DIR)/../../submodules/surf/ethernet/GigEthCore/core \
                     $(PROJ_DIR)/../../submodules/surf/ethernet/GigEthCore/gtx7 \
                     $(PROJ_DIR)/../../submodules/surf/ethernet/EthMacCore \
                     $(PROJ_DIR)/../../submodules/surf/ethernet/IpV4Engine \
                     $(PROJ_DIR)/../../submodules/surf/ethernet/UdpEngine \
                     $(PROJ_DIR)/../../common/AtlasChess2Feb  \
                     $(PROJ_DIR)

export SDK_SRC_PATH = $(PROJ_DIR)/../../common/AtlasChess2Feb/src

# Use top level makefile
include ../../submodules/ruckus/system_vivado_v1.mk
