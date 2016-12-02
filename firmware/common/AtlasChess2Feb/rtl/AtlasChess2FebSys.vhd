-------------------------------------------------------------------------------
-- Title      : 
-------------------------------------------------------------------------------
-- File       : AtlasChess2FebSys.vhd
-- Author     : Larry Ruckman  <ruckman@slac.stanford.edu>
-- Company    : SLAC National Accelerator Laboratory
-- Created    : 2016-06-07
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
use ieee.std_logic_arith.all;
use ieee.std_logic_unsigned.all;

use work.StdRtlPkg.all;
use work.AxiLitePkg.all;
use work.AxiStreamPkg.all;
use work.I2cPkg.all;
use work.AtlasChess2FebPkg.all;

library unisim;
use unisim.vcomponents.all;

entity AtlasChess2FebSys is
   generic (
      TPD_G            : time            := 1 ns;
      FSBL_G           : boolean         := false;
      CPU_G            : boolean         := false;  -- True=Microblaze, False=No Microblaze
      AXI_CLK_FREQ_G   : real            := 156.25E+6;
      AXI_ERROR_RESP_G : slv(1 downto 0) := AXI_RESP_DECERR_C);      
   port (
      -- Timing Clock and Reset
      timingClk320MHz  : in    sl;
      timingRst320MHz  : in    sl;
      -- AXI-Lite Interface   
      axilClk          : in    sl;
      axilRst          : in    sl;
      mbReadMaster     : out   AxiLiteReadMasterType;
      mbReadSlave      : in    AxiLiteReadSlaveType;
      mbWriteMaster    : out   AxiLiteWriteMasterType;
      mbWriteSlave     : in    AxiLiteWriteSlaveType;
      sAxilWriteMaster : in    AxiLiteWriteMasterType;
      sAxilWriteSlave  : out   AxiLiteWriteSlaveType;
      sAxilReadMaster  : in    AxiLiteReadMasterType;
      sAxilReadSlave   : out   AxiLiteReadSlaveType;
      -- System Interface 
      status           : in    AtlasChess2FebStatusType;
      config           : out   AtlasChess2FebConfigType;
      -- System Ports
      tempAlertL       : in    sl;
      oeClk            : out   Slv(2 downto 0);
      pwrScl           : inout sl;
      pwrSda           : inout sl;
      configScl        : inout sl;
      configSda        : inout sl;
      -- Boot Memory Ports
      bootCsL          : out   sl;
      bootMosi         : out   sl;
      bootMiso         : in    sl;
      -- MB Interface
      mbTxMaster       : out   AxiStreamMasterType;
      mbTxSlave        : in    AxiStreamSlaveType;
      -- XADC Ports
      vPIn             : in    sl;
      vNIn             : in    sl); 
end AtlasChess2FebSys;

