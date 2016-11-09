-------------------------------------------------------------------------------
-- Title      : 
-------------------------------------------------------------------------------
-- File       : AtlasChess2FebAsicRxReg.vhd
-- Author     : Larry Ruckman  <ruckman@slac.stanford.edu>
-- Company    : SLAC National Accelerator Laboratory
-- Created    : 2016-06-01
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
use ieee.std_logic_unsigned.all;
use ieee.std_logic_arith.all;

use work.StdRtlPkg.all;
use work.AxiLitePkg.all;

entity AtlasChess2FebAsicRxReg is
   generic (
      TPD_G            : time            := 1 ns;
      AXI_ERROR_RESP_G : slv(1 downto 0) := AXI_RESP_DECERR_C);
   port (
      -- IDelay Control Interface
      refClk200MHz    : in  sl;
      refRst200MHz    : in  sl;
      phaseSel        : out slv(13 downto 0);
      delayInLoad     : out slv(13 downto 0);
      delayInData     : out Slv5Array(13 downto 0);
      delayOutData    : in  Slv5Array(13 downto 0);
      -- AXI-Lite Register Interface
      axilClk         : in  sl;
      axilRst         : in  sl;
      axilReadMaster  : in  AxiLiteReadMasterType;
      axilReadSlave   : out AxiLiteReadSlaveType;
      axilWriteMaster : in  AxiLiteWriteMasterType;
      axilWriteSlave  : out AxiLiteWriteSlaveType);
end AtlasChess2FebAsicRxReg;

architecture rtl of AtlasChess2FebAsicRxReg is

   type RegType is record
      phaseSel       : slv(13 downto 0);
      delayLoad      : slv(13 downto 0);
      delayData      : Slv5Array(13 downto 0);
      axilReadSlave  : AxiLiteReadSlaveType;
      axilWriteSlave : AxiLiteWriteSlaveType;
   end record RegType;
   
   constant REG_INIT_C : RegType := (
      phaseSel       => (others => '0'),
      delayLoad      => (others => '0'),
      delayData      => (others => (others => '0')),
      axilReadSlave  => AXI_LITE_READ_SLAVE_INIT_C,
      axilWriteSlave => AXI_LITE_WRITE_SLAVE_INIT_C);

   signal r   : RegType := REG_INIT_C;
   signal rin : RegType;

   signal delayData : Slv5Array(13 downto 0);

   -- attribute dont_touch      : string;
   -- attribute dont_touch of r : signal is "true";
   
begin

   comb : process (axilReadMaster, axilRst, axilWriteMaster, delayData, r) is
      variable v             : RegType;
      variable axilStatus    : AxiLiteStatusType;
      variable wrIndex       : natural range 0 to 15;
      variable rdIndex       : natural range 0 to 15;
      variable axilWriteResp : slv(1 downto 0);
      variable axilReadResp  : slv(1 downto 0);
   begin
      -- Latch the current value
      v := r;

      -- Reset strobe signals
      v.delayLoad           := (others => '0');
      v.axilReadSlave.rdata := (others => '0');
      axilWriteResp         := AXI_RESP_OK_C;
      axilReadResp          := AXI_RESP_OK_C;

      -- Determine the transaction type
      axiSlaveWaitTxn(axilWriteMaster, axilReadMaster, v.axilWriteSlave, v.axilReadSlave, axilStatus);

      -- Update the variables
      wrIndex := conv_integer(axilWriteMaster.awaddr(5 downto 2));
      rdIndex := conv_integer(axilReadMaster.araddr(5 downto 2));

      -- Check for write operation
      if (axilStatus.writeEnable = '1') then
         if (wrIndex < 14) then
            -- Update the IDelay channel
            v.delayLoad(wrIndex) := '1';
            v.delayData(wrIndex) := axilWriteMaster.wdata(4 downto 0);
         elsif (wrIndex = 14) then
            -- Update the phase select bus
            v.phaseSel := axilWriteMaster.wdata(13 downto 0);
         else
            -- Address Decoding error
            axilWriteResp := AXI_ERROR_RESP_G;
         end if;
         -- Send AXI-Lite response
         axiSlaveWriteResponse(v.axilWriteSlave, axilWriteResp);
      end if;

      -- Check for read operation
      if (axilStatus.readEnable = '1') then
         if (rdIndex < 14) then
            -- Return the delay configuration
            v.axilReadSlave.rdata(4 downto 0) := delayData(rdIndex);
         elsif (rdIndex = 14) then
            -- Return the phase select value
            v.axilReadSlave.rdata(13 downto 0) := r.phaseSel;
         else
            -- Address Decoding error
            axilReadResp := AXI_ERROR_RESP_G;
         end if;
         -- Send AXI-Lite response
         axiSlaveReadResponse(v.axilReadSlave, axilReadResp);
      end if;

      -- Synchronous Reset
      if axilRst = '1' then
         v := REG_INIT_C;
      end if;

      -- Register the variable for next clock cycle
      rin <= v;

      -- Outputs
      axilReadSlave  <= r.axilReadSlave;
      axilWriteSlave <= r.axilWriteSlave;
      
   end process comb;

   seq : process (axilClk) is
   begin
      if rising_edge(axilClk) then
         r <= rin after TPD_G;
      end if;
   end process seq;

   SyncOutPhaseSel : entity work.SynchronizerVector
      generic map (
         TPD_G   => TPD_G,
         WIDTH_G => 14)
      port map (
         clk     => refClk200MHz,
         dataIn  => r.phaseSel,
         dataOut => phaseSel);       

   GEN_DELAY_CH :
   for i in 13 downto 0 generate
      
      SyncOutDelayLoad : entity work.PwrUpRst
         generic map (
            TPD_G      => TPD_G,
            DURATION_G => 32)
         port map (
            clk    => refClk200MHz,
            arst   => r.delayLoad(i),
            rstOut => delayInLoad(i));           

      SyncOutDelayData : entity work.SynchronizerVector
         generic map (
            TPD_G   => TPD_G,
            WIDTH_G => 5)
         port map (
            clk     => refClk200MHz,
            dataIn  => r.delayData(i),
            dataOut => delayInData(i));    

      SyncInDelayData : entity work.SynchronizerVector
         generic map (
            TPD_G   => TPD_G,
            WIDTH_G => 5)
         port map (
            clk     => axilClk,
            dataIn  => delayOutData(i),
            dataOut => delayData(i));       

   end generate GEN_DELAY_CH;

end rtl;
