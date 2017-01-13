-------------------------------------------------------------------------------
-- Title      : 
-------------------------------------------------------------------------------
-- File       : AtlasChess2FebClk.vhd
-- Author     : Larry Ruckman  <ruckman@slac.stanford.edu>
-- Company    : SLAC National Accelerator Laboratory
-- Created    : 2016-06-02
-- Last update: 2016-08-09
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
use work.AtlasChess2FebPkg.all;

library unisim;
use unisim.vcomponents.all;

entity AtlasChess2FebClk is
   generic (
      TPD_G : time := 1 ns);      
   port (
      -- Reference Clocks
      locClk40MHz     : in  sl;
      extClk40MHzP    : in  sl;
      extClk40MHzN    : in  sl;
      -- Configuration
      refSelect       : in  sl;
      pllRst          : in  sl;
      -- Status 
      refClk40MHz     : out sl;
      refLocked       : out sl;
      -- Timing Clocks
      timingClk320MHz : out sl;
      timingRst320MHz : out sl;
      timingClk40MHz  : out sl;
      timingRst40MHz  : out sl);
end AtlasChess2FebClk;

architecture mapping of AtlasChess2FebClk is

   signal locClock40MHz : sl;
   signal extClock40MHz : sl;
   signal clk40MHz      : sl;
   signal clkSelect     : sl;

   attribute dont_touch                  : string;
   attribute dont_touch of locClock40MHz : signal is "TRUE";
   attribute dont_touch of extClock40MHz : signal is "TRUE";
   attribute dont_touch of clk40MHz      : signal is "TRUE";
   attribute dont_touch of clkSelect     : signal is "TRUE";
   
begin

   refClk40MHz <= clk40MHz;

   U_Local : IBUFG
      port map (
         I => locClk40MHz,
         O => locClock40MHz);

   U_Remote : IBUFDS
      port map (
         I  => extClk40MHzP,
         IB => extClk40MHzN,
         O  => extClock40MHz);     

   U_BUFGMUX : BUFGMUX
      port map (
         O  => clk40MHz,                -- 1-bit output: Clock output
         I0 => locClock40MHz,           -- 1-bit input: Clock input (S=0)
         I1 => extClock40MHz,           -- 1-bit input: Clock input (S=1)
         S  => refSelect);              -- 1-bit input: Clock select   

   U_MMCM : entity work.ClockManager7
      generic map(
         TPD_G              => TPD_G,
         TYPE_G             => "MMCM",
         INPUT_BUFG_G       => false,
         FB_BUFG_G          => true,
         RST_IN_POLARITY_G  => '1',
         NUM_CLOCKS_G       => 2,
         -- MMCM attributes
         BANDWIDTH_G        => "OPTIMIZED",
         CLKIN_PERIOD_G     => 25.0,    -- 40 MHz
         DIVCLK_DIVIDE_G    => 1,       -- 40 MHz = 40 MHz/1
         CLKFBOUT_MULT_F_G  => 25.0,    -- 1 GHz = 40 MHz x 25
         -----------------------
         -- 50 MHz Configuration
         -----------------------         
         -- CLKOUT0_DIVIDE_F_G => 2.50, -- 400 MHz = 1 GHz/2.5
         -- CLKOUT1_DIVIDE_G   => 20)   -- 50 MHz = 1 GHz/20            
         -----------------------
         -- 45.45 MHz Configuration
         -----------------------         
         -- CLKOUT0_DIVIDE_F_G => 2.75, -- 363.6 MHz = 1 GHz/2.75
         -- CLKOUT1_DIVIDE_G   => 22)   -- 45.45 MHz = 1 GHz/22         
         -----------------------
         -- 40 MHz Configuration
         -----------------------         
         CLKOUT0_DIVIDE_F_G => 3.125,   -- 320 MHz = 1 GHz/3.125
         CLKOUT1_DIVIDE_G   => 25)      -- 40 MHz = 1 GHz/25
         -----------------------
         -- 35.7 MHz Configuration
         -----------------------
         -- CLKOUT0_DIVIDE_F_G => 3.50, -- 285.7 MHz = 1 GHz/3.5
         -- CLKOUT1_DIVIDE_G   => 28)   -- 35.7 MHz = 1 GHz/28           
         -----------------------
         -- 31.25 MHz Configuration
         -----------------------
         -- CLKOUT0_DIVIDE_F_G => 4.00, -- 250 MHz = 1 GHz/4.0
         -- CLKOUT1_DIVIDE_G   => 32)   -- 31.25 MHz = 1 GHz/32         
         -----------------------
         -- 20 MHz Configuration
         -----------------------
         -- CLKOUT0_DIVIDE_F_G => 6.25, -- 160 MHz = 1 GHz/6.25
         -- CLKOUT1_DIVIDE_G   => 50)   -- 20 MHz = 1 GHz/50
         
      port map(
         clkIn     => clk40MHz,
         rstIn     => pllRst,
         clkOut(0) => timingClk320MHz,
         clkOut(1) => timingClk40MHz,
         rstOut(0) => timingRst320MHz,
         rstOut(1) => timingRst40MHz,
         locked    => refLocked);    

end mapping;
