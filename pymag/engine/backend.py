from pymag.engine.data_holders import ResultHolder, StimulusObject
from pymag.engine.utils import SimulationStatus, butter_lowpass_filter

# import numba
from PyQt5 import QtCore
import time
import cmtj
import numpy as np
from scipy.fft import fft


def compute_vsd(stime, m_xs, frequency, integration_step):
    I_amp = 20000
    Isdd = (I_amp / 8) * np.sin(2 * np.pi * frequency * stime)
    Rlow = 100 * len(m_xs)
    dR = 0.1
    SD = -Isdd * np.sum(Rlow + dR * m_xs, axis=0)
    SD_voltage = butter_lowpass_filter(SD,
                                       cutoff=10e6,
                                       fs=1. / integration_step,
                                       order=3)
    return np.mean(SD_voltage)


def compute_vsd_(stime, dynamicR, frequency, integration_step):
    I_amp = 20000
    Isdd = (I_amp / 8) * np.sin(2 * np.pi * frequency * stime)

    SD = -Isdd * dynamicR
    SD_voltage = butter_lowpass_filter(SD,
                                       cutoff=10e6,
                                       fs=1. / integration_step,
                                       order=3)
    return np.mean(SD_voltage)


# @numba.jit(nopython=True, parallel=False)
def calculate_resistance(Rx0, Ry0, AMR, AHE, SMR, m, number_of_layers, l, w):
    R_P = Rx0[0]
    R_AP = Ry0[0]

    if m.ndim == 2:

        SxAll = np.zeros((number_of_layers, ))
        SyAll = np.zeros((number_of_layers, ))

    elif m.ndim == 3:
        SxAll = np.zeros((number_of_layers, m.shape[2]))
        SyAll = np.zeros((number_of_layers, m.shape[2]))

    for i in range(0, number_of_layers):
        w_l = w[i] / l[i]
        SxAll[i] = 1 / (Rx0[i] + (AMR[i] * m[i, 0]**2 + SMR[i] * m[i, 1]**2))
        SyAll[i] = 1 / (Ry0[i] + 0.5 * AHE[i] * m[i, 2] + (w_l) *
                        (SMR[i] - AMR[i]) * m[i, 0] * m[i, 1])

    Rx = 1 / np.sum(SxAll, axis=0)
    Ry = 1 / np.sum(SyAll, axis=0)

    if number_of_layers > 1:
        Rz = R_P + (R_AP - R_P) / 2 * (1 - np.sum(m[0, :] * m[1, :], axis=0))
    else:
        Rz = 0

    return Rx, Ry, Rz


