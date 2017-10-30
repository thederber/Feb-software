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
      extInjSigTrg    : out sl;
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
   signal hitDet         : Slv112Array(2 downto 0);
   signal hitDetSync     : Slv112Array(2 downto 0);
   signal hitDetTime     : Slv128Array(2 downto 0);
   signal hitDetTimeSync : Slv128Array(2 downto 0);
   signal hitDetIndex    : Slv3Array(2 downto 0);
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
   attribute dont_touch of hitDetIndex    : signal is "TRUE";
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
      axiSlaveRegisterR(axilEp, x"00", 0, hitDetSync(0)(14*0 + 13 downto 14*0));
      axiSlaveRegisterR(axilEp, x"04", 0, hitDetSync(1)(14*0 + 13 downto 14*0));
      axiSlaveRegisterR(axilEp, x"08", 0, hitDetSync(2)(14*0 + 13 downto 14*0));
      axiSlaveRegisterR(axilEp, x"20", 0, hitDetSync(0)(14*1 + 13 downto 14*1));
      axiSlaveRegisterR(axilEp, x"24", 0, hitDetSync(1)(14*1 + 13 downto 14*1));
      axiSlaveRegisterR(axilEp, x"28", 0, hitDetSync(2)(14*1 + 13 downto 14*1));
      axiSlaveRegisterR(axilEp, x"30", 0, hitDetSync(0)(14*2 + 13 downto 14*2));
      axiSlaveRegisterR(axilEp, x"34", 0, hitDetSync(1)(14*2 + 13 downto 14*2));
      axiSlaveRegisterR(axilEp, x"38", 0, hitDetSync(2)(14*2 + 13 downto 14*2));
      axiSlaveRegisterR(axilEp, x"40", 0, hitDetSync(0)(14*3 + 13 downto 14*3));
      axiSlaveRegisterR(axilEp, x"44", 0, hitDetSync(1)(14*3 + 13 downto 14*3));
      axiSlaveRegisterR(axilEp, x"48", 0, hitDetSync(2)(14*3 + 13 downto 14*3));
      axiSlaveRegisterR(axilEp, x"50", 0, hitDetSync(0)(14*4 + 13 downto 14*4));
      axiSlaveRegisterR(axilEp, x"54", 0, hitDetSync(1)(14*4 + 13 downto 14*4));
      axiSlaveRegisterR(axilEp, x"58", 0, hitDetSync(2)(14*4 + 13 downto 14*4));
      axiSlaveRegisterR(axilEp, x"60", 0, hitDetSync(0)(14*5 + 13 downto 14*5));
      axiSlaveRegisterR(axilEp, x"64", 0, hitDetSync(1)(14*5 + 13 downto 14*5));
      axiSlaveRegisterR(axilEp, x"68", 0, hitDetSync(2)(14*5 + 13 downto 14*5));
      axiSlaveRegisterR(axilEp, x"70", 0, hitDetSync(0)(14*6 + 13 downto 14*6));
      axiSlaveRegisterR(axilEp, x"74", 0, hitDetSync(1)(14*6 + 13 downto 14*6));
      axiSlaveRegisterR(axilEp, x"78", 0, hitDetSync(2)(14*6 + 13 downto 14*6));
      axiSlaveRegisterR(axilEp, x"80", 0, hitDetSync(0)(14*7 + 13 downto 14*7));
      axiSlaveRegisterR(axilEp, x"84", 0, hitDetSync(1)(14*7 + 13 downto 14*7));
      axiSlaveRegisterR(axilEp, x"88", 0, hitDetSync(2)(14*7 + 13 downto 14*7));

      axiSlaveRegisterR(axilEp, x"00", 16, hitDetTimeSync(0)(16*0 + 15 downto 16*0));
      axiSlaveRegisterR(axilEp, x"04", 16, hitDetTimeSync(1)(16*0 + 15 downto 16*0));
      axiSlaveRegisterR(axilEp, x"08", 16, hitDetTimeSync(2)(16*0 + 15 downto 16*0));
      axiSlaveRegisterR(axilEp, x"20", 16, hitDetTimeSync(0)(16*1 + 15 downto 16*1));
      axiSlaveRegisterR(axilEp, x"24", 16, hitDetTimeSync(1)(16*1 + 15 downto 16*1));
      axiSlaveRegisterR(axilEp, x"28", 16, hitDetTimeSync(2)(16*1 + 15 downto 16*1));
      axiSlaveRegisterR(axilEp, x"30", 16, hitDetTimeSync(0)(16*2 + 15 downto 16*2));
      axiSlaveRegisterR(axilEp, x"34", 16, hitDetTimeSync(1)(16*2 + 15 downto 16*2));
      axiSlaveRegisterR(axilEp, x"38", 16, hitDetTimeSync(2)(16*2 + 15 downto 16*2));
      axiSlaveRegisterR(axilEp, x"40", 16, hitDetTimeSync(0)(16*3 + 15 downto 16*3));
      axiSlaveRegisterR(axilEp, x"44", 16, hitDetTimeSync(1)(16*3 + 15 downto 16*3));
      axiSlaveRegisterR(axilEp, x"48", 16, hitDetTimeSync(2)(16*3 + 15 downto 16*3));
      axiSlaveRegisterR(axilEp, x"50", 16, hitDetTimeSync(0)(16*4 + 15 downto 16*4));
      axiSlaveRegisterR(axilEp, x"54", 16, hitDetTimeSync(1)(16*4 + 15 downto 16*4));
      axiSlaveRegisterR(axilEp, x"58", 16, hitDetTimeSync(2)(16*4 + 15 downto 16*4));
      axiSlaveRegisterR(axilEp, x"60", 16, hitDetTimeSync(0)(16*5 + 15 downto 16*5));
      axiSlaveRegisterR(axilEp, x"64", 16, hitDetTimeSync(1)(16*5 + 15 downto 16*5));
      axiSlaveRegisterR(axilEp, x"68", 16, hitDetTimeSync(2)(16*5 + 15 downto 16*5));
      axiSlaveRegisterR(axilEp, x"70", 16, hitDetTimeSync(0)(16*6 + 15 downto 16*6));
      axiSlaveRegisterR(axilEp, x"74", 16, hitDetTimeSync(1)(16*6 + 15 downto 16*6));
      axiSlaveRegisterR(axilEp, x"78", 16, hitDetTimeSync(2)(16*6 + 15 downto 16*6));
      axiSlaveRegisterR(axilEp, x"80", 16, hitDetTimeSync(0)(16*7 + 15 downto 16*7));
      axiSlaveRegisterR(axilEp, x"84", 16, hitDetTimeSync(1)(16*7 + 15 downto 16*7));
      axiSlaveRegisterR(axilEp, x"88", 16, hitDetTimeSync(2)(16*7 + 15 downto 16*7));

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
            DATA_WIDTH_G => 112)
         port map (
            wr_clk => timingClk320MHz,
            din    => hitDet(i),
            rd_clk => axilClk,
            dout   => hitDetSync(i));

      U_hitDetTime : entity work.SynchronizerFifo
         generic map (
            TPD_G        => TPD_G,
            DATA_WIDTH_G => 128)
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
            cnt   <= (others => '0') after TPD_G;
         elsif cnt /= x"FFFF" then
            -- Increment the counter
            cnt <= cnt + 1 after TPD_G;
         end if;

         if (calPulse = '1') then
            -- Reset the registers
            pulse <= not(invPulse) and not(r.calPulseInh)   after TPD_G;
         
         else
            -- Check for max. count
            if (cnt = calWidth) then
               -- Set the flag
               pulse <= invPulse and not(r.calPulseInh)     after TPD_G;
            end if;
         end if;

         -- Check for one-shot calibration pulse
         if (calPulse = '1') then
            -- Set the flag
            pulseDelayed <= invPulse and not(r.calPulseInh)     after TPD_G;
         else
            if (cnt = calDelay) then
               -- Reset the registers
               pulseDelayed <= not(invPulse) and not(r.calPulseInh)   after TPD_G;
            end if;
            -- Check for max. count
            if (cnt = (calDelay + calWidth)) then
               -- Set the flag
               pulseDelayed <= invPulse and not(r.calPulseInh)     after TPD_G;
            end if;
         end if;
         extInjSigTrg    <= pulseDelayed;
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
               D1 => pulseDelayed,
               D2 => pulseDelayed,
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
            hitDet          <= (others => (others => '0')) after TPD_G;
            hitDetTime      <= (others => (others => '0')) after TPD_G;
            timer           <= (others => '0')             after TPD_G;
            hitDetIndex     <= (others => (others => '0')) after TPD_G;
         elsif (timer /= x"FFFF") then
            -- Increment the counter
            timer <= timer + 1 after TPD_G;
            -- Loop through the channels
            for i in 2 downto 0 loop
               -- Check for first hit after calibration pulse
               if (dataValid(i) = '1')  then
                  case hitDetIndex(i) is 
                     when "000" =>
                        -- Latch the hit values
                        if  hitDet(i)(14*0 + 13) = '0' then -- this if prevents overwritting the values
                            hitDet(i)(14*0 + 13)                        <= dataValid(i)            after TPD_G;
                            hitDet(i)(14*0 + 12)                        <= multiHit(i)             after TPD_G;
                            hitDet(i)(14*0 + 11 downto 14*0 + 7)        <= col(i)                  after TPD_G;
                            hitDet(i)(14*0 + 6  downto 14*0 + 0)        <= row(i)                  after TPD_G;
                            -- Latch the hit time after calibration pulse
                            hitDetTime(i)(16*0 + 15 downto 16*0 + 0)    <= timer                   after TPD_G;
                        end if;
                     when "001" =>
                        -- Latch the hit values
                        if hitDet(i)(14*1 + 13) = '0' then
                           hitDet(i)(14*1 + 13)                        <= dataValid(i)            after TPD_G;
                           hitDet(i)(14*1 + 12)                        <= multiHit(i)             after TPD_G;
                           hitDet(i)(14*1 + 11 downto 14*1 + 7)        <= col(i)                  after TPD_G;
                           hitDet(i)(14*1 + 6  downto 14*1 + 0)        <= row(i)                  after TPD_G;
                           -- Latch the hit time after calibration pulse
                           hitDetTime(i)(16*1 + 15 downto 16*1 + 0)    <= timer                   after TPD_G;
                        end if;
                     when "010" =>
                        -- Latch the hit values
                        if hitDet(i)(14*2 + 13) = '0' then
                           hitDet(i)(14*2 + 13)                        <= dataValid(i)            after TPD_G;
                           hitDet(i)(14*2 + 12)                        <= multiHit(i)             after TPD_G;
                           hitDet(i)(14*2 + 11 downto 14*2 + 7)        <= col(i)                  after TPD_G;
                           hitDet(i)(14*2 + 6  downto 14*2 + 0)        <= row(i)                  after TPD_G;
                           -- Latch the hit time after calibration pulse
                           hitDetTime(i)(16*2 + 15 downto 16*2 + 0)    <= timer                   after TPD_G;
                        end if;
                     when "011" =>
                        -- Latch the hit values
                        if hitDet(i)(14*3 + 13) = '0' then
                           hitDet(i)(14*3 + 13)                        <= dataValid(i)            after TPD_G;
                           hitDet(i)(14*3 + 12)                        <= multiHit(i)             after TPD_G;
                           hitDet(i)(14*3 + 11 downto 14*3 + 7)        <= col(i)                  after TPD_G;
                           hitDet(i)(14*3 + 6  downto 14*3 + 0)        <= row(i)                  after TPD_G;
                           -- Latch the hit time after calibration pulse
                           hitDetTime(i)(16*3 + 15 downto 16*3 + 0)    <= timer                   after TPD_G;
                        end if;
                     when "100" =>
                        -- Latch the hit values
                        if hitDet(i)(14*4 + 13) = '0' then
                           hitDet(i)(14*4 + 13)                        <= dataValid(i)            after TPD_G;
                           hitDet(i)(14*4 + 12)                        <= multiHit(i)             after TPD_G;
                           hitDet(i)(14*4 + 11 downto 14*4 + 7)        <= col(i)                  after TPD_G;
                           hitDet(i)(14*4 + 6  downto 14*4 + 0)        <= row(i)                  after TPD_G;
                           -- Latch the hit time after calibration pulse
                           hitDetTime(i)(16*4 + 15 downto 16*4 + 0)    <= timer                   after TPD_G;
                        end if;
                     when "101" =>
                        -- Latch the hit values
                        if hitDet(i)(14*5 + 13) = '0' then
                           hitDet(i)(14*5 + 13)                        <= dataValid(i)            after TPD_G;
                           hitDet(i)(14*5 + 12)                        <= multiHit(i)             after TPD_G;
                           hitDet(i)(14*5 + 11 downto 14*5 + 7)        <= col(i)                  after TPD_G;
                           hitDet(i)(14*5 + 6  downto 14*5 + 0)        <= row(i)                  after TPD_G;
                           -- Latch the hit time after calibration pulse
                           hitDetTime(i)(16*5 + 15 downto 16*5 + 0)    <= timer                   after TPD_G;
                        end if;
                     when "110" =>
                        -- Latch the hit values
                        if hitDet(i)(14*6 + 13) = '0' then
                           hitDet(i)(14*6 + 13)                        <= dataValid(i)            after TPD_G;
                           hitDet(i)(14*6 + 12)                        <= multiHit(i)             after TPD_G;
                           hitDet(i)(14*6 + 11 downto 14*6 + 7)        <= col(i)                  after TPD_G;
                           hitDet(i)(14*6 + 6  downto 14*6 + 0)        <= row(i)                  after TPD_G;
                           -- Latch the hit time after calibration pulse
                           hitDetTime(i)(16*6 + 15 downto 16*6 + 0)    <= timer                   after TPD_G;
                        end if;
                     when "111" =>
                        -- Latch the hit values
                        if hitDet(i)(14*7 + 13) = '0' then
                           hitDet(i)(14*7 + 13)                        <= dataValid(i)            after TPD_G;
                           hitDet(i)(14*7 + 12)                        <= multiHit(i)             after TPD_G;
                           hitDet(i)(14*7 + 11 downto 14*7 + 7)        <= col(i)                  after TPD_G;
                           hitDet(i)(14*7 + 6  downto 14*7 + 0)        <= row(i)                  after TPD_G;
                           -- Latch the hit time after calibration pulse
                           hitDetTime(i)(16*7 + 15 downto 16*7 + 0)    <= timer                   after TPD_G;
                        end if;
                  end case;

                  -- Increment hit index
                  hitDetIndex(i)                                                  <= hitDetIndex(i)     + 1 after TPD_G;
               end if;
            end loop;
         end if;
      end if;
   end process;

end rtl;
