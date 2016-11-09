-------------------------------------------------------------------------------
-- Title      : 
-------------------------------------------------------------------------------
-- File       : AtlasChess2FebAsic.vhd
-- Author     : Larry Ruckman  <ruckman@slac.stanford.edu>
-- Company    : SLAC National Accelerator Laboratory
-- Created    : 2016-06-07
-- Last update: 2016-08-30
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
use work.AxiStreamPkg.all;
use work.SsiPkg.all;
use work.AtlasChess2FebPkg.all;

library unisim;
use unisim.vcomponents.all;

entity AtlasChess2FebAsic is
   generic (
      TPD_G            : time             := 1 ns;
      AXI_BASE_ADDR_G  : slv(31 downto 0) := (others => '0');
      AXI_ERROR_RESP_G : slv(1 downto 0)  := AXI_RESP_DECERR_C;
      IODELAY_GROUP_G  : string           := "CHESS2_IODELAY_GRP");      
   port (
      -- System Ports
      extBusy         : out sl;
      -- CHESS2 ASIC Serial Ports
      chessDinP       : in  Slv14Array(2 downto 0);
      chessDinN       : in  Slv14Array(2 downto 0);
      chessClk320MHzP : out Slv(2 downto 0);
      chessClk320MHzN : out Slv(2 downto 0);
      chessClk40MHz   : out Slv(2 downto 0);
      -- Reference clock and Reset
      refClk200MHz    : in  sl;
      refRst200MHz    : in  sl;
      -- Timing Interface
      timingClk40MHz  : in  sl;
      timingRst40MHz  : in  sl;
      timingClk320MHz : in  sl;
      timingRst320MHz : in  sl;
      timingTrig      : in  sl;
      timingMsg       : in  slv(63 downto 0);
      dlyRst          : in  sl;
      dlyTiming       : in  slv(DELAY_ADDR_WIDTH_C-1 downto 0);
      dlyChess        : in  slv(DELAY_ADDR_WIDTH_C-1 downto 0);
      -- CHESS2 RX MSG Configuration
      destId          : in  slv(5 downto 0);
      opCode          : in  slv(7 downto 0);
      frameType       : in  slv(31 downto 0);
      wordSize        : in  slv(7 downto 0);
      -- AXI Stream Interface
      axisClk         : in  sl;
      axisRst         : in  sl;
      mAxisMaster     : out AxiStreamMasterType;
      mAxisSlave      : in  AxiStreamSlaveType;
      -- AXI-Lite Register Interface
      axilClk         : in  sl;
      axilRst         : in  sl;
      axilReadMaster  : in  AxiLiteReadMasterType;
      axilReadSlave   : out AxiLiteReadSlaveType;
      axilWriteMaster : in  AxiLiteWriteMasterType;
      axilWriteSlave  : out AxiLiteWriteSlaveType);   
end AtlasChess2FebAsic;

architecture mapping of AtlasChess2FebAsic is
   
   constant NUM_AXIL_MASTERS_C : natural := 3;

   constant CHESS2_INDEX0_C : natural := 0;
   constant CHESS2_INDEX1_C : natural := 1;
   constant CHESS2_INDEX2_C : natural := 2;

   constant CHESS2_ADDR0_C : slv(31 downto 0) := (x"00000000"+AXI_BASE_ADDR_G);
   constant CHESS2_ADDR1_C : slv(31 downto 0) := (x"00010000"+AXI_BASE_ADDR_G);
   constant CHESS2_ADDR2_C : slv(31 downto 0) := (x"00020000"+AXI_BASE_ADDR_G);

   constant AXIL_CROSSBAR_CONFIG_C : AxiLiteCrossbarMasterConfigArray(NUM_AXIL_MASTERS_C-1 downto 0) := (
      CHESS2_INDEX0_C => (
         baseAddr     => CHESS2_ADDR0_C,
         addrBits     => 16,
         connectivity => X"FFFF"),
      CHESS2_INDEX1_C => (
         baseAddr     => CHESS2_ADDR1_C,
         addrBits     => 16,
         connectivity => X"FFFF"),
      CHESS2_INDEX2_C => (
         baseAddr     => CHESS2_ADDR2_C,
         addrBits     => 16,
         connectivity => X"FFFF"));  

   signal mAxilWriteMasters : AxiLiteWriteMasterArray(NUM_AXIL_MASTERS_C-1 downto 0);
   signal mAxilWriteSlaves  : AxiLiteWriteSlaveArray(NUM_AXIL_MASTERS_C-1 downto 0);
   signal mAxilReadMasters  : AxiLiteReadMasterArray(NUM_AXIL_MASTERS_C-1 downto 0);
   signal mAxilReadSlaves   : AxiLiteReadSlaveArray(NUM_AXIL_MASTERS_C-1 downto 0);

   signal chessMasters : AxiStreamMasterArray(NUM_AXIL_MASTERS_C-1 downto 0);
   signal chessSlaves  : AxiStreamSlaveArray(NUM_AXIL_MASTERS_C-1 downto 0);

   signal chessMaster : AxiStreamMasterType;
   signal chessSlave  : AxiStreamSlaveType;

   signal delayIn   : slv(64 downto 0);
   signal delayOut  : slv(64 downto 0);
   signal delayCnt  : slv(DELAY_ADDR_WIDTH_C-1 downto 0);
   signal delayRdEn : sl;

   signal dataValid : slv(NUM_AXIL_MASTERS_C-1 downto 0);
   signal multiHit  : slv(NUM_AXIL_MASTERS_C-1 downto 0);
   signal col       : Slv5Array(NUM_AXIL_MASTERS_C-1 downto 0);
   signal row       : Slv7Array(NUM_AXIL_MASTERS_C-1 downto 0);

   attribute IODELAY_GROUP                 : string;
   attribute IODELAY_GROUP of U_IDELAYCTRL : label is IODELAY_GROUP_G;
   
