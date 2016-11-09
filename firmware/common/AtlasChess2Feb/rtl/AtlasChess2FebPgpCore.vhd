-------------------------------------------------------------------------------
-- Title      : 
-------------------------------------------------------------------------------
-- File       : AtlasChess2FebPgpCore.vhd
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
use work.AxiLitePkg.all;
use work.AxiStreamPkg.all;
use work.SsiPkg.all;
use work.Pgp2bPkg.all;
use work.AtlasChess2FebPkg.all;

library unisim;
use unisim.vcomponents.all;

entity AtlasChess2FebPgpCore is
   generic (
      TPD_G            : time            := 1 ns;
      AXI_ERROR_RESP_G : slv(1 downto 0) := AXI_RESP_DECERR_C);        
   port (
      -- Reference Clock and Reset
      refclk200MHz     : out sl;
      refRst200MHz     : out sl;
      -- AXI-Lite Interface   
      axilClk          : out sl;
      axilRst          : out sl;
      mAxilReadMaster  : out AxiLiteReadMasterType;
      mAxilReadSlave   : in  AxiLiteReadSlaveType;
      mAxilWriteMaster : out AxiLiteWriteMasterType;
      mAxilWriteSlave  : in  AxiLiteWriteSlaveType;
      -- Streaming CHESS2 Data (axilClk domain)
      sAxisMaster      : in  AxiStreamMasterType;
      sAxisSlave       : out AxiStreamSlaveType;
      -- MB Interface (axilClk domain)
      mbTxMaster       : in  AxiStreamMasterType;
      mbTxSlave        : out AxiStreamSlaveType;
      -- Trigger Interface (axilClk domain)
      pgpTxIn          : in  Pgp2bTxInType;
      pgpTxOut         : out Pgp2bTxOutType;
      pgpRxIn          : in  Pgp2bRxInType;
      pgpRxOut         : out Pgp2bRxOutType;
      -- PGP Ports
      pgpClkP          : in  sl;
      pgpClkN          : in  sl;
      pgpRxP           : in  sl;
      pgpRxN           : in  sl;
      pgpTxP           : out sl;
      pgpTxN           : out sl);
end AtlasChess2FebPgpCore;

architecture mapping of AtlasChess2FebPgpCore is

   signal pgpTxMasters : AxiStreamMasterArray(3 downto 0) := (others => AXI_STREAM_MASTER_INIT_C);
   signal pgpTxSlaves  : AxiStreamSlaveArray(3 downto 0)  := (others => AXI_STREAM_SLAVE_FORCE_C);

   signal pgpRxMasters : AxiStreamMasterArray(3 downto 0) := (others => AXI_STREAM_MASTER_INIT_C);
   signal pgpRxCtrl    : AxiStreamCtrlArray(3 downto 0)   := (others => AXI_STREAM_CTRL_UNUSED_C);

   signal refClkDiv2 : sl;
   signal refClk     : sl;
   signal stableClk  : sl;
   signal stableRst  : sl;
   signal pgpClk     : sl;
   signal pgpRst     : sl;
   
