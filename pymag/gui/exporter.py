import os
import pickle

from pymag.gui.simulation_manager import Simulation, SimulationManager
from PyQt5.QtWidgets import QFileDialog, QWidget


class Exporter:
    def __init__(self, simulation_manager: SimulationManager,
                 parent: QWidget) -> None:
        self.parent: QWidget = parent
        self.simulation_manager: SimulationManager = simulation_manager

    def open_directory_dialog(self, msg: str) -> str:
        return QFileDialog.getExistingDirectory(self.parent, msg, "")

    def export_workspace_binary(self):
        """
        Export active simulations to binary files
        """
        # pick up location
        location: str = self.open_directory_dialog(msg="Export workspace")
        if not location:
            return
        assert os.path.isdir(location)
        simulation: Simulation
        selected_sims = self.simulation_manager.get_selected_simulations()
        if not len(selected_sims):
            print("No active simulations to save!")
            return
        for simulation in selected_sims:
            # get simulation
            full_sim_path = os.path.join(location, simulation.simulation_name)
            pickle.dump(simulation, open(full_sim_path + ".pkl", "wb"))

    def load_workspace_binary(self) -> None:
        """
        Adds simulations to a simulation manager
        """
        location = self.open_directory_dialog(msg="Load workspace")
        if not location:
            return
        assert os.path.isdir(location)
        # read every sim in that location
        for sim_fn in os.listdir(location):
            if not sim_fn.endswith(".pkl"):
                return
            sim_loc = os.path.join(location, sim_fn)
            simulation: Simulation = pickle.load(open(sim_loc, "rb"))
            if isinstance(simulation, Simulation):
                self.simulation_manager.add_simulation(simulation)
            else:
                print(
                    f"Object found in [{location}] was not a simulation object"
                )

        # TOOD: make this more elegant
        self.parent.simulation_manager.update()