architecture mapping of AtlasChess2FebSys is

   constant SHARED_MEM_WIDTH_C : positive                           := 9;
   constant IRQ_ADDR_C         : slv(SHARED_MEM_WIDTH_C-1 downto 0) := (others => '1');

   constant NUM_AXIL_MASTERS_C : natural := 7;

   constant VERSION_INDEX_C  : natural := 0;
   constant XADC_INDEX_C     : natural := 1;
   constant BOOT_MEM_INDEX_C : natural := 2;
   constant SYS_REG_INDEX_C  : natural := 3;
   constant MEM_INDEX_C      : natural := 4;
   constant PWR_INDEX_C      : natural := 5;
   constant CONFIG_INDEX_C   : natural := 6;

   constant VERSION_ADDR_C  : slv(31 downto 0) := x"00000000";
   constant XADC_ADDR_C     : slv(31 downto 0) := x"00010000";
   constant BOOT_MEM_ADDR_C : slv(31 downto 0) := x"00020000";
   constant SYS_REG_ADDR_C  : slv(31 downto 0) := x"00030000";
   constant MEM_REG_ADDR_C  : slv(31 downto 0) := x"00040000";
   constant PWR_ADDR_C      : slv(31 downto 0) := x"00050000";
   constant CONFIG_ADDR_C   : slv(31 downto 0) := x"00060000";

   constant AXIL_CROSSBAR_CONFIG_C : AxiLiteCrossbarMasterConfigArray(NUM_AXIL_MASTERS_C-1 downto 0) := (
      VERSION_INDEX_C  => (
         baseAddr      => VERSION_ADDR_C,
         addrBits      => 16,
         connectivity  => x"FFFF"),
      XADC_INDEX_C     => (
         baseAddr      => XADC_ADDR_C,
         addrBits      => 16,
         connectivity  => x"FFFF"),
      BOOT_MEM_INDEX_C => (
         baseAddr      => BOOT_MEM_ADDR_C,
         addrBits      => 16,
         connectivity  => x"FFFF"),
      SYS_REG_INDEX_C  => (
         baseAddr      => SYS_REG_ADDR_C,
         addrBits      => 16,
         connectivity  => x"FFFF"),
      MEM_INDEX_C      => (
         baseAddr      => MEM_REG_ADDR_C,
         addrBits      => 16,
         connectivity  => x"FFFF"),
      PWR_INDEX_C      => (
         baseAddr      => PWR_ADDR_C,
         addrBits      => 16,
         connectivity  => x"FFFF"),
      CONFIG_INDEX_C   => (
         baseAddr      => CONFIG_ADDR_C,
         addrBits      => 16,
         connectivity  => x"FFFF"));  

   signal mAxilWriteMasters : AxiLiteWriteMasterArray(NUM_AXIL_MASTERS_C-1 downto 0);
   signal mAxilWriteSlaves  : AxiLiteWriteSlaveArray(NUM_AXIL_MASTERS_C-1 downto 0);
   signal mAxilReadMasters  : AxiLiteReadMasterArray(NUM_AXIL_MASTERS_C-1 downto 0);
   signal mAxilReadSlaves   : AxiLiteReadSlaveArray(NUM_AXIL_MASTERS_C-1 downto 0);
   
   constant PWR_I2C_C : I2cAxiLiteDevArray(0 to 1) := (
      0             => MakeI2cAxiLiteDevType(
         i2cAddress => "1101111",       -- 0xDE = LTC4151CMS#PBF
         dataSize   => 8,               -- in units of bits
         addrSize   => 8,               -- in units of bits
         endianness => '1'),            -- Big endian   
      1             => MakeI2cAxiLiteDevType(
         i2cAddress => "1001000",       -- 0x90 = SA56004ATK
         dataSize   => 8,               -- in units of bits
         addrSize   => 8,               -- in units of bits
         endianness => '1'));           -- Big endian                   

   signal bootSck    : sl;
   signal axiWrValid : sl;
   signal axiWrAddr  : slv(SHARED_MEM_WIDTH_C-1 downto 0);
   signal irqReq     : slv(7 downto 0);
   signal irqCount   : slv(27 downto 0);

