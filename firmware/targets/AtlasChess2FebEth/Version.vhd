------------------------------------------------------------------------------
-- This file is part of 'ATLAS CHESS2 DEV'.
-- It is subject to the license terms in the LICENSE.txt file found in the 
-- top-level directory of this distribution and at: 
--    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html. 
-- No part of 'ATLAS CHESS2 DEV', including this file, 
-- may be copied, modified, propagated, or distributed except according to 
-- the terms contained in the LICENSE.txt file.
------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;

package Version is

   constant FPGA_VERSION_C : std_logic_vector(31 downto 0) := x"00000003";  -- MAKE_VERSION

   constant BUILD_STAMP_C : string := "AtlasChess2FebEth: Vivado v2016.2 (x86_64) Built Fri Jan 27 09:35:38 PST 2017 by ruckman";

end Version;

-------------------------------------------------------------------------------
-- Revision History:
--
-- 01/25/2017 (0x00000003): Added debugSendCnt register
-- 01/24/2017 (0x00000002): Added hitDetTime registers
-- 01/23/2017 (0x00000001): Initial Build
--
-------------------------------------------------------------------------------

