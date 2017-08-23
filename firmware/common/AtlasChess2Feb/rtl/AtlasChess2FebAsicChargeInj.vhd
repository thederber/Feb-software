-------------------------------------------------------------------------------
-- Title      : 
-------------------------------------------------------------------------------
-- File       : AtlasChess2FebAsicChargeInj.vhd
-- Author     : Larry Ruckman  <ruckman@slac.stanford.edu>
-- Company    : SLAC National Accelerator Laboratory
-- Created    : 2016-06-07
-- Last update: 2017-04-28
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

library unisim;
use unisim.vcomponents.all;

entity AtlasChess2FebAsicChargeInj is
   generic (
      TPD_G            : time            := 1 ns;
      AXI_ERROR_RESP_G : slv(1 downto 0) := AXI_RESP_DECERR_C);
   port (
      -- Test Structure Ports
      testClk         : out sl;
      dacEnL          : out sl;
      term100         : out sl;
      term300         : out sl;
      lvdsTxSel       : out sl;
      acMode          : out sl;
      bitSel          : out sl;
      injSig          : out slv(1 downto 0);
      -- CHESS2 Interface
      dataValid       : in  slv(2 downto 0);
      multiHit        : in  slv(2 downto 0);
      col             : in  Slv5Array(2 downto 0);
      row             : in  Slv7Array(2 downto 0);
      -- Timing Interface
      timingClk320MHz : in  sl;
      timingRst320MHz : in  sl;
      -- AXI-Lite Interface
      axilClk         : in  sl;
      axilRst         : in  sl;
      axilReadMaster  : in  AxiLiteReadMasterType;
      axilReadSlave   : out AxiLiteReadSlaveType;
      axilWriteMaster : in  AxiLiteWriteMasterType;
      axilWriteSlave  : out AxiLiteWriteSlaveType);
end AtlasChess2FebAsicChargeInj;

architecture rtl of AtlasChess2FebAsicChargeInj is

   type RegType is record
      calPulse       : sl;
      invPulse       : sl;
      calWidth       : slv(15 downto 0);
      calDelay       : slv(15 downto 0);
      calPulseInh    : sl;
      axilReadSlave  : AxiLiteReadSlaveType;
      axilWriteSlave : AxiLiteWriteSlaveType;
   end record RegType;

   constant REG_INIT_C : RegType := (
      calPulse       => '0',
      invPulse       => '1',            -- default to active LOW pulse
      calWidth       => toSlv(7, 16),
      calDelay       => toSlv(7, 16),
      calPulseInh    => '0',            -- 
      axilReadSlave  => AXI_LITE_READ_SLAVE_INIT_C,
      axilWriteSlave => AXI_LITE_WRITE_SLAVE_INIT_C);

   signal r   : RegType := REG_INIT_C;
   signal rin : RegType;

   signal calPulse       : sl;
   signal invPulse       : sl;
   signal pulse          : sl;
   signal pulseDelayed   : sl;
   signal pulseReg       : slv(1 downto 0);
   signal calWidth       : slv(15 downto 0);
   signal calDelay       : slv(15 downto 0);
   signal cnt            : slv(15 downto 0);
   signal hitDet         : Slv14Array(2 downto 0);
   signal hitDetSync     : Slv14Array(2 downto 0);
   signal hitDetTime     : Slv16Array(2 downto 0);
   signal hitDetTimeSync : Slv16Array(2 downto 0);
   signal timer          : slv(15 downto 0);

   attribute dont_touch                   : string;
   attribute dont_touch of calPulse       : signal is "TRUE";
   attribute dont_touch of invPulse       : signal is "TRUE";
   attribute dont_touch of pulse          : signal is "TRUE";
   attribute dont_touch of pulseReg       : signal is "TRUE";
   attribute dont_touch of calWidth       : signal is "TRUE";
   attribute dont_touch of calDelay       : signal is "TRUE";
   attribute dont_touch of cnt            : signal is "TRUE";
   attribute dont_touch of hitDet         : signal is "TRUE";
   attribute dont_touch of hitDetSync     : signal is "TRUE";
   attribute dont_touch of hitDetTime     : signal is "TRUE";
   attribute dont_touch of hitDetTimeSync : signal is "TRUE";
   attribute dont_touch of timer          : signal is "TRUE";

