import datetime
from pymag.gui.core import LayerStructure, SimulationResults, SimulationStimulus
import cmtj
import time as tm
import numpy as np
from scipy import fft
from pymag.engine.utils import butter_lowpass_filter, cos_between_arrays, normalize
import multiprocessing
import time as tm


class Solver:
    @staticmethod
    def calc_trajectoryRK45(spin_device,
                            m_init,
                            Hext,
                            f=6.5e9,
                            I_amp=0,
                            LLGtime=4e-9,
                            LLGsteps=2000):
        DynamicR = []
        PIMM_ = []
        m_traj = np.empty((0, 3), float)
        M_full = np.empty((0, spin_device.number_of_layers, 3), float)

        t = np.linspace(0, LLGtime, LLGsteps)
        I = I_amp / 8 * np.sin(
            2 * np.pi * f *
            t)  #+ 2*np.pi*self.plotter.IACphi/360  +   2*np.pi*Ry0[0]/360)
        Isdd = I_amp / 8 * np.sin(2 * np.pi * f * t)
        m = np.array(m_init)

        CKu = spin_device.Ku
        CMs = spin_device.Ms
        Ckdir = [cmtj.CVector(*kdir) for kdir in spin_device.Kdir]

        CJu = spin_device.J
        Cth = spin_device.th
        Calpha = spin_device.alpha
        Cdt = LLGtime / LLGsteps
        CHext = cmtj.CVector(*Hext)
        CNdemag = [cmtj.CVector(*spin_device.Ndemag2[i, :]) for i in range(3)]

        Cm_all = [
            cmtj.CVector(*m[i, :]) for i in range(spin_device.number_of_layers)
        ]
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

            if spin_device.number_of_layers == 1:
                Cm_all[0] = cmtj.RK45(Cm_all[layer], m_null, CHext, layer, Cdt,
                                      CHOe, CMs, CKu, CJu, Ckdir, Cth, Calpha,
                                      CNdemag)
                DynamicR.append(1)
            else:
                for layer in range(spin_device.number_of_layers):
                    Cm_all[layer] = cmtj.RK45(
                        Cm_all[layer],
                        Cm_all[(layer + 1) % spin_device.number_of_layers],
                        CHext, layer, Cdt, CHOe, CMs, CKu, CJu, Ckdir, Cth,
                        Calpha, CNdemag)

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

        m = np.asarray([cm[i] for cm in Cm_all])

        m_avg = (np.matmul(
            m.T, (np.array(spin_device.th) * np.array(spin_device.Ms)))) / sum(
                np.array(spin_device.th) * np.array(spin_device.Ms))
        return np.array(m), m_avg, np.asarray(
            DynamicR), Cdt, SD_voltage_after_bias, m_traj, M_full, PIMM_


class PostProcessing():
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

        # for i in range(0,number_of_layers):
        #     SxAll.append(1/(   Rx0[i] + Rx0[i] * AMR[i] * m[i, 0] ** 2 + Rx0[i] * SMR[i] * m[i, 1] ** 2)       )
        #     SyAll.append(1/(   Ry0[i] + AHE[i] * m[i, 2] + Rx0[i] * (AMR[i] + SMR[i]) * m[i, 0] * m[i, 1])     )

        Rx = 1 / sum(SxAll)
        Ry = 1 / sum(SyAll)

        if number_of_layers > 1:
            Rz = R_P + (R_AP -
                        R_P) / 2 * (1 - cos_between_arrays(m[0, :], m[1, :]))
        else:
            Rz = 0

        return Rx, Ry, Rz


