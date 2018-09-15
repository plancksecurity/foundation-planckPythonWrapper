#pragma once

#include <boost/python.hpp>
#include "identity.hh"
#include "message.hh"
#include "adapter.hh"
#include <pEp/pEpEngine.h>

namespace pEp {
    namespace PythonAdapter {
        void _throw_status(PEP_STATUS status);
        void messageToSend(Message msg);
        PEP_STATUS _messageToSend(::message *msg);
        extern Adapter adapter;
    }
}

