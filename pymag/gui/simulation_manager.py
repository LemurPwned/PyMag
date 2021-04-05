from queue import Queue
from typing import List, Union

from pymag.engine.backend import SolverTask
from pymag.engine.data_holders import (ExperimentData, GenericHolder,
                                       ResultHolder, SimulationInput)
from PyQt5 import QtCore


class Simulation(GenericHolder):
    def __init__(self,
                 simulation_input: SimulationInput,
                 simulation_result: ResultHolder = None,
                 simulation_name: str = "SimName") -> None:
        self.simulated: bool = False
        self.simulation_input: SimulationInput = simulation_input
        self.simulation_result: ResultHolder = simulation_result
        self.name: str = simulation_name

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


class GeneralManager():
    def __init__(self) -> None:
        self.selected_indices: List[int] = []
        self.items: Union[List[Simulation], List[ExperimentData]] = []

    def add_to_selected(self, indx) -> None:
        self.selected_indices.append(indx)
        self.selected_indices = sorted(self.selected_indices)

    def add_item(self, item: Union[Simulation, ExperimentData]):
        self.items.append(item)
        self.add_to_selected(len(self.items) - 1)

    def get_selected_items(
            self) -> Union[List[Simulation], List[ExperimentData]]:
        return [self.items[indx] for indx in self.selected_indices]

    def get_item(self, indx) -> Union[Simulation, ExperimentData]:
        return self.items[indx]

    def swap_item_status(self, index):
        if index in self.selected_indices:
            self.selected_indices.remove(index)
        else:
            self.selected_indices.append(index)

    def remove_selected(self) -> None:
        """
        Remove the simulations that were active
        """
        for indx in sorted(self.selected_indices, reverse=True):
            del self.items[indx]

    def get_item_names(self) -> List[str]:
        return [self.items[i].name for i in range(len(self.items))]


class ExperimentManager(GeneralManager):
    def __init__(self) -> None:
        super().__init__()
        self.items: List[ExperimentData] = []

    def add_experiment(self, experiment: ExperimentData):
        self.add_item(experiment)

    def get_selected_experiments(self) -> List[ExperimentData]:
        return self.get_selected_items()

    def get_experiment(self, indx: int) -> ExperimentData:
        return self.get_item(indx)


class SimulationManager(GeneralManager):
    def __init__(self, queue: Queue, progress_bar, kill_btn=None) -> None:
        super().__init__()
        self.items: List[Simulation] = []
        self.backend = Backend(queue, progress_bar, kill_btn=kill_btn)

    def add_simulation(self, simulation: Simulation):
        self.add_item(simulation)

    def reset_simulation_output(self, index):
        self.items[index].simulation_result = None

    def reset_selected_simulations_output(self):
        """
        Nullify the output of the simulation if the simulation
        has been 
        """
        for indx in self.selected_indices:
            self.reset_simulation_output(indx)

    def get_selected_simulations(self) -> List[Simulation]:
        return self.get_selected_items()

    def get_simulation(self, indx: int) -> Simulation:
        return self.get_item(indx)

    def get_simulation_result(self, indx) -> ResultHolder:
        return self.items[indx].get_simulation_result()

    def mark_as_done(self, indx: int):
        self.items[indx].simulated = True

    def simulate_selected(self):
        self.backend.start_simulations(self.selected_indices,
                                       self.get_selected_simulations())

    def update_simulation_data(self, simulation_index: int,
                               partial_result: ResultHolder):
        self.items[simulation_index].update_simulation_result(partial_result)


class Backend(QtCore.QObject):
    changed = QtCore.pyqtSignal(int)

    def __init__(self, queue, progress_unit, kill_btn=None):
        super().__init__()
        self._num = 0
        self.queue = queue
        self.progress_bar = progress_unit
        self.kill_btn = kill_btn

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
        self.kill_btn.clicked.connect(self.thread.kill)
        self.thread.start()
