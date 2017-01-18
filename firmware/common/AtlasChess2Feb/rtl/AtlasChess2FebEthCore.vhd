-------------------------------------------------------------------------------
-- Title      : 
-------------------------------------------------------------------------------
-- File       : AtlasChess2FebEthCore.vhd
-- Author     : Larry Ruckman  <ruckman@slac.stanford.edu>
-- Company    : SLAC National Accelerator Laboratory
-- Created    : 2016-06-02
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
use work.SsiPkg.all;
use work.EthMacPkg.all;
use work.AtlasChess2FebPkg.all;
use work.Pgp2bPkg.all;

library unisim;
use unisim.vcomponents.all;

entity AtlasChess2FebEthCore is
   generic (
      TPD_G            : time             := 1 ns;
      DEV_G            : boolean          := true;         -- true = Adds non-RSSI on port 8193
      DHCP_G           : boolean          := true;         -- true = DHCP, false = static address
      IP_ADDR_G        : slv(31 downto 0) := x"0A01A8C0";  -- 192.168.1.10 (before DHCP)
      AXI_ERROR_RESP_G : slv(1 downto 0)  := AXI_RESP_DECERR_C);        
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
      -- Emulate PGP Timing Interface
      pgpTxIn          : in  Pgp2bTxInType;
      pgpTxOut         : out Pgp2bTxOutType;
      pgpRxIn          : in  Pgp2bRxInType;
      pgpRxOut         : out Pgp2bRxOutType;
      -- Eth/RSSI Status
      phyReady         : out sl;
      rssiStatus       : out slv(6 downto 0);
      axilReadMaster   : in  AxiLiteReadMasterType;
      axilReadSlave    : out AxiLiteReadSlaveType;
      axilWriteMaster  : in  AxiLiteWriteMasterType;
      axilWriteSlave   : out AxiLiteWriteSlaveType;
      -- GbE Ports
      gtClkP           : in  sl;
      gtClkN           : in  sl;
      gtRxP            : in  sl;
      gtRxN            : in  sl;
      gtTxP            : out sl;
      gtTxN            : out sl);
end AtlasChess2FebEthCore;

architecture mapping of AtlasChess2FebEthCore is

   constant SERVER_SIZE_C  : positive                  := ite(DEV_G, 2, 1);
   constant SERVER_PORTS_C : PositiveArray(1 downto 0) := (0 => 8192, 1 => 8193);
   constant AXIL_CROSSBAR_CONFIG_C : AxiLiteCrossbarMasterConfigArray(0 downto 0) := (
      0               => (
         baseAddr     => x"00000000",
         addrBits     => 31,
         connectivity => x"FFFF"));    

   constant RSSI_SIZE_C   : positive                                     := 3;
   constant AXIS_CONFIG_C : AxiStreamConfigArray(RSSI_SIZE_C-1 downto 0) := (others => ssiAxiStreamConfig(4));

   signal gtClkDiv2  : sl;
   signal refClk     : sl;
   signal refRst     : sl;
   signal ethClk     : sl;
   signal ethRst     : sl;
   signal ethClkDiv2 : sl;
   signal ethRstDiv2 : sl;

   signal efuse    : slv(31 downto 0);
   signal localMac : slv(47 downto 0);

   signal rxMaster : AxiStreamMasterType;
   signal rxSlave  : AxiStreamSlaveType;
   signal txMaster : AxiStreamMasterType;
   signal txSlave  : AxiStreamSlaveType;

   signal ibServerMasters : AxiStreamMasterArray(SERVER_SIZE_C-1 downto 0);
   signal ibServerSlaves  : AxiStreamSlaveArray(SERVER_SIZE_C-1 downto 0);
   signal obServerMasters : AxiStreamMasterArray(SERVER_SIZE_C-1 downto 0);
   signal obServerSlaves  : AxiStreamSlaveArray(SERVER_SIZE_C-1 downto 0);

   signal rssiIbMasters : AxiStreamMasterArray(RSSI_SIZE_C-1 downto 0);
   signal rssiIbSlaves  : AxiStreamSlaveArray(RSSI_SIZE_C-1 downto 0);
   signal rssiObMasters : AxiStreamMasterArray(RSSI_SIZE_C-1 downto 0);
   signal rssiObSlaves  : AxiStreamSlaveArray(RSSI_SIZE_C-1 downto 0);

   signal mAxilReadMasters  : AxiLiteReadMasterArray(SERVER_SIZE_C-1 downto 0);
   signal mAxilReadSlaves   : AxiLiteReadSlaveArray(SERVER_SIZE_C-1 downto 0);
   signal mAxilWriteMasters : AxiLiteWriteMasterArray(SERVER_SIZE_C-1 downto 0);
   signal mAxilWriteSlaves  : AxiLiteWriteSlaveArray(SERVER_SIZE_C-1 downto 0);

   signal pgpRxTrig : Pgp2bRxOutType := PGP2B_RX_OUT_INIT_C;
   
