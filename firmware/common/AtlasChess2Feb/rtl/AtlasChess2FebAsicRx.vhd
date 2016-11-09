-------------------------------------------------------------------------------
-- Title      : 
-------------------------------------------------------------------------------
-- File       : AtlasChess2FebAsicRx.vhd
-- Author     : Larry Ruckman  <ruckman@slac.stanford.edu>
-- Company    : SLAC National Accelerator Laboratory
-- Created    : 2016-06-01
-- Last update: 2016-08-30
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
use work.AxiLitePkg.all;
use work.AxiStreamPkg.all;
use work.SsiPkg.all;

library unisim;
use unisim.vcomponents.all;

entity AtlasChess2FebAsicRx is
   generic (
      TPD_G              : time            := 1 ns;
      AXI_ERROR_RESP_G   : slv(1 downto 0) := AXI_RESP_DECERR_C;
      INDEX_G            : natural         := 0;
      DELAY_ADDR_WIDTH_G : positive        := 10;
      IODELAY_GROUP_G    : string          := "CHESS2_IODELAY_GRP");
   port (
      -- CHESS2 ASIC Ports
      chessDinP       : in  slv(13 downto 0);
      chessDinN       : in  slv(13 downto 0);
      chessClk320MHzP : out sl;
      chessClk320MHzN : out sl;
      chessClk40MHz   : out sl;
      -- Reference clock and Reset
      refClk200MHz    : in  sl;
      refRst200MHz    : in  sl;
      -- Timing Interface
      timingClk40MHz  : in  sl;
      timingRst40MHz  : in  sl;
      timingClk320MHz : in  sl;
      timingRst320MHz : in  sl;
      dlyRst          : in  sl;
      dlyChess        : in  slv(DELAY_ADDR_WIDTH_G-1 downto 0);
      -- CHESS2 RX Output
      dataValid       : out sl;
      multiHit        : out sl;
      col             : out slv(4 downto 0);
      row             : out slv(6 downto 0);
      -- AXI-Lite Register Interface
      axilClk         : in  sl;
      axilRst         : in  sl;
      axilReadMaster  : in  AxiLiteReadMasterType;
      axilReadSlave   : out AxiLiteReadSlaveType;
      axilWriteMaster : in  AxiLiteWriteMasterType;
      axilWriteSlave  : out AxiLiteWriteSlaveType);
end AtlasChess2FebAsicRx;

architecture mapping of AtlasChess2FebAsicRx is

   signal phaseSel      : slv(13 downto 0);
   signal delayInLoad   : slv(13 downto 0);
   signal delayInData   : Slv5Array(13 downto 0);
   signal delayOutData  : Slv5Array(13 downto 0);
   signal chessDin      : slv(13 downto 0);
   signal chessDinDelay : slv(13 downto 0);
   signal delayCnt      : slv(DELAY_ADDR_WIDTH_G-1 downto 0);
   signal delayRdEn     : sl;

begin

   U_ClkOutBuf320MHz : entity work.ClkOutBufDiff
      port map (
         clkIn   => timingClk320MHz,
         clkOutP => chessClk320MHzP,
         clkOutN => chessClk320MHzN);

   U_ClkOutBuf40MHz : entity work.ClkOutBufSingle
      port map (
         clkIn  => timingClk40MHz,
         clkOut => chessClk40MHz);

   U_Rx :
   for i in 13 downto 0 generate
      U_Bit : entity work.AtlasChess2FebAsicRxIdelay
         generic map (
            TPD_G           => TPD_G,
            IODELAY_GROUP_G => IODELAY_GROUP_G)
         port map (
            -- ADC Data (clk320MHz domain)
            dataInP      => chessDinP(i),
            dataInN      => chessDinN(i),
            dataOut      => chessDin(i),
            phaseSel     => phaseSel(i),
            -- IO_Delay (refClk200MHz domain)
            delayInLoad  => delayInLoad(i),
            delayInData  => delayInData(i),
            delayOutData => delayOutData(i),
            -- Clocks
            clk320MHz    => timingClk320MHz,
            refClk200MHz => refClk200MHz);      
   end generate;

   U_Delay : entity work.FifoSync
      generic map (
         TPD_G         => TPD_G,
         BRAM_EN_G     => true,
         FWFT_EN_G     => true,
         PIPE_STAGES_G => 1,            -- Pipeline to help with timing 
         DATA_WIDTH_G  => 14,
         ADDR_WIDTH_G  => DELAY_ADDR_WIDTH_G)
      port map (
         clk        => timingClk320MHz,
         rst        => dlyRst,
         din        => chessDin,
         wr_en      => '1',
         rd_en      => delayRdEn,
         data_count => delayCnt,
         dout       => chessDinDelay);   

   delayRdEn <= '1' when(delayCnt >= dlyChess) else '0';

   -- Decode the data bus
   dataValid <= chessDinDelay(0);
   multiHit  <= chessDinDelay(1);
   col(4)    <= chessDinDelay(2);
   col(3)    <= chessDinDelay(3);
   col(2)    <= chessDinDelay(4);
   col(1)    <= chessDinDelay(5);
   col(0)    <= chessDinDelay(6);
   row(0)    <= chessDinDelay(7);
   row(1)    <= chessDinDelay(8);
   row(2)    <= chessDinDelay(9);
   row(3)    <= chessDinDelay(10);
   row(4)    <= chessDinDelay(11);
   row(5)    <= chessDinDelay(12);
   row(6)    <= chessDinDelay(13);

   U_Reg : entity work.AtlasChess2FebAsicRxReg
      generic map (
         TPD_G            => TPD_G,
         AXI_ERROR_RESP_G => AXI_ERROR_RESP_G)
      port map (
         -- IDelay Control Interface
         refClk200MHz    => refClk200MHz,
         refRst200MHz    => refRst200MHz,
         phaseSel        => phaseSel,
         delayInLoad     => delayInLoad,
         delayInData     => delayInData,
         delayOutData    => delayOutData,
         -- AXI-Lite Register Interface
         axilClk         => axilClk,
         axilRst         => axilRst,
         axilReadMaster  => axilReadMaster,
         axilReadSlave   => axilReadSlave,
         axilWriteMaster => axilWriteMaster,
         axilWriteSlave  => axilWriteSlave);

end mapping;
