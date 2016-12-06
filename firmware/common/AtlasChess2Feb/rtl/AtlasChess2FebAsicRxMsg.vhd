-------------------------------------------------------------------------------
-- Title      : 
-------------------------------------------------------------------------------
-- File       : AtlasChess2FebAsicRxMsg.vhd
-- Author     : Larry Ruckman  <ruckman@slac.stanford.edu>
-- Company    : SLAC National Accelerator Laboratory
-- Created    : 2016-06-01
-- Last update: 2016-12-05
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
use work.AxiStreamPkg.all;
use work.SsiPkg.all;
use work.Pgp2bPkg.all;

entity AtlasChess2FebAsicRxMsg is
   generic (
      TPD_G          : time                  := 1 ns;
      COMM_MODE_G    : boolean               := false;
      NUM_ASIC_G     : positive range 1 to 4 := 3;
      CASCADE_SIZE_G : positive              := 4);
   port (
      -- CHESS2 Interface
      dataValid       : in  slv(NUM_ASIC_G-1 downto 0);
      multiHit        : in  slv(NUM_ASIC_G-1 downto 0);
      col             : in  Slv5Array(NUM_ASIC_G-1 downto 0);
      row             : in  Slv7Array(NUM_ASIC_G-1 downto 0);
      -- CHESS2 Configuration
      destId          : in  slv(5 downto 0);
      opCode          : in  slv(7 downto 0);
      frameType       : in  slv(31 downto 0);
      wordSize        : in  slv(7 downto 0);
      -- Timing Interface
      timingClk320MHz : in  sl;
      timingRst320MHz : in  sl;
      timingTrig      : in  sl;
      timingMsg       : in  slv(63 downto 0);
      -- AXI Stream Interface
      axisClk         : in  sl;
      axisRst         : in  sl;
      extBusy         : out sl;
      mAxisMaster     : out AxiStreamMasterType;
      mAxisSlave      : in  AxiStreamSlaveType);
end AtlasChess2FebAsicRxMsg;

architecture mapping of AtlasChess2FebAsicRxMsg is

   constant AXIS_CONFIG_C : AxiStreamConfigType := ssiAxiStreamConfig(16);
   
   type StateType is (
      IDLE_S,
      HDR_S,
      CATCHUP_A_S,
      CATCHUP_B_S,
      MOVE_S); 

   type RegType is record
      wordSize  : slv(7 downto 0);
      frame     : slv(31 downto 0);
      trigCnt   : slv(15 downto 0);
      tData     : Slv64Array(2 downto 0);
      timingMsg : slv(31 downto 0);
      cnt       : slv(7 downto 0);
      txMaster  : AxiStreamMasterType;
      state     : StateType;
   end record RegType;
   
   constant REG_INIT_C : RegType := (
      wordSize  => (others => '0'),
      frame     => (others => '0'),
      trigCnt   => (others => '0'),
      tData     => (others => (others => '0')),
      timingMsg => (others => '0'),
      cnt       => (others => '0'),
      txMaster  => AXI_STREAM_MASTER_INIT_C,
      state     => IDLE_S);      

   signal r   : RegType := REG_INIT_C;
   signal rin : RegType;

   signal txCtrl : AxiStreamCtrlType;

   -- attribute dont_touch           : string;
   -- attribute dont_touch of r      : signal is "TRUE";
   -- attribute dont_touch of txCtrl : signal is "TRUE";

