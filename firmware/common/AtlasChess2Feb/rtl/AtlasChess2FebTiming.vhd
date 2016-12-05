-------------------------------------------------------------------------------
-- Title      : 
-------------------------------------------------------------------------------
-- File       : AtlasChess2FebTiming.vhd
-- Author     : Larry Ruckman  <ruckman@slac.stanford.edu>
-- Company    : SLAC National Accelerator Laboratory
-- Created    : 2016-06-02
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
use work.Pgp2bPkg.all;
use work.AtlasChess2FebPkg.all;

entity AtlasChess2FebTiming is
   generic (
      TPD_G            : time             := 1 ns;
      AXI_BASE_ADDR_G  : slv(31 downto 0) := (others => '0');
      AXI_CLK_FREQ_G   : real             := 156.25E+6;
      AXI_ERROR_RESP_G : slv(1 downto 0)  := AXI_RESP_DECERR_C;
      IODELAY_GROUP_G  : string           := "CHESS2_IODELAY_GRP");
   port (
      -- AXI-Lite Interface
      axilClk         : in  sl;
      axilRst         : in  sl;
      axilReadMaster  : in  AxiLiteReadMasterType;
      axilReadSlave   : out AxiLiteReadSlaveType;
      axilWriteMaster : in  AxiLiteWriteMasterType;
      axilWriteSlave  : out AxiLiteWriteSlaveType;
      -- Timing Interface
      timingClk320MHz : in  sl;
      timingRst320MHz : in  sl;
      timingTrig      : out sl;
      timingMsg       : out slv(63 downto 0);
      timingMode      : in  TimingModeType;
      softTrig        : in  sl;
      evrOpCode       : out slv(7 downto 0);
      -- Reference clock and Reset
      refClk200MHz    : in  sl;
      refRst200MHz    : in  sl;
      -- System Ports
      extTrigL        : in  sl;
      -- PGP Timing Interface
      pgpTxIn         : out Pgp2bTxInType;
      pgpTxOut        : in  Pgp2bTxOutType;
      pgpRxIn         : out Pgp2bRxInType;
      pgpRxOut        : in  Pgp2bRxOutType;
      -- SLAC Timing Ports
      evrClkP         : in  sl;
      evrClkN         : in  sl;
      evrRxP          : in  sl;
      evrRxN          : in  sl;
      evrTxP          : out sl;
      evrTxN          : out sl);         
end AtlasChess2FebTiming;

