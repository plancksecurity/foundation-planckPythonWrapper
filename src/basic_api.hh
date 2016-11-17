#pragma once

#include "pEpmodule.hh"

namespace pEp {
    namespace PythonAdapter {
        void update_identity(Identity& ident);
        void myself(Identity& ident);
        string _trustwords(Identity me, Identity partner, string lang);
        void trust_personal_key(Identity ident);

        void set_identity_flags(Identity ident, identity_flags_t flags);
        void unset_identity_flags(Identity ident, identity_flags_t flags);
    }
}

