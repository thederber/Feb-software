-------------------------------------------------------------------------------
-- Title      : 
-------------------------------------------------------------------------------
-- File       : AtlasChess2FebCore.vhd
-- Author     : Larry Ruckman  <ruckman@slac.stanford.edu>
-- Company    : SLAC National Accelerator Laboratory
-- Created    : 2016-06-01
-- Last update: 2016-12-02
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
use work.Pgp2bPkg.all;
use work.AtlasChess2FebPkg.all;

library unisim;
use unisim.vcomponents.all;

entity AtlasChess2FebCore is
   generic (
      TPD_G            : time             := 1 ns;
      COMM_MODE_G      : boolean          := false;         -- true = ETH mode, false = PGP mode
      AXI_ERROR_RESP_G : slv(1 downto 0)  := AXI_RESP_DECERR_C;
      -- ETH configuration
      ETH_DEV_G        : boolean          := true;          -- true = Adds non-RSSI on port 8193
      ETH_DHCP_G       : boolean          := true;          -- true = DHCP, false = static address
      ETH_IP_ADDR_G    : slv(31 downto 0) := x"0A01A8C0");  -- 192.168.1.10 (before DHCP) 
   port (
      -- CHESS2 ASIC Serial Ports
      chessDinP       : in    Slv14Array(2 downto 0);
      chessDinN       : in    Slv14Array(2 downto 0);
      chessClk320MHzP : out   slv(2 downto 0);
      chessClk320MHzN : out   slv(2 downto 0);
      chessClk40MHz   : out   slv(2 downto 0);
      -- Test Structure Ports
      testClk         : out   sl;
      dacEnL          : out   sl;
      term100         : out   sl;
      term300         : out   sl;
      lvdsTxSel       : out   sl;
      acMode          : out   sl;
      bitSel          : out   sl;
      injSig          : out   slv(1 downto 0);
      -- SACI Ports
      saciClk         : out   sl;
      saciCmd         : out   sl;
      saciRstL        : out   sl;
      saciSelL        : out   slv(3 downto 0);
      saciRsp         : in    slv(3 downto 0);
      -- DAC Ports
      dacSlowCsL      : out   slv(1 downto 0);
      dacSlowSck      : out   slv(1 downto 0);
      dacSlowMosi     : out   slv(1 downto 0);
      -- SLAC Timing Ports
      evrClkP         : in    sl;
      evrClkN         : in    sl;
      evrRxP          : in    sl;
      evrRxN          : in    sl;
      evrTxP          : out   sl;
      evrTxN          : out   sl;
      -- PGP/GbE Ports
      gtClkP          : in    sl;
      gtClkN          : in    sl;
      gtRxP           : in    sl;
      gtRxN           : in    sl;
      gtTxP           : out   sl;
      gtTxN           : out   sl;
      -- System Ports
      extTrigL        : in    sl;
      extBusy         : out   sl;
      tempAlertL      : in    sl;
      redL            : out   slv(1 downto 0);
      blueL           : out   slv(1 downto 0);
      greenL          : out   slv(1 downto 0);
      led             : out   slv(3 downto 0);
      oeClk           : out   slv(2 downto 0);
      pwrSyncSclk     : out   sl;
      pwrSyncFclk     : out   sl;
      pwrScl          : inout sl;
      pwrSda          : inout sl;
      configScl       : inout sl;
      configSda       : inout sl;
      -- Reference Clock
      locClk40MHz     : in    sl;
      extClk40MHzP    : in    sl;
      extClk40MHzN    : in    sl;
      -- Boot Memory Ports
      bootCsL         : out   sl;
      bootMosi        : out   sl;
      bootMiso        : in    sl;
      -- XADC Ports
      vPIn            : in    sl;
      vNIn            : in    sl);      
end AtlasChess2FebCore;

