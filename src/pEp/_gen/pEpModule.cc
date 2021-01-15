#include <string>
#include <iostream>
#include <pybind11/pybind11.h>
#include <pybind11/detail/common.h>
#include "adapter_main.hh"

using namespace std;
namespace alib = pEp::Adapter;

string testfunc() {
    return "fsdfg";
}

void *getSessionHandle() {
    void *handle = static_cast<void *>(alib::session());
    return handle;
}

PYBIND11_MODULE(_gen, m) {
    m.doc() = "pybind11 example plugin"; // optional module docstring
    m.def("add", &testfunc, "A function which adds two numbers");

    // PEP_SESSION
    m.def("get_handle", &getSessionHandle);

    #include "gen/py_module.pybind11"

}
