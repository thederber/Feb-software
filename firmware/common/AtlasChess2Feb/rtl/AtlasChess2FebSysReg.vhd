-------------------------------------------------------------------------------
-- Title      : 
-------------------------------------------------------------------------------
-- File       : AtlasChess2FebSysReg.vhd
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
use work.AtlasChess2FebPkg.all;

entity AtlasChess2FebSysReg is
   generic (
      TPD_G            : time            := 1 ns;
      AXI_ERROR_RESP_G : slv(1 downto 0) := AXI_RESP_DECERR_C);
   port (
      -- Timing Clock and Reset
      timingClk320MHz : in  sl;
      timingRst320MHz : in  sl;
      -- AXI-Lite Interface
      axilClk         : in  sl;
      axilRst         : in  sl;
      axilReadMaster  : in  AxiLiteReadMasterType;
      axilReadSlave   : out AxiLiteReadSlaveType;
      axilWriteMaster : in  AxiLiteWriteMasterType;
      axilWriteSlave  : out AxiLiteWriteSlaveType;
      -- System Interface 
      status          : in  AtlasChess2FebStatusType;
      config          : out AtlasChess2FebConfigType);
end AtlasChess2FebSysReg;

architecture rtl of AtlasChess2FebSysReg is

   constant STATUS_SIZE_C : natural := 1;

   type RegType is record
      cntRst         : sl;
      rollOverEn     : slv(STATUS_SIZE_C-1 downto 0);
      config         : AtlasChess2FebConfigType;
      axilReadSlave  : AxiLiteReadSlaveType;
      axilWriteSlave : AxiLiteWriteSlaveType;
   end record RegType;
   
   constant REG_INIT_C : RegType := (
      cntRst         => '1',
      rollOverEn     => (others => '0'),
      config         => CHESS2_FEB_CONFIG_INIT_C,
      axilReadSlave  => AXI_LITE_READ_SLAVE_INIT_C,
      axilWriteSlave => AXI_LITE_WRITE_SLAVE_INIT_C);

   signal r   : RegType := REG_INIT_C;
   signal rin : RegType;

   signal regIn      : AtlasChess2FebStatusType := CHESS2_FEB_STATUS_INIT_C;
   signal statusOut  : slv(STATUS_SIZE_C-1 downto 0);
   signal cntOut     : SlVectorArray(STATUS_SIZE_C-1 downto 0, 31 downto 0);
   signal refClkFreq : slv(31 downto 0);
   
