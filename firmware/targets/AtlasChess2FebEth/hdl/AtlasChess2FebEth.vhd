-------------------------------------------------------------------------------
-- Title      : 
-------------------------------------------------------------------------------
-- File       : AtlasChess2FebEth.vhd
-- Author     : Larry Ruckman  <ruckman@slac.stanford.edu>
-- Company    : SLAC National Accelerator Laboratory
-- Created    : 2016-06-01
-- Last update: 2016-11-18
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

entity AtlasChess2FebEth is
   generic (
      TPD_G  : time    := 1 ns;
      FSBL_G : boolean := false);
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

begin

   U_Core : entity work.AtlasChess2FebCore
      generic map (
         TPD_G     => TPD_G,
         ETH_G     => true,             -- ETH mode
         DHCP_G    => true,             -- true = DHCP, false = static address
         IP_ADDR_G => x"0A01A8C0")      -- 192.168.1.10 (before DHCP)            
      port map (
         -- CHESS2 ASIC Serial Ports
         chessDinP       => chessDinP,
         chessDinN       => chessDinN,
         chessClk320MHzP => chessClk320MHzP,
         chessClk320MHzN => chessClk320MHzN,
         chessClk40MHz   => chessClk40MHz,
         -- Test Structure Ports
         testClk         => testClk,
         dacEnL          => dacEnL,
         term100         => term100,
         term300         => term300,
         lvdsTxSel       => lvdsTxSel,
         acMode          => acMode,
         bitSel          => bitSel,
         injSig          => injSig,
         -- SACI Ports
         saciClk         => saciClk,
         saciCmd         => saciCmd,
         saciRstL        => saciRstL,
         saciSelL        => saciSelL,
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
         vNIn            => vNIn);

end top_level;
