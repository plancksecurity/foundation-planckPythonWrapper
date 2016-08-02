#include <Python.h>
#include <pEp/pEpEngine.h>

namespace pEp {
    namespace PythonAdapter {
        const char *version_string = "p≡p Python adapter version 0.1";

        PyObject *about(PyObject *self, PyObject *args);
    }

    void module_free(void *);

    struct PyMethodDef pEpMethods[] = {
        {"about", pEp::PythonAdapter::about, METH_VARARGS, "about p≡p"},
        {NULL, NULL, 0, NULL}
    };

    struct PyModuleDef pEpmodule = {
        PyModuleDef_HEAD_INIT,
        "pEp",
        "p≡p Python adapter",
        -1,
        pEpMethods,
        NULL,
        NULL,
        NULL,
        pEp::module_free
    };

    extern PEP_SESSION session;
}

PyMODINIT_FUNC PyInit_pEp(void);

