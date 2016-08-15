#include "Identity.hh"
#include "pEpmodule.hh"
#include "message_api.hh"
#include <typeinfo>
#include <sstream>
#include <pEp/identity_list.h>
#include <pEp/keymanagement.h>
#include <pEp/message_api.h>

namespace pEp {
    namespace PythonAdapter {
        using namespace std;

        Identity::Identity(string address, string username, string user_id,
                string fpr, int comm_type, string lang)
            : _ident(new_identity(address.c_str(), fpr.c_str(),
                        user_id.c_str(), username.c_str()), &::free_identity)
        {
            if (!_ident)
                throw bad_alloc();
            _ident->comm_type = (PEP_comm_type) comm_type;
            this->lang(lang);
        }

        Identity::Identity(const Identity& second)
            : _ident(second._ident)
        {

        }

        Identity::Identity(pEp_identity *ident)
            : _ident(ident, &::free_identity)
        {

        }

        Identity::~Identity()
        {

        }

        Identity::operator pEp_identity *()
        {
            return _ident.get();
        }

        Identity::operator const pEp_identity *() const
        {
            return _ident.get();
        }

        string Identity::_repr()
        {
            stringstream build;
            build << "Identity(";
            string address;
            if (_ident->address)
                address = string(_ident->address);
            build << repr(address) << ", ";
            string username;
            if (_ident->username)
                username = string(_ident->username);
            build << repr(username) << ", ";
            string user_id;
            if (_ident->user_id)
                user_id = string(_ident->user_id);
            build << repr(user_id) << ", ";
            string fpr;
            if (_ident->fpr)
                fpr = string(_ident->fpr);
            build << repr(fpr) << ", ";
            build << (int) _ident->comm_type << ", ";
            string lang = _ident->lang;
            build << repr(lang) << ")";
            return build.str();
        }

        string Identity::_str()
        {
            if (!(_ident->address && _ident->address[0]))
                return "";
            if (!(_ident->username && _ident->username[0]))
                return _ident->address;
            return string(_ident->username) + " <" + _ident->address + ">";
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

        int Identity::rating()
        {
            if (!(_ident->address))
                throw invalid_argument("address must be given");

            PEP_rating rating = PEP_rating_undefined;
            PEP_STATUS status = ::identity_rating(session, _ident.get(), &rating);
            _throw_status(status);

            return (int) rating;
        }

        int Identity::color()
        {
            return _color(rating());
        }

        Identity identity_attr(pEp_identity *&ident)
        {
            if (!ident)
                throw out_of_range("no identity assigned");

            pEp_identity *_dup = identity_dup(ident);
            if (!_dup)
                throw bad_alloc();

            Identity _ident(_dup);
            return _ident;
        }

        void identity_attr(pEp_identity *&ident, object value)
        {
            Identity& _ident = extract< Identity& >(value);
            pEp_identity *_dup = ::identity_dup(_ident);
            if (!_dup)
                throw bad_alloc();
            PEP_STATUS status = update_identity(session, _dup);
            _throw_status(status);
            free_identity(ident);
            ident = _dup;
        }

        list identitylist_attr(identity_list *&il)
        {
            list result;

            for (identity_list *_il = il; _il && _il->ident; _il = _il->next) {
                pEp_identity *ident = ::identity_dup(_il->ident);
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
                pEp_identity *_ident = extract_identity();
                pEp_identity *_dup = ::identity_dup(_ident);
                if (!_dup) {
                    free_identity_list(_il);
                    throw bad_alloc();
                }
                PEP_STATUS status = update_identity(session, _dup);
                if (status != PEP_STATUS_OK) {
                    free_identity_list(_il);
                    _throw_status(status);
                }
                _i = identity_list_add(_i, _dup);
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

