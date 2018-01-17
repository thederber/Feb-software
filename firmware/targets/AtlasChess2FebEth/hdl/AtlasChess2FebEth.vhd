-------------------------------------------------------------------------------
-- Title      : 
-------------------------------------------------------------------------------
-- File       : AtlasChess2FebEth.vhd
-- Author     : Larry Ruckman  <ruckman@slac.stanford.edu>
-- Company    : SLAC National Accelerator Laboratory
-- Created    : 2016-06-01
-- Last update: 2018-01-16
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

library unisim;
use unisim.vcomponents.all;

entity AtlasChess2FebEth is
   generic (
      TPD_G        : time := 1 ns;
      BUILD_INFO_G : BuildInfoType);
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
end AtlasChess2FebEth;

architecture top_level of AtlasChess2FebEth is


  signal bufferControl : slv(31 downto 0);
  signal testClksig    : sl;
  signal dacEnLsig     : sl;
  signal term100sig    : sl;
  signal term300sig    : sl;
  signal lvdsTxSelsig  : sl;
  signal acModesig     : sl;
  signal bitSelsig     : sl;
  signal saciClksig    : sl;
  signal saciCmdsig    : sl;
  signal saciRstLsig   : sl;  
  signal saciSelLsig   : slv(3 downto 0);

  
begin

  -----------------------------------------------------------------------------
  -- adding buffers to manually turn off pins
  -----------------------------------------------------------------------------
   OBUFT_testClk : OBUFT
   generic map (
      DRIVE => 12,
      IOSTANDARD => "DEFAULT",
      SLEW => "SLOW")
   port map (
      O => testClk,     -- Buffer output (connect directly to top-level port)
      I => testClksig,     -- Buffer input
      T => bufferControl(0)      -- 3-state enable input 
   );

   OBUFT_dacEnL : OBUFT
   generic map (
      DRIVE => 12,
      IOSTANDARD => "DEFAULT",
      SLEW => "SLOW")
   port map (
      O => dacEnL,     -- Buffer output (connect directly to top-level port)
      I => dacEnLsig,     -- Buffer input
      T => bufferControl(1)      -- 3-state enable input 
   );

   OBUFT_term100 : OBUFT
   generic map (
      DRIVE => 12,
      IOSTANDARD => "DEFAULT",
      SLEW => "SLOW")
   port map (
      O => term100,     -- Buffer output (connect directly to top-level port)
      I => term100sig,     -- Buffer input
      T => bufferControl(2)      -- 3-state enable input 
   );

   OBUFT_term300 : OBUFT
   generic map (
      DRIVE => 12,
      IOSTANDARD => "DEFAULT",
      SLEW => "SLOW")
   port map (
      O => term300,     -- Buffer output (connect directly to top-level port)
      I => term300sig,     -- Buffer input
      T => bufferControl(3)      -- 3-state enable input 
   );

   OBUFT_lvdsTxSel : OBUFT
   generic map (
      DRIVE => 12,
      IOSTANDARD => "DEFAULT",
      SLEW => "SLOW")
   port map (
      O => lvdsTxSel,     -- Buffer output (connect directly to top-level port)
      I => lvdsTxSelsig,     -- Buffer input
      T => bufferControl(4)      -- 3-state enable input 
   );

   OBUFT_acModes : OBUFT
   generic map (
      DRIVE => 12,
      IOSTANDARD => "DEFAULT",
      SLEW => "SLOW")
   port map (
      O => acMode,     -- Buffer output (connect directly to top-level port)
      I => acModesig,     -- Buffer input
      T => bufferControl(5)      -- 3-state enable input 
   );

   OBUFT_bitSel : OBUFT
   generic map (
      DRIVE => 12,
      IOSTANDARD => "DEFAULT",
      SLEW => "SLOW")
   port map (
      O => bitSel,     -- Buffer output (connect directly to top-level port)
      I => bitSelsig,     -- Buffer input
      T => bufferControl(6)      -- 3-state enable input 
   );

   OBUFT_saciClk : OBUFT
   generic map (
      DRIVE => 12,
      IOSTANDARD => "DEFAULT",
      SLEW => "SLOW")
   port map (
      O => saciClk,     -- Buffer output (connect directly to top-level port)
      I => saciClksig,     -- Buffer input
      T => bufferControl(7)      -- 3-state enable input 
   );
   
   OBUFT_saciCmd : OBUFT
   generic map (
      DRIVE => 12,
      IOSTANDARD => "DEFAULT",
      SLEW => "SLOW")
   port map (
      O => saciCmd,     -- Buffer output (connect directly to top-level port)
      I => saciCmdsig,     -- Buffer input
      T => bufferControl(8)      -- 3-state enable input 
   );
   
   OBUFT_saciRstL : OBUFT
   generic map (
      DRIVE => 12,
      IOSTANDARD => "DEFAULT",
      SLEW => "SLOW")
   port map (
      O => saciRstL,     -- Buffer output (connect directly to top-level port)
      I => saciRstLsig,     -- Buffer input
      T => bufferControl(9)      -- 3-state enable input 
   );

   OBUFT_saciSelL_0 : OBUFT
   generic map (
      DRIVE => 12,
      IOSTANDARD => "DEFAULT",
      SLEW => "SLOW")
   port map (
      O => saciSelL(0),     -- Buffer output (connect directly to top-level port)
      I => saciSelLsig(0),     -- Buffer input
      T => bufferControl(10)      -- 3-state enable input 
   );

   OBUFT_saciSelL_1 : OBUFT
   generic map (
      DRIVE => 12,
      IOSTANDARD => "DEFAULT",
      SLEW => "SLOW")
   port map (
      O => saciSelL(1),     -- Buffer output (connect directly to top-level port)
      I => saciSelLsig(1),     -- Buffer input
      T => bufferControl(11)      -- 3-state enable input 
   );

   OBUFT_saciSelL_2 : OBUFT
   generic map (
      DRIVE => 12,
      IOSTANDARD => "DEFAULT",
      SLEW => "SLOW")
   port map (
      O => saciSelL(2),     -- Buffer output (connect directly to top-level port)
      I => saciSelLsig(2),     -- Buffer input
      T => bufferControl(12)      -- 3-state enable input 
   );

   OBUFT_saciSelL_3 : OBUFT
   generic map (
      DRIVE => 12,
      IOSTANDARD => "DEFAULT",
      SLEW => "SLOW")
   port map (
      O => saciSelL(3),     -- Buffer output (connect directly to top-level port)
      I => saciSelLsig(3),     -- Buffer input
      T => bufferControl(13)      -- 3-state enable input 
   );
  
