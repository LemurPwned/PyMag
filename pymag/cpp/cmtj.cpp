#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>

#include "cvector.hpp"
// #include "parallel.hpp"
#include "junction.hpp"
#include <stdio.h>
#include <vector>

using namespace pybind11::literals;

namespace py = pybind11;

#define USING_PY true



PYBIND11_MODULE(cmtj, m)
{
    m.doc() = "Python binding for C++ CMTJ Library";

    m.def("RK45", &Junction::RK45);
    m.def("LLG", &Junction::LLG);

    m.def("c_dot", &c_dot);
    m.def("cos_between_arrays", &cos_between_arrays);
    m.def("SpinDiode2Layers", &SpinDiode2Layers);

    py::class_<CVector>(m, "CVector")
        .def(py::init<
             double, double, double>())
        .def_readwrite("x", &CVector::x)
        .def_readwrite("y", &CVector::y)
        .def_readwrite("z", &CVector::z)
        .def("length", &CVector::length);

    py::implicitly_convertible<std::list<float>, CVector>();
}