architecture mapping of AtlasChess2FebTiming is

   constant NUM_AXIL_MASTERS_C : natural := 2;

   constant PGP_INDEX_C : natural := 0;
   constant EVR_INDEX_C : natural := 1;

   constant PGP_ADDR_C : slv(31 downto 0) := (x"00000000"+AXI_BASE_ADDR_G);
   constant EVR_ADDR_C : slv(31 downto 0) := (x"00010000"+AXI_BASE_ADDR_G);

   constant AXIL_CROSSBAR_CONFIG_C : AxiLiteCrossbarMasterConfigArray(NUM_AXIL_MASTERS_C-1 downto 0) := (
      PGP_INDEX_C     => (
         baseAddr     => PGP_ADDR_C,
         addrBits     => 16,
         connectivity => X"FFFF"),
      EVR_INDEX_C     => (
         baseAddr     => EVR_ADDR_C,
         addrBits     => 16,
         connectivity => X"FFFF"));  

   signal mAxilWriteMasters : AxiLiteWriteMasterArray(NUM_AXIL_MASTERS_C-1 downto 0);
   signal mAxilWriteSlaves  : AxiLiteWriteSlaveArray(NUM_AXIL_MASTERS_C-1 downto 0);
   signal mAxilReadMasters  : AxiLiteReadMasterArray(NUM_AXIL_MASTERS_C-1 downto 0);
   signal mAxilReadSlaves   : AxiLiteReadSlaveArray(NUM_AXIL_MASTERS_C-1 downto 0);

   signal extTrig : sl;

   signal pgpEn     : sl;
   signal pgpOpCode : slv(7 downto 0);

   signal evrClk       : sl;
   signal evrRst       : sl;
   signal evrTrig      : sl;
   signal evrTs        : slv(63 downto 0);
   signal evrEn        : sl;
   signal evrTimeStamp : slv(63 downto 0);
   
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

   SyncExtTrig : entity work.SynchronizerOneShot
      generic map (
         TPD_G           => TPD_G,
         IN_POLARITY_G   => '0',
         RELEASE_DELAY_G => 32)         -- 100 ns period
      port map (
         clk     => timingClk320MHz,
         rst     => timingRst320MHz,
         dataIn  => extTrigL,
         dataOut => extTrig);

   U_PgpMon : entity work.Pgp2bAxi
      generic map (
         TPD_G              => TPD_G,
         AXI_ERROR_RESP_G   => AXI_ERROR_RESP_G,
         COMMON_TX_CLK_G    => true,
         COMMON_RX_CLK_G    => true,
         WRITE_EN_G         => false,
         AXI_CLK_FREQ_G     => AXI_CLK_FREQ_G,
         STATUS_CNT_WIDTH_G => 32,
         ERROR_CNT_WIDTH_G  => 16)
      port map (
         -- TX PGP Interface (pgpTxClk)
         pgpTxClk        => axilClk,
         pgpTxClkRst     => axilRst,
         pgpTxIn         => pgpTxIn,
         pgpTxOut        => pgpTxOut,
         -- RX PGP Interface (pgpRxClk)
         pgpRxClk        => axilClk,
         pgpRxClkRst     => axilRst,
         pgpRxIn         => pgpRxIn,
         pgpRxOut        => pgpRxOut,
         -- AXI-Lite Register Interface (axilClk domain)
         axilClk         => axilClk,
         axilRst         => axilRst,
         axilReadMaster  => mAxilReadMasters(PGP_INDEX_C),
         axilReadSlave   => mAxilReadSlaves(PGP_INDEX_C),
         axilWriteMaster => mAxilWriteMasters(PGP_INDEX_C),
         axilWriteSlave  => mAxilWriteSlaves(PGP_INDEX_C));      

   SyncPgpOpCodes : entity work.SynchronizerFifo
      generic map(
         TPD_G        => TPD_G,
         DATA_WIDTH_G => 8)
      port map(
         -- Write Ports (wr_clk domain)
         wr_clk => axilClk,
         wr_en  => pgpRxOut.opCodeEn,
         din    => pgpRxOut.opCode,
         -- Read Ports (rd_clk domain)
         rd_clk => timingClk320MHz,
         rd_en  => '1',
         valid  => pgpEn,
         dout   => pgpOpCode); 

   U_EVR : entity work.AtlasChess2FebEvr
      generic map (
         TPD_G            => TPD_G,
         AXI_ERROR_RESP_G => AXI_ERROR_RESP_G)
      port map (
         -- AXI-Lite Register and Status Bus Interface (axiClk domain)
         axilClk         => axilClk,
         axilRst         => axilRst,
         axilReadMaster  => mAxilReadMasters(EVR_INDEX_C),
         axilReadSlave   => mAxilReadSlaves(EVR_INDEX_C),
         axilWriteMaster => mAxilWriteMasters(EVR_INDEX_C),
         axilWriteSlave  => mAxilWriteSlaves(EVR_INDEX_C),
         -- EVR Interface
         evrClk          => evrClk,
         evrRst          => evrRst,
         evrTrig         => evrTrig,
         evrTs           => evrTs,
         evrOpCode       => evrOpCode,
         -- SLAC Timing Ports
         evrClkP         => evrClkP,
         evrClkN         => evrClkN,
         evrRxP          => evrRxP,
         evrRxN          => evrRxN,
         evrTxP          => evrTxP,
         evrTxN          => evrTxN);           

   SyncEvrTimeStamp : entity work.SynchronizerFifo
      generic map(
         TPD_G        => TPD_G,
         DATA_WIDTH_G => 64)
      port map(
         rst    => evrRst,
         -- Write Ports (wr_clk domain)
         wr_clk => evrClk,
         wr_en  => evrTrig,
         din    => evrTs,
         -- Read Ports (rd_clk domain)
         rd_clk => timingClk320MHz,
         rd_en  => '1',
         valid  => evrEn,
         dout   => evrTimeStamp);                 

   U_TimingMsg : entity work.AtlasChess2FebTimingMsg
      generic map (
         TPD_G => TPD_G)
      port map (
         -- Trigger Interface
         extTrig         => extTrig,
         softTrig       => softTrig,
         -- PGP OP-Code Interface
         pgpEn           => pgpEn,
         pgpOpCode       => pgpOpCode,
         -- EVR Timing Interface
         evrEn           => evrEn,
         evrTimeStamp    => evrTimeStamp,
         -- Timing Interface
         timingClk320MHz => timingClk320MHz,
         timingRst320MHz => timingRst320MHz,
         timingTrig      => timingTrig,
         timingMsg       => timingMsg,
         timingMode      => timingMode);      

end mapping;
