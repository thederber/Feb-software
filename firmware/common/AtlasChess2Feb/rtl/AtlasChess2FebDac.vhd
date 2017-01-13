-------------------------------------------------------------------------------
-- Title      : 
-------------------------------------------------------------------------------
-- File       : AtlasChess2FebDac.vhd
-- Author     : Larry Ruckman  <ruckman@slac.stanford.edu>
-- Company    : SLAC National Accelerator Laboratory
-- Created    : 2016-06-07
-- Last update: 2017-01-12
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
use ieee.std_logic_arith.all;
use ieee.std_logic_unsigned.all;

use work.StdRtlPkg.all;
use work.AxiLitePkg.all;

library unisim;
use unisim.vcomponents.all;

entity AtlasChess2FebDac is
   generic (
      TPD_G            : time             := 1 ns;
      AXI_BASE_ADDR_G  : slv(31 downto 0) := (others => '0');
      AXI_CLK_FREQ_G   : real             := 156.25E+6;
      AXI_ERROR_RESP_G : slv(1 downto 0)  := AXI_RESP_DECERR_C);
   port (
      -- AXI-Lite Interface
      axilClk         : in  sl;
      axilRst         : in  sl;
      axilReadMaster  : in  AxiLiteReadMasterType;
      axilReadSlave   : out AxiLiteReadSlaveType;
      axilWriteMaster : in  AxiLiteWriteMasterType;
      axilWriteSlave  : out AxiLiteWriteSlaveType;
      -- DAC Ports
      dacSlowCsL      : out slv(1 downto 0);
      dacSlowSck      : out slv(1 downto 0);
      dacSlowMosi     : out slv(1 downto 0));
end AtlasChess2FebDac;

architecture mapping of AtlasChess2FebDac is

   constant VREF_C  : real := 3.3;
   constant RANGE_C : real := 4095.0;

   constant DAC_INIT0_C : Slv12Array(3 downto 0) := (
      0 => toSlv(integer((1.70/VREF_C)*RANGE_C), 12),   -- CASC       = 1.70V
      1 => toSlv(integer((1.61/VREF_C)*RANGE_C), 12),   -- PIXTH      = 1.61V
      2 => toSlv(integer((2.10/VREF_C)*RANGE_C), 12),   -- BLR        = 2.10V
      3 => toSlv(integer((1.60/VREF_C)*RANGE_C), 12));  -- BL         = 1.60V

   constant DAC_INIT1_C : Slv12Array(3 downto 0) := (
      0 => toSlv(integer((1.20/VREF_C)*RANGE_C), 12),   -- LVDS_VCOM  = 1.20V
      1 => toSlv(integer((3.30/VREF_C)*RANGE_C), 12),   -- LVDS_VCTRL = 3.30V
      2 => toSlv(integer((0.00/VREF_C)*RANGE_C), 12),   -- DAC_REFP   = 0.00V
      3 => toSlv(integer((0.00/VREF_C)*RANGE_C), 12));  -- DAC_REFN   = 0.00V      

   constant NUM_AXIL_MASTERS_C : natural := 2;

   constant SLOW_DAC0_INDEX_C : natural := 0;
   constant SLOW_DAC1_INDEX_C : natural := 1;

   constant SLOW_DAC0_ADDR_C : slv(31 downto 0) := (x"00000000"+AXI_BASE_ADDR_G);
   constant SLOW_DAC1_ADDR_C : slv(31 downto 0) := (x"00010000"+AXI_BASE_ADDR_G);

   constant AXIL_CROSSBAR_CONFIG_C : AxiLiteCrossbarMasterConfigArray(NUM_AXIL_MASTERS_C-1 downto 0) := (
      SLOW_DAC0_INDEX_C => (
         baseAddr       => SLOW_DAC0_ADDR_C,
         addrBits       => 16,
         connectivity   => X"FFFF"),
      SLOW_DAC1_INDEX_C => (
         baseAddr       => SLOW_DAC1_ADDR_C,
         addrBits       => 16,
         connectivity   => X"FFFF"));

   signal mAxilWriteMasters : AxiLiteWriteMasterArray(NUM_AXIL_MASTERS_C-1 downto 0);
   signal mAxilWriteSlaves  : AxiLiteWriteSlaveArray(NUM_AXIL_MASTERS_C-1 downto 0);
   signal mAxilReadMasters  : AxiLiteReadMasterArray(NUM_AXIL_MASTERS_C-1 downto 0);
   signal mAxilReadSlaves   : AxiLiteReadSlaveArray(NUM_AXIL_MASTERS_C-1 downto 0);

begin

   --------------------------
   -- AXI-Lite: Crossbar Core
   --------------------------  
   U_XBAR : entity work.AxiLiteCrossbar
      generic map (
         TPD_G              => TPD_G,
         DEC_ERROR_RESP_G   => AXI_ERROR_RESP_G,
         NUM_SLAVE_SLOTS_G  => 1,
         NUM_MASTER_SLOTS_G => NUM_AXIL_MASTERS_C,
         MASTERS_CONFIG_G   => AXIL_CROSSBAR_CONFIG_C)
      port map (
         axiClk              => axilClk,
         axiClkRst           => axilRst,
         sAxiWriteMasters(0) => axilWriteMaster,
         sAxiWriteSlaves(0)  => axilWriteSlave,
         sAxiReadMasters(0)  => axilReadMaster,
         sAxiReadSlaves(0)   => axilReadSlave,
         mAxiWriteMasters    => mAxilWriteMasters,
         mAxiWriteSlaves     => mAxilWriteSlaves,
         mAxiReadMasters     => mAxilReadMasters,
         mAxiReadSlaves      => mAxilReadSlaves);

   -----------------------
   -- Slow DAC SPI Modules
   ----------------------- 
   U_SPI0 : entity work.AtlasChess2FebDacSpi
      generic map (
         TPD_G            => TPD_G,
         DAC_INIT_G       => DAC_INIT0_C,
         AXI_CLK_FREQ_G   => AXI_CLK_FREQ_G,
         AXI_ERROR_RESP_G => AXI_ERROR_RESP_G)
      port map (
         -- AXI-Lite Interface
         axilClk         => axilClk,
         axilRst         => axilRst,
         axilReadMaster  => mAxilReadMasters(SLOW_DAC0_INDEX_C),
         axilReadSlave   => mAxilReadSlaves(SLOW_DAC0_INDEX_C),
         axilWriteMaster => mAxilWriteMasters(SLOW_DAC0_INDEX_C),
         axilWriteSlave  => mAxilWriteSlaves(SLOW_DAC0_INDEX_C),
         -- Slow DAC's SPI Ports
         dacSlowCsL      => dacSlowCsL(0),
         dacSlowSck      => dacSlowSck(0),
         dacSlowMosi     => dacSlowMosi(0));

   U_SPI1 : entity work.AtlasChess2FebDacSpi
      generic map (
         TPD_G            => TPD_G,
         DAC_INIT_G       => DAC_INIT1_C,
         AXI_CLK_FREQ_G   => AXI_CLK_FREQ_G,
         AXI_ERROR_RESP_G => AXI_ERROR_RESP_G)
      port map (
         -- AXI-Lite Interface
         axilClk         => axilClk,
         axilRst         => axilRst,
         axilReadMaster  => mAxilReadMasters(SLOW_DAC1_INDEX_C),
         axilReadSlave   => mAxilReadSlaves(SLOW_DAC1_INDEX_C),
         axilWriteMaster => mAxilWriteMasters(SLOW_DAC1_INDEX_C),
         axilWriteSlave  => mAxilWriteSlaves(SLOW_DAC1_INDEX_C),
         -- Slow DAC's SPI Ports
         dacSlowCsL      => dacSlowCsL(1),
         dacSlowSck      => dacSlowSck(1),
         dacSlowMosi     => dacSlowMosi(1));
         
end mapping;
