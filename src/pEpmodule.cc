#include "pEpmodule.hh"
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

    void module_free(void *)
    {
        release(session);
    }
}

using namespace pEp;

PyMODINIT_FUNC PyInit_pEp(void)
{
    PEP_STATUS status = init(&session);
    if (status != PEP_STATUS_OK)
        return NULL;

    return PyModule_Create(&pEpmodule);
}