begin

   --------------------- 
   -- AXI Lite Interface
   --------------------- 
   comb : process (axilReadMaster, axilRst, axilWriteMaster, cntOut, r, refClkFreq, statusOut) is
      variable v      : RegType;
      variable axilEp : AxiLiteEndPointType;
      variable i      : natural;
   begin
      -- Latch the current value
      v := r;

      -- Reset the strobe
      v.config.softRst := '0';
      v.config.hardRst := '0';
      v.config.pllRst  := '0';
      v.config.dlyRst  := '0';
      v.cntRst         := '0';

      -- Determine the transaction type
      axiSlaveWaitTxn(axilEp, axilWriteMaster, axilReadMaster, v.axilWriteSlave, v.axilReadSlave);

      if (axilReadMaster.rready = '1') then
         v.axilReadSlave.rdata := (others => '0');
      end if;

      -- Mapping registers      
      for i in STATUS_SIZE_C-1 downto 0 loop
         axiSlaveRegisterR(axilEp, toSlv((i*4), 12), 0, muxSlVectorArray(cntOut, i));
      end loop;
      axiSlaveRegisterR(axilEp, x"100", 0, statusOut);
      axiSlaveRegisterR(axilEp, x"1FC", 0, refClkFreq);

      axiSlaveRegister(axilEp, x"800", 0, v.config.refSelect);
      axiSlaveRegister(axilEp, x"804", 0, v.config.timingMode);
      axiSlaveRegister(axilEp, x"808", 0, v.config.pllRst);
      axiSlaveRegister(axilEp, x"80C", 0, v.config.dlyRst);
      axiSlaveRegister(axilEp, x"810", 0, v.config.dlyTiming);
      axiSlaveRegister(axilEp, x"814", 0, v.config.dlyChess);
      axiSlaveRegister(axilEp, x"818", 0, v.config.destId);
      axiSlaveRegister(axilEp, x"81C", 0, v.config.frameType);
      axiSlaveRegister(axilEp, x"820", 0, v.config.wordSize);

      axiSlaveRegister(axilEp, x"F00", 0, v.rollOverEn);
      axiSlaveRegister(axilEp, x"F10", 0, v.cntRst);
      axiSlaveRegister(axilEp, x"FF8", 0, v.config.softRst);
      axiSlaveRegister(axilEp, x"FFC", 0, v.config.hardRst);

      -- Close out the transaction
      axiSlaveDefault(axilEp, v.axilWriteSlave, v.axilReadSlave, AXI_ERROR_RESP_G);

      -- Check for change in delay configurations
      if (r.config.dlyTiming) /= (v.config.dlyTiming) or (r.config.dlyChess) /= (v.config.dlyChess) then
         v.config.dlyRst := '1';
      end if;

      -- Reset
      if (axilRst = '1') then
         v := REG_INIT_C;
      end if;

      -- Register the variable for next clock cycle
      rin <= v;

      -- Outputs
      axilWriteSlave <= r.axilWriteSlave;
      axilReadSlave  <= r.axilReadSlave;
      
   end process comb;

   seq : process (axilClk) is
   begin
      if (rising_edge(axilClk)) then
         r <= rin after TPD_G;
      end if;
   end process seq;

   --------------------------
   -- Synchronization: Inputs
   --------------------------   
   U_sysClkFreq : entity work.SyncClockFreq
      generic map (
         TPD_G          => TPD_G,
         REF_CLK_FREQ_G => AXIL_CLK_FREQ_C)
      port map (
         -- Frequency Measurement and Monitoring Outputs (locClk domain)
         freqOut => refClkFreq,
         -- Clocks
         clkIn   => status.refClk40MHz,
         locClk  => axilClk,
         refClk  => axilClk); 

   U_SyncStatusVec : entity work.SyncStatusVector
      generic map (
         TPD_G          => TPD_G,
         OUT_POLARITY_G => '1',
         CNT_RST_EDGE_G => true,
         CNT_WIDTH_G    => 32,
         WIDTH_G        => STATUS_SIZE_C)     
      port map (
         -- Input Status bit Signals (wrClk domain)                  
         statusIn(0)  => status.refLocked,
         -- Output Status bit Signals (rdClk domain)           
         statusOut    => statusOut,
         -- Status Bit Counters Signals (rdClk domain) 
         cntRstIn     => r.cntRst,
         rollOverEnIn => r.rollOverEn,
         cntOut       => cntOut,
         -- Clocks and Reset Ports
         wrClk        => axilClk,
         rdClk        => axilClk);      

   ---------------------------
   -- Synchronization: Outputs
   ---------------------------
   config.refSelect  <= r.config.refSelect;   -- Bypass the SYNC because controls clock MUX
   config.timingMode <= r.config.timingMode;  -- Bypass the SYNC because controls clock MUX

   SyncOut_softRst : entity work.RstSync
      generic map (
         TPD_G => TPD_G)   
      port map (
         clk      => axilClk,
         asyncRst => r.config.softRst,
         syncRst  => config.softRst); 

   SyncOut_hardRst : entity work.RstSync
      generic map (
         TPD_G => TPD_G)   
      port map (
         clk      => axilClk,
         asyncRst => r.config.hardRst,
         syncRst  => config.hardRst); 

   SyncOut_pllRst : entity work.RstSync
      generic map (
         TPD_G => TPD_G)   
      port map (
         clk      => axilClk,
         asyncRst => r.config.pllRst,
         syncRst  => config.pllRst);

   SyncOutDelayLoad : entity work.PwrUpRst
      generic map (
         TPD_G      => TPD_G,
         DURATION_G => 8)
      port map (
         clk    => timingClk320MHz,
         arst   => r.config.dlyRst,
         rstOut => config.dlyRst);      

   SyncOutDlyTiming : entity work.SynchronizerVector
      generic map (
         TPD_G   => TPD_G,
         WIDTH_G => DELAY_ADDR_WIDTH_C)
      port map (
         clk     => timingClk320MHz,
         dataIn  => r.config.dlyTiming,
         dataOut => config.dlyTiming);    

   SyncOutDlyChess : entity work.SynchronizerVector
      generic map (
         TPD_G   => TPD_G,
         WIDTH_G => DELAY_ADDR_WIDTH_C)
      port map (
         clk     => timingClk320MHz,
         dataIn  => r.config.dlyChess,
         dataOut => config.dlyChess); 

   SyncOutDestId : entity work.SynchronizerVector
      generic map (
         TPD_G   => TPD_G,
         WIDTH_G => 6)
      port map (
         clk     => timingClk320MHz,
         dataIn  => r.config.destId,
         dataOut => config.destId);     

   SyncOutFrameType : entity work.SynchronizerVector
      generic map (
         TPD_G   => TPD_G,
         WIDTH_G => 32)
      port map (
         clk     => timingClk320MHz,
         dataIn  => r.config.frameType,
         dataOut => config.frameType);  

   SyncOutWordSize : entity work.SynchronizerVector
      generic map (
         TPD_G   => TPD_G,
         WIDTH_G => 8)
      port map (
         clk     => timingClk320MHz,
         dataIn  => r.config.wordSize,
         dataOut => config.wordSize);           

end rtl;