architecture mapping of AtlasChess2FebCore is

   constant AXIL_CLK_FREQ_C : real := ite(COMM_MODE_G, 125.0E+6, 156.25E+6);

   constant NUM_AXIL_SLAVES_C  : natural := 2;
   constant NUM_AXIL_MASTERS_C : natural := 6;

   constant SYS_INDEX_C    : natural := 0;
   constant DAC_INDEX_C    : natural := 1;
   constant TIMING_INDEX_C : natural := 2;
   constant CHESS2_INDEX_C : natural := 3;
   constant ETH_INDEX_C    : natural := 4;
   constant SACI_INDEX_C   : natural := 5;

   constant SYS_ADDR_C    : slv(31 downto 0) := X"00000000";
   constant DAC_ADDR_C    : slv(31 downto 0) := X"00100000";
   constant TIMING_ADDR_C : slv(31 downto 0) := X"00200000";
   constant CHESS2_ADDR_C : slv(31 downto 0) := X"00300000";
   constant ETH_ADDR_C    : slv(31 downto 0) := X"00400000";
   constant SACI_ADDR_C   : slv(31 downto 0) := X"01000000";
   
   constant AXIL_CROSSBAR_CONFIG_C : AxiLiteCrossbarMasterConfigArray(NUM_AXIL_MASTERS_C-1 downto 0) := (
      SYS_INDEX_C     => (
         baseAddr     => SYS_ADDR_C,
         addrBits     => 20,
         connectivity => X"FFFF"),
      DAC_INDEX_C     => (
         baseAddr     => DAC_ADDR_C,
         addrBits     => 20,
         connectivity => X"FFFF"),
      TIMING_INDEX_C  => (
         baseAddr     => TIMING_ADDR_C,
         addrBits     => 20,
         connectivity => X"FFFF"),
      CHESS2_INDEX_C  => (
         baseAddr     => CHESS2_ADDR_C,
         addrBits     => 20,
         connectivity => X"FFFF"),
      ETH_INDEX_C     => (
         baseAddr     => ETH_ADDR_C,
         addrBits     => 20,
         connectivity => X"FFFF"),
      SACI_INDEX_C    => (
         baseAddr     => SACI_ADDR_C,
         addrBits     => 24,
         connectivity => X"FFFF"));  

   signal sAxilWriteMasters : AxiLiteWriteMasterArray(NUM_AXIL_SLAVES_C-1 downto 0);
   signal sAxilWriteSlaves  : AxiLiteWriteSlaveArray(NUM_AXIL_SLAVES_C-1 downto 0);
   signal sAxilReadMasters  : AxiLiteReadMasterArray(NUM_AXIL_SLAVES_C-1 downto 0);
   signal sAxilReadSlaves   : AxiLiteReadSlaveArray(NUM_AXIL_SLAVES_C-1 downto 0);

   signal mAxilWriteMasters : AxiLiteWriteMasterArray(NUM_AXIL_MASTERS_C-1 downto 0);
   signal mAxilWriteSlaves  : AxiLiteWriteSlaveArray(NUM_AXIL_MASTERS_C-1 downto 0);
   signal mAxilReadMasters  : AxiLiteReadMasterArray(NUM_AXIL_MASTERS_C-1 downto 0);
   signal mAxilReadSlaves   : AxiLiteReadSlaveArray(NUM_AXIL_MASTERS_C-1 downto 0);

   signal mbTxMaster : AxiStreamMasterType;
   signal mbTxSlave  : AxiStreamSlaveType;

   signal chessMaster : AxiStreamMasterType;
   signal chessSlave  : AxiStreamSlaveType;

   signal status : AtlasChess2FebStatusType;
   signal config : AtlasChess2FebConfigType;

   signal axilClk : sl;
   signal axilRst : sl;

   signal refclk200MHz : sl;
   signal refRst200MHz : sl;

   signal pgpTxIn  : Pgp2bTxInType  := PGP2B_TX_IN_INIT_C;
   signal pgpTxOut : Pgp2bTxOutType := PGP2B_TX_OUT_INIT_C;
   signal pgpRxIn  : Pgp2bRxInType  := PGP2B_RX_IN_INIT_C;
   signal pgpRxOut : Pgp2bRxOutType := PGP2B_RX_OUT_INIT_C;

   signal ethReady   : sl              := '0';
   signal rssiStatus : slv(6 downto 0) := (others => '0');

   signal timingClk320MHz : sl;
   signal timingRst320MHz : sl;
   signal timingClk40MHz  : sl;
   signal timingRst40MHz  : sl;
   signal timingTrig      : sl;
   signal timingMsg       : slv(63 downto 0) := (others => '0');
   signal evrOpCode       : slv(7 downto 0);
   
