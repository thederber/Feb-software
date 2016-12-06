-------------------------------------------------------------------------------
-- Title      : 
-------------------------------------------------------------------------------
-- File       : AtlasChess2FebPkg.vhd
-- Author     : Larry Ruckman  <ruckman@slac.stanford.edu>
-- Company    : SLAC National Accelerator Laboratory
-- Created    : 2016-06-01
-- Last update: 2016-12-06
-- Platform   : 
-- Standard   : VHDL'93/02
-------------------------------------------------------------------------------
-- Description: 
-------------------------------------------------------------------------------
-- This file is part of 'ATLAS CHESS2 DEV'.
-- It is subject to the license terms in the LICENSE.txt file found in the 
-- top-level directory of this distribution and at: 
--    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html. 
-- No part of 'ATLAS CHESS2 DEV', including this file, 
-- may be copied, modified, propagated, or distributed except according to 
-- the terms contained in the LICENSE.txt file.
-------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;

use work.StdRtlPkg.all;

package AtlasChess2FebPkg is

   constant DELAY_ADDR_WIDTH_C : positive := 12;

   subtype TimingModeType is slv(1 downto 0);
   constant TIMING_LEMO_TRIG_C : TimingModeType := "00";
   constant TIMING_PGP_TRIG_C  : TimingModeType := "01";
   constant TIMING_SLAC_EVR_C  : TimingModeType := "10";

   type AtlasChess2FebConfigType is record
      softTrig   : sl;
      softRst    : sl;
      hardRst    : sl;
      pllRst     : sl;
      destId     : slv(5 downto 0);
      frameType  : slv(31 downto 0);
      wordSize   : slv(7 downto 0);
      timingMode : TimingModeType;
      dlyRst     : sl;
      dlyTiming  : slv(DELAY_ADDR_WIDTH_C-1 downto 0);
      dlyChess   : slv(DELAY_ADDR_WIDTH_C-1 downto 0);
      refSelect  : sl;
      chessClkOe : sl;
   end record;
   constant CHESS2_FEB_CONFIG_INIT_C : AtlasChess2FebConfigType := (
      softTrig   => '0',
      softRst    => '1',
      hardRst    => '1',
      pllRst     => '1',
      destId     => (others => '0'),
      frameType  => (others => '0'),
      wordSize   => (others => '0'),
      timingMode => TIMING_LEMO_TRIG_C,
      dlyRst     => '1',
      dlyTiming  => (others => '0'),
      dlyChess   => (others => '0'),
      refSelect  => '0',
      chessClkOe => '0');  

   type AtlasChess2FebStatusType is record
      refClk40MHz : sl;
      refLocked   : sl;
   end record;
   constant CHESS2_FEB_STATUS_INIT_C : AtlasChess2FebStatusType := (
      refClk40MHz => '0',
      refLocked   => '0');    

end package;
