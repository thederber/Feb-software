/**
 *-----------------------------------------------------------------------------
 * Title         : Stream sink example.
 * ----------------------------------------------------------------------------
 * File          : StreamSink.h
 * Author        : Ryan Herbst <rherbst@slac.stanford.edu>
 * Created       : 10/23/2016
 * Last update   : 10/23/2016
 *-----------------------------------------------------------------------------
 * Description :
 *    Example class for receiving stream data.
 *-----------------------------------------------------------------------------
 * This file is part of the rogue_example software. It is subject to 
 * the license terms in the LICENSE.txt file found in the top-level directory 
 * of this distribution and at: 
    * https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html. 
 * No part of the rogue_example software, including this file, may be 
 * copied, modified, propagated, or distributed except according to the terms 
 * contained in the LICENSE.txt file.
 *-----------------------------------------------------------------------------
**/
#ifndef __STREAM_SINK_H__
#define __STREAM_SINK_H__
#include <stdint.h>
#include <rogue/interfaces/stream/Slave.h>

//! Receive slave data, count frames and total bytes for example purposes.
class StreamSink : public rogue::interfaces::stream::Slave {

      //! Rx count
      uint32_t rxCount_;

      //! Rx bytes
      uint32_t rxBytes_;

   public:

      //! Class creation
      static boost::shared_ptr<StreamSink> create ();

      //! Setup class in python
      static void setup_python();

      //! Creator with default taps and size
      StreamSink();

      //! Deconstructor
      ~StreamSink();

      //! Get rx count
      uint32_t getRxCount();

      //! Get rx total bytes
      uint32_t getRxBytes();

      //! Reset counters
      void resetCount();

      //! Accept a frame from master
      void acceptFrame ( boost::shared_ptr<rogue::interfaces::stream::Frame> frame );
};

// Convienence
typedef boost::shared_ptr<StreamSink> StreamSinkPtr;

#endif

