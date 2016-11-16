
# Define target output
target: prom

# Define target part
export PRJ_PART = XC7K70TFBG676-3

# List of build core directories.
export MODULE_DIRS = $(PROJ_DIR)/../../submodules/surf  \
                     $(PROJ_DIR)/../../common/AtlasChess2Feb  \
                     $(PROJ_DIR)

# Define the Microblaze source path
###export SDK_SRC_PATH = $(PROJ_DIR)/../../common/AtlasChess2Feb/src

# Use top level makefile
include ../../submodules/ruckus/system_vivado.mk
