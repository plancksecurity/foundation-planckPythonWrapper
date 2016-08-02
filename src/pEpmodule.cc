#include "pEpmodule.hh"
#include <pEp/pEpEngine.h>

namespace pEp {
    namespace PythonAdapter {
        PyObject *about(PyObject *self, PyObject *args)
        {
            return PyUnicode_FromString(version_string);
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
