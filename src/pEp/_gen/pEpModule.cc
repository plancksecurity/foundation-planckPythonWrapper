#include <string>
#include <iostream>
#include <pybind11/pybind11.h>
#include <pybind11/detail/common.h>
#include "adapter_main.hh"
#include <pEp/Adapter.hh>
#include <pEp/callback_dispatcher.hh>

using namespace std;
namespace alib = pEp::Adapter;

PEP_SESSION pep_session() {
    return alib::session();
}

PYBIND11_MODULE(_gen, m) {

    // PEP_SESSION
//    m.def("pep_session",(PEP_SESSION(*)()) &pep_session);

    #include "gen/py_module.pybind11"
}