--   IBUF_IBUFDISABLE_inst : IBUF_IBUFDISABLE
--   generic map (
--      IBUF_LOW_PWR => "TRUE", -- Low power (TRUE) vs. performance (FALSE) setting for referenced I/O standards
--      IOSTANDARD => "DEFAULT", -- Specify the input I/O standard
--      USE_IBUFDISABLE => "TRUE") -- Set to "TRUE" to enable IBUFDISABLE feature
--   port map (
--      O => O,     -- Buffer output
--      I => I,     -- Buffer input (connect directly to top-level port)
--      IBUFDISABLE => IBUFDISABLE -- Buffer disable input, low=disable
--   );

--   OBUFTDS_inst : OBUFTDS
--   generic map (
--      IOSTANDARD => "DEFAULT")
--   port map (
--      O => O,     -- Diff_p output (connect directly to top-level port)
--      OB => OB,   -- Diff_n output (connect directly to top-level port)
--      I => I,     -- Buffer input
--      T => T      -- 3-state enable input
--   );

--   IBUFDS_IBUFDISABLE_inst : IBUFDS_IBUFDISABLE
--   generic map (
--      DIFF_TERM => "FALSE", -- Differential Termination 
--      IBUF_LOW_PWR => "TRUE", -- Low power (TRUE) vs. performance (FALSE) setting for referenced I/O standards
--      IOSTANDARD => "DEFAULT", -- Specify the input I/O standard
--      USE_IBUFDISABLE => "TRUE") -- Set to "TRUE" to enable IBUFDISABLE feature
--   port map (
--      O => O,  -- Buffer output
--      I => I,  -- Diff_p buffer input (connect directly to top-level port)
--      IB => IB, -- Diff_n buffer input (connect directly to top-level port)
--      IBUFDISABLE => IBUFDISABLE -- Buffer disable input, low=disable
-- );

   
   U_Core : entity work.AtlasChess2FebCore
      generic map (
         TPD_G         => TPD_G,
         BUILD_INFO_G  => BUILD_INFO_G,
         COMM_MODE_G   => true,         -- true = ETH mode, false = PGP mode
         -- ETH configuration 
         ETH_DEV_G     => false,        -- true = Adds non-RSSI on port 8193
         ETH_DHCP_G    => true,         -- true = DHCP, false = static address
         ETH_IP_ADDR_G => x"0A01A8C0")  -- 192.168.1.10 (before DHCP)            
      port map (
         -- CHESS2 ASIC Serial Ports
         chessDinP       => chessDinP,
         chessDinN       => chessDinN,
         chessClk320MHzP => chessClk320MHzP,
         chessClk320MHzN => chessClk320MHzN,
         chessClk40MHz   => chessClk40MHz,
         -- Test Structure Ports
         testClk         => testClksig,
         dacEnL          => dacEnLsig,
         term100         => term100sig,
         term300         => term300sig,
         lvdsTxSel       => lvdsTxSelsig,
         acMode          => acModesig,
         bitSel          => bitSelsig,
         injSig          => injSig,
         -- SACI Ports
         saciClk         => saciClksig,
         saciCmd         => saciCmdsig,
         saciRstL        => saciRstLsig,
         saciSelL        => saciSelLsig,
         saciRsp         => saciRsp,
         -- DAC Ports
         dacSlowCsL      => dacSlowCsL,
         dacSlowSck      => dacSlowSck,
         dacSlowMosi     => dacSlowMosi,
         -- SLAC Timing Ports
         evrClkP         => evrClkP,
         evrClkN         => evrClkN,
         evrRxP          => evrRxP,
         evrRxN          => evrRxN,
         evrTxP          => evrTxP,
         evrTxN          => evrTxN,
         -- PGP/GbE Ports
         gtClkP          => gtClkP,
         gtClkN          => gtClkN,
         gtRxP           => gtRxP,
         gtRxN           => gtRxN,
         gtTxP           => gtTxP,
         gtTxN           => gtTxN,
         -- System Ports
         extTrigL        => extTrigL,
         extBusy         => extBusy,
         tempAlertL      => tempAlertL,
         redL            => redL,
         blueL           => blueL,
         greenL          => greenL,
         led             => led,
         oeClk           => oeClk,
         pwrSyncSclk     => pwrSyncSclk,
         pwrSyncFclk     => pwrSyncFclk,
         pwrScl          => pwrScl,
         pwrSda          => pwrSda,
         configScl       => configScl,
         configSda       => configSda,
         -- Reference Clock
         locClk40MHz     => locClk40MHz,
         extClk40MHzP    => extClk40MHzP,
         extClk40MHzN    => extClk40MHzN,
         -- Boot Memory Ports
         bootCsL         => bootCsL,
         bootMosi        => bootMosi,
         bootMiso        => bootMiso,
         -- XADC Ports
         vPIn            => vPIn,
         vNIn            => vNIn,
         bufferControl => bufferControl);

end top_level;
