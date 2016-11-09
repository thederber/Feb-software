-------------------------------------------------------------------------------
-- Title      : 
-------------------------------------------------------------------------------
-- File       : AtlasChess2FebEvr.vhd
-- Author     : Larry Ruckman  <ruckman@slac.stanford.edu>
-- Company    : SLAC National Accelerator Laboratory
-- Created    : 2016-06-07
-- Last update: 2016-06-10
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

entity AtlasChess2FebEvr is
   generic (
      TPD_G            : time            := 1 ns;
      AXI_ERROR_RESP_G : slv(1 downto 0) := AXI_RESP_DECERR_C);
   port (
      -- AXI-Lite Interface
      axilClk         : in  sl;
      axilRst         : in  sl;
      axilReadMaster  : in  AxiLiteReadMasterType;
      axilReadSlave   : out AxiLiteReadSlaveType;
      axilWriteMaster : in  AxiLiteWriteMasterType;
      axilWriteSlave  : out AxiLiteWriteSlaveType;
      -- EVR Interface
      evrClk          : out sl;
      evrRst          : out sl;
      evrTrig         : out sl;
      evrTs           : out slv(63 downto 0);
      evrOpCode       : out slv(7 downto 0);
      -- SLAC Timing Ports
      evrClkP         : in  sl;
      evrClkN         : in  sl;
      evrRxP          : in  sl;
      evrRxN          : in  sl;
      evrTxP          : out sl;
      evrTxN          : out sl);      
end AtlasChess2FebEvr;

architecture rtl of AtlasChess2FebEvr is

   type RegType is record
      evrOpCodeDet   : slv(7 downto 0);
      evrOffsetFix   : slv(31 downto 0);
      axilReadSlave  : AxiLiteReadSlaveType;
      axilWriteSlave : AxiLiteWriteSlaveType;
   end record RegType;
   constant REG_INIT_C : RegType := (
      evrOpCodeDet   => (others => '0'),
      evrOffsetFix   => x"FFFFFFFE",
      axilReadSlave  => AXI_LITE_READ_SLAVE_INIT_C,
      axilWriteSlave => AXI_LITE_WRITE_SLAVE_INIT_C);
   signal r   : RegType := REG_INIT_C;
   signal rin : RegType;

   signal evrOpCodeDet : slv(7 downto 0);
   signal evrOffsetFix : slv(31 downto 0);
   signal evrClock     : sl;
   signal evrReset     : sl;
   signal rxError      : sl;
   signal rxLinkUp     : sl;
   signal rxData       : slv(15 downto 0);

   type EvrType is record
      eventStream : slv(7 downto 0);
      seconds     : slv(31 downto 0);
      secondsTmp  : slv(31 downto 0);
      offset      : slv(31 downto 0);
      armed       : slv(2 downto 0);
      evrTrig     : sl;
   end record EvrType;
   constant EVR_INIT_C : EvrType := (
      eventStream => (others => '0'),
      seconds     => (others => '0'),
      secondsTmp  => (others => '0'),
      offset      => (others => '0'),
      armed       => (others => '0'),
      evrTrig     => '0');
   signal evr   : EvrType := EVR_INIT_C;
   signal evrin : EvrType;
   
