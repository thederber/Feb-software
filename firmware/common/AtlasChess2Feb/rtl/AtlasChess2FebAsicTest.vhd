-------------------------------------------------------------------------------
-- Title      : 
-------------------------------------------------------------------------------
-- File       : AtlasChess2FebAsicTest.vhd
-- Author     : Larry Ruckman  <ruckman@slac.stanford.edu>
-- Company    : SLAC National Accelerator Laboratory
-- Created    : 2016-06-07
-- Last update: 2017-01-23
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

entity AtlasChess2FebAsicTest is
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
end AtlasChess2FebAsicTest;

architecture rtl of AtlasChess2FebAsicTest is

   type RegType is record
      calPulse       : sl;
      invPulse       : sl;
      calWidth       : slv(15 downto 0);
      axilReadSlave  : AxiLiteReadSlaveType;
      axilWriteSlave : AxiLiteWriteSlaveType;
   end record RegType;

   constant REG_INIT_C : RegType := (
      calPulse       => '0',
      invPulse       => '0',
      calWidth       => toSlv(7, 16),
      axilReadSlave  => AXI_LITE_READ_SLAVE_INIT_C,
      axilWriteSlave => AXI_LITE_WRITE_SLAVE_INIT_C);

   signal r   : RegType := REG_INIT_C;
   signal rin : RegType;

   signal calPulse   : sl;
   signal invPulse   : sl;
   signal pulse      : sl;
   signal pulseReg   : slv(1 downto 0);
   signal calWidth   : slv(15 downto 0);
   signal cnt        : slv(15 downto 0);
   signal hitDet     : Slv14Array(2 downto 0);
   signal hitDetSync : Slv14Array(2 downto 0);

   attribute dont_touch             : string;
   attribute dont_touch of calPulse : signal is "TRUE";
   attribute dont_touch of pulse    : signal is "TRUE";

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
   comb : process (axilReadMaster, axilRst, axilWriteMaster, hitDetSync, r) is
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
      axiSlaveRegister(axilEp, x"10", 0, v.calPulse);
      axiSlaveRegister(axilEp, x"14", 0, v.calWidth);
      axiSlaveRegister(axilEp, x"18", 0, v.invPulse);

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

   process (timingClk320MHz) is
   begin
      if (rising_edge(timingClk320MHz)) then
         if (calPulse = '1') then
            pulse <= not(invPulse)   after TPD_G;
            cnt   <= (others => '0') after TPD_G;
         else
            if (cnt = calWidth) then
               pulse <= invPulse after TPD_G;
            else
               cnt <= cnt + 1 after TPD_G;
            end if;
         end if;
      end if;
   end process;

   GEN_ODDR :
   for i in 1 downto 0 generate

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
         if (calPulse = '1') then
            hitDet <= (others => (others => '0')) after TPD_G;
         else
            for i in 2 downto 0 loop
               if (dataValid(i) = '1') and (hitDet(i)(13) = '0') then
                  hitDet(i)(13)          <= dataValid(i) after TPD_G;
                  hitDet(i)(12)          <= multiHit(i)  after TPD_G;
                  hitDet(i)(11 downto 7) <= col(i)       after TPD_G;
                  hitDet(i)(6 downto 0)  <= row(i)       after TPD_G;
               end if;
            end loop;
         end if;
      end if;
   end process;

end rtl;
