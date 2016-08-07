#pragma once

#include <boost/python.hpp>
#include <pEp/pEpEngine.h>
#include <string>
#include "str_attr.hh"

namespace pEp {
    namespace PythonAdapter {
        using namespace utility;

        // Identity is owning a pEp_identity

        class Identity {
            pEp_identity *_ident;

        public:
            Identity(string address = "", string fpr = "", string user_id = "",
                    string username = "", int comm_type = 0, string lang = "");

            Identity(const Identity& second);
            Identity(pEp_identity *ident);
            ~Identity();
            operator pEp_identity *();
            void attach(pEp_identity *ident);
            pEp_identity *detach();

            string _repr();

            string address() { return str_attr(_ident->address); }
            void address(string value) { str_attr(_ident->address, value); }

            string fpr() { return str_attr(_ident->fpr); }
            void fpr(string value) { str_attr(_ident->fpr, value); }

            string user_id() { return str_attr(_ident->user_id); }
            void user_id(string value) { str_attr(_ident->user_id, value); }

            string username() { return str_attr(_ident->username); }
            void username(string value) { str_attr(_ident->username, value); }

            PEP_comm_type comm_type() { return _ident->comm_type; }
            void comm_type(PEP_comm_type value) { _ident->comm_type = value; };

            std::string lang();
            void lang(std::string value);

            bool me() { return _ident->me; }
            void me(bool value) { _ident->me = value; }

            identity_flags_t flags() { return _ident->flags; }
            void flags(identity_flags_t flags) { _ident->flags = flags; }
        };

        Identity identity_attr(pEp_identity *&ident);
        void identity_attr(pEp_identity *&ident, object value);

        list identitylist_attr(identity_list *&il);
        void identitylist_attr(identity_list *&il, list value);
    }
}