begin

   --------------------- 
   -- AXI Lite Interface
   --------------------- 
   combReg : process (axilReadMaster, axilRst, axilWriteMaster, r) is
      variable v      : RegType;
      variable axilEp : AxiLiteEndPointType;
      variable i      : natural;
   begin
      -- Latch the current value
      v := r;

      -- Determine the transaction type
      axiSlaveWaitTxn(axilEp, axilWriteMaster, axilReadMaster, v.axilWriteSlave, v.axilReadSlave);

      -- Mapping registers      
      axiSlaveRegister(axilEp, x"800", 0, v.evrOpCodeDet);
      axiSlaveRegister(axilEp, x"804", 0, v.evrOffsetFix);

      -- Close out the transaction
      axiSlaveDefault(axilEp, v.axilWriteSlave, v.axilReadSlave, AXI_ERROR_RESP_G);

      -- Reset
      if (axilRst = '1') then
         v := REG_INIT_C;
      end if;

      -- Register the variable for next clock cycle
      rin <= v;

      -- Outputs
      axilWriteSlave <= r.axilWriteSlave;
      axilReadSlave  <= r.axilReadSlave;
      evrOpCode      <= r.evrOpCodeDet;
      
   end process combReg;

   seqReg : process (axilClk) is
   begin
      if (rising_edge(axilClk)) then
         r <= rin after TPD_G;
      end if;
   end process seqReg;

   Sync_evrOpCodeDet : entity work.SynchronizerVector
      generic map (
         TPD_G   => TPD_G,
         WIDTH_G => 8)    
      port map (
         clk     => evrClock,
         dataIn  => r.evrOpCodeDet,
         dataOut => evrOpCodeDet);   

   Sync_evrOffsetFix : entity work.SynchronizerVector
      generic map (
         TPD_G   => TPD_G,
         WIDTH_G => 32)    
      port map (
         clk     => evrClock,
         dataIn  => r.evrOffsetFix,
         dataOut => evrOffsetFix);            

   U_GTX : entity work.AtlasChess2FebEvrGtx
      generic map (
         TPD_G => TPD_G)
      port map (
         -- Stable Clock Reference
         stableClk  => axilClk,
         -- EVR Ports
         evrRefClkP => evrClkP,
         evrRefClkN => evrClkN,
         evrRxP     => evrRxP,
         evrRxN     => evrRxN,
         evrTxP     => evrTxP,
         evrTxN     => evrTxN,
         -- EVR Interface
         evrClk     => evrClock,
         evrRst     => evrReset,
         rxLinkUp   => rxLinkUp,
         rxError    => rxError,
         rxData     => rxData);

   evrClk <= evrClock;
   evrRst <= evrReset;

   ----------------
   -- EVR Interface
   ----------------
   combEvr : process (evr, evrOffsetFix, evrOpCodeDet, evrReset, rxData, rxLinkUp) is
      variable v : EvrType;
   begin
      -- Latch the current value
      v := evr;

      -- Reset strobing signals
      v.evrTrig := '0';

      -- Increment counter
      v.offset := evr.offset + 1;

      -- Extract out the event and data bus
      v.eventStream := rxData(7 downto 0);

      -- On receive of 0x7D, clear offset, move secondsTmp to output register
      if evr.eventStream = x"7D" then
         v.seconds    := evr.secondsTmp;
         v.secondsTmp := (others => '0');
         v.offset     := evrOffsetFix;
         v.armed(0)   := '1';
         v.armed(1)   := evr.armed(0);
         v.armed(2)   := evr.armed(1);
      -- On receive of 0x71, shift a 1 into secondsTmp
      elsif evr.eventStream = x"71" then
         v.secondsTmp := evr.secondsTmp(30 downto 0) & '1';
      -- On receive of 0x70, shift a 0 into secondsTmp
      elsif evr.eventStream = x"70" then
         v.secondsTmp := evr.secondsTmp(30 downto 0) & '0';
      end if;

      -- Check for OP-code trigger
      if (evr.eventStream = evrOpCodeDet) and (evr.armed = "111") then
         v.evrTrig := '1';
      end if;

      -- Reset
      if (evrReset = '1') or (rxLinkUp = '0') then
         v        := EVR_INIT_C;
         v.offset := evrOffsetFix;
      end if;

      -- Register the variable for next clock cycle
      evrin <= v;

      -- Outputs
      evrTrig             <= evr.evrTrig;
      evrTs(63 downto 32) <= evr.seconds;
      evrTs(31 downto 0)  <= evr.offset;
      
   end process combEvr;

   seqEvr : process (evrClock) is
   begin
      if (rising_edge(evrClock)) then
         evr <= evrin after TPD_G;
      end if;
   end process seqEvr;
   
end rtl;
