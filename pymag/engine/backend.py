from pymag.engine.data_holders import Layer, ResultHolder, Stimulus
from typing import List
from scipy.fft import fft
from pymag.engine.solver import Solver
from PyQt5 import QtCore


class SolverTask(QtCore.QThread):
    progress = QtCore.pyqtSignal(int)

    def __init__(self, queue, simulation_indices, simulations, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.queue = queue
        self.simulation_indices = simulation_indices
        self.simulations = simulations

    def run(self):
        all_H_sweep_vals = sum([
            sim.get_simulation_input().stimulus.H_sweep.shape[0]
            for sim in self.simulations
        ])
        all_H_indx = 0

        for sim_index, simulation in zip(self.simulation_indices,
                                         self.simulations):
            simulation_input = simulation.get_simulation_input()
            stimulus: Stimulus = simulation_input.stimulus
            layers: List[Layer] = simulation_input.layers
            m, _, _, _, _, _, _, _ = Solver.calc_trajectoryRK45(
                layers=layers,
                m_init=Solver.init_vector_gen(len(layers),
                                              H_sweep=stimulus.H_sweep),
                Hext=stimulus.H_sweep[0, :],
                f=0,
                I_amp=0,
                LLG_time=stimulus.LLG_time,
                LLG_steps=stimulus.LLG_steps)
            for Hval in stimulus.H_sweep:
                m, _, _, _, _, _, _, PIMM = Solver.calc_trajectoryRK45(
                    layers=layers,
                    m_init=m,
                    Hext=Hval,
                    f=0,
                    I_amp=0,
                    LLG_time=stimulus.LLG_time,
                    LLG_steps=stimulus.LLG_steps)
                Hstep_result = Solver.run_H_step(m=m,
                                                 Hval=Hval,
                                                 freqs=stimulus.SD_freqs,
                                                 layers=layers,
                                                 LLG_time=stimulus.LLG_time,
                                                 LLG_steps=stimulus.LLG_steps)
                all_H_indx += 1
                progr = 100 * (all_H_indx + 1) / (all_H_sweep_vals)

                yf = abs(fft(PIMM))
                partial_result = ResultHolder(mode=stimulus.mode,
                                              H_mag=stimulus.Hmag,
                                              PIMM_delta_f=stimulus.PIMM_freqs,
                                              SD_freqs=stimulus.SD_freqs,
                                              PIMM=yf[0:(len(yf) // 2)],
                                              **{
                                                  key: Hstep_result[key]
                                                  for key in ('Rx', 'Ry', 'Rz',
                                                              'SD', 'm_avg',
                                                              'm_traj')
                                              })

                self.queue.put((sim_index, partial_result))
                self.progress.emit(progr)
