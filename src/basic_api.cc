#include "basic_api.hh"
#include <sstream>
#include <pEp/keymanagement.h>

namespace pEp {
    namespace PythonAdapter {
        void _throw_status(PEP_STATUS status)
        {
            if (status == PEP_STATUS_OK)
                return;
            if (status >= 0x400 && status <= 0x4ff)
                return;
 
            if (status == PEP_OUT_OF_MEMORY)
                throw bad_alloc();

            stringstream build;
            build << "p≡p error: " << status;
            throw runtime_error(build.str());
        }

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

