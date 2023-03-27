// This file is under GNU Affero General Public License 3.0
// see LICENSE.txt

#ifndef BASIC_API_HH
#define BASIC_API_HH

#include "pEpmodule.hh"

namespace pEp {
    namespace PythonAdapter {

        void update_identity(Identity &ident);

        void myself(Identity &ident);

        string _trustwords(Identity me, Identity partner, string lang, bool full);

        void trust_personal_key(Identity ident);

        void set_identity_flags(Identity ident, identity_flags_t flags);

        void unset_identity_flags(Identity ident, identity_flags_t flags);

        void key_reset_trust(Identity ident);

        boost::python::tuple import_key(string key_data);

        string export_key(Identity ident);

        string export_secret_key(Identity ident);

        void set_own_key(Identity &ident, string fpr);

        void set_comm_partner_key(Identity &ident, string fpr);
    } /* namespace PythonAdapter */
} /* namespace pEp */

#endif /* BASIC_API_HH */
