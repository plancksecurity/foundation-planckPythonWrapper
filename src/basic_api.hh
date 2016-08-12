#pragma once

#include "pEpmodule.hh"

namespace pEp {
    namespace PythonAdapter {
        void update_identity(Identity& ident);
        void myself(Identity& ident);
        string _trustwords(Identity me, Identity partner, string lang);
    }
}

