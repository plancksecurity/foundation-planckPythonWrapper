#include <string>
#include <pybind11/pybind11.h>

using namespace std;

string testfunc() {
    return "fsdfg";
}

PYBIND11_MODULE(_gen, m) {
    m.doc() = "pybind11 example plugin"; // optional module docstring
    m.def("add", &testfunc, "A function which adds two numbers");
}