begin

   axilClk <= pgpClk;
   pgpRst  <= pgpRst;

   U_IBUFDS_GTE2 : IBUFDS_GTE2
      port map (
         I     => pgpClkP,
         IB    => pgpClkN,
         CEB   => '0',
         ODIV2 => refClkDiv2,
         O     => refClk);    

   U_BUFG : BUFG
      port map (
         I => refClkDiv2,
         O => stableClk);           

   U_PwrUpRst : entity work.PwrUpRst
      generic map(
         TPD_G => TPD_G)   
      port map (
         clk    => stableClk,
         rstOut => stableRst);  

   U_MMCM : entity work.ClockManager7
      generic map(
         TPD_G              => TPD_G,
         TYPE_G             => "MMCM",
         INPUT_BUFG_G       => false,
         FB_BUFG_G          => false,
         RST_IN_POLARITY_G  => '1',
         NUM_CLOCKS_G       => 2,
         -- MMCM attributes
         BANDWIDTH_G        => "OPTIMIZED",
         CLKIN_PERIOD_G     => 6.4,     -- 156.25 MHz
         DIVCLK_DIVIDE_G    => 1,       -- 156.25 MHz = 156.25 MHz/1
         CLKFBOUT_MULT_F_G  => 8.0,     -- 1.25 GHz = 156.25 MHz x 8
         CLKOUT0_DIVIDE_F_G => 6.250,   -- 200 MHz = 1.25 GHz/6.25
         CLKOUT1_DIVIDE_G   => 8)       -- 156.25 MHz = 1.25 GHz/8
      port map(
         clkIn     => stableClk,
         rstIn     => stableRst,
         clkOut(0) => refclk200MHz,
         clkOut(1) => pgpClk,
         rstOut(0) => refRst200MHz,
         rstOut(1) => pgpRst);          

   Pgp2bGtx7VarLat_Inst : entity work.Pgp2bGtx7VarLat
      generic map (
         TPD_G             => TPD_G,
         -- CPLL Configurations
         TX_PLL_G          => "CPLL",
         RX_PLL_G          => "CPLL",
         CPLL_REFCLK_SEL_G => "001",
         CPLL_FBDIV_G      => 2,
         CPLL_FBDIV_45_G   => 5,
         CPLL_REFCLK_DIV_G => 1,
         -- MGT Configurations
         RXOUT_DIV_G       => 2,
         TXOUT_DIV_G       => 2,
         RX_CLK25_DIV_G    => 13,
         TX_CLK25_DIV_G    => 13,
         RX_OS_CFG_G       => "0000010000000",
         RXCDR_CFG_G       => x"03000023ff40200020",
         RXDFEXYDEN_G      => '1',
         RX_DFE_KL_CFG2_G  => x"301148AC",
         -- VC Configuration
         VC_INTERLEAVE_G   => 0,
         NUM_VC_EN_G       => 3)          
      port map (
         -- GT Clocking
         stableClk        => pgpClk,
         gtCPllRefClk     => refClk,
         gtCPllLock       => open,
         gtQPllRefClk     => '0',
         gtQPllClk        => '0',
         gtQPllLock       => '1',
         gtQPllRefClkLost => '0',
         gtQPllReset      => open,
         -- GT Serial IO
         gtTxP            => pgpTxP,
         gtTxN            => pgpTxN,
         gtRxP            => pgpRxP,
         gtRxN            => pgpRxN,
         -- Tx Clocking
         pgpTxReset       => pgpRst,
         pgpTxRecClk      => open,
         pgpTxClk         => pgpClk,
         pgpTxMmcmReset   => open,
         pgpTxMmcmLocked  => '1',
         -- Rx clocking
         pgpRxReset       => pgpRst,
         pgpRxRecClk      => open,
         pgpRxClk         => pgpClk,
         pgpRxMmcmReset   => open,
         pgpRxMmcmLocked  => '1',
         -- Non VC TX Signals
         pgpTxIn          => pgpTxIn,
         pgpTxOut         => pgpTxOut,
         -- Non VC RX Signals
         pgpRxIn          => pgpRxIn,
         pgpRxOut         => pgpRxOut,
         -- Frame TX Interface
         pgpTxMasters     => pgpTxMasters,
         pgpTxSlaves      => pgpTxSlaves,
         -- Frame RX Interface
         pgpRxMasters     => pgpRxMasters,
         pgpRxCtrl        => pgpRxCtrl);                     

   -- VC0 TX, Streaming Data Interface     
   pgpTxMasters(0) <= sAxisMaster;
   sAxisSlave      <= pgpTxSlaves(0);

   -- VC1 RX/TX, Register access control        
   U_SRPv0 : entity work.SrpV0AxiLite
      generic map (
         TPD_G               => TPD_G,
         RESP_THOLD_G        => 1,
         SLAVE_READY_EN_G    => false,
         EN_32BIT_ADDR_G     => true,
         BRAM_EN_G           => true,
         XIL_DEVICE_G        => "7SERIES",
         USE_BUILT_IN_G      => false,
         ALTERA_SYN_G        => false,
         ALTERA_RAM_G        => "M9K",
         GEN_SYNC_FIFO_G     => false,
         FIFO_ADDR_WIDTH_G   => 9,
         FIFO_PAUSE_THRESH_G => 2**8,
         AXI_STREAM_CONFIG_G => SSI_PGP2B_CONFIG_C)            
      port map (
         -- Streaming Slave (Rx) Interface (sAxisClk domain) 
         sAxisClk            => pgpClk,
         sAxisRst            => pgpRst,
         sAxisMaster         => pgpRxMasters(1),
         sAxisCtrl           => pgpRxCtrl(1),
         -- Streaming Master (Tx) Data Interface (mAxisClk domain)
         mAxisClk            => pgpClk,
         mAxisRst            => pgpRst,
         mAxisMaster         => pgpTxMasters(1),
         mAxisSlave          => pgpTxSlaves(1),
         -- AXI Lite Bus (axiLiteClk domain)
         axiLiteClk          => pgpClk,
         axiLiteRst          => pgpRst,
         mAxiLiteReadMaster  => mAxilReadMaster,
         mAxiLiteReadSlave   => mAxilReadSlave,
         mAxiLiteWriteMaster => mAxilWriteMaster,
         mAxiLiteWriteSlave  => mAxilWriteSlave);       

   -- VC2 TX, Streaming Data Interface    
   MBTX_FIFO : entity work.AxiStreamFifo
      generic map (
         -- General Configurations
         TPD_G               => TPD_G,
         PIPE_STAGES_G       => 1,
         SLAVE_READY_EN_G    => true,
         VALID_THOLD_G       => 1,
         -- FIFO configurations
         BRAM_EN_G           => true,
         USE_BUILT_IN_G      => false,
         GEN_SYNC_FIFO_G     => true,
         CASCADE_SIZE_G      => 1,
         FIFO_ADDR_WIDTH_G   => 9,
         FIFO_FIXED_THRESH_G => true,
         FIFO_PAUSE_THRESH_G => 128,
         -- AXI Stream Port Configurations
         SLAVE_AXI_CONFIG_G  => ssiAxiStreamConfig(4),
         MASTER_AXI_CONFIG_G => SSI_PGP2B_CONFIG_C)    
      port map (
         -- Slave Port
         sAxisClk    => pgpClk,
         sAxisRst    => pgpRst,
         sAxisMaster => mbTxMaster,
         sAxisSlave  => mbTxSlave,
         -- Master Port
         mAxisClk    => pgpClk,
         mAxisRst    => pgpRst,
         mAxisMaster => pgpTxMasters(2),
         mAxisSlave  => pgpTxSlaves(2));   

end mapping;
