#include "pEpmodule.hh"
#include <string>
#include <pEp/pEpEngine.h>
#include "Identity.hh"

namespace pEp {
    namespace PythonAdapter {
        using namespace std;

        string about()
        {
            string version = string(version_string) + "\np≡p version "
                + PEP_VERSION + "\n";
            return version;
        }
    }
}

BOOST_PYTHON_MODULE(pEp)
{
    using namespace boost::python;
    using namespace pEp::PythonAdapter;

    docstring_options doc_options(true, true, false);

    def("about", about, "delivers the p≡p about string");

    class_<Identity>("Identity", "p≡p identity")
        .add_property("address", (string(Identity::*)()) &Identity::address,
                (void(Identity::*)(string)) &Identity::address,
                "email address or URI")
        .add_property("fpr", (string(Identity::*)()) &Identity::fpr,
                (void(Identity::*)(string)) &Identity::fpr,
                "key ID (fingerprint)")
        .add_property("user_id", (string(Identity::*)()) &Identity::user_id,
                (void(Identity::*)(string)) &Identity::user_id,
                "ID of person associated")
        .add_property("username", (string(Identity::*)()) &Identity::username,
                (void(Identity::*)(string)) &Identity::username,
                "name of person associated")
        .add_property("comm_type", (int(Identity::*)())
                (PEP_comm_type(Identity::*)()) &Identity::comm_type,
                (void(Identity::*)(int))
                (void(Identity::*)(PEP_comm_type)) &Identity::comm_type,
                 "communication type (p≡p internal)")
        .add_property("lang", (string(Identity::*)()) &Identity::lang,
                (void(Identity::*)(string)) &Identity::lang,
                "ISO 639-1 language code")
        .add_property("me", (bool(Identity::*)()) &Identity::me,
                (void(Identity::*)(bool)) &Identity::me,
                 "true if own identity, false otherwise")
        .add_property("flags", (identity_flags_t(Identity::*)()) &Identity::flags,
                (void(Identity::*)(identity_flags_t)) &Identity::flags);
}

