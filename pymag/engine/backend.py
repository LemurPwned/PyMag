import time

from numpy.core.fromnumeric import mean
from numpy.fft import fftfreq
import cmtj
import numpy as np
from pymag.engine.data_holders import Layer, ResultHolder, StimulusObject, VoltageSpinDiodeData
from pymag.engine.utils import SimulationStatus, butter_lowpass_filter
# import numba
from PyQt5 import QtCore
from scipy.fft import fft
from typing import List
from copy import deepcopy


def compute_vsd(frequency, dynamicR, integration_step, dynamicI) -> VoltageSpinDiodeData:
    SD = -dynamicI * dynamicR
    fs = 1.0/integration_step
    SD_dc = butter_lowpass_filter(SD,
                                  cutoff=10e6,
                                  fs=fs,
                                  order=3)
    SD_fft = fft(SD)[:len(SD)//2]
    freqs = fftfreq(len(SD), integration_step)[:len(SD)//2]
    amplitude = np.abs(SD_fft)
    phase = np.angle(SD_fft)

    # first harmonic
    # argmax in range frequency
    fhar_index = np.argsort(np.abs(freqs - frequency))[:5]  # neighbourhood
    max_fhar_amp_indx = np.argmax(SD_fft[fhar_index])
    # second harmonic
    # argmax in range 2*frequency
    shar_index = np.argsort(np.abs(freqs - 2*frequency))[:5]  # neighbourhood
    max_shar_amp_indx = np.argmax(SD_fft[shar_index])
    return VoltageSpinDiodeData(
        DC=np.mean(SD_dc).reshape(1, 1),
        FHarmonic=amplitude[fhar_index][max_fhar_amp_indx].reshape(1, 1),
        SHarmonic=amplitude[shar_index][max_shar_amp_indx].reshape(1, 1),
        FHarmonic_phase=phase[fhar_index][max_fhar_amp_indx].reshape(1, 1),
        SHarmonic_phase=phase[shar_index][max_shar_amp_indx].reshape(1, 1)
    )


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
        Rz = R_P + ((R_AP - R_P) / 2) * (1 - np.sum(m[0, :] * m[1, :], axis=0))
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
        org_layers: List[Layer] = sim_input.layers

        Rx0 = np.asarray([l.Rx0 for l in org_layers])
        Ry0 = np.asarray([l.Ry0 for l in org_layers])
        SMR = np.asarray([l.SMR for l in org_layers])
        AMR = np.asarray([l.AMR for l in org_layers])
        AHE = np.asarray([l.AHE for l in org_layers])
        w = np.asarray([l.w for l in org_layers])
        l = np.asarray([l.l for l in org_layers])

        no_org_layers = len(org_layers)

        org_layer_strs = [
            f"{str(org_layers[i].layer)}" for i in range(no_org_layers)
        ]
        layers = [layer.to_cmtj() for layer in org_layers]
        junction = cmtj.Junction(filename="", layers=layers)
        # assign IEC interacton
        for i in range(no_org_layers - 1):
            junction.setIECDriver(
                org_layer_strs[i], org_layer_strs[i + 1],
                cmtj.ScalarDriver.getConstantDriver(org_layers[i].J))

        # initialise the magnetisation vectors
        m_init_PIMM = [
            cmtj.CVector(*(stimulus.H_sweep[0] /
                           np.linalg.norm(stimulus.H_sweep[0])))
            for _ in range(len(layers))
        ]
        m_init_VSD = [
            cmtj.CVector(*(stimulus.H_sweep[0] /
                           np.linalg.norm(stimulus.H_sweep[0])))
            for _ in range(len(layers))
        ]
        """
        Primary PIMM loop
        """
        for Hval in stimulus.H_sweep:
            if not self.handle_signals():
                return
            Rx_vsd = None
            Ry_vsd = None
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
            junction.setLayerCurrentDriver("all", cmtj.NullDriver())

            junction.runSimulation(s_time, int_step, int_step)
            for i in range(no_org_layers):
                m_init_PIMM[i] = junction.getLayerMagnetisation(
                    org_layer_strs[i])
            log = junction.getLog()
            mixed = np.mean([
                np.asarray(log[f"{org_layer_strs[i]}_mz"])*org_layers[i].Ms
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
            """
            Secondary VSD loop 
            """
            for frequency in stimulus.SD_freqs:
                if not self.handle_signals():
                    return
                junction.clearLog()
                for i in range(no_org_layers):
                    junction.setLayerMagnetisation(org_layer_strs[i],
                                                   m_init_VSD[i])

                self.configure_VSD_excitation(
                    frequency=frequency,
                    org_layers_strs=org_layer_strs,
                    org_layers=org_layers,
                    junction=junction,
                    stimulus=stimulus
                )
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

                dynamicRx, dynamicRy, _ = calculate_resistance(Rx0, Ry0, AMR, AHE, SMR,
                                                               m, no_org_layers, l, w)
                dynamicI = stimulus.I_dc + stimulus.I_rf * \
                    np.sin(2 * np.pi * frequency * np.asarray(log['time']))

                Rxx_vsd_data = compute_vsd(
                    dynamicR=dynamicRx,
                    frequency=frequency,
                    integration_step=int_step,
                    dynamicI=dynamicI)
                Rxy_vsd_data = compute_vsd(
                    dynamicR=dynamicRy,
                    frequency=frequency,
                    integration_step=int_step,
                    dynamicI=dynamicI)
                if Rx_vsd is None:
                    Rx_vsd = Rxx_vsd_data
                    Ry_vsd = Rxy_vsd_data
                else:
                    Rx_vsd.merge_vsd(Rxx_vsd_data, axis=1)
                    Ry_vsd.merge_vsd(Rxy_vsd_data, axis=1)
            # run PIMM
            if not self.handle_signals():
                return
            partial_result = ResultHolder(mode=stimulus.mode,
                                          H_mag=stimulus.sweep,
                                          PIMM_freqs=stimulus.PIMM_freqs,
                                          SD_freqs=stimulus.SD_freqs,
                                          Rx=Rx,
                                          Ry=Ry,
                                          Rz=Rz,
                                          m_avg=m_avg,
                                          m_traj=[0, 0, 0],
                                          PIMM=yf[:len(yf) // 2],
                                          Rxx_vsd=Rx_vsd,
                                          Rxy_vsd=Ry_vsd)
            yield partial_result

    def configure_VSD_excitation(self, frequency: float,
                                 org_layers_strs: List[str],
                                 org_layers: List[Layer],
                                 junction: cmtj.Junction,
                                 stimulus: StimulusObject):
        """
        Decide what kind of excitation is present in the junction.
        Set both Oersted field and current adequately.
        Convert current to layer current density.
        """
        HoeDrivers: List[cmtj.AxialDriver] = [
            cmtj.AxialDriver(
                cmtj.ScalarDriver.getSineDriver(
                    l.Hoe*stimulus.I_dc, l.Hoe*stimulus.I_rf, frequency, 0),
                cmtj.ScalarDriver.getSineDriver(
                    l.Hoe*stimulus.I_dc, l.Hoe*stimulus.I_rf, frequency, 0),
                cmtj.ScalarDriver.getSineDriver(
                    l.Hoe*stimulus.I_dc, l.Hoe*stimulus.I_dc, frequency, 0))
            for l in org_layers]
        for i in range(len(org_layers)):
            driver = HoeDrivers[i]
            driver.applyMask(org_layers[i].Hoedir)
            junction.setLayerOerstedFieldDriver(
                org_layers_strs[i], driver)
            # for converting to current density
            if stimulus.I_dir == [1, 0, 0]:
                area = org_layers[i].w*org_layers[i].th
            elif stimulus.I_dir == [0, 1, 0]:
                area = org_layers[i].l*org_layers[i].th
            else:
                area = org_layers[i].w*org_layers[i].l
            junction.setLayerCurrentDriver(org_layers_strs[i],
                                           cmtj.ScalarDriver.getSineDriver(stimulus.I_dc/area,
                                           stimulus.I_rf/area, frequency, 0))

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
        batch_update = []
        batch_update_count = 2  # how many steps per plot update?
        for sim_index, simulation in zip(self.simulation_indices,
                                         self.simulations):
            for partial_result in self.simulation_setup(simulation=simulation):
                batch_update.append(
                    (sim_index, partial_result, SimulationStatus.IN_PROGRESS)
                )
                all_H_indx += 1
                progr = 100 * (all_H_indx + 1) / all_H_sweep_vals
                self.progress.emit(progr)
                if len(batch_update) and ((len(batch_update) % batch_update_count) == 0):
                    self.queue.put(deepcopy(batch_update))
                    # clear
                    batch_update.clear()
            if not self.is_killed:
                # put the remaining batch if not empty
                if len(batch_update):
                    self.queue.put(
                        deepcopy(batch_update))
                    # clear
                    batch_update.clear()
                self.queue.put((sim_index, ..., SimulationStatus.DONE))
        self.queue.put(({}, ..., SimulationStatus.ALL_DONE))
