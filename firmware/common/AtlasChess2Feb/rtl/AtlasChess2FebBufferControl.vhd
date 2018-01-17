-------------------------------------------------------------------------------
-- Title      : 
-------------------------------------------------------------------------------
-- File       : AtlasChess2FebAsicChargeInj.vhd
-- Author     : Larry Ruckman  <ruckman@slac.stanford.edu>
-- Company    : SLAC National Accelerator Laboratory
-- Created    : 2016-06-07
-- Last update: 2018-01-17
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

entity AtlasChess2FebBufferControl is
   generic (
      TPD_G            : time            := 1 ns;
      AXI_ERROR_RESP_G : slv(1 downto 0) := AXI_RESP_DECERR_C);
   port (
      -- Control signal
      bufferControl   : out slv(31 downto 0);
      -- AXI-Lite Interface
      axilClk         : in  sl;
      axilRst         : in  sl;
      axilReadMaster  : in  AxiLiteReadMasterType;
      axilReadSlave   : out AxiLiteReadSlaveType;
      axilWriteMaster : in  AxiLiteWriteMasterType;
      axilWriteSlave  : out AxiLiteWriteSlaveType);
end AtlasChess2FebBufferControl;

architecture rtl of AtlasChess2FebBufferControl is

   type RegType is record
      bufferControlReg    : slv(31 downto 0);
      axilReadSlave       : AxiLiteReadSlaveType;
      axilWriteSlave      : AxiLiteWriteSlaveType;
   end record RegType;

   constant REG_INIT_C : RegType := (
      bufferControlReg  => (others=>'0'),
      axilReadSlave     => AXI_LITE_READ_SLAVE_INIT_C,
      axilWriteSlave    => AXI_LITE_WRITE_SLAVE_INIT_C);

   signal r   : RegType := REG_INIT_C;
   signal rin : RegType;


--   attribute dont_touch                   : string;
--   attribute dont_touch of calPulse       : signal is "TRUE";


begin

   --------------------- 
   -- AXI Lite Interface
   --------------------- 
   comb : process (axilReadMaster, axilRst, axilWriteMaster, r) is
      variable v      : RegType;
      variable axilEp : AxiLiteEndPointType;
      variable i      : natural;
   begin
      -- Latch the current value
      v := r;

      -- Determine the transaction type
      axiSlaveWaitTxn(axilEp, axilWriteMaster, axilReadMaster, v.axilWriteSlave, v.axilReadSlave);

      if (axilReadMaster.rready = '1') then
         v.axilReadSlave.rdata := (others => '0');
      end if;
     
      -- Mapping registers     
      axiSlaveRegister (axilEp, x"00", 0, v.bufferControlReg);

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

   --sync ports to axiClk clock
   process(axilClk) begin
      if rising_edge(axilClk) then
         bufferControl <= r.bufferControlReg after TPD_G;
      end if;
   end process;

end rtl;
