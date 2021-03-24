from pymag.engine.data_holders import Layer
from typing import List
import cmtj
import numpy as np
from pymag.engine.utils import butter_lowpass_filter, cos_between_arrays, normalize
import multiprocessing


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
        PIMM_ = []
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

                DynamicR[i] = cmtj.SpinDiode2Layers(CIdir, Cm_all[0],
                                                    Cm_all[1], 100, 0.1)
            PIMM_.append(np.sum([m.z for m in Cm_all]))

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
    def calculate_resistance(Rx0, Ry0, AMR, AHE, SMR, m, number_of_layers, l,
                             w):
        R_P = Rx0[0]
        R_AP = Ry0[0]

        SxAll = []
        SyAll = []
        w_l = w[0] / l[0]
        for i in range(0, number_of_layers):
            SxAll.append(1 / (Rx0[i] + Rx0[i] * AMR[i] * m[i, 0]**2 +
                              Rx0[i] * SMR[i] * m[i, 1]**2))
            SyAll.append(1 / (Ry0[i] + AHE[i] * m[i, 2] + Rx0[i] * (w_l) *
                              (AMR[i] + SMR[i]) * m[i, 0] * m[i, 1]))

        Rx = 1 / sum(SxAll)
        Ry = 1 / sum(SyAll)

        if number_of_layers > 1:
            Rz = R_P + (R_AP -
                        R_P) / 2 * (1 - cos_between_arrays(m[0, :], m[1, :]))
        else:
            Rz = 0

        return Rx, Ry, Rz

    @staticmethod
    def init_vector_gen(number_of_layers, H_sweep):
        m_init = []
        for _ in range(0, number_of_layers):
            m_init.append(normalize(H_sweep[0, :]))
        return m_init

    def run_H_step(m, Hval, freqs, layers: List[Layer], LLG_time, LLG_steps):
        pool = multiprocessing.Pool(8)
        results = []
        mag_stat = (pool.apply_async(Solver.calc_trajectoryRK45,
                                     args=(layers, m, Hval, 0, 0, LLG_time,
                                           LLG_steps)))
        for f in freqs:
            results.append(
                pool.apply_async(Solver.calc_trajectoryRK45,
                                 args=(layers, m, Hval, f, 20000, LLG_time,
                                       LLG_steps)))

        SD = list(zip(*[r.get() for r in results]))[4]
        pool.close()
        pool.join()
        m = mag_stat.get()[0]
        m_avg = mag_stat.get()[1]
        dynamic_r = mag_stat.get()[2]
        m_traj = mag_stat.get()[5]

        Rx0 = [l.Rx0 for l in layers]
        Ry0 = [l.Ry0 for l in layers]
        SMR = [l.SMR for l in layers]
        AMR = [l.AMR for l in layers]
        AHE = [l.AHE for l in layers]
        w = [l.w for l in layers]
        l = [l.l for l in layers]
        no_layers = len(layers)

        Rx, Ry, Rz = Solver.calculate_resistance(Rx0, Ry0, AMR, AHE, SMR, m,
                                                 no_layers, l, w)

        return {
            "SD": SD,
            "m": m,
            "m_avg": m_avg,
            "m_traj": m_traj,
            "dynamic_r": dynamic_r,
            # "PIMM": PIMM_,
            # "yf": yf,
            "Rx": Rx,
            "Ry": Ry,
            "Rz": Rz
        }
