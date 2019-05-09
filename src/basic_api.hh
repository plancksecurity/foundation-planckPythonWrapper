// This file is under GNU Affero General Public License 3.0
// see LICENSE.txt

#pragma once

#include "pEpmodule.hh"

DYNAMIC_API PEP_STATUS key_reset_trust(
        PEP_SESSION session,
        pEp_identity *ident
    );
namespace pEp {
    namespace PythonAdapter {
        void update_identity(Identity& ident);
        void myself(Identity& ident);
        string _trustwords(Identity me, Identity partner, string lang, bool full);
        void trust_personal_key(Identity ident);

        void set_identity_flags(Identity ident, identity_flags_t flags);
        void unset_identity_flags(Identity ident, identity_flags_t flags);

        void key_reset_trust(Identity ident);

        boost::python::list import_key(string key_data);
    }
}

