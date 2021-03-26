from pymag.engine.utils import SimulationStatus
from pymag.engine.data_holders import Layer, ResultHolder, Stimulus
from typing import List
from pymag.engine.solver import Solver
from PyQt5 import QtCore
import time


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
                if self.is_killed:
                    self.queue.put((self.simulation_indices, ...,
                                    SimulationStatus.KILLED))
                    self.progress.emit(0)
                    return
                while self.is_paused:
                    time.sleep(0.1)
                Hstep_result = Solver.run_H_step(m=m,
                                                 Hval=Hval,
                                                 freqs=stimulus.SD_freqs,
                                                 layers=layers,
                                                 LLG_time=stimulus.LLG_time,
                                                 LLG_steps=stimulus.LLG_steps)
                all_H_indx += 1
                progr = 100 * (all_H_indx + 1) / (all_H_sweep_vals)
                m = Hstep_result["m"]

                partial_result = ResultHolder(mode=stimulus.mode,
                                              H_mag=stimulus.Hmag,
                                              PIMM_freqs=stimulus.PIMM_freqs,
                                              SD_freqs=stimulus.SD_freqs,
                                              **{
                                                  key: Hstep_result[key]
                                                  for key in ('Rx', 'Ry', 'Rz',
                                                              'SD', 'm_avg',
                                                              'PIMM', 'm_traj')
                                              })

                self.queue.put(
                    (sim_index, partial_result, SimulationStatus.IN_PROGRESS))
                self.progress.emit(progr)

            self.queue.put((sim_index, ..., SimulationStatus.DONE))