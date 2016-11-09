-------------------------------------------------------------------------------
-- Title      : 
-------------------------------------------------------------------------------
-- File       : AtlasChess2FebTimingMsg.vhd
-- Author     : Larry Ruckman  <ruckman@slac.stanford.edu>
-- Company    : SLAC National Accelerator Laboratory
-- Created    : 2016-06-07
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
use ieee.std_logic_arith.all;
use ieee.std_logic_unsigned.all;

use work.StdRtlPkg.all;
use work.AtlasChess2FebPkg.all;

entity AtlasChess2FebTimingMsg is
   generic (
      TPD_G : time := 1 ns);      
   port (
      -- External Trigger Interface
      extTrig         : in  sl;
      -- PGP OP-Code Interface
      pgpEn           : in  sl;
      pgpOpCode       : in  slv(7 downto 0);
      -- EVR Timing Interface
      evrEn           : in  sl;
      evrTimeStamp    : in  slv(63 downto 0);
      -- Timing Interface
      timingClk320MHz : in  sl;
      timingRst320MHz : in  sl;
      timingTrig      : out sl;
      timingMsg       : out slv(63 downto 0);
      timingMode      : in  TimingModeType);
end AtlasChess2FebTimingMsg;

architecture rtl of AtlasChess2FebTimingMsg is

   constant PGP_SYNC_C : slv(7 downto 0) := x"AA";
   constant PGP_TRIG_C : slv(7 downto 0) := x"55";

   type RegType is record
      timingTrig : sl;
      timingMsg  : slv(63 downto 0);
   end record RegType;
   
   constant REG_INIT_C : RegType := (
      timingTrig => '0',
      timingMsg  => (others => '0'));      

   signal r   : RegType := REG_INIT_C;
   signal rin : RegType;

   signal timingModeSync : TimingModeType;

begin

   U_Sync : entity work.SynchronizerVector
      generic map (
         TPD_G   => TPD_G,
         WIDTH_G => 2)
      port map (
         clk     => timingClk320MHz,
         rst     => timingRst320MHz,
         dataIn  => timingMode,
         dataOut => timingModeSync);

   comb : process (evrEn, evrTimeStamp, extTrig, pgpEn, pgpOpCode, r, timingModeSync,
                   timingRst320MHz) is
      variable v : RegType;
   begin
      -- Latch the current value
      v := r;

      -- Reset the flags
      v.timingTrig := '0';

      -- State Machine
      case (timingModeSync) is
         ----------------------------------------------------------------------
         when TIMING_LEMO_TRIG_C =>
            -- Increment the counter
            v.timingMsg  := r.timingMsg + 1;
            -- Forward the trigger
            v.timingTrig := extTrig;
            -- Check for PGP SYNC
            if (pgpEn = '1') and (pgpOpCode = PGP_SYNC_C) then
               v.timingMsg := (others => '0');
            end if;
         ----------------------------------------------------------------------
         when TIMING_PGP_TRIG_C =>
            -- Increment the counter
            v.timingMsg := r.timingMsg + 1;
            -- Check for PGP Trig
            if (pgpEn = '1') and (pgpOpCode = PGP_TRIG_C) then
               v.timingTrig := '1';
            end if;
            -- Check for PGP SYNC
            if (pgpEn = '1') and (pgpOpCode = PGP_SYNC_C) then
               v.timingMsg := (others => '0');
            end if;
         ----------------------------------------------------------------------
         when TIMING_SLAC_EVR_C =>
            -- Forward the trigger and timestamp
            v.timingTrig := evrEn;
            v.timingMsg  := evrTimeStamp;
         ----------------------------------------------------------------------
         when others =>
            v := REG_INIT_C;
      ----------------------------------------------------------------------
      end case;

      -- Synchronous Reset
      if timingRst320MHz = '1' then
         v := REG_INIT_C;
      end if;

      -- Register the variable for next clock cycle
      rin <= v;

      -- Outputs        
      timingTrig <= r.timingTrig;
      timingMsg  <= r.timingMsg;
      
   end process comb;

   seq : process (timingClk320MHz) is
   begin
      if rising_edge(timingClk320MHz) then
         r <= rin after TPD_G;
      end if;
   end process seq;

end rtl;