begin

   testClk   <= '0';
   dacEnL    <= '1';
   term100   <= '0';
   term300   <= '0';
   lvdsTxSel <= '0';
   acMode    <= '0';
   bitSel    <= '0';

   --------------------- 
   -- AXI Lite Interface
   --------------------- 
   comb : process (axilReadMaster, axilRst, axilWriteMaster, hitDetSync,
                   hitDetTimeSync, r) is
      variable v      : RegType;
      variable axilEp : AxiLiteEndPointType;
      variable i      : natural;
   begin
      -- Latch the current value
      v := r;

      -- Reset the strobe
      v.calPulse := '0';

      -- Determine the transaction type
      axiSlaveWaitTxn(axilEp, axilWriteMaster, axilReadMaster, v.axilWriteSlave, v.axilReadSlave);

      if (axilReadMaster.rready = '1') then
         v.axilReadSlave.rdata := (others => '0');
      end if;

      -- Mapping registers     
      axiSlaveRegisterR(axilEp, x"00", 0, hitDetSync(0));
      axiSlaveRegisterR(axilEp, x"04", 0, hitDetSync(1));
      axiSlaveRegisterR(axilEp, x"08", 0, hitDetSync(2));

      axiSlaveRegisterR(axilEp, x"00", 16, hitDetTimeSync(0));
      axiSlaveRegisterR(axilEp, x"04", 16, hitDetTimeSync(1));
      axiSlaveRegisterR(axilEp, x"08", 16, hitDetTimeSync(2));

      axiSlaveRegister(axilEp, x"10", 0,  v.calPulse);
      axiSlaveRegister(axilEp, x"14", 0,  v.calWidth);
      axiSlaveRegister(axilEp, x"14", 16, v.calDelay);
      axiSlaveRegister(axilEp, x"18", 0,  v.invPulse);
      axiSlaveRegister(axilEp, x"1C", 0,  v.calPulseInh);

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
   GEN_VEC :
   for i in 2 downto 0 generate

      U_hitDetSync : entity work.SynchronizerFifo
         generic map (
            TPD_G        => TPD_G,
            DATA_WIDTH_G => 14)
         port map (
            wr_clk => timingClk320MHz,
            din    => hitDet(i),
            rd_clk => axilClk,
            dout   => hitDetSync(i));

      U_hitDetTime : entity work.SynchronizerFifo
         generic map (
            TPD_G        => TPD_G,
            DATA_WIDTH_G => 16)
         port map (
            wr_clk => timingClk320MHz,
            din    => hitDetTime(i),
            rd_clk => axilClk,
            dout   => hitDetTimeSync(i));

   end generate GEN_VEC;

   ---------------------------
   -- Synchronization: Outputs
   ---------------------------
   U_calPulse : entity work.SynchronizerOneShot
      generic map (
         TPD_G         => TPD_G,
         PULSE_WIDTH_G => 1)
      port map (
         clk     => timingClk320MHz,
         dataIn  => r.calPulse,
         dataOut => calPulse);

   U_invPulse : entity work.Synchronizer
      generic map (
         TPD_G => TPD_G)
      port map (
         clk     => timingClk320MHz,
         dataIn  => r.invPulse,
         dataOut => invPulse);

   U_calWidth : entity work.SynchronizerFifo
      generic map (
         TPD_G        => TPD_G,
         DATA_WIDTH_G => 16)
      port map (
         wr_clk => axilClk,
         din    => r.calWidth,
         rd_clk => timingClk320MHz,
         dout   => calWidth);

   U_calDelay : entity work.SynchronizerFifo
      generic map (
         TPD_G        => TPD_G,
         DATA_WIDTH_G => 16)
      port map (
         wr_clk => axilClk,
         din    => r.calDelay,
         rd_clk => timingClk320MHz,
         dout   => calDelay);

   process (timingClk320MHz, r) is
   begin
      if (rising_edge(timingClk320MHz)) then
         -- Check for one-shot calibration pulse
         if (calPulse = '1') then
            -- Reset the registers
            pulse <= not(invPulse) and not(r.calPulseInh)   after TPD_G;
            cnt   <= (others => '0') after TPD_G;
         else
            -- Check for max. count
            if (cnt = calWidth) then
               -- Set the flag
               pulse <= invPulse and not(r.calPulseInh)     after TPD_G;
            end if;

            -- Increment the counter
            cnt <= cnt + 1 after TPD_G;

         end if;

         -- Check for one-shot calibration pulse
         if (calPulse = '1') then
            -- Set the flag
            pulseDelayed <= invPulse and not(r.calPulseInh)     after TPD_G;
         else
            if (cnt = clcDelay) then
               -- Reset the registers
               pulseDelayed <= not(invPulse) and not(r.calPulseInh)   after TPD_G;
            end if;
            -- Check for max. count
            if (cnt = (calDelay + calWidth)) then
               -- Set the flag
               pulseDelayed <= invPulse and not(r.calPulseInh)     after TPD_G;
            end if;
         end if;

      end if;
   end process;




   GEN_ODDR :
   for i in 1 downto 0 generate

      ODDR_0 :  if (i=0) generate
         U_ODDR : ODDR
            generic map(
               DDR_CLK_EDGE => "SAME_EDGE")
            port map (
               C  => timingClk320MHz,
               Q  => pulseReg(i),
               CE => '1',
               D1 => pulseDelayed,
               D2 => pulseDelayed,
               R  => '0',
               S  => '0');
      end generate;

      ODDR_1 :  if (i=1) generate
         U_ODDR : ODDR
            generic map(
               DDR_CLK_EDGE => "SAME_EDGE")
            port map (
               C  => timingClk320MHz,
               Q  => pulseReg(i),
               CE => '1',
               D1 => pulse,
               D2 => pulse,
               R  => '0',
               S  => '0');
      end generate;

      U_OBUF : OBUF
         port map (
            I => pulseReg(i),
            O => injSig(i));

   end generate GEN_ODDR;

   ----------------------------------------
   -- Hit detection after calibration pulse
   ----------------------------------------
   process (timingClk320MHz) is
      variable i : natural;
   begin
      if (rising_edge(timingClk320MHz)) then
         -- Check for one-shot calibration pulse
         if (calPulse = '1') then
            -- Reset the registers
            hitDet     <= (others => (others => '0')) after TPD_G;
            hitDetTime <= (others => (others => '0')) after TPD_G;
            timer      <= (others => '0')             after TPD_G;
         elsif (timer /= x"FFFF") then
            -- Increment the counter
            timer <= timer + 1 after TPD_G;
            -- Loop through the channels
            for i in 2 downto 0 loop
               -- Check for first hit after calibration pulse
               if (dataValid(i) = '1') and (hitDet(i)(13) = '0') then
                  -- Latch the hit values
                  hitDet(i)(13)          <= dataValid(i) after TPD_G;
                  hitDet(i)(12)          <= multiHit(i)  after TPD_G;
                  hitDet(i)(11 downto 7) <= col(i)       after TPD_G;
                  hitDet(i)(6 downto 0)  <= row(i)       after TPD_G;
                  -- Latch the hit time after calibration pulse
                  hitDetTime(i)          <= timer        after TPD_G;
               end if;
            end loop;
         end if;
      end if;
   end process;

end rtl;
