#pragma once

#include <pEp/pEpEngine.h>
#include <string>
#include "str_attr.hh"

namespace pEp {
    namespace PythonAdapter {
        using namespace utility;

        class Identity {
            pEp_identity *_ident;

        public:
            Identity();
            Identity(const Identity& second);
            Identity(pEp_identity *ident);
            ~Identity();
            operator pEp_identity *();
            void attach(pEp_identity *ident);
            pEp_identity *detach();

            void address(string value) { str_attr(_ident->address, value); }
            string address() { return str_attr(_ident->address); }

            void fpr(string value) { str_attr(_ident->fpr, value); }
            string fpr() { return str_attr(_ident->fpr); }

            void user_id(string value) { str_attr(_ident->user_id, value); }
            string user_id() { return str_attr(_ident->user_id); }

            void username(string value) { str_attr(_ident->username, value); }
            string username() { return str_attr(_ident->username); }

            void comm_type(PEP_comm_type value) { _ident->comm_type = value; };
            PEP_comm_type comm_type() { return _ident->comm_type; }

            void lang(std::string value);
            std::string lang();

            void me(bool value) { _ident->me = value; }
            bool me() { return _ident->me; }

            void flags(identity_flags_t flags) { _ident->flags = flags; }
            identity_flags_t flags() { return _ident->flags; }
        };
    }
}

