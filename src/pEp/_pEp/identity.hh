// This file is under GNU Affero General Public License 3.0
// see LICENSE.txt

#ifndef IDENTITY_HH
#define IDENTITY_HH

// System
#include "adapter_main.hh"
#include "str_attr.hh"

namespace pEp {
namespace PythonAdapter {

// Identity is owning a pEp_identity
class Identity {
  protected:
    shared_ptr<::pEp_identity> _ident;

  public:
    Identity(string address = "", string username = "", string user_id = "", string fpr = "", int comm_type = 0, string lang = "", ::identity_flags_t flags = 0);

    Identity(const Identity &second);

    Identity(::pEp_identity *ident);

    virtual ~Identity();

    operator ::pEp_identity *();

    operator const ::pEp_identity *() const;

    string _repr();

    string _str();

    string address() { return str_attr(_ident->address); }

    void address(string value) { str_attr(_ident->address, value); }

    string fpr() { return str_attr(_ident->fpr); }

    void fpr(string value) { str_attr(_ident->fpr, value); }

    string user_id() { return str_attr(_ident->user_id); }

    void user_id(string value) { str_attr(_ident->user_id, value); }

    string username() { return str_attr(_ident->username); }

    void username(string value);

    ::PEP_comm_type comm_type() { return _ident->comm_type; }

    void comm_type(::PEP_comm_type value) { _ident->comm_type = value; };

    std::string lang();

    void lang(std::string value);

    ::identity_flags_t flags() { return _ident->flags; }

    void flags(::identity_flags_t flags) { _ident->flags = flags; }

    int rating();

    ::PEP_color color();

    Identity copy();

    Identity deepcopy(bp::dict &memo);

    virtual void update();

    void key_reset(const string &fpr = "");

    void key_mistrusted();

    bool is_pEp_user();

    void enable_for_sync();

    void disable_for_sync();
};

//        class Myself : public Identity {
//        public:
//            Myself(string address, string username, string user_id = "", string lang = "");
//
//            virtual void update();
//        };

Identity identity_attr(::pEp_identity *&ident);

void identity_attr(::pEp_identity *&ident, bp::object value);

bp::list identitylist_attr(::identity_list *&il);

void identitylist_attr(::identity_list *&il, bp::list value);

} // namespace PythonAdapter
} // namespace pEp

#endif /* IDENTITY_HH */
