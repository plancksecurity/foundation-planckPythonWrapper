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
        .add_property("address", &Identity::get_address,
                &Identity::set_address, "email address or URI")
        .add_property("fpr", &Identity::get_fpr,
                &Identity::set_fpr, "key ID (fingerprint)")
        .add_property("user_id", &Identity::get_user_id,
                &Identity::set_user_id, "ID of person associated")
        .add_property("username", &Identity::get_username,
                &Identity::set_username, "name of person associated")
        .add_property("comm_type", &Identity::get_comm_type,
                &Identity::set_comm_type, "communication type (p≡p internal)")
        .add_property("lang", &Identity::get_lang,
                &Identity::set_lang, "ISO 639-1 language code")
        .add_property("me", &Identity::get_me,
                &Identity::set_me, "true if own identity, false otherwise")
        .add_property("flags", &Identity::get_flags,
                &Identity::set_flags);
}

