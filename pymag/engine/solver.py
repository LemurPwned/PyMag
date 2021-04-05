import multiprocessing
from os import cpu_count
from sys import platform
from typing import List

import cmtj
import numba
import numpy as np
from pymag.engine.data_holders import Layer
from pymag.engine.utils import butter_lowpass_filter, normalize
from scipy.fft import fft

cpu_count = multiprocessing.cpu_count()


class Solver:
    @staticmethod
    def calc_trajectoryRK45(layers: List[Layer],
                            m_init,
                            Hext,
                            f=6.5e9,
                            I_amp=0,
                            LLG_time=4e-9,
                            LLG_steps=2000):

        n_layers = len(layers)
        m_traj = np.empty((0, 3), float)
        M_full = np.empty((0, n_layers, 3), float)

        t = np.linspace(0, LLG_time, LLG_steps)
        I = I_amp / 8 * np.sin(
            2 * np.pi * f *
            t)  #+ 2*np.pi*self.plotter.IACphi/360  +   2*np.pi*Ry0[0]/360)
        Isdd = I_amp / 8 * np.sin(2 * np.pi * f * t)
        m = np.array(m_init)

        CKdir = [cmtj.CVector(*l.Kdir) for l in layers]

        Cdt = LLG_time / LLG_steps
        CHext = cmtj.CVector(*Hext)
        CNdemag = [
            cmtj.CVector(layers[0].N[0], 0., 0.),
            cmtj.CVector(0., layers[0].N[1], 0.),
            cmtj.CVector(0., 0., layers[0].N[2])
        ]
        Cm_all = [cmtj.CVector(*m[i, :]) for i in range(n_layers)]
        CMs = [l.Ms for l in layers]
        CKu = [l.Ku for l in layers]
        CJu = [l.J for l in layers]
        Cth = [l.th for l in layers]
        Calpha = [l.alpha for l in layers]

        CIdir = cmtj.CVector(1, 0, 0)
        m_null = cmtj.CVector(1, 0, 0)
        CHOe_pulse = cmtj.CVector(0, 0, 10000)
        CHOe_null = cmtj.CVector(0, 0, 0)

        DynamicR = np.zeros(len(t))
        PIMM_ = np.zeros(len(t))
        # for i in range(len(t)):
        #     CHOe = CHOe_null
        #     if I_amp == 0 and i == 0:
        #         CHOe = CHOe_pulse
        #     elif I_amp == 0 and i != 0:
        #         CHOe = CHOe_null
        #     else:
        #         CHOe = cmtj.CVector(0, 5 * I[i], 0)

        #     if n_layers == 1:
        #         Cm_all[0] = cmtj.RK45(Cm_all[0], m_null, CHext, 0, Cdt, CHOe,
        #                               CMs, CKu, CJu, CKdir, Cth, Calpha,
        #                               CNdemag)
        #         DynamicR[i] = 1
        #     else:
        #         for layer in range(n_layers):
        #             Cm_all[layer] = cmtj.RK45(Cm_all[layer],
        #                                       Cm_all[(layer + 1) % n_layers],
        #                                       CHext, layer, Cdt, CHOe, CMs,
        #                                       CKu, CJu, CKdir, Cth, Calpha,
        #                                       CNdemag)

        for i in range(0, len(t)):
            CHOe = CHOe_null
            if I_amp == 0 and i == 0:
                CHOe = CHOe_pulse
            elif I_amp == 0 and i != 0:
                CHOe = CHOe_null
            else:
                CHOe = cmtj.CVector(0, 5 * I[i], 0)

            for layer in range(0, n_layers):
                if layer == 0:
                    if n_layers == 1:
                        Cm_bottom = m_null  # m_bottom = np.array([0, 0, 0])
                    else:
                        Cm_bottom = Cm_all[layer + 1]  #m_bottom = m[layer + 1]
                    Cm_top = m_null  #m_top = np.array([0, 0, 0])
                else:
                    if layer == n_layers - 1:
                        if n_layers == 1:
                            Cm_top = m_null  #m_top = np.array([0, 0, 0]) poprawiłem z Cm_bottom
                        else:
                            Cm_top = Cm_all[layer - 1]  #m_top = m[layer - 1]
                        Cm_bottom = m_null  #m_bottom = np.array([0, 0, 0])
                    else:
                        Cm_bottom = Cm_all[layer + 1]  #m_bottom = m[layer + 1]
                        Cm_top = Cm_all[layer - 1]  #m_top = m[layer - 1]

                Cm = Cm_all[layer]
                Cm_all[layer] = cmtj.RK45(Cm, Cm_top, Cm_bottom, CHext, layer,
                                          Cdt, CHOe, CMs, CKu, CJu, CKdir, Cth,
                                          Calpha, CNdemag)
                if n_layers == 1:
                    DynamicR[i] = 1.
                else:
                    DynamicR[i] = cmtj.SpinDiode2Layers(
                        CIdir, Cm_all[0], Cm_all[1], 100, 0.1)
            PIMM_[i] = np.sum([m.z for m in Cm_all])

        if I_amp == 0:
            SD_voltage_after_bias = 0
        else:
            SD_voltage = -Isdd * DynamicR
            SD_voltage = butter_lowpass_filter(SD_voltage,
                                               cutoff=10e6,
                                               fs=1 / Cdt,
                                               order=3)
            SD_voltage_after_bias = np.mean(
                SD_voltage
            )  # butter_bandpass_filter(SD_voltage, 0.001, 1e3, 1/dt, order=4)
        m = np.asarray([[cm.x, cm.y, cm.z] for cm in Cm_all])

        m_avg = (np.matmul(m.T, (np.array(Cth) * np.array(CMs)))) / sum(
            np.array(Cth) * np.array(CMs))
        return np.array(m), m_avg, np.asarray(
            DynamicR), Cdt, SD_voltage_after_bias, m_traj, M_full, PIMM_

    @staticmethod
    @numba.jit(nopython=True, parallel=False)
    def calculate_resistance(Rx0, Ry0, AMR, AHE, SMR, m, number_of_layers, l,
                             w):
        R_P = Rx0[0]
        R_AP = Ry0[0]

        SxAll = np.zeros((number_of_layers, ))
        SyAll = np.zeros((number_of_layers, ))
        w_l = w[0] / l[0]
        for i in range(0, number_of_layers):
            SxAll[i] = 1 / (Rx0[i] + Rx0[i] * AMR[i] * m[i, 0]**2 +
                            Rx0[i] * SMR[i] * m[i, 1]**2)
            SyAll[i] = 1 / (Ry0[i] + AHE[i] * m[i, 2] + Rx0[i] * (w_l) *
                            (AMR[i] + SMR[i]) * m[i, 0] * m[i, 1])

        Rx = 1 / np.sum(SxAll)
        Ry = 1 / np.sum(SyAll)

        if number_of_layers > 1:
            Rz = R_P + (R_AP - R_P) / 2 * (1 - np.sum(m[0, :] * m[1, :]))
        else:
            Rz = 0

        return Rx, Ry, Rz

    @staticmethod
    def init_vector_gen(number_of_layers, H_sweep):
        m_init = []
        for _ in range(0, number_of_layers):
            m_init.append(normalize(H_sweep[0, :]))
        return m_init

    def serial_run_H_step(m, Hval, freqs, layers: List[Layer], LLG_time,
                          LLG_steps):
        SD = []
        m, m_avg, dynamic_r, _, _, m_traj, _, PIMM = Solver.calc_trajectoryRK45(
            layers, m, Hval, 0, 0, LLG_time, LLG_steps)
        for f in freqs:
            _, _, _, _, SD_voltage_after_bias, _, _, _ = Solver.calc_trajectoryRK45(
                layers, m, Hval, f, 20000, LLG_time, LLG_steps)
            SD.append(SD_voltage_after_bias)

        return m, m_avg, dynamic_r, m_traj, SD, PIMM

    def parallel_run_H_step(m, Hval, freqs, layers: List[Layer], LLG_time,
                            LLG_steps):
        pool = multiprocessing.Pool(cpu_count - 1)
        results = []
        m, m_avg, dynamic_r, _, _, m_traj, _, PIMM = Solver.calc_trajectoryRK45(
            layers, m, Hval, 0, 0, LLG_time, LLG_steps)
        results = pool.starmap(Solver.calc_trajectoryRK45,
                               iterable=((layers, m, Hval, f, 20000, LLG_time,
                                          LLG_steps) for f in freqs))
        SD = list(zip(*results))[4]
        pool.close()
        pool.join()

        return m, m_avg, dynamic_r, m_traj, SD, PIMM

    def run_H_step(m, Hval, freqs, layers: List[Layer], LLG_time, LLG_steps):
        # TODO change this to more viable speed on macs
        if platform == "linux" or platform == "linux2" or True:
            # linux
            m, m_avg, dynamic_r, m_traj, SD, PIMM = Solver.parallel_run_H_step(
                m, Hval, freqs, layers, LLG_time, LLG_steps)
        else:
            # OSX or Windows
            m, m_avg, dynamic_r, m_traj, SD, PIMM = Solver.serial_run_H_step(
                m, Hval, freqs, layers, LLG_time, LLG_steps)

        Rx0 = np.asarray([l.Rx0 for l in layers])
        Ry0 = np.asarray([l.Ry0 for l in layers])
        SMR = np.asarray([l.SMR for l in layers])
        AMR = np.asarray([l.AMR for l in layers])
        AHE = np.asarray([l.AHE for l in layers])
        w = np.asarray([l.w for l in layers])
        l = np.asarray([l.l for l in layers])
        no_layers = len(layers)

        Rx, Ry, Rz = Solver.calculate_resistance(Rx0, Ry0, AMR, AHE, SMR, m,
                                                 no_layers, l, w)

        yf = abs(fft(PIMM))
        return {
            "SD": SD,
            "m": m,
            "m_avg": m_avg,
            "m_traj": m_traj,
            "dynamic_r": dynamic_r,
            "PIMM": yf[0:(len(yf) // 2)],
            "Rx": Rx,
            "Ry": Ry,
            "Rz": Rz
        }