class SolverTask(QtCore.QThread):
    progress = QtCore.pyqtSignal(int)

    def __init__(self, queue, simulation_indices, simulations, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.queue = queue
        self.simulation_indices = simulation_indices
        self.simulations = simulations
        self.is_paused = False
        self.is_killed = False

    def kill(self):
        self.is_killed = True

    def pause(self):
        self.is_paused = True

    def simulation_setup(self, simulation: 'Simulation'):
        sim_input = simulation.get_simulation_input()
        stimulus: StimulusObject = sim_input.stimulus

        s_time = stimulus.LLG_time
        int_step = s_time / stimulus.LLG_steps
        org_layers = sim_input.layers

        # Irf = stimulus

        Rx0 = np.asarray([l.Rx0 for l in org_layers])
        Ry0 = np.asarray([l.Ry0 for l in org_layers])
        SMR = np.asarray([l.SMR for l in org_layers])
        AMR = np.asarray([l.AMR for l in org_layers])
        AHE = np.asarray([l.AHE for l in org_layers])
        w = np.asarray([l.w for l in org_layers])
        l = np.asarray([l.l for l in org_layers])

        # Hoe is per Ampere
        Hoes = np.asarray([l.Hoe for l in org_layers])
        no_org_layers = len(org_layers)

        org_layer_strs = [
            f"{str(org_layers[i].layer)}" for i in range(no_org_layers)
        ]
        layers = [layer.to_cmtj() for layer in org_layers]
        junction = cmtj.Junction(filename="", layers=layers)
        for i in range(no_org_layers - 1):
            junction.setIECDriver(
                org_layer_strs[i], org_layer_strs[i + 1],
                cmtj.ScalarDriver.getConstantDriver(org_layers[i].J))
        m_init_PIMM = [
            cmtj.CVector(*(stimulus.H_sweep[0] /
                           np.linalg.norm(stimulus.H_sweep[0])))
            for i in range(len(layers))
        ]
        m_init_VSD = [
            cmtj.CVector(*(stimulus.H_sweep[0] /
                           np.linalg.norm(stimulus.H_sweep[0])))
            for i in range(len(layers))
        ]
        for Hval in stimulus.H_sweep:
            if not self.handle_signals():
                return
            SD_results = []
            HDriver = cmtj.AxialDriver(
                cmtj.ScalarDriver.getConstantDriver(Hval[0]),
                cmtj.ScalarDriver.getConstantDriver(Hval[1]),
                cmtj.ScalarDriver.getConstantDriver(Hval[2]))
            junction.setLayerExternalFieldDriver("all", HDriver)
            # run vsd
            junction.clearLog()
            for i in range(no_org_layers):
                junction.setLayerMagnetisation(org_layer_strs[i],
                                               m_init_PIMM[i])

            HoeDriver = cmtj.AxialDriver(
                cmtj.NullDriver(), cmtj.NullDriver(),
                cmtj.ScalarDriver.getStepDriver(0, 1000, 0.0, 1e-11))
            junction.setLayerOerstedFieldDriver("all", HoeDriver)
            junction.runSimulation(s_time, int_step, int_step)
            for i in range(no_org_layers):
                m_init_PIMM[i] = junction.getLayerMagnetisation(
                    org_layer_strs[i])
            log = junction.getLog()
            mixed = np.mean([
                np.asarray(log[f"{org_layer_strs[i]}_mz"])
                for i in range(no_org_layers)
            ],
                axis=0)
            mixed = np.squeeze(mixed)
            yf = np.abs(fft(mixed))
            # take last m step
            m = np.asarray([[
                log[f'{org_layer_strs[i]}_mx'][-1],
                log[f'{org_layer_strs[i]}_my'][-1],
                log[f'{org_layer_strs[i]}_mz'][-1]
            ] for i in range(no_org_layers)])
            Rx, Ry, Rz = calculate_resistance(Rx0, Ry0, AMR, AHE, SMR, m,
                                              no_org_layers, l, w)
            m_avg = np.mean(m, axis=0)

            for frequency in stimulus.SD_freqs:
                if not self.handle_signals():
                    return
                junction.clearLog()
                for i in range(no_org_layers):
                    junction.setLayerMagnetisation(org_layer_strs[i],
                                                   m_init_VSD[i])
                HoeDriver = cmtj.AxialDriver(
                    cmtj.NullDriver(),
                    cmtj.ScalarDriver.getSineDriver(0, 5 * 20000 / 8,
                                                    frequency, 0),
                    cmtj.NullDriver())
                junction.setLayerOerstedFieldDriver("all", HoeDriver)
                junction.runSimulation(s_time, int_step, int_step)
                for i in range(len(layers)):
                    m_init_VSD[i] = junction.getLayerMagnetisation(
                        org_layer_strs[i])
                log = junction.getLog()
                m = np.asarray([[
                    log[f'{org_layer_strs[i]}_mx'],
                    log[f'{org_layer_strs[i]}_my'],
                    log[f'{org_layer_strs[i]}_mz']
                ] for i in range(no_org_layers)])

                dynamicR, _, _ = calculate_resistance(Rx0, Ry0, AMR, AHE, SMR,
                                                      m, no_org_layers, l, w)

                vmix = compute_vsd_(stime=np.asarray(log['time']),
                                    dynamicR=dynamicR,
                                    frequency=frequency,
                                    integration_step=int_step)
                SD_results.append(vmix)
            # run PIMM
            if not self.handle_signals():
                return
            partial_result = ResultHolder(mode=stimulus.mode,
                                          H_mag=stimulus.sweep,
                                          PIMM_freqs=stimulus.PIMM_freqs,
                                          SD_freqs=stimulus.SD_freqs,
                                          SD=SD_results,
                                          Rx=Rx,
                                          Ry=Ry,
                                          Rz=Rz,
                                          m_avg=m_avg,
                                          m_traj=[0, 0, 0],
                                          PIMM=yf[:len(yf) // 2])
            yield partial_result

    def handle_signals(self):
        if self.is_killed:
            self.queue.put(
                (self.simulation_indices, ..., SimulationStatus.KILLED))
            self.progress.emit(0)
            return 0
        while self.is_paused:
            time.sleep(0.1)
        return 1

    def run(self):
        all_H_sweep_vals = sum([
            len(sim.get_simulation_input().stimulus.H_sweep)
            for sim in self.simulations
        ])
        all_H_indx = 0
        final_PIMM = []
        for sim_index, simulation in zip(self.simulation_indices,
                                         self.simulations):
            for partial_result in self.simulation_setup(simulation=simulation):
                self.queue.put(
                    (sim_index, partial_result, SimulationStatus.IN_PROGRESS))
                all_H_indx += 1
                progr = 100 * (all_H_indx + 1) / (all_H_sweep_vals)
                self.progress.emit(progr)
                final_PIMM.append(partial_result.PIMM.tolist()[0])
            if not self.is_killed:
                self.queue.put((sim_index, ..., SimulationStatus.DONE))
        self.queue.put(({}, ..., SimulationStatus.ALL_DONE))
