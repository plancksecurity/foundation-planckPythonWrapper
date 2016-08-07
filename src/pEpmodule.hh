#pragma once

#include <boost/python.hpp>
#include "Identity.hh"
#include "Message.hh"
#include <pEp/pEpEngine.h>

namespace pEp {
    namespace PythonAdapter {
        extern PEP_SESSION session;
        void _throw_status(PEP_STATUS status);
    }
}

