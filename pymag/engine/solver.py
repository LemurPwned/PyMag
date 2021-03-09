import cmtj
import numpy as np
from scipy import fft
from pymag.engine.utils import butter_lowpass_filter, cos_between_arrays, normalize
import multiprocessing
import time as tm


class Solver:
    @staticmethod
    def calc_trajectoryRK45(CKu,
                            CMs,
                            CJu,
                            Cth,
                            CKdir,
                            CNdemag,
                            Calpha,
                            n_layers,
                            m_init,
                            Hext,
                            f=6.5e9,
                            I_amp=0,
                            LLG_time=4e-9,
                            LLG_steps=2000):
        DynamicR = []
        PIMM_ = []
        m_traj = np.empty((0, 3), float)
        M_full = np.empty((0, n_layers, 3), float)

        t = np.linspace(0, LLG_time, LLG_steps)
        I = I_amp / 8 * np.sin(
            2 * np.pi * f *
            t)  #+ 2*np.pi*self.plotter.IACphi/360  +   2*np.pi*Ry0[0]/360)
        Isdd = I_amp / 8 * np.sin(2 * np.pi * f * t)
        m = np.array(m_init)

        CKdir = [cmtj.CVector(*kdir) for kdir in CKdir]

        Cdt = LLG_time / LLG_steps
        CHext = cmtj.CVector(*Hext)
        CNdemag = [cmtj.CVector(*CNdemag[i, :]) for i in range(3)]

        Cm_all = [cmtj.CVector(*m[i, :]) for i in range(n_layers)]
        CIdir = cmtj.CVector(1, 0, 0)
        m_null = cmtj.CVector(1, 0, 0)
        CHOe_pulse = cmtj.CVector(0, 0, 10000)
        CHOe_null = cmtj.CVector(0, 0, 0)

        for i in range(len(t)):
            CHOe = CHOe_null
            if I_amp == 0 and i == 0:
                CHOe = CHOe_pulse
            elif I_amp == 0 and i != 0:
                CHOe = CHOe_null
            else:
                CHOe = cmtj.CVector(0, 5 * I[i], 0)

            if n_layers == 1:
                Cm_all[0] = cmtj.RK45(Cm_all[0], m_null, CHext, 0, Cdt, CHOe,
                                      CMs, CKu, CJu, CKdir, Cth, Calpha,
                                      CNdemag)
                DynamicR.append(1)
            else:
                for layer in range(n_layers):
                    Cm_all[layer] = cmtj.RK45(Cm_all[layer],
                                              Cm_all[(layer + 1) % n_layers],
                                              CHext, layer, Cdt, CHOe, CMs,
                                              CKu, CJu, CKdir, Cth, Calpha,
                                              CNdemag)

                DynamicR.append(
                    cmtj.SpinDiode2Layers(CIdir, Cm_all[0], Cm_all[1], 100,
                                          0.1))
            PIMM_.append(np.sum([m.z for m in Cm_all]))

        if I_amp == 0:
            SD_voltage_after_bias = 0
        else:
            SD_voltage = -np.multiply(Isdd, DynamicR)
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
        # print(l,w, l_w)
        # input()
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

    def __init__(self, parent) -> None:
        self.stop = False
        self.plotter = parent

    def run_H_step(m, Hval, freqs, spin_device, LLG_time, LLG_steps):
        pool = multiprocessing.Pool()
        results = []
        mag_stat = (pool.apply_async(
            Solver.calc_trajectoryRK45,
            args=(spin_device["Ku"], spin_device["Ms"], spin_device["J"],
                  spin_device["th"], spin_device["Kdir"],
                  spin_device["Ndemag"], spin_device["alpha"],
                  spin_device["number_of_layers"], m, Hval, 0, 0, LLG_time,
                  LLG_steps)))
        for f in freqs:
            results.append(
                pool.apply_async(Solver.calc_trajectoryRK45,
                                 args=(spin_device["Ku"], spin_device["Ms"],
                                       spin_device["J"], spin_device["th"],
                                       spin_device["Kdir"],
                                       spin_device["Ndemag"],
                                       spin_device["alpha"],
                                       spin_device["number_of_layers"], m,
                                       Hval, f, 20000, LLG_time, LLG_steps)))

        SD_f = list(zip(*[r.get() for r in results]))[4]
        pool.close()
        pool.join()
        m = mag_stat.get()[0]
        m_avg = mag_stat.get()[1]
        dynamic_r = mag_stat.get()[2]
        m_traj = mag_stat.get()[5]
        PIMM_ = mag_stat.get()[7]

        yf = abs(np.fft.fft(PIMM_))
        Rx, Ry, Rz = Solver.calculate_resistance(
            spin_device["Rx0"], spin_device["Ry0"], spin_device["AMR"],
            spin_device["AHE"], spin_device["SMR"], m,
            spin_device["number_of_layers"], spin_device["l"],
            spin_device["w"])

        return {
            "SD_f": SD_f,
            "m": m,
            "m_avg": m_avg,
            "m_traj": m_traj,
            "dynamic_r": dynamic_r,
            "PIMM": PIMM_,
            "yf": yf,
            "Rx": Rx,
            "Ry": Ry,
            "Rz": Rz
        }
