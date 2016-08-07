#pragma once

#include "pEpmodule.hh"

namespace pEp {
    namespace PythonAdapter {
        void _throw_status(PEP_STATUS status);

        void update_identity(Identity& ident);
        void myself(Identity& ident);
    }
}