class SimulationRunner:
    def __init__(self, parent) -> None:
        self.stop = False
        self.plotter = parent

    def initVectorGen(SpinDevice, Stimulus):
        m_init = []
        for _ in range(0, SpinDevice.number_of_layers):
            m_init.append(normalize(Stimulus.H_sweep[0, :]))
        return m_init

    def run_simulation(self, spin_device, stimulus, sim_results, sim_num,
                       curve, sim_name):
        for _ in range(2):
            m, _, _, _, _, _, _, _ = Solver.calc_trajectoryRK45(
                spin_device=spin_device,
                m_init=self.initVectorGen(spin_device, stimulus),
                Hext=stimulus.H_sweep[0, :],
                f=0,
                I_amp=0,
                LLGtime=stimulus.LLGtime,
                LLGsteps=stimulus.LLGsteps)

        for H_it in range(0, stimulus.H_sweep.shape[0]):
            pool = multiprocessing.Pool()
            results = []
            MagnStat = (pool.apply_async(
                Solver.calc_trajectoryRK45,
                args=(spin_device, m, stimulus.H_sweep[H_it, :], 0, 0,
                      stimulus.LLGtime, stimulus.LLGsteps)))
            for f in stimulus.freqs:
                results.append(
                    pool.apply_async(
                        Solver.calc_trajectoryRK45,
                        args=(spin_device, m, stimulus.H_sweep[H_it, :], f,
                              20000, stimulus.LLGtime, stimulus.LLGsteps)))

            SD_f = list(zip(*[r.get() for r in results]))[4]
            pool.close()
            pool.join()
            m = MagnStat.get()[0]
            m_avg = MagnStat.get()[1]
            DynamicR = MagnStat.get()[2]
            mtraj = MagnStat.get()[5]
            PIMM_ = MagnStat.get()[7]

            sim_results.Spectrogram_VSD = np.concatenate(
                (sim_results.Spectrogram_VSD, [SD_f]), axis=0)
            yf = abs(fft(PIMM_))
            sim_results.Spectrogram_data = np.concatenate(
                (sim_results.Spectrogram_data, np.array([yf[0:(len(yf) // 2)]
                                                         ])),
                axis=0)
            sim_results.Mlayers = np.concatenate(
                (sim_results.Mlayers, np.array([m])), axis=0)
            sim_results.M_avg = np.concatenate(
                (sim_results.M_avg, np.array([m_avg])), axis=0)
            sim_results.H.append(((stimulus.H_sweep[H_it][0])**2 +
                                  (stimulus.H_sweep[H_it][1])**2 +
                                  (stimulus.H_sweep[H_it][2])**2)**0.5)
            sim_results.Hmag_out.append(stimulus.Hmag[H_it])

            Rx, Ry, Rz = PostProcessing.calculate_resistance(
                spin_device.Rx0, spin_device.Ry0, spin_device.AMR,
                spin_device.AHE, spin_device.SMR, m,
                spin_device.number_of_layers, spin_device.l, spin_device.w)
            sim_results.Rx.append(Rx)
            sim_results.Ry.append(Ry)
            sim_results.Rz.append(Rz)

            data = np.array([
                sim_results.Hmag_out[:], sim_results.M_avg[:, 0],
                sim_results.M_avg[:, 1], sim_results.M_avg[:, 2],
                sim_results.Rx[:], sim_results.Ry[:], sim_results.Rz[:]
            ]).T
            progres = 100 * (H_it + 1) / (stimulus.H_sweep.shape[0])

            self.plotter.simulationsMenegement.simulations_list["results"].pop(
                sim_num)
            self.plotter.simulationsMenegement.simulations_list[
                "settings"].pop(sim_num)
            self.plotter.simulationsMenegement.simulations_list[
                "results"].insert(
                    sim_num, {
                        "MR": data,
                        "SD_freqs": stimulus.freqs,
                        "SD": sim_results.Spectrogram_VSD,
                        "PIMM_freqs": stimulus.PIMM_delta_f,
                        "PIMM": sim_results.Spectrogram_data,
                        "traj": mtraj,
                        "mode": stimulus.mode
                    })
            self.plotter.simulationsMenegement.simulations_list[
                "settings"].insert(sim_num, ["X", sim_name, "In process..."])
            curve.put((progres, {
                "MR": data,
                "SD_freqs": stimulus.freqs,
                "SD": sim_results.Spectrogram_VSD,
                "PIMM_freqs": stimulus.PIMM_delta_f,
                "PIMM": sim_results.Spectrogram_data,
                "traj": mtraj,
                "mode": stimulus.mode
            }))

    def run_scheduled_simulations(self):
        while True:
            if self.stop:
                list_todo = self.plotter.simulationsMenegement.active_experiments
                self.plotter.simulationsMenegement.active_experiments = []

                backend = self.plotter.ctrLayout.Backend_choose.currentText()
                print("Simulation started with backend", backend)

                for sim_num in list_todo:
                    spin_device = LayerStructure(sim_num)
                    stimulus = SimulationStimulus(sim_num)
                    sim_name = self.plotter.simulationsMenegement.simulations_list[
                        "settings"][sim_num][1]
                    SimulationTimeStamp = datetime.datetime.now()
                    sim_results = SimulationResults(Stimulus=stimulus,
                                                    SpinDevice=spin_device)

                    self.run_simulation(spin_device, stimulus,
                                        sim_results, sim_num,
                                        self.plotter.get_queue(), sim_name)

            else:
                tm.sleep(0.001)