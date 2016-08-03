#include "pEpmodule.hh"
#include <string>
#include <pEp/pEpEngine.h>

namespace pEp {
    namespace PythonAdapter {
        using namespace std;

        string about(void)
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
    def("about", about);
}

