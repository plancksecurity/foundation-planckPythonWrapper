#include "basic_api.hh"
#include <sstream>
#include <pEp/keymanagement.h>

namespace pEp {
    namespace PythonAdapter {
        void update_identity(Identity& ident)
        {
            if (ident.address() == "")
                throw invalid_argument("address needed");
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
            if (ident.address() == "")
                throw invalid_argument("address needed");
            if (ident.username() == "")
                throw invalid_argument("username needed");
            if (!(ident.user_id() == "" || ident.user_id() == PEP_OWN_USERID))
                throw invalid_argument("user_id must be empty or '" PEP_OWN_USERID "'");

            ident.me(true);
            ident.user_id(PEP_OWN_USERID);

            PEP_STATUS status = myself(session, ident);
            _throw_status(status);
        }

        string _trustwords(Identity me, Identity partner, string lang)
        {
            if (me.fpr() == "" || partner.fpr() == "")
                throw invalid_argument("fingerprint needed in Identities");

            if (lang == "" && me.lang() == partner.lang())
                lang = me.lang();

            char *words = NULL;
            size_t size = 0;
            PEP_STATUS status = trustwords(session, me.fpr().c_str(),
                    lang.c_str(), &words, &size, 5);
            _throw_status(status);
            string my_words = words;

            free(words);
            words = NULL;
            size = 0;
            status = trustwords(session, partner.fpr().c_str(), lang.c_str(),
                    &words, &size, 5);
            _throw_status(status);
            string partner_words = words;
            free(words);

            if (me.fpr() > partner.fpr())
                return partner_words + my_words;
            else
                return my_words + partner_words;
        }
        
        void trust_personal_key(Identity ident)
        {
            if (ident.fpr() == "")
                throw invalid_argument("fingerprint needed in Identities");
            if (ident.user_id() == "")
                throw invalid_argument("user_id must be provided");

            PEP_STATUS status = trust_personal_key(session, ident);
            _throw_status(status);
        }
    }
}

