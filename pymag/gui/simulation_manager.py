from typing import List

from pymag.engine.data_holders import (GenericHolder, ResultHolder,
                                       SimulationInput)


class Simulation(GenericHolder):
    def __init__(self) -> None:
        self.simulated: bool = False
        self.simulation_input: SimulationInput = None
        self.simulation_result: ResultHolder = None

    def set_simulation_input(self, sinput: SimulationInput):
        self.simulation_input = sinput

    def get_simulation_input(self) -> SimulationInput:
        return self.simulation_input

    def set_simulation_result(self, sresult: ResultHolder):
        self.simulation_result = sresult

    def get_simulation_result(self) -> ResultHolder:
        return self.simulation_result


class SimulationManager:
    def __init__(self) -> None:
        self.simulations: List[Simulation] = []
        self.selected_simulation_indices = []

    def add_to_selected(self, simulation_index):
        self.selected_simulation_indices.append(simulation_index)
        self.selected_simulation_indices = sorted(
            self.selected_simulation_indices)

    def remove_from_selected(self, simulation_index):
        if simulation_index in self.selected_simulation_indices:
            self.selected_simulation_indices.remove(simulation_index)

    def iterate_selected(self):
        for indx in self.selected_simulation_indices:
            yield self.simulations[indx]

    def get_simulation(self, indx) -> Simulation:
        return self.simulations[indx]

    def get_simulation_result(self, indx) -> ResultHolder:
        return self.simulations[indx].get_simulation_result()
