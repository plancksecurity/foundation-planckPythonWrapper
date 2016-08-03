#pragma once

#include <boost/python.hpp>
#include <pEp/pEpEngine.h>
#include <string>
#include "str_attr.hh"

namespace pEp {
    namespace PythonAdapter {
        using namespace utility;
        using namespace boost::python;

        class Identity {
            pEp_identity *_ident;

        public:
            Identity();
            Identity(const Identity& second);
            ~Identity();
            operator pEp_identity *();

            void set_address(string value) { str_attr(_ident->address, value); }
            string get_address() { return str_attr(_ident->address); }

            void set_fpr(string value) { str_attr(_ident->fpr, value); }
            string get_fpr() { return str_attr(_ident->fpr); }

            void set_user_id(string value) { str_attr(_ident->user_id, value); }
            string get_user_id() { return str_attr(_ident->user_id); }

            void set_username(string value) { str_attr(_ident->username, value); }
            string get_username() { return str_attr(_ident->username); }

            void set_comm_type(PEP_comm_type value) { _ident->comm_type = value; };
            PEP_comm_type get_comm_type() { return _ident->comm_type; }

            void set_lang(std::string value);
            std::string get_lang();

            void set_me(bool value) { _ident->me = value; }
            bool get_me() { return _ident->me; }

            void set_flags(identity_flags_t flags) { _ident->flags = flags; }
            identity_flags_t get_flags() { return _ident->flags; }
        };
    }
}

