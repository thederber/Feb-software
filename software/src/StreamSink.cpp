/**
 *-----------------------------------------------------------------------------
 * Title         : Stream sink example.
 * ----------------------------------------------------------------------------
 * File          : StreamSink.cpp
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
#include <unistd.h>
#include <stdarg.h>
#include <boost/make_shared.hpp>
#include <rogue/common.h>
#include <rogue/interfaces/stream/Frame.h>
#include "StreamSink.h"

namespace ris = rogue::interfaces::stream;
namespace bp  = boost::python;

//! Class creation
StreamSinkPtr StreamSink::create () {
   StreamSinkPtr p = boost::make_shared<StreamSink>();
   return(p);
}

//! Creator
StreamSink::StreamSink() {
   rxCount_ = 0;
   rxBytes_ = 0;
}

//! Deconstructor
StreamSink::~StreamSink() { }

//! Get rx count
uint32_t StreamSink::getRxCount() {
   return(rxCount_);
}

//! Get rx bytes
uint32_t StreamSink::getRxBytes() {
   return(rxBytes_);
}

//! Reset counters
// Counters should really be locked!
void StreamSink::resetCount() {
   rxCount_    = 0;
   rxBytes_    = 0;
}

//! Accept a frame from master
void StreamSink::acceptFrame ( ris::FramePtr frame ) {
   rxBytes_ += frame->getPayload();
   rxCount_++;
}

void StreamSink::setup_python() {

   bp::class_<StreamSink, StreamSinkPtr, bp::bases<ris::Slave>, boost::noncopyable >("StreamSink",bp::init<>())
      .def("create",         &StreamSink::create)
      .staticmethod("create")
      .def("getRxCount",     &StreamSink::getRxCount)
      .def("getRxBytes",     &StreamSink::getRxBytes)
      .def("resetCount",     &StreamSink::resetCount)
   ;

   bp::implicitly_convertible<StreamSinkPtr, ris::SlavePtr>();

}