begin

   axilClk <= ethClk;
   axilRst <= ethRst;

   --------------------
   -- Local MAC Address
   --------------------
   U_EFuse : EFUSE_USR
      port map (
         EFUSEUSR => efuse);

   localMac(23 downto 0)  <= x"56_00_08";  -- 08:00:56:XX:XX:XX (big endian SLV)   
   localMac(47 downto 24) <= efuse(31 downto 8);

   ------------------
   -- Reference Clock
   ------------------
   U_IBUFDS_GTE2 : IBUFDS_GTE2
      port map (
         I     => gtClkP,
         IB    => gtClkN,
         CEB   => '0',
         ODIV2 => gtClkDiv2,
         O     => open);    

   U_BUFG : BUFG
      port map (
         I => gtClkDiv2,
         O => refClk);

   -----------------
   -- Power Up Reset
   -----------------
   U_PwrUpRst : entity work.PwrUpRst
      generic map (
         TPD_G => TPD_G)
      port map (
         clk    => refClk,
         rstOut => refRst);   

   ----------------
   -- Clock Manager
   ----------------
   U_MMCM : entity work.ClockManager7
      generic map(
         TPD_G              => TPD_G,
         TYPE_G             => "MMCM",
         INPUT_BUFG_G       => false,
         FB_BUFG_G          => true,
         RST_IN_POLARITY_G  => '1',
         NUM_CLOCKS_G       => 3,
         -- MMCM attributes
         BANDWIDTH_G        => "OPTIMIZED",
         CLKIN_PERIOD_G     => 6.4,     -- 156.25 MHz
         DIVCLK_DIVIDE_G    => 5,       -- 31.25 MHz = 156.25 MHz/5
         CLKFBOUT_MULT_F_G  => 32.0,    -- 1.0GHz = 32 x 31.25 MHz
         CLKOUT0_DIVIDE_F_G => 8.0,     -- 125 MHz = 1.0GHz/8
         CLKOUT1_DIVIDE_G   => 16,      -- 62.5 MHz = 1.0GHz/16
         CLKOUT2_DIVIDE_G   => 5)       -- 200 MHz = 1.0GHz/5
      port map(
         clkIn     => refClk,
         rstIn     => refRst,
         clkOut(0) => ethClk,
         clkOut(1) => ethClkDiv2,
         clkOut(2) => refclk200MHz,
         rstOut(0) => ethRst,
         rstOut(1) => ethRstDiv2,
         rstOut(2) => refRst200MHz); 

   -------------------------
   -- GigE Core for KINTEX-7
   -------------------------
   U_ETH_PHY_MAC : entity work.GigEthGtx7
      generic map (
         TPD_G         => TPD_G,
         AXIS_CONFIG_G => EMAC_AXIS_CONFIG_C)
      port map (
         -- Local Configurations
         localMac    => localMac,
         -- Streaming DMA Interface 
         dmaClk      => ethClk,
         dmaRst      => ethRst,
         dmaIbMaster => rxMaster,
         dmaIbSlave  => rxSlave,
         dmaObMaster => txMaster,
         dmaObSlave  => txSlave,
         -- PHY + MAC signals
         sysClk62    => ethClkDiv2,
         sysClk125   => ethClk,
         sysRst125   => ethRst,
         extRst      => refRst,
         phyReady    => phyReady,
         -- MGT Ports
         gtTxP       => gtTxP,
         gtTxN       => gtTxN,
         gtRxP       => gtRxP,
         gtRxN       => gtRxN);          

   ----------------------
   -- IPv4/ARP/UDP Engine
   ----------------------
   U_UDP : entity work.UdpEngineWrapper
      generic map (
         -- Simulation Generics
         TPD_G          => TPD_G,
         -- UDP Server Generics
         SERVER_EN_G    => true,
         SERVER_SIZE_G  => SERVER_SIZE_C,
         SERVER_PORTS_G => SERVER_PORTS_C,
         -- UDP Client Generics
         CLIENT_EN_G    => false,
         -- General IPv4/ARP/DHCP Generics
         DHCP_G         => DHCP_G,
         CLK_FREQ_G     => 125.0E+6,
         COMM_TIMEOUT_G => 30)
      port map (
         -- Local Configurations
         localMac        => localMac,
         localIp         => IP_ADDR_G,
         -- Interface to Ethernet Media Access Controller (MAC)
         obMacMaster     => rxMaster,
         obMacSlave      => rxSlave,
         ibMacMaster     => txMaster,
         ibMacSlave      => txSlave,
         -- Interface to UDP Server engine(s)
         obServerMasters => obServerMasters,
         obServerSlaves  => obServerSlaves,
         ibServerMasters => ibServerMasters,
         ibServerSlaves  => ibServerSlaves,
         -- Clock and Reset
         clk             => ethClk,
         rst             => ethRst); 

   ------------------------------------------
   -- Software's RSSI Server Interface @ 8192
   ------------------------------------------
   U_RssiServer : entity work.RssiCoreWrapper
      generic map (
         TPD_G               => TPD_G,
         MAX_SEG_SIZE_G      => 1024,
         SEGMENT_ADDR_SIZE_G => 7,
         APP_STREAMS_G       => RSSI_SIZE_C,
         APP_STREAM_ROUTES_G => (
            0                => X"00",
            1                => X"01",
            2                => X"02"),
         CLK_FREQUENCY_G     => 125.0E+6,
         TIMEOUT_UNIT_G      => 1.0E-3,  -- In units of seconds
         SERVER_G            => true,
         RETRANSMIT_ENABLE_G => true,
         BYPASS_CHUNKER_G    => false,
         WINDOW_ADDR_SIZE_G  => 3,
         PIPE_STAGES_G       => 1,
         APP_AXIS_CONFIG_G   => AXIS_CONFIG_C,
         TSP_AXIS_CONFIG_G   => EMAC_AXIS_CONFIG_C,
         INIT_SEQ_N_G        => 16#80#)
      port map (
         clk_i             => ethClk,
         rst_i             => ethRst,
         openRq_i          => '1',
         -- Application Layer Interface
         sAppAxisMasters_i => rssiIbMasters,
         sAppAxisSlaves_o  => rssiIbSlaves,
         mAppAxisMasters_o => rssiObMasters,
         mAppAxisSlaves_i  => rssiObSlaves,
         -- Transport Layer Interface
         sTspAxisMaster_i  => obServerMasters(0),
         sTspAxisSlave_o   => obServerSlaves(0),
         mTspAxisMaster_o  => ibServerMasters(0),
         mTspAxisSlave_i   => ibServerSlaves(0),
         -- AXI-Lite Interface
         axiClk_i          => ethClk,
         axiRst_i          => ethRst,
         axilReadMaster    => axilReadMaster,
         axilReadSlave     => axilReadSlave,
         axilWriteMaster   => axilWriteMaster,
         axilWriteSlave    => axilWriteSlave,
         -- Internal statuses
         statusReg_o       => rssiStatus);         

   ---------------------------------------
   -- TDEST = 0x0: Register access control   
   ---------------------------------------
   U_SRPv0 : entity work.SrpV0AxiLite
      generic map (
         TPD_G               => TPD_G,
         RESP_THOLD_G        => 1,
         SLAVE_READY_EN_G    => true,
         EN_32BIT_ADDR_G     => true,
         BRAM_EN_G           => true,
         XIL_DEVICE_G        => "7SERIES",
         USE_BUILT_IN_G      => false,
         ALTERA_SYN_G        => false,
         ALTERA_RAM_G        => "M9K",
         GEN_SYNC_FIFO_G     => true,
         FIFO_ADDR_WIDTH_G   => 9,
         FIFO_PAUSE_THRESH_G => 2**8,
         AXI_STREAM_CONFIG_G => AXIS_CONFIG_C(0))            
      port map (
         -- Streaming Slave (Rx) Interface (sAxisClk domain) 
         sAxisClk            => ethClk,
         sAxisRst            => ethRst,
         sAxisMaster         => rssiObMasters(0),
         sAxisSlave          => rssiObSlaves(0),
         -- Streaming Master (Tx) Data Interface (mAxisClk domain)
         mAxisClk            => ethClk,
         mAxisRst            => ethRst,
         mAxisMaster         => rssiIbMasters(0),
         mAxisSlave          => rssiIbSlaves(0),
         -- AXI Lite Bus (axiLiteClk domain)
         axiLiteClk          => ethClk,
         axiLiteRst          => ethRst,
         mAxiLiteReadMaster  => mAxilReadMasters(0),
         mAxiLiteReadSlave   => mAxilReadSlaves(0),
         mAxiLiteWriteMaster => mAxilWriteMasters(0),
         mAxiLiteWriteSlave  => mAxilWriteSlaves(0));       

   -----------------------------------------------------
   -- TDEST = 0x1: Streaming CHESS2 Data Interface  
   -- TDEST = 0x1: Emulate PGP's non-VC Timing Interface  
   -----------------------------------------------------
   rssiIbMasters(1)   <= sAxisMaster;
   sAxisSlave         <= rssiIbSlaves(1);
   rssiObSlaves(1)    <= AXI_STREAM_SLAVE_FORCE_C;  -- always ready
   pgpRxTrig.opCodeEn <= rssiObMasters(1).tValid and rssiObMasters(1).tLast;
   pgpRxTrig.opCode   <= rssiObMasters(1).tData(7 downto 0);

   ----------------------------
   -- TDEST = 0x2: MB Interface  
   ----------------------------
   rssiIbMasters(2) <= mbTxMaster;
   mbTxSlave        <= rssiIbSlaves(2);
   rssiObSlaves(2)  <= AXI_STREAM_SLAVE_FORCE_C;  -- Blowoff unused stream

   -----------------------------------      
   -- Bypass non-RSSI Development Path 
   -----------------------------------      
   BYP_DEBUG_SRP : if (DEV_G = false) generate
      
      mAxilReadMaster     <= mAxilReadMasters(0);
      mAxilReadSlaves(0)  <= mAxilReadSlave;
      mAxilWriteMaster    <= mAxilWriteMasters(0);
      mAxilWriteSlaves(0) <= mAxilWriteSlave;
      
   end generate;

   ----------------------------
   -- Non-RSSI Development Path 
   ----------------------------   
   GEN_DEBUG_SRP : if (DEV_G = true) generate
      
      U_SRPv0_Debug : entity work.SrpV0AxiLite
         generic map (
            TPD_G               => TPD_G,
            RESP_THOLD_G        => 1,
            SLAVE_READY_EN_G    => true,
            EN_32BIT_ADDR_G     => true,
            BRAM_EN_G           => true,
            XIL_DEVICE_G        => "7SERIES",
            USE_BUILT_IN_G      => false,
            ALTERA_SYN_G        => false,
            ALTERA_RAM_G        => "M9K",
            GEN_SYNC_FIFO_G     => true,
            FIFO_ADDR_WIDTH_G   => 9,
            FIFO_PAUSE_THRESH_G => 2**8,
            AXI_STREAM_CONFIG_G => EMAC_AXIS_CONFIG_C)            
         port map (
            -- Streaming Slave (Rx) Interface (sAxisClk domain) 
            sAxisClk            => ethClk,
            sAxisRst            => ethRst,
            sAxisMaster         => obServerMasters(1),
            sAxisSlave          => obServerSlaves(1),
            -- Streaming Master (Tx) Data Interface (mAxisClk domain)
            mAxisClk            => ethClk,
            mAxisRst            => ethRst,
            mAxisMaster         => ibServerMasters(1),
            mAxisSlave          => ibServerSlaves(1),
            -- AXI Lite Bus (axiLiteClk domain)
            axiLiteClk          => ethClk,
            axiLiteRst          => ethRst,
            mAxiLiteReadMaster  => mAxilReadMasters(1),
            mAxiLiteReadSlave   => mAxilReadSlaves(1),
            mAxiLiteWriteMaster => mAxilWriteMasters(1),
            mAxiLiteWriteSlave  => mAxilWriteSlaves(1));        


      U_XBAR : entity work.AxiLiteCrossbar
         generic map (
            TPD_G              => TPD_G,
            DEC_ERROR_RESP_G   => AXI_ERROR_RESP_G,
            NUM_SLAVE_SLOTS_G  => 2,
            NUM_MASTER_SLOTS_G => 1,
            MASTERS_CONFIG_G   => AXIL_CROSSBAR_CONFIG_C)
         port map (
            axiClk              => ethClk,
            axiClkRst           => ethRst,
            sAxiWriteMasters    => mAxilWriteMasters,
            sAxiWriteSlaves     => mAxilWriteSlaves,
            sAxiReadMasters     => mAxilReadMasters,
            sAxiReadSlaves      => mAxilReadSlaves,
            mAxiWriteMasters(0) => mAxilWriteMaster,
            mAxiWriteSlaves(0)  => mAxilWriteSlave,
            mAxiReadMasters(0)  => mAxilReadMaster,
            mAxiReadSlaves(0)   => mAxilReadSlave);   

   end generate;
   
end mapping;
