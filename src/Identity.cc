#include "Identity.hh"
#include <typeinfo>

namespace pEp {
    namespace PythonAdapter {
        using namespace std;

        Identity::Identity()
            : _ident(new_identity(NULL, NULL, NULL, NULL))
        {
            if (!_ident)
                throw bad_alloc();
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

        Identity::operator pEp_identity *()
        {
            if (!_ident)
                throw bad_cast();
            return _ident;
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
    }
}

