// This file is under GNU Affero General Public License 3.0
// see LICENSE.txt

#include "basic_api.hh"
#include <sstream>
#include <pEp/keymanagement.h>
#include <pEp/message_api.h>

namespace pEp {
    namespace PythonAdapter {
        void update_identity(Identity& ident)
        {
            if (ident.address() == "")
                throw invalid_argument("address needed");
            if (ident.user_id() == PEP_OWN_USERID)
                throw runtime_error("update_identity: '" PEP_OWN_USERID
                        "' may only be used for own identities");

            PEP_STATUS status = update_identity(adapter.session(), ident);
            _throw_status(status);
        }

        void myself(Identity& ident)
        {
            if (ident.address() == "")
                throw invalid_argument("address needed");
            if (ident.username() == "")
                throw invalid_argument("username needed");

            if (ident.user_id() == "")
                ident.user_id(ident.address());

            PEP_STATUS status = myself(adapter.session(), ident);
            _throw_status(status);
        }

        string _trustwords(Identity me, Identity partner, string lang, bool full)
        {
            if (me.fpr() == "" || partner.fpr() == "")
                throw invalid_argument("fingerprint needed in Identities");

            if (lang == "" && me.lang() == partner.lang())
                lang = me.lang();

            char *words = NULL;
            size_t size = 0;
            PEP_STATUS status =  get_trustwords(adapter.session(), me, partner,
                                        lang.c_str(),&words, &size, full);
            _throw_status(status);
            return words;
        }

        void trust_personal_key(Identity ident)
        {
            if (ident.fpr() == "")
                throw invalid_argument("fingerprint needed in Identities");
            if (ident.user_id() == "")
                throw invalid_argument("user_id must be provided");

            PEP_STATUS status = trust_personal_key(adapter.session(), ident);
            _throw_status(status);
        }

        void set_identity_flags(Identity ident, identity_flags_t flags)
        {
            if (ident.address() == "")
                throw invalid_argument("address needed");
            if (ident.user_id() == "")
                throw invalid_argument("user_id needed");

            PEP_STATUS status = set_identity_flags(adapter.session(), ident, flags);
            _throw_status(status);
        }

        void unset_identity_flags(Identity ident, identity_flags_t flags)
        {
            if (ident.address() == "")
                throw invalid_argument("address needed");
            if (ident.user_id() == "")
                throw invalid_argument("user_id needed");

            PEP_STATUS status = unset_identity_flags(adapter.session(), ident, flags);
            _throw_status(status);
        }

        void key_reset_trust(Identity ident)
        {
            if (ident.fpr() == "")
                throw invalid_argument("fpr needed");
            if (ident.address() == "")
                throw invalid_argument("address needed");
            if (ident.user_id() == "")
                throw invalid_argument("user_id needed");

            PEP_STATUS status = key_reset_trust(adapter.session(), ident);
            _throw_status(status);
        }



        boost::python::list import_key(string key_data)
        {
            ::identity_list *private_keys = NULL;
            PEP_STATUS status = ::import_key(adapter.session(), key_data.c_str(), key_data.size(), &private_keys);
            if (status && status != PEP_KEY_IMPORTED)
                _throw_status(status);

            auto result = boost::python::list();
            for (::identity_list *il = private_keys; il && il->ident; il=il->next) {
                ::pEp_identity *ident = ::identity_dup(il->ident);
                if (!ident) {
                    free_identity_list(private_keys);
                    throw bad_alloc();
                }
                result.append(Identity(ident));
            }

            free_identity_list(private_keys);
            return result;
        }

        string export_key(Identity ident)
        {
            PEP_STATUS status = PEP_STATUS_OK;
            char* key_data = NULL;
            size_t size;
            status = ::export_key(adapter.session(), ident.fpr().c_str(), &key_data, &size);

            _throw_status(status);
            return key_data;
        }

        string export_secret_key(Identity ident)
        {
            PEP_STATUS status = PEP_STATUS_OK;
            char* key_data = NULL;
            size_t size;
            status = ::export_secret_key(adapter.session(), ident.fpr().c_str(), &key_data, &size);

            _throw_status(status);
            return key_data;
        }

        void set_own_key(Identity& ident, string fpr)
        {
            if (ident.address() == "")
                throw invalid_argument("address needed");
            if (ident.username() == "")
                throw invalid_argument("username needed");
            if (ident.user_id() == "")
                throw invalid_argument("user_id needed");
            if (fpr == "")
                throw invalid_argument("fpr needed");


            const char* fpr_c = fpr.c_str();
            PEP_STATUS status = set_own_key(adapter.session(), ident, fpr_c);
            _throw_status(status);
        }
    }
}
