export GIT_BYPASS = 0
##########################################################################
## Revision History:
##
## 01/23/2017 (0x00000001): Initial Build
## 01/24/2017 (0x00000002): Added hitDetTime registers
## 01/25/2017 (0x00000003): Added debugSendCnt register
## 01/31/2017 (0x00000004): Fixed bug in sysReg.refClkFreq
## 02/01/2017 (0x00000005): Changed default of chargeInj.invPulse to 0x1
##                          Changed default of sysReg.wordSize to 0x7
## 03/02/2017 (0x00000006): Updating to ruckus v1.1
## 08/23/2017 (0x00000007): Adding charge inj pulse delay.
## 08/23/2017 (0x00000008): Increasing the number of detected hit to 8.
##########################################################################
export PRJ_VERSION = 0x0000000A

# Define target output
target: prom

# Define target part
export PRJ_PART = XC7K70TFBG676-3

# Define the Microblaze source path
export SDK_SRC_PATH = $(PROJ_DIR)/../../common/AtlasChess2Feb/src

# Use top level makefile
include ../../submodules/ruckus/system_vivado.mk