begin

   --------------
   -- Misc. Ports
   --------------
   saciRstL <= not(axilRst);

   led(3) <= pgpRxOut.remLinkReady;
   led(2) <= pgpRxOut.linkReady;
   led(1) <= rssiStatus(0);
   led(0) <= ethReady;

   redL   <= "11";
   blueL  <= "11";
   greenL <= "00";

   oeClk <= (others => '1');

   pwrSyncSclk <= '0';
   pwrSyncFclk <= '0';

   testClk   <= '0';
   dacEnL    <= '1';
   term100   <= '0';
   term300   <= '0';
   lvdsTxSel <= '0';
   acMode    <= '0';
   bitSel    <= '0';
   injSig    <= (others => '0');

   ---------------
   -- Timing Clock 
   ---------------
   U_Clk : entity work.AtlasChess2FebClk
      generic map(
         TPD_G => TPD_G)
      port map(
         -- Reference Clocks
         locClk40MHz     => locClk40MHz,
         extClk40MHzP    => extClk40MHzP,
         extClk40MHzN    => extClk40MHzN,
         -- Configuration
         refSelect       => config.refSelect,
         pllRst          => config.pllRst,
         -- Status 
         refClk40MHz     => status.refClk40MHz,
         refLocked       => status.refLocked,
         -- Timing Clocks
         timingClk320MHz => timingClk320MHz,
         timingRst320MHz => timingRst320MHz,
         timingClk40MHz  => timingClk40MHz,
         timingRst40MHz  => timingRst40MHz);

   ---------------------
   -- PGP Front End Core
   ---------------------
   Pgp_Config : if (COMM_MODE_G = false) generate
      
      U_PGP : entity work.AtlasChess2FebPgpCore
         generic map (
            TPD_G            => TPD_G,
            AXI_ERROR_RESP_G => AXI_ERROR_RESP_G)   
         port map (
            -- Reference Clock and Reset
            refclk200MHz     => refclk200MHz,
            refRst200MHz     => refRst200MHz,
            -- AXI-Lite Interface   
            axilClk          => axilClk,
            axilRst          => axilRst,
            mAxilReadMaster  => sAxilReadMasters(0),
            mAxilReadSlave   => sAxilReadSlaves(0),
            mAxilWriteMaster => sAxilWriteMasters(0),
            mAxilWriteSlave  => sAxilWriteSlaves(0),
            -- Streaming CHESS2 Data (axilClk domain)
            sAxisMaster      => chessMaster,
            sAxisSlave       => chessSlave,
            -- MB Interface (axilClk domain)
            mbTxMaster       => mbTxMaster,
            mbTxSlave        => mbTxSlave,
            -- Trigger Interface (axilClk domain)
            pgpTxIn          => pgpTxIn,
            pgpTxOut         => pgpTxOut,
            pgpRxIn          => pgpRxIn,
            pgpRxOut         => pgpRxOut,
            -- PGP Ports
            pgpClkP          => gtClkP,
            pgpClkN          => gtClkN,
            pgpRxP           => gtRxP,
            pgpRxN           => gtRxN,
            pgpTxP           => gtTxP,
            pgpTxN           => gtTxN);    

      U_ETH : entity work.AxiLiteEmpty
         generic map (
            TPD_G => TPD_G)
         port map (
            -- AXI-Lite Bus
            axiClk         => axilClk,
            axiClkRst      => axilRst,
            axiReadMaster  => mAxilReadMasters(ETH_INDEX_C),
            axiReadSlave   => mAxilReadSlaves(ETH_INDEX_C),
            axiWriteMaster => mAxilWriteMasters(ETH_INDEX_C),
            axiWriteSlave  => mAxilWriteSlaves(ETH_INDEX_C));              

   end generate;

   ---------------------
   -- GbE Front End Core
   ---------------------
   Eth_Config : if (COMM_MODE_G = true) generate
      
      U_ETH : entity work.AtlasChess2FebEthCore
         generic map (
            TPD_G            => TPD_G,
            DEV_G            => ETH_DEV_G,
            DHCP_G           => ETH_DHCP_G,
            IP_ADDR_G        => ETH_IP_ADDR_G,
            AXI_ERROR_RESP_G => AXI_ERROR_RESP_G)   
         port map (
            -- Reference Clock and Reset
            refclk200MHz     => refclk200MHz,
            refRst200MHz     => refRst200MHz,
            -- AXI-Lite Interface   
            axilClk          => axilClk,
            axilRst          => axilRst,
            mAxilReadMaster  => sAxilReadMasters(0),
            mAxilReadSlave   => sAxilReadSlaves(0),
            mAxilWriteMaster => sAxilWriteMasters(0),
            mAxilWriteSlave  => sAxilWriteSlaves(0),
            -- Streaming CHESS2 Data (axilClk domain)
            sAxisMaster      => chessMaster,
            sAxisSlave       => chessSlave,
            -- MB Interface (axilClk domain)
            mbTxMaster       => mbTxMaster,
            mbTxSlave        => mbTxSlave,
            -- Emulate PGP Timing Interface
            pgpTxIn          => pgpTxIn,
            pgpTxOut         => pgpTxOut,
            pgpRxIn          => pgpRxIn,
            pgpRxOut         => pgpRxOut,
            -- Eth/RSSI Status
            phyReady         => ethReady,
            rssiStatus       => rssiStatus,
            axilReadMaster   => mAxilReadMasters(ETH_INDEX_C),
            axilReadSlave    => mAxilReadSlaves(ETH_INDEX_C),
            axilWriteMaster  => mAxilWriteMasters(ETH_INDEX_C),
            axilWriteSlave   => mAxilWriteSlaves(ETH_INDEX_C),
            -- GbE Ports
            gtClkP           => gtClkP,
            gtClkN           => gtClkN,
            gtRxP            => gtRxP,
            gtRxN            => gtRxN,
            gtTxP            => gtTxP,
            gtTxN            => gtTxN);    

   end generate;

   --------------------------
   -- AXI-Lite: Crossbar Core
   --------------------------  
   U_XBAR : entity work.AxiLiteCrossbar
      generic map (
         TPD_G              => TPD_G,
         DEC_ERROR_RESP_G   => AXI_ERROR_RESP_G,
         NUM_SLAVE_SLOTS_G  => NUM_AXIL_SLAVES_C,
         NUM_MASTER_SLOTS_G => NUM_AXIL_MASTERS_C,
         MASTERS_CONFIG_G   => AXIL_CROSSBAR_CONFIG_C)
      port map (
         axiClk           => axilClk,
         axiClkRst        => axilRst,
         sAxiWriteMasters => sAxilWriteMasters,
         sAxiWriteSlaves  => sAxilWriteSlaves,
         sAxiReadMasters  => sAxilReadMasters,
         sAxiReadSlaves   => sAxilReadSlaves,
         mAxiWriteMasters => mAxilWriteMasters,
         mAxiWriteSlaves  => mAxilWriteSlaves,
         mAxiReadMasters  => mAxilReadMasters,
         mAxiReadSlaves   => mAxilReadSlaves);

   -----------------
   -- System Wrapper
   -----------------
   U_Sys : entity work.AtlasChess2FebSys
      generic map (
         TPD_G            => TPD_G,
         FSBL_G           => false,     -- not supported in standard build
         AXI_ERROR_RESP_G => AXI_ERROR_RESP_G)
      port map (
         -- Timing Clock and Reset
         timingClk320MHz  => timingClk320MHz,
         timingRst320MHz  => timingRst320MHz,
         -- AXI-Lite Interface   
         axilClk          => axilClk,
         axilRst          => axilRst,
         mbReadMaster     => sAxilReadMasters(1),
         mbReadSlave      => sAxilReadSlaves(1),
         mbWriteMaster    => sAxilWriteMasters(1),
         mbWriteSlave     => sAxilWriteSlaves(1),
         sAxilReadMaster  => mAxilReadMasters(SYS_INDEX_C),
         sAxilReadSlave   => mAxilReadSlaves(SYS_INDEX_C),
         sAxilWriteMaster => mAxilWriteMasters(SYS_INDEX_C),
         sAxilWriteSlave  => mAxilWriteSlaves(SYS_INDEX_C),
         -- System Interface 
         status           => status,
         config           => config,
         -- System Ports
         tempAlertL       => tempAlertL,
         pwrScl           => pwrScl,
         pwrSda           => pwrSda,
         configScl        => configScl,
         configSda        => configSda,
         -- Boot Memory Ports
         bootCsL          => bootCsL,
         bootMosi         => bootMosi,
         bootMiso         => bootMiso,
         -- MB Interface
         mbTxMaster       => mbTxMaster,
         mbTxSlave        => mbTxSlave,
         -- XADC Ports
         vPIn             => vPIn,
         vNIn             => vNIn);

   --------------
   -- DAC Modules
   --------------
   U_Dac : entity work.AtlasChess2FebDac
      generic map (
         TPD_G            => TPD_G,
         AXI_BASE_ADDR_G  => AXIL_CROSSBAR_CONFIG_C(DAC_INDEX_C).baseAddr,
         AXI_CLK_FREQ_G   => AXIL_CLK_FREQ_C,
         AXI_ERROR_RESP_G => AXI_ERROR_RESP_G)
      port map (
         -- AXI-Lite Interface
         axilClk         => axilClk,
         axilRst         => axilRst,
         axilReadMaster  => mAxilReadMasters(DAC_INDEX_C),
         axilReadSlave   => mAxilReadSlaves(DAC_INDEX_C),
         axilWriteMaster => mAxilWriteMasters(DAC_INDEX_C),
         axilWriteSlave  => mAxilWriteSlaves(DAC_INDEX_C),
         -- DAC Ports
         dacSlowCsL      => dacSlowCsL,
         dacSlowSck      => dacSlowSck,
         dacSlowMosi     => dacSlowMosi);

   ------------------
   -- Timing TRIG/MSG 
   ------------------         
   U_Timing : entity work.AtlasChess2FebTiming
      generic map(
         TPD_G            => TPD_G,
         AXI_BASE_ADDR_G  => AXIL_CROSSBAR_CONFIG_C(TIMING_INDEX_C).baseAddr,
         AXI_ERROR_RESP_G => AXI_ERROR_RESP_G) 
      port map(
         -- AXI-Lite Interface
         axilClk         => axilClk,
         axilRst         => axilRst,
         axilReadMaster  => mAxilReadMasters(TIMING_INDEX_C),
         axilReadSlave   => mAxilReadSlaves(TIMING_INDEX_C),
         axilWriteMaster => mAxilWriteMasters(TIMING_INDEX_C),
         axilWriteSlave  => mAxilWriteSlaves(TIMING_INDEX_C),
         -- Timing Interface
         timingClk320MHz => timingClk320MHz,
         timingRst320MHz => timingRst320MHz,
         timingTrig      => timingTrig,
         timingMsg       => timingMsg,
         timingMode      => config.timingMode,
         softTrig        => config.softTrig,
         evrOpCode       => evrOpCode,
         -- Reference Clock and Reset
         refclk200MHz    => refclk200MHz,
         refRst200MHz    => refRst200MHz,
         -- System Ports
         extTrigL        => extTrigL,
         -- PGP Timing Interface
         pgpTxIn         => pgpTxIn,
         pgpTxOut        => pgpTxOut,
         pgpRxIn         => pgpRxIn,
         pgpRxOut        => pgpRxOut,
         -- SLAC Timing Ports
         evrClkP         => evrClkP,
         evrClkN         => evrClkN,
         evrRxP          => evrRxP,
         evrRxN          => evrRxN,
         evrTxP          => evrTxP,
         evrTxN          => evrTxN);           

   -------------------
   -- CHESS2 RX Engine
   -------------------
   U_Asic : entity work.AtlasChess2FebAsic
      generic map (
         TPD_G            => TPD_G,
         AXI_BASE_ADDR_G  => AXIL_CROSSBAR_CONFIG_C(CHESS2_INDEX_C).baseAddr,
         AXI_ERROR_RESP_G => AXI_ERROR_RESP_G)
      port map(
         -- System Ports
         extBusy         => extBusy,
         -- CHESS2 ASIC Serial Ports
         chessDinP       => chessDinP,
         chessDinN       => chessDinN,
         chessClk320MHzP => chessClk320MHzP,
         chessClk320MHzN => chessClk320MHzN,
         chessClk40MHz   => chessClk40MHz,
         -- Reference clock and Reset
         refClk200MHz    => refClk200MHz,
         refRst200MHz    => refRst200MHz,
         -- Timing Interface
         timingClk40MHz  => timingClk40MHz,
         timingRst40MHz  => timingRst40MHz,
         timingClk320MHz => timingClk320MHz,
         timingRst320MHz => timingRst320MHz,
         timingTrig      => timingTrig,
         timingMsg       => timingMsg,
         dlyRst          => config.dlyRst,
         dlyTiming       => config.dlyTiming,
         dlyChess        => config.dlyChess,
         -- CHESS2 RX MSG Configuration
         destId          => config.destId,
         opCode          => evrOpCode,
         frameType       => config.frameType,
         wordSize        => config.wordSize,
         -- AXI Stream Interface
         axisClk         => axilClk,
         axisRst         => axilRst,
         mAxisMaster     => chessMaster,
         mAxisSlave      => chessSlave,
         -- AXI-Lite Register Interface
         axilClk         => axilClk,
         axilRst         => axilRst,
         axilReadMaster  => mAxilReadMasters(CHESS2_INDEX_C),
         axilReadSlave   => mAxilReadSlaves(CHESS2_INDEX_C),
         axilWriteMaster => mAxilWriteMasters(CHESS2_INDEX_C),
         axilWriteSlave  => mAxilWriteSlaves(CHESS2_INDEX_C));

   -----------------
   -- AXI-Lite: SACI
   -----------------
   U_SACI : entity work.AxiLiteSaciMaster
      generic map (
         TPD_G              => TPD_G,
         AXIL_ERROR_RESP_G  => AXI_ERROR_RESP_G,
         AXIL_CLK_PERIOD_G  => (1.0/AXIL_CLK_FREQ_C),    -- In units of seconds
         AXIL_TIMEOUT_G     => 1.0E-3,                   -- In units of seconds
         SACI_CLK_PERIOD_G  => (256.0/AXIL_CLK_FREQ_C),  -- In units of seconds        
         SACI_CLK_FREERUN_G => false,
         SACI_NUM_CHIPS_G   => 4,
         SACI_RSP_BUSSED_G  => false)
      port map (
         -- SACI interface
         saciClk         => saciClk,
         saciCmd         => saciCmd,
         saciSelL        => saciSelL,
         saciRsp         => saciRsp,
         -- AXI-Lite Register Interface
         axilClk         => axilClk,
         axilRst         => axilRst,
         axilReadMaster  => mAxilReadMasters(SACI_INDEX_C),
         axilReadSlave   => mAxilReadSlaves(SACI_INDEX_C),
         axilWriteMaster => mAxilWriteMasters(SACI_INDEX_C),
         axilWriteSlave  => mAxilWriteSlaves(SACI_INDEX_C));

end mapping;
