#include "Identity.hh"
#include <typeinfo>
#include <sstream>
#include <pEp/identity_list.h>

namespace pEp {
    namespace PythonAdapter {
        using namespace std;

        Identity::Identity(string address, string fpr, string user_id, string
                username, int comm_type, string lang)
            : _ident(new_identity(address.c_str(), fpr.c_str(),
                        user_id.c_str(), username.c_str()))
        {
            if (!_ident)
                throw bad_alloc();
            _ident->comm_type = (PEP_comm_type) comm_type;
            this->lang(lang);
        }

        Identity::Identity(const Identity& second)
            : _ident(identity_dup(second._ident))
        {
            if (!_ident)
                throw bad_alloc();
        }

        Identity::Identity(pEp_identity *ident)
            : _ident(ident)
        {

        }

        Identity::~Identity()
        {
            free_identity(_ident);
        }

        Identity::operator pEp_identity *()
        {
            if (!_ident)
                throw bad_cast();
            return _ident;
        }

        void Identity::attach(pEp_identity *ident)
        {
            free_identity(_ident);
            _ident = ident;
        }

        pEp_identity *Identity::detach()
        {
            pEp_identity *new_one = new_identity(NULL, NULL, NULL, NULL);
            if (!new_one)
                throw bad_alloc();

            pEp_identity *ident = _ident;
            _ident = new_one;

            return ident;
        }

        string Identity::_repr()
        {
            stringstream build;
            build << "Identity(";
            string address;
            if (_ident->address)
                address = string(_ident->address);
            build << repr(address) << ", ";
            string fpr;
            if (_ident->fpr)
                fpr = string(_ident->fpr);
            build << repr(fpr) << ", ";
            string user_id;
            if (_ident->user_id)
                user_id = string(_ident->user_id);
            build << repr(user_id) << ", ";
            string username;
            if (_ident->username)
                username = string(_ident->username);
            build << repr(username) << ", ";
            build << (int) _ident->comm_type << ", ";
            string lang = _ident->lang;
            build << repr(lang) << ")";
            return build.str();
        }

        void Identity::lang(string value)
        {
            if (value == "")
                memset(_ident->lang, 0, 3);
            else if (value.length() != 2)
                throw length_error("length of lang must be 2");
            else
                memcpy(_ident->lang, value.data(), 2);
        }

        string Identity::lang()
        {
            return _ident->lang;
        }

        Identity identity_attr(pEp_identity *&ident)
        {
            pEp_identity *_dup;

            if (!ident)
                _dup = new_identity(NULL, NULL, NULL, NULL);
            else
                _dup = identity_dup(ident);
            if (!_dup)
                throw bad_alloc();

            Identity _ident(_dup);
            return _ident;
        }

        void identity_attr(pEp_identity *&ident, object value)
        {
            extract< string > extract_string(value);
            if (extract_string.check()) {
                string str = extract_string();
                pEp_identity *_ident = new_identity(str.c_str(), NULL, NULL, NULL);
                if (!_ident)
                    throw bad_alloc();
                free_identity(ident);
                ident = _ident;
                return;
            }

            Identity& _ident = extract< Identity& >(value);
            free_identity(ident);
            ident = _ident.detach();
        }

        list identitylist_attr(identity_list *&il)
        {
            list result;

            for (identity_list *_il = il; _il && _il->ident; _il = _il->next) {
                pEp_identity *ident = identity_dup(_il->ident);
                if (!ident)
                    throw bad_alloc();
                result.append(object(Identity(ident)));
            }

            return result;
        }

        void identitylist_attr(identity_list *&il, list value)
        {
            identity_list *_il = new_identity_list(NULL);
            if (!_il)
                throw bad_alloc();

            identity_list *_i = _il;
            for (int i=0; i<len(value); i++) {
                extract< Identity& > extract_identity(value[i]);
                if (!extract_identity.check()) {
                    free_identity_list(_il);
                }
                pEp_identity *_ident = extract_identity().detach();
                _i = identity_list_add(_i, _ident);
                if (!_i) {
                    free_identity_list(_il);
                    throw bad_alloc();
                }
            }

            free_identity_list(il);
            il = _il;
        }
    }
}