begin

   U_IDELAYCTRL : IDELAYCTRL
      port map (
         RDY    => open,                -- 1-bit output: Ready output
         REFCLK => refClk200MHz,        -- 1-bit input: Reference clock input
         RST    => refRst200MHz);       -- 1-bit input: Active high reset input      

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

   ----------------------
   -- Timing Delay Module
   ----------------------
   U_Delay : entity work.FifoSync
      generic map (
         TPD_G         => TPD_G,
         BRAM_EN_G     => true,
         FWFT_EN_G     => true,
         PIPE_STAGES_G => 1,            -- Pipeline to help with timing 
         DATA_WIDTH_G  => 65,
         ADDR_WIDTH_G  => DELAY_ADDR_WIDTH_C)
      port map (
         clk        => timingClk320MHz,
         rst        => dlyRst,
         din        => delayIn,
         wr_en      => '1',
         rd_en      => delayRdEn,
         data_count => delayCnt,
         dout       => delayOut);   

   delayIn   <= timingTrig & timingMsg;
   delayRdEn <= '1' when(delayCnt >= dlyTiming) else '0';

   -----------------------------
   -- AXI-Lite: CHESS2 RX Engine
   -----------------------------
   U_Chess :
   for i in NUM_AXIL_MASTERS_C-1 downto 0 generate
      U_Rx : entity work.AtlasChess2FebAsicRx
         generic map (
            TPD_G              => TPD_G,
            INDEX_G            => i,
            DELAY_ADDR_WIDTH_G => DELAY_ADDR_WIDTH_C,
            AXI_ERROR_RESP_G   => AXI_ERROR_RESP_G,
            IODELAY_GROUP_G    => IODELAY_GROUP_G)   
         port map (
            -- CHESS2 ASIC Ports
            chessDinP       => chessDinP(i),
            chessDinN       => chessDinN(i),
            chessClk320MHzP => chessClk320MHzP(i),
            chessClk320MHzN => chessClk320MHzN(i),
            chessClk40MHz   => chessClk40MHz(i),
            -- Reference clock and Reset
            refClk200MHz    => refClk200MHz,
            refRst200MHz    => refRst200MHz,
            -- Timing Interface
            timingClk40MHz  => timingClk40MHz,
            timingRst40MHz  => timingRst40MHz,
            timingClk320MHz => timingClk320MHz,
            timingRst320MHz => timingRst320MHz,
            dlyRst          => dlyRst,
            dlyChess        => dlyChess,
            -- CHESS2 RX Output
            dataValid       => dataValid(i),
            multiHit        => multiHit(i),
            col             => col(i),
            row             => row(i),
            -- AXI-Lite Register Interface (axilClk domain)
            axilClk         => axilClk,
            axilRst         => axilRst,
            axilReadMaster  => mAxilReadMasters(CHESS2_INDEX0_C+i),
            axilReadSlave   => mAxilReadSlaves(CHESS2_INDEX0_C+i),
            axilWriteMaster => mAxilWriteMasters(CHESS2_INDEX0_C+i),
            axilWriteSlave  => mAxilWriteSlaves(CHESS2_INDEX0_C+i));    
   end generate;

   U_RxMsg : entity work.AtlasChess2FebAsicRxMsg
      generic map (
         TPD_G      => TPD_G,
         NUM_ASIC_G => NUM_AXIL_MASTERS_C)
      port map (
         -- CHESS2 Interface
         dataValid       => dataValid,
         multiHit        => multiHit,
         col             => col,
         row             => row,
         -- CHESS2 Configuration
         destId          => destId,
         opCode          => opCode,
         frameType       => frameType,
         wordSize        => wordSize,
         -- CHESS2/Timing Interface
         timingClk320MHz => timingClk320MHz,
         timingRst320MHz => timingRst320MHz,
         timingTrig      => delayOut(64),
         timingMsg       => delayOut(63 downto 0),
         -- AXI Stream Interface
         axisClk         => axisClk,
         axisRst         => axisRst,
         extBusy         => extBusy,
         mAxisMaster     => mAxisMaster,
         mAxisSlave      => mAxisSlave);

end mapping;
