import numpy as np
from pymag.engine.solver import PostProcessing, SimulationRunner, Solver
from PyQt5 import QtCore


class SolverTask(QtCore.QThread):
    progress = QtCore.pyqtSignal(int)

    def __init__(self, queue, device_list, stimulus_list, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.queue = queue
        self.device_list = device_list
        self.stimulus_list = stimulus_list

    def run(self):
        all_H_sweep_vals = sum(
            [stimulus["H_sweep"].shape[0] for stimulus in self.stimulus_list])
        all_H_indx = 0

        for device, stimulus in zip(self.device_list, self.stimulus_list):
            simulation_results = {
                "Hmag_out": [],
                "H": [],
                "m_avg": np.empty((0, 3), float),
                "m": np.empty((0, device["number_of_layers"], 3), np.float32),
                "Rx": [],
                "Ry": [],
                "Rz": [],
                "SD_f": np.empty((0, len(stimulus["freqs"])), float),
                "spectrogram_PIMM": np.empty((0, stimulus["spectrum_len"]),
                                             float)
            }
            m, _, _, _, _, _, _, _ = Solver.calc_trajectoryRK45(
                device["Ku"],
                device["Ms"],
                device["J"],
                device["th"],
                device["Kdir"],
                device["Ndemag"],
                device["alpha"],
                device["number_of_layers"],
                m_init=PostProcessing.init_vector_gen(
                    device["number_of_layers"], H_sweep=stimulus["H_sweep"]),
                Hext=stimulus["H_sweep"][0, :],
                f=0,
                I_amp=0,
                LLG_time=stimulus["LLG_time"],
                LLG_steps=stimulus["LLG_steps"])
            for hstep, Hval in enumerate(stimulus["H_sweep"]):
                Hstep_result = SimulationRunner.run_H_step(
                    m=m,
                    Hval=Hval,
                    freqs=stimulus["freqs"],
                    spin_device=device,
                    LLG_time=stimulus["LLG_time"],
                    LLG_steps=stimulus["LLG_steps"])
                all_H_indx += 1
                progr = 100 * (all_H_indx + 1) / (all_H_sweep_vals)

                for key in ["SD_f", "m", "m_avg"]:
                    simulation_results[key] = np.concatenate(
                        (simulation_results[key], [Hstep_result[key]]), axis=0)

                for key in ["Rx", "Ry", "Rz"]:
                    simulation_results[key].append(key)

                simulation_results["Hmag_out"].append(stimulus["H_mag"][hstep])
                simulation_results["spectrogram_PIMM"] = np.concatenate(
                    (simulation_results["spectrogram_PIMM"],
                     np.asarray([
                         Hstep_result["yf"][0:(len(Hstep_result["yf"]) // 2)]
                     ])))

                self.queue.put((progr, {
                    "MR":
                    np.array([
                        simulation_results["Hmag_out"],
                        simulation_results["m_avg"][:, 0],
                        simulation_results["m_avg"][:, 1],
                        simulation_results["m_avg"][:, 2],
                        simulation_results["Rx"], simulation_results["Ry"],
                        simulation_results["Rz"]
                    ]),
                    "SD_freqs":
                    stimulus["freqs"],
                    "SD":
                    simulation_results["SD_f"],
                    "PIMM_freqs":
                    stimulus["PIMM_delta_f"],
                    "PIMM":
                    simulation_results["spectrogram_PIMM"],
                    "traj":
                    Hstep_result["m_traj"],
                    "mode":
                    stimulus["mode"]
                }))

                # self.progress.emit()


class Backend(QtCore.QObject):
    changed = QtCore.pyqtSignal(int)

    def __init__(self, queue):
        super().__init__()
        self._num = 0
        self.queue = queue
        # self.progress_bar = progress_unit

    @QtCore.pyqtProperty(int, notify=changed)
    def num(self):
        return self._num

    @QtCore.pyqtSlot(int)
    def set_progress(self, val):
        if self._num == val:
            return
        self._num = val
        # self.progress_bar.setValue(self._num)
        self.changed.emit(self._num)

    @QtCore.pyqtSlot()
    def start_process(self, device_list, stimulus_list):
        self.thread = SolverTask(queue=self.queue,
                            device_list=device_list,
                            stimulus_list=stimulus_list,
                            parent=self)
        self.thread.progress.connect(self.set_progress)
        self.thread.start()