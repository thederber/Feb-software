-------------------------------------------------------------------------------
-- Title      : 
-------------------------------------------------------------------------------
-- File       : AtlasChess2FebAsicRxIdelay.vhd
-- Author     : Larry Ruckman  <ruckman@slac.stanford.edu>
-- Company    : SLAC National Accelerator Laboratory
-- Created    : 2015-03-20
-- Last update: 2016-06-02
-- Platform   : 
-- Standard   : VHDL'93/02
-------------------------------------------------------------------------------
-- Description: ADC DDR Deserializer
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
use ieee.std_logic_unsigned.all;
use ieee.std_logic_arith.all;

use work.StdRtlPkg.all;

library unisim;
use unisim.vcomponents.all;

entity AtlasChess2FebAsicRxIdelay is
   generic (
      TPD_G           : time            := 1 ns;
      DELAY_INIT_G    : slv(4 downto 0) := (others => '0');
      IODELAY_GROUP_G : string          := "CHESS2_IODELAY_GRP");
   port (
      -- ADC Data (clk320MHz domain)
      dataInP      : in  sl;
      dataInN      : in  sl;
      dataOut      : out sl;
      phaseSel     : in  sl;
      -- IO_Delay (refClk200MHz domain)
      delayInLoad  : in  sl;
      delayInData  : in  slv(4 downto 0);
      delayOutData : out slv(4 downto 0);
      -- Clocks
      clk320MHz    : in  sl;
      refClk200MHz : in  sl);
end AtlasChess2FebAsicRxIdelay;

architecture rtl of AtlasChess2FebAsicRxIdelay is
   
   signal data    : sl;
   signal dataDly : sl;
   signal Q1      : sl;
   signal Q2      : sl;

   attribute IODELAY_GROUP               : string;
   attribute IODELAY_GROUP of U_IDELAYE2 : label is IODELAY_GROUP_G;
   
begin

   U_IBUFDS : IBUFDS
      port map (
         I  => dataInP,
         IB => dataInN,
         O  => data);                 

   U_IDELAYE2 : IDELAYE2
      generic map (
         CINVCTRL_SEL          => "FALSE",     -- Enable dynamic clock inversion (FALSE, TRUE)
         DELAY_SRC             => "IDATAIN",   -- Delay input (IDATAIN, DATAIN)
         HIGH_PERFORMANCE_MODE => "FALSE",     -- Reduced jitter ("TRUE"), Reduced power ("FALSE")
         IDELAY_TYPE           => "VAR_LOAD",  -- FIXED, VARIABLE, VAR_LOAD, VAR_LOAD_PIPE
         IDELAY_VALUE          => conv_integer(DELAY_INIT_G),  -- Input delay tap setting (0-31)
         PIPE_SEL              => "FALSE",     -- Select pipelined mode, FALSE, TRUE
         REFCLK_FREQUENCY      => 200.0,  -- IDELAYCTRL clock input frequency in MHz (190.0-210.0, 290.0-310.0).
         SIGNAL_PATTERN        => "DATA")      -- DATA, CLOCK input signal
      port map (
         CNTVALUEOUT => delayOutData,   -- 5-bit output: Counter value output
         DATAOUT     => dataDly,        -- 1-bit output: Delayed data output
         C           => refClk200MHz,   -- 1-bit input: Clock input
         CE          => '0',            -- 1-bit input: Active high enable increment/decrement input
         CINVCTRL    => '0',            -- 1-bit input: Dynamic clock inversion input
         CNTVALUEIN  => delayInData,    -- 5-bit input: Counter value input
         DATAIN      => '0',            -- 1-bit input: Internal delay data input
         IDATAIN     => data,           -- 1-bit input: Data input from the I/O
         INC         => '0',            -- 1-bit input: Increment / Decrement tap delay input
         LD          => '1',            -- 1-bit input: Load IDELAY_VALUE input
         LDPIPEEN    => '0',            -- 1-bit input: Enable PIPELINE register to load data input
         REGRST      => delayInLoad);   -- 1-bit input: Active-high reset tap-delay input

   U_IDDR : IDDR
      generic map (
         DDR_CLK_EDGE => "SAME_EDGE_PIPELINED",  -- "OPPOSITE_EDGE", "SAME_EDGE", or "SAME_EDGE_PIPELINED"
         INIT_Q1      => '0',           -- Initial value of Q1: '0' or '1'
         INIT_Q2      => '0',           -- Initial value of Q2: '0' or '1'
         SRTYPE       => "SYNC")        -- Set/Reset type: "SYNC" or "ASYNC" 
      port map (
         D  => dataDly,                 -- 1-bit DDR data input
         C  => clk320MHz,               -- 1-bit clock input
         CE => '1',                     -- 1-bit clock enable input
         R  => '0',                     -- 1-bit reset
         S  => '0',                     -- 1-bit set
         Q1 => Q1,                      -- 1-bit output for positive edge of clock 
         Q2 => Q2);                     -- 1-bit output for negative edge of clock

   process(clk320MHz)
   begin
      if rising_edge(clk320MHz) then
         if phaseSel = '0' then
            dataOut <= Q1 after TPD_G;
         else
            dataOut <= Q2 after TPD_G;
         end if;
      end if;
   end process;
   
end rtl;