begin

   ----------------------------
   -- AXI-Lite: Microblaze Core
   ----------------------------
   GEN_CPU : if CPU_G = true generate
      
      U_CPU : entity work.MicroblazeBasicCoreWrapper
         generic map (
            TPD_G           => TPD_G,
            AXIL_ADDR_MSB_C => false)
         port map (
            -- Master AXI-Lite Interface: [0x00000000:0x7FFFFFFF]
            mAxilWriteMaster => mbWriteMaster,
            mAxilWriteSlave  => mbWriteSlave,
            mAxilReadMaster  => mbReadMaster,
            mAxilReadSlave   => mbReadSlave,
            -- Streaming
            mAxisMaster      => mbTxMaster,
            mAxisSlave       => mbTxSlave,
            -- IRQ
            interrupt        => irqReq,
            -- Clock and Reset
            clk              => axilClk,
            rst              => axilRst);    

      -----------------------------
      -- Microblaze User Interrupts
      -----------------------------
      process (axilClk)
      begin
         if rising_edge(axilClk) then
            irqReq <= (others => '0') after TPD_G;
            if axilRst = '1' then
               irqCount <= (others => '0') after TPD_G;
            else
               -- IRQ[0]
               if irqCount = x"9502f90" then
                  irqReq(0) <= '1'             after TPD_G;
                  irqCount  <= (others => '0') after TPD_G;
               else
                  irqCount <= irqCount + 1 after TPD_G;
               end if;
               -- IRQ[1]
               if (axiWrValid = '1') and (axiWrAddr = IRQ_ADDR_C) then
                  irqReq(1) <= '1' after TPD_G;
               end if;
            end if;
         end if;
      end process;
      
   end generate GEN_CPU;

   GEN_N_CPU : if CPU_G = false generate
      mbWriteMaster <= AXI_LITE_WRITE_MASTER_INIT_C;
      mbReadMaster  <= AXI_LITE_READ_MASTER_INIT_C;
   end generate GEN_N_CPU;

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
         sAxiWriteMasters(0) => sAxilWriteMaster,
         sAxiWriteSlaves(0)  => sAxilWriteSlave,
         sAxiReadMasters(0)  => sAxilReadMaster,
         sAxiReadSlaves(0)   => sAxilReadSlave,
         mAxiWriteMasters    => mAxilWriteMasters,
         mAxiWriteSlaves     => mAxilWriteSlaves,
         mAxiReadMasters     => mAxilReadMasters,
         mAxiReadSlaves      => mAxilReadSlaves);

   ---------------------------
   -- AXI-Lite: Version Module
   ---------------------------          
   U_AxiVersion : entity work.AxiVersion
      generic map (
         TPD_G              => TPD_G,
         AXI_ERROR_RESP_G   => AXI_ERROR_RESP_G,
         CLK_PERIOD_G       => (1.0/AXI_CLK_FREQ_G),
         XIL_DEVICE_G       => "7SERIES",
         EN_DEVICE_DNA_G    => true,
         EN_DS2411_G        => false,
         EN_ICAP_G          => true,
         AUTO_RELOAD_EN_G   => FSBL_G,
         AUTO_RELOAD_TIME_G => 10.0,    -- 10 seconds
         AUTO_RELOAD_ADDR_G => x"04000000")
      port map (
         -- AXI-Lite Register Interface
         axiReadMaster  => mAxilReadMasters(VERSION_INDEX_C),
         axiReadSlave   => mAxilReadSlaves(VERSION_INDEX_C),
         axiWriteMaster => mAxilWriteMasters(VERSION_INDEX_C),
         axiWriteSlave  => mAxilWriteSlaves(VERSION_INDEX_C),
         -- Clocks and Resets
         axiClk         => axilClk,
         axiRst         => axilRst);           

   -----------------------
   -- AXI-Lite XADC Module
   -----------------------
   U_Xadc : entity work.AxiXadcMinimumCore
      port map (
         -- XADC Ports
         vPIn           => vPIn,
         vNIn           => vNIn,
         -- AXI-Lite Register Interface
         axiReadMaster  => mAxilReadMasters(XADC_INDEX_C),
         axiReadSlave   => mAxilReadSlaves(XADC_INDEX_C),
         axiWriteMaster => mAxilWriteMasters(XADC_INDEX_C),
         axiWriteSlave  => mAxilWriteSlaves(XADC_INDEX_C),
         -- Clocks and Resets
         axiClk         => axilClk,
         axiRst         => axilRst);

   ------------------------------
   -- AXI-Lite: Boot Flash Module
   ------------------------------
   U_BootProm : entity work.AxiMicronN25QCore
      generic map (
         TPD_G            => TPD_G,
         AXI_ERROR_RESP_G => AXI_ERROR_RESP_G,
         MEM_ADDR_MASK_G  => x"00000000",           -- Using hardware write protection
         AXI_CLK_FREQ_G   => AXI_CLK_FREQ_G,        -- units of Hz
         SPI_CLK_FREQ_G   => (AXI_CLK_FREQ_G/8.0))  -- units of Hz
      port map (
         -- FLASH Memory Ports
         csL            => bootCsL,
         sck            => bootSck,
         mosi           => bootMosi,
         miso           => bootMiso,
         -- AXI-Lite Register Interface
         axiReadMaster  => mAxilReadMasters(BOOT_MEM_INDEX_C),
         axiReadSlave   => mAxilReadSlaves(BOOT_MEM_INDEX_C),
         axiWriteMaster => mAxilWriteMasters(BOOT_MEM_INDEX_C),
         axiWriteSlave  => mAxilWriteSlaves(BOOT_MEM_INDEX_C),
         -- Clocks and Resets
         axiClk         => axilClk,
         axiRst         => axilRst); 

   -----------------------------------------------------
   -- Using the STARTUPE2 to access the FPGA's CCLK port
   -----------------------------------------------------
   STARTUPE2_Inst : STARTUPE2
      port map (
         CFGCLK    => open,             -- 1-bit output: Configuration main clock output
         CFGMCLK   => open,  -- 1-bit output: Configuration internal oscillator clock output
         EOS       => open,  -- 1-bit output: Active high output signal indicating the End Of Startup.
         PREQ      => open,             -- 1-bit output: PROGRAM request to fabric output
         CLK       => '0',              -- 1-bit input: User start-up clock input
         GSR       => '0',  -- 1-bit input: Global Set/Reset input (GSR cannot be used for the port name)
         GTS       => '0',  -- 1-bit input: Global 3-state input (GTS cannot be used for the port name)
         KEYCLEARB => '0',  -- 1-bit input: Clear AES Decrypter Key input from Battery-Backed RAM (BBRAM)
         PACK      => '0',              -- 1-bit input: PROGRAM acknowledge input
         USRCCLKO  => bootSck,          -- 1-bit input: User CCLK input
         USRCCLKTS => '0',              -- 1-bit input: User CCLK 3-state enable input
         USRDONEO  => '1',              -- 1-bit input: User DONE pin output control
         USRDONETS => '1');             -- 1-bit input: User DONE 3-state enable output            

   -----------------------------------
   -- AXI-Lite: System Register Module
   -----------------------------------
   U_SysReg : entity work.AtlasChess2FebSysReg
      generic map (
         TPD_G            => TPD_G,
         AXI_CLK_FREQ_G   => AXI_CLK_FREQ_G,
         AXI_ERROR_RESP_G => AXI_ERROR_RESP_G)
      port map (
         -- Timing Clock and Reset
         timingClk320MHz => timingClk320MHz,
         timingRst320MHz => timingRst320MHz,
         -- AXI-Lite Interface
         axilClk         => axilClk,
         axilRst         => axilRst,
         axilReadMaster  => mAxilReadMasters(SYS_REG_INDEX_C),
         axilReadSlave   => mAxilReadSlaves(SYS_REG_INDEX_C),
         axilWriteMaster => mAxilWriteMasters(SYS_REG_INDEX_C),
         axilWriteSlave  => mAxilWriteSlaves(SYS_REG_INDEX_C),
         -- System Interface 
         status          => status,
         config          => config);

   --------------------------------------------------------          
   -- AXI-Lite: Microblaze/Software Shared Memory Interface
   --------------------------------------------------------               
   U_Mem : entity work.AxiDualPortRam
      generic map (
         TPD_G        => TPD_G,
         BRAM_EN_G    => true,
         REG_EN_G     => true,
         AXI_WR_EN_G  => true,
         SYS_WR_EN_G  => false,
         COMMON_CLK_G => false,
         ADDR_WIDTH_G => SHARED_MEM_WIDTH_C,
         DATA_WIDTH_G => 32)
      port map (
         -- Clock and Reset
         clk            => axilClk,
         rst            => axilRst,
         -- AXI-Lite Write Monitor
         axiWrValid     => axiWrValid,
         axiWrAddr      => axiWrAddr,
         -- AXI-Lite Interface
         axiClk         => axilClk,
         axiRst         => axilRst,
         axiReadMaster  => mAxilReadMasters(MEM_INDEX_C),
         axiReadSlave   => mAxilReadSlaves(MEM_INDEX_C),
         axiWriteMaster => mAxilWriteMasters(MEM_INDEX_C),
         axiWriteSlave  => mAxilWriteSlaves(MEM_INDEX_C));               

   ----------------------
   -- AXI-Lite: Power I2C
   ----------------------
   U_PwrI2C : entity work.AxiI2cRegMaster
      generic map (
         TPD_G            => TPD_G,
         AXI_ERROR_RESP_G => AXI_ERROR_RESP_G,
         DEVICE_MAP_G     => PWR_I2C_C,
         AXI_CLK_FREQ_G   => AXI_CLK_FREQ_G)
      port map (
         -- I2C Ports
         scl            => pwrScl,
         sda            => pwrSda,
         -- AXI-Lite Register Interface
         axiReadMaster  => mAxilReadMasters(PWR_INDEX_C),
         axiReadSlave   => mAxilReadSlaves(PWR_INDEX_C),
         axiWriteMaster => mAxilWriteMasters(PWR_INDEX_C),
         axiWriteSlave  => mAxilWriteSlaves(PWR_INDEX_C),
         -- Clocks and Resets
         axiClk         => axilClk,
         axiRst         => axilRst);         

   -----------------------
   -- AXI-Lite: CONFIG I2C
   -----------------------
   U_ConfigI2C : entity work.AxiI2cEeprom
      generic map (
         TPD_G            => TPD_G,
         ADDR_WIDTH_G     => 13,
         I2C_ADDR_G       => "1010000",
         AXI_ERROR_RESP_G => AXI_ERROR_RESP_G,
         AXI_CLK_FREQ_G   => AXI_CLK_FREQ_G)
      port map (
         -- I2C Ports
         scl             => configScl,
         sda             => configSda,
         -- AXI-Lite Register Interface
         axilReadMaster  => mAxilReadMasters(CONFIG_INDEX_C),
         axilReadSlave   => mAxilReadSlaves(CONFIG_INDEX_C),
         axilWriteMaster => mAxilWriteMasters(CONFIG_INDEX_C),
         axilWriteSlave  => mAxilWriteSlaves(CONFIG_INDEX_C),
         -- Clocks and Resets
         axilClk         => axilClk,
         axilRst         => axilRst);         

end mapping;