begin

   comb : process (col, dataValid, destId, frameType, multiHit, opCode, r, row, timingMsg,
                   timingRst320MHz, timingTrig, txCtrl, wordSize) is
      variable v    : RegType;
      variable i    : natural;
      variable data : slv(63 downto 0);
   begin
      -- Latch the current value
      v := r;

      -- Format the data word
      data := (others => '0');
      for i in NUM_ASIC_G-1 downto 0 loop
         data(13+(16*i) downto (16*i)) := dataValid(i) & multiHit(i) & col(i) & row(i);
      end loop;

      -- Reset the flags
      v.txMaster.tValid := '0';
      v.txMaster.tLast  := '0';
      v.txMaster.tUser  := (others => '0');

      -- Wait for trigger
      if timingTrig = '1' then
         -- Increment the counter
         v.trigCnt := r.trigCnt + 1;
      end if;

      -- State Machine
      case (r.state) is
         ----------------------------------------------------------------------
         when IDLE_S =>
            -- Wait for trigger and ready to move data
            if (timingTrig = '1') and (txCtrl.pause = '0') then
               -- Send the header
               v.txMaster.tValid               := '1';
               v.txMaster.tKeep                := x"FFFF";
               -- Increment the counter
               v.frame                         := r.frame + 1;
               -- Set SOF bit
               ssiSetUserSof(AXIS_CONFIG_C, v.txMaster, '1');
               -- Set the hdr[0]
               v.txMaster.tData(1 downto 0)    := "00";  -- Virtual Channel ID = 0x0        
               v.txMaster.tData(7 downto 2)    := destId;              -- Destination ID = lane + Z
               v.txMaster.tData(31 downto 8)   := r.frame(23 downto 0);    -- Transaction ID
               -- Set the hdr[1]
               v.txMaster.tData(47 downto 32)  := r.trigCnt;           -- Acquire Counter
               v.txMaster.tData(55 downto 48)  := opCode;              -- OP Code
               v.txMaster.tData(59 downto 56)  := "0000";              -- Element ID
               v.txMaster.tData(63 downto 60)  := destId(3 downto 0);  -- Destination ID = Z only
               -- Set the hdr[2]
               v.txMaster.tData(95 downto 64)  := r.frame;             -- Frame Number
               -- Set the hdr[3]
               v.txMaster.tData(127 downto 96) := timingMsg(31 downto 0);  -- Ticks
               -- Save the data and reset of the timing message
               v.tData(0)                      := data;
               v.timingMsg                     := timingMsg(63 downto 32);
               -- Next state
               v.state                         := HDR_S;
            end if;
         ----------------------------------------------------------------------
         when HDR_S =>
            -- Send the header
            v.txMaster.tValid               := '1';
            v.txMaster.tKeep                := x"FFFF";
            -- Set the hdr[4]
            v.txMaster.tData(31 downto 0)   := r.timingMsg;            -- Fiducials  
            -- Set the hdr[5]
            v.txMaster.tData(47 downto 32)  := x"0000";  -- sbtemp[0]              
            v.txMaster.tData(63 downto 48)  := x"0000";  -- sbtemp[1]   
            -- Set the hdr[6]
            v.txMaster.tData(79 downto 64)  := x"0000";  -- sbtemp[2]              
            v.txMaster.tData(95 downto 80)  := x"0000";  -- sbtemp[3]               
            -- Set the hdr[7]
            v.txMaster.tData(127 downto 96) := frameType;              -- =Frame Type         
            -- Save the data
            v.tData(1)                      := data;
            v.wordSize                      := wordSize;
            -- Next state
            v.state                         := CATCHUP_A_S;
         ----------------------------------------------------------------------
         when CATCHUP_A_S =>
            -- Send the data
            v.txMaster.tValid               := '1';
            v.txMaster.tData(63 downto 0)   := r.tData(0);
            v.txMaster.tData(127 downto 64) := r.tData(1);
            -- Save the data
            v.tData(2)                      := data;
            -- Check the packet length
            if r.wordSize = 0 then
               -- Terminate the frame
               v.txMaster.tKeep := x"00FF";
               v.txMaster.tLast := '1';
               -- Next state
               v.state          := IDLE_S;
            elsif r.wordSize = 1 then
               -- Terminate the frame
               v.txMaster.tKeep := x"FFFF";
               v.txMaster.tLast := '1';
               -- Next state
               v.state          := IDLE_S;
            else
               -- Next state
               v.state := CATCHUP_B_S;
            end if;
         ----------------------------------------------------------------------
         when CATCHUP_B_S =>
            -- Send the data
            v.txMaster.tValid               := '1';
            v.txMaster.tData(63 downto 0)   := r.tData(2);
            v.txMaster.tData(127 downto 64) := data;
            -- Check the packet length
            if r.wordSize = 2 then
               -- Terminate the frame
               v.txMaster.tKeep := x"00FF";
               v.txMaster.tLast := '1';
               -- Next state
               v.state          := IDLE_S;
            elsif r.wordSize = 3 then
               -- Terminate the frame
               v.txMaster.tKeep := x"FFFF";
               v.txMaster.tLast := '1';
               -- Next state
               v.state          := IDLE_S;
            else
               -- Setup for continuous
               v.cnt            := x"04";
               v.txMaster.tKeep := x"FFFF";
               -- Next state
               v.state          := MOVE_S;
            end if;
         ----------------------------------------------------------------------
         when MOVE_S =>
            -- Increment the counter
            v.cnt := r.cnt + 1;
            -- Check for WRD[0]
            if r.txMaster.tKeep = x"FFFF" then
               v.txMaster.tKeep              := x"00FF";
               v.txMaster.tData(63 downto 0) := data;
            -- Check for WRD[1]
            else
               v.txMaster.tValid               := '1';
               v.txMaster.tKeep                := x"FFFF";
               v.txMaster.tData(127 downto 64) := data;
            end if;
            -- Check the packet length
            if r.wordSize = r.cnt then
               -- Terminate the frame
               v.txMaster.tValid := '1';
               v.txMaster.tLast  := '1';
               -- Next state
               v.state           := IDLE_S;
            end if;
      ----------------------------------------------------------------------
      end case;

      -- Synchronous Reset
      if timingRst320MHz = '1' then
         v := REG_INIT_C;
      end if;

      -- Register the variable for next clock cycle
      rin <= v;

      -- Outputs
      extBusy <= txCtrl.pause;
      
   end process comb;

   seq : process (timingClk320MHz) is
   begin
      if rising_edge(timingClk320MHz) then
         r <= rin after TPD_G;
      end if;
   end process seq;

   TX_FIFO : entity work.AxiStreamFifo
      generic map (
         -- General Configurations
         TPD_G               => TPD_G,
         INT_PIPE_STAGES_G   => 1,
         PIPE_STAGES_G       => 1,
         SLAVE_READY_EN_G    => false,
         VALID_THOLD_G       => 1,
         -- FIFO configurations
         BRAM_EN_G           => true,
         USE_BUILT_IN_G      => false,
         GEN_SYNC_FIFO_G     => false,
         CASCADE_SIZE_G      => CASCADE_SIZE_G,
         FIFO_ADDR_WIDTH_G   => 9,
         FIFO_FIXED_THRESH_G => true,
         FIFO_PAUSE_THRESH_G => 250,
         CASCADE_PAUSE_SEL_G => (CASCADE_SIZE_G-1),
         -- AXI Stream Port Configurations
         SLAVE_AXI_CONFIG_G  => AXIS_CONFIG_C,
         MASTER_AXI_CONFIG_G => ite(COMM_MODE_G, ssiAxiStreamConfig(4), SSI_PGP2B_CONFIG_C)) 
      port map (
         -- Slave Port
         sAxisClk    => timingClk320MHz,
         sAxisRst    => timingRst320MHz,
         sAxisMaster => r.txMaster,
         sAxisCtrl   => txCtrl,
         -- Master Port
         mAxisClk    => axisClk,
         mAxisRst    => axisRst,
         mAxisMaster => mAxisMaster,
         mAxisSlave  => mAxisSlave);    

end mapping;
