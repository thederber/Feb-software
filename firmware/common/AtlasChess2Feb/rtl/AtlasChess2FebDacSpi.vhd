-------------------------------------------------------------------------------
-- Title      : 
-------------------------------------------------------------------------------
-- File       : AtlasChess2FebDacSpi.vhd
-- Author     : Larry Ruckman  <ruckman@slac.stanford.edu>
-- Company    : SLAC National Accelerator Laboratory
-- Created    : 2016-02-19
-- Last update: 2016-12-04
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

entity AtlasChess2FebDacSpi is
   generic (
      TPD_G            : time            := 1 ns;
      AXI_CLK_FREQ_G   : real            := 156.25E+6;
      AXI_ERROR_RESP_G : slv(1 downto 0) := AXI_RESP_DECERR_C);
   port (
      -- AXI-Lite Interface
      axilClk         : in  sl;
      axilRst         : in  sl;
      axilReadMaster  : in  AxiLiteReadMasterType;
      axilReadSlave   : out AxiLiteReadSlaveType;
      axilWriteMaster : in  AxiLiteWriteMasterType;
      axilWriteSlave  : out AxiLiteWriteSlaveType;
      -- Slow DAC's SPI Ports
      dacSlowCsL      : out sl;
      dacSlowSck      : out sl;
      dacSlowMosi     : out sl);
end AtlasChess2FebDacSpi;

architecture rtl of AtlasChess2FebDacSpi is

   constant DATA_SIZE_C : positive := 16;

   type RegType is record
      wrEn           : sl;
      wrData         : slv(DATA_SIZE_C-1 downto 0);
      data           : Slv12Array(3 downto 0);
      axilReadSlave  : AxiLiteReadSlaveType;
      axilWriteSlave : AxiLiteWriteSlaveType;
   end record RegType;
   
   constant REG_INIT_C : RegType := (
      wrEn           => '0',
      wrData         => (others => '0'),
      data           => (others => (others => '0')),
      axilReadSlave  => AXI_LITE_READ_SLAVE_INIT_C,
      axilWriteSlave => AXI_LITE_WRITE_SLAVE_INIT_C);   

   signal r   : RegType := REG_INIT_C;
   signal rin : RegType;

   signal rdy : sl;

   -- attribute dont_touch               : string;
   -- attribute dont_touch of r          : signal is "TRUE";
   
begin

   U_SpiMaster : entity work.SpiMaster
      generic map (
         TPD_G             => TPD_G,
         NUM_CHIPS_G       => 1,
         DATA_SIZE_G       => DATA_SIZE_C,
         CPHA_G            => '0',      -- Sample on leading edge
         CPOL_G            => '0',      -- Sample on rising edge
         CLK_PERIOD_G      => (1.0/AXI_CLK_FREQ_G),
         SPI_SCLK_PERIOD_G => 1.0E-6)
      port map (
         clk       => axilClk,
         sRst      => axilRst,
         chipSel   => "0",
         wrEn      => r.wrEn,
         wrData    => r.wrData,
         rdEn      => rdy,
         rdData    => open,
         spiCsL(0) => dacSlowCsL,
         spiSclk   => dacSlowSck,
         spiSdi    => dacSlowMosi,
         spiSdo    => '0');

   --------------------- 
   -- AXI Lite Interface
   --------------------- 
   comb : process (axilReadMaster, axilRst, axilWriteMaster, r, rdy) is
      variable v             : RegType;
      variable axilStatus    : AxiLiteStatusType;
      variable axilWriteResp : slv(1 downto 0);
      variable axilReadResp  : slv(1 downto 0);
   begin
      -- Latch the current value
      v := r;

      -- Determine the transaction type
      axiSlaveWaitTxn(axilWriteMaster, axilReadMaster, v.axilWriteSlave, v.axilReadSlave, axilStatus);

      -- Reset the strobes
      axilWriteResp := AXI_RESP_OK_C;
      axilReadResp  := AXI_RESP_OK_C;
      v.wrEn        := '0';

      -- Check for write request and not in the middle of SPI transaction 
      if (axilStatus.writeEnable = '1') and (rdy = '1') then
         -- Decode address and perform write
         case (axilWriteMaster.awaddr(3 downto 0)) is
            when x"0"   => v.data(0)     := axilWriteMaster.wdata(11 downto 0);
            when x"4"   => v.data(1)     := axilWriteMaster.wdata(11 downto 0);
            when x"8"   => v.data(2)     := axilWriteMaster.wdata(11 downto 0);
            when x"C"   => v.data(3)     := axilWriteMaster.wdata(11 downto 0);
            when others => axilWriteResp := AXI_ERROR_RESP_G;
         end case;
         -- Send AXI-Lite Response
         axiSlaveWriteResponse(v.axilWriteSlave, axilWriteResp);
      end if;

      -- Check for read request
      if (axilStatus.readEnable = '1') then
         -- Decode address and perform read
         case (axilReadMaster.araddr(3 downto 0)) is
            when x"0"   => v.axilReadSlave.rdata(11 downto 0) := r.data(0);
            when x"4"   => v.axilReadSlave.rdata(11 downto 0) := r.data(1);
            when x"8"   => v.axilReadSlave.rdata(11 downto 0) := r.data(2);
            when x"C"   => v.axilReadSlave.rdata(11 downto 0) := r.data(3);
            when others => axilReadResp                       := AXI_ERROR_RESP_G;
         end case;
         -- Send AXI-Lite Response
         axiSlaveReadResponse(v.axilReadSlave, axilReadResp);
      end if;

      -- Loop through the channels
      for i in 3 downto 0 loop
         -- Check if any register changed
         if (r.data(i)) /= (v.data(i)) then
            -- Start the SPI transfer
            v.wrEn                 := '1';
            -- Update the write data bus
            v.wrData(15 downto 14) := toSlv(i, 2);  -- Address Bits
            v.wrData(13 downto 12) := "00";         -- Normal operation.
            v.wrData(11 downto 0)  := v.data(i);    -- DAC Value
         end if;
      end loop;

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
   
end rtl;
