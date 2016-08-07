#include "basic_api.hh"
#include <sstream>
#include <pEp/keymanagement.h>

namespace pEp {
    namespace PythonAdapter {
        void update_identity(Identity& ident)
        {
            if (ident.me())
                throw runtime_error("update_identity: not for own identities");
            if (ident.user_id() == PEP_OWN_USERID)
                throw runtime_error("update_identity: '" PEP_OWN_USERID
                        "' may only be used for own identities");

            PEP_STATUS status = update_identity(session, ident);
            _throw_status(status);
        }

        void myself(Identity& ident)
        {
            ident.me(true);
            ident.user_id(PEP_OWN_USERID);

            PEP_STATUS status = myself(session, ident);
            _throw_status(status);
        }
    }
}

