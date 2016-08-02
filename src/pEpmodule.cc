#include "pEpmodule.hh"
#include <pEp/pEpEngine.h>
#include <string>

namespace pEp {
    namespace PythonAdapter {
        using namespace std;

        PyObject *about(PyObject *self, PyObject *args)
        {
            string version = string(version_string) + "\np≡p version "
                + PEP_VERSION + "\n";
            return PyUnicode_FromString(version.c_str());
        }
    }
}

PyMODINIT_FUNC PyInit_pEp(void)
{
    PEP_SESSION session;
    PEP_STATUS status = init(&session);
    if (status != PEP_STATUS_OK)
        return NULL;

    return PyModule_Create(&pEpmodule);
}
