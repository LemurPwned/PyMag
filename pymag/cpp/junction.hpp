#ifndef JUNCTION_H
#define JUNCTION_H

#include <algorithm>
#include <chrono>
#include <cmath>
#include <complex>
#include <cstring>
#include <fstream>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <stdio.h>
#include <string>
#include <tuple>
#include <vector>

#include "cvector.hpp"

#define MAGNETIC_PERMEABILITY 12.57e-7
#define GYRO 221000.0
#define TtoAm 795774.715459
#define HBAR 6.62607015e-34 / (2. * M_PI)
#define ELECTRON_CHARGE 1.60217662e-19
#define BOLTZMANN_CONST 1.380649e-23
#define PERGYR 220880.0

CVector calculate_tensor_interaction(CVector m,
                                     std::vector<CVector> tensor,
                                     double Ms)
{
    CVector res(
        -Ms * tensor[0][0] * m[0] - Ms * tensor[0][1] * m[1] - Ms * tensor[0][2] * m[2],
        -Ms * tensor[1][0] * m[0] - Ms * tensor[1][1] * m[1] - Ms * tensor[1][2] * m[2],
        -Ms * tensor[2][0] * m[0] - Ms * tensor[2][1] * m[1] - Ms * tensor[2][2] * m[2]);
    return res;
}

CVector c_cross(CVector a, CVector b)
{
    CVector res(
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0]);

    return res;
}

double c_dot(CVector a, CVector b)
{
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
}

double cos_between_arrays(CVector a, CVector b)
{
    double res = c_dot(a, b) / (a.length() * b.length());

    return res * res;
}

double SpinDiode2Layers(CVector I, CVector m1, CVector m2, double Rlow, double deltaR)
{
    double SD = Rlow + deltaR * cos_between_arrays(I, m1) + Rlow + deltaR * cos_between_arrays(I, m2);

    return SD;
}

class Junction
{
    std::vector<std::string> vectorNames = {"x", "y", "z"};

public:
    static CVector RK45(CVector mag, CVector mTop, CVector mBottom, CVector Hext, int layer, double dt, CVector HOe,
                        std::vector<double> Ms,
                        std::vector<double> Ku,
                        std::vector<double> Ju,
                        std::vector<CVector> Kdir,
                        std::vector<double> th,
                        std::vector<double> alpha,
                        std::vector<CVector> demag)
    {

        CVector k1, k2, k3, k4, dm;

        k1 = Junction::LLG(mag, mTop, mBottom, Hext, HOe, layer, Ms,
                           Ku,
                           Ju,
                           Kdir,
                           th,
                           alpha,
                           demag) *
             dt;
        k2 = Junction::LLG(mag + k1 * 0.5, mTop, mBottom, Hext, HOe, layer, Ms,
                           Ku,
                           Ju,
                           Kdir,
                           th,
                           alpha,
                           demag) *
             dt;
        k3 = Junction::LLG(mag + k2 * 0.5, mTop, mBottom, Hext, HOe, layer, Ms,
                           Ku,
                           Ju,
                           Kdir,
                           th,
                           alpha,
                           demag) *
             dt;
        k4 = Junction::LLG(mag + k3, mTop, mBottom, Hext, HOe, layer, Ms,
                           Ku,
                           Ju,
                           Kdir,
                           th,
                           alpha,
                           demag) *
             dt;

        dm = (k1 + (k2 * 2.0) + (k3 * 2.0) + k4) / 6.0;
        mag = mag + dm;
        mag.normalize();
        return mag;
    }

    static CVector LLG(CVector mag, CVector mTop, CVector mBottom, CVector Hext, CVector HOe, int layer,
                       std::vector<double> Ms,
                       std::vector<double> Ku,
                       std::vector<double> Ju,
                       std::vector<CVector> Kdir,
                       std::vector<double> th,
                       std::vector<double> alpha,
                       std::vector<CVector> demag)
    {

        CVector Heff, noise, dm, Pprod, Hprod;

        Heff = Hext + HOe + Kdir[layer] * ((2 * Ku[layer] / Ms[layer]) * c_dot(mag, Kdir[layer])) - calculate_tensor_interaction(mag, demag, -1) * (Ms[layer] / MAGNETIC_PERMEABILITY);
        
        if (layer == 0)
        {
             Heff = Heff + (mBottom - mag) * (Ju[0] / (Ms[layer] * th[layer]));
        }
        else if (layer == 1)
        {
             Heff = Heff + (mTop - mag) * (Ju[0] / (Ms[layer] * th[layer]));
        }

        Hprod = c_cross(mag, Heff);
        dm = Hprod * -PERGYR + c_cross(mag, Hprod) * alpha[layer] * -PERGYR;

        return dm;
    }
};

#endif
