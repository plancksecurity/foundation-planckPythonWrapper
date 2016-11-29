#pragma once

#include <boost/python.hpp>
#include "identity.hh"
#include "message.hh"
#include <pEp/pEpEngine.h>

namespace pEp {
    namespace PythonAdapter {
        extern PEP_SESSION session;
        void _throw_status(PEP_STATUS status);
    }
}

