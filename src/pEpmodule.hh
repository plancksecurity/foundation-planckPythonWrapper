#include <Python.h>

namespace pEp {
    namespace PythonAdapter {
        const char *version_string = "p≡p Python adapter version 0.1";

        PyObject *about(PyObject *self, PyObject *args);
    }
}

static PyMethodDef pEpMethods[] = {
    {"about", pEp::PythonAdapter::about, METH_VARARGS, "about p≡p"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef pEpmodule = {
   PyModuleDef_HEAD_INIT,
   "pEp",
   NULL,
   -1,
   pEpMethods
};

PyMODINIT_FUNC PyInit_pEp(void);

