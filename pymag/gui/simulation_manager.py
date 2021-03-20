from pymag.engine.backend import SolverTask
from typing import Any, Dict, List
from PyQt5 import QtCore
from pymag.engine.data_holders import (GenericHolder, ResultHolder,
                                       SimulationInput)


class Simulation(GenericHolder):
    def __init__(self,
                 simulation_input,
                 simulation_result=None,
                 simulation_name="SimName") -> None:
        self.simulated: bool = False
        self.simulation_input: SimulationInput = simulation_input
        self.simulation_result: ResultHolder = simulation_result
        self.simulation_name = simulation_name

    def set_simulation_input(self, sinput: SimulationInput):
        self.simulation_input = sinput

    def get_simulation_input(self) -> SimulationInput:
        return self.simulation_input

    def set_simulation_result(self, sresult: ResultHolder):
        self.simulation_result = sresult

    def update_simulation_result(self, partial_result: ResultHolder):
        # TODO check if simulation's finished
        if self.simulation_result is None:
            self.simulation_result = partial_result
        else:
            self.simulation_result.merge_result(partial_result)

    def get_simulation_result(self) -> ResultHolder:
        return self.simulation_result


class SimulationManager():
    def __init__(self, queue, progress_bar) -> None:
        self.simulations: List[Simulation] = []
        self.selected_simulation_indices = []
        self.backend = Backend(queue, progress_bar)

    def add_simulation(self, simulation: Simulation):
        self.simulations.append(simulation)
        self.add_to_selected(len(self.simulations) - 1)

    def add_to_selected(self, simulation_index):
        self.selected_simulation_indices.append(simulation_index)
        self.selected_simulation_indices = sorted(
            self.selected_simulation_indices)

    def remove_from_selected(self, simulation_index):
        if simulation_index in self.selected_simulation_indices:
            self.selected_simulation_indices.remove(simulation_index)

    def remove_selected(self):
        """
        Remove the simulations that were active
        """
        for index in sorted(self.selected_simulation_indices, reverse=True):
            del self.simulations[index]

    def swap_simulation_status(self, index):
        if index in self.selected_simulation_indices:
            self.selected_simulation_indices.remove(index)
        else:
            self.selected_simulation_indices.append(index)

    def get_selected_simulations(self) -> List[Simulation]:
        return [
            self.simulations[indx] for indx in self.selected_simulation_indices
        ]

    def get_simulation(self, indx) -> Simulation:
        return self.simulations[indx]

    def get_simulation_result(self, indx) -> ResultHolder:
        return self.simulations[indx].get_simulation_result()

    def simulate_selected(self):
        self.backend.start_simulations(self.selected_simulation_indices,
                                       self.get_selected_simulations())

    def update_simulation_data(self, simulation_index: int,
                               partial_result: ResultHolder):
        self.simulations[simulation_index].update_simulation_result(
            partial_result)

    def get_simulation_names(self):
        return [
            self.simulations[i].simulation_name
            for i in range(len(self.simulations))
        ]


class Backend(QtCore.QObject):
    changed = QtCore.pyqtSignal(int)

    def __init__(self, queue, progress_unit):
        super().__init__()
        self._num = 0
        self.queue = queue
        self.progress_bar = progress_unit

    @QtCore.pyqtProperty(int, notify=changed)
    def num(self):
        return self._num

    @QtCore.pyqtSlot(int)
    def set_progress(self, val):
        if self._num == val:
            return
        self._num = val
        self.progress_bar.setValue(self._num)
        self.changed.emit(self._num)

    @QtCore.pyqtSlot()
    def start_simulations(self, simulation_indices: List[int],
                          simulations: List[Simulation]):
        self.thread = SolverTask(queue=self.queue,
                                 simulations=simulations,
                                 simulation_indices=simulation_indices,
                                 parent=self)
        self.thread.progress.connect(self.set_progress)
        # self.thread.stop_signal.connect(self.stop_signal)
        # self.thread.terminate()
        self.thread.start()
