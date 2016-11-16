-------------------------------------------------------------------------------
-- Title      : 
-------------------------------------------------------------------------------
-- File       : AtlasChess2FebDac.vhd
-- Author     : Larry Ruckman  <ruckman@slac.stanford.edu>
-- Company    : SLAC National Accelerator Laboratory
-- Created    : 2016-06-07
-- Last update: 2016-11-16
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
   DAC_SPI : for i in 1 downto 0 generate
      U_SPI : entity work.AtlasChess2FebDacSpi
         generic map (
            TPD_G            => TPD_G,
            AXI_CLK_FREQ_G   => AXI_CLK_FREQ_G,
            AXI_ERROR_RESP_G => AXI_ERROR_RESP_G)
         port map (
            -- AXI-Lite Interface
            axilClk         => axilClk,
            axilRst         => axilRst,
            axilReadMaster  => mAxilReadMasters(SLOW_DAC0_INDEX_C+i),
            axilReadSlave   => mAxilReadSlaves(SLOW_DAC0_INDEX_C+i),
            axilWriteMaster => mAxilWriteMasters(SLOW_DAC0_INDEX_C+i),
            axilWriteSlave  => mAxilWriteSlaves(SLOW_DAC0_INDEX_C+i),
            -- Slow DAC's SPI Ports
            dacSlowCsL      => dacSlowCsL(i),
            dacSlowSck      => dacSlowSck(i),
            dacSlowMosi     => dacSlowMosi(i));
   end generate DAC_SPI;
   
end mapping;
