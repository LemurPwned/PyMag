import os
import pickle
from pymag.engine.data_holders import ExperimentData
from typing import List, Tuple

from pymag.gui.simulation_manager import ExperimentManager, Simulation, SimulationManager
from PyQt5.QtWidgets import QFileDialog, QWidget


class Exporter:
    def __init__(self, simulation_manager: SimulationManager,
                 experiment_manager: ExperimentData, parent: QWidget) -> None:
        self.parent: QWidget = parent
        self.simulation_manager: SimulationManager = simulation_manager
        self.experiment_manager: ExperimentManager = experiment_manager

    def open_directory_dialog(self, msg: str) -> str:
        return QFileDialog.getExistingDirectory(self.parent, msg, options=QFileDialog.DontUseNativeDialog)

    def open_file_dialog(self, msg: str) -> Tuple[str, str]:
        return QFileDialog.getSaveFileName(self.parent, msg, options=QFileDialog.DontUseNativeDialog)

    def open_multiple_file_dialog(self, msg: str) -> Tuple[List[str], str]:
        return QFileDialog.getOpenFileNames(
            self.parent,
            msg,
            "",
            filter="Dat files (*.dat *.csv *.txt);;CSV files (*.csv);;TXT (*.txt)", options=QFileDialog.DontUseNativeDialog)

    def export_current_stimulus(self):
        ...

    def load_experimental_data(self):
        """
        Adds experiment data to experiment manager 
        and updates the plots
        """
        file_paths, _ = self.open_multiple_file_dialog("Open experiment files")
        for fn in file_paths:
            self.experiment_manager.add_experiment(ExperimentData.from_csv(fn))

        self.parent.measurement_manager.update()

    def export_simulations_csv(self):
        folder_location = self.open_directory_dialog(
            "Export active simulations to csv")
        selected_sims = self.simulation_manager.get_selected_simulations()
        for simulation in selected_sims:
            save_path = os.path.join(folder_location, simulation.name)
            result = simulation.get_simulation_result()
            if result:
                result.to_csv(save_path)
        # TODO inform if the simulation cannot be exported since it's empty
        # TODO a spin bar if it takes too long

    def save_workspace_binary(self):
        """
        Export active simulations to binary files
        """
        # pick up location
        directory, _ = self.open_file_dialog(msg="Save workspace")
        if not directory:
            return
        selected_sims = self.simulation_manager.get_selected_simulations()
        if not len(selected_sims):
            # TODO popup
            print("No active simulations to save!")
            return

        pickle.dump(selected_sims, open(directory + ".pkl", "wb"))

    def load_workspace_binary(self) -> None:
        """
        Adds simulations to a simulation manager
        """
        location, _ = self.open_file_dialog(msg="Load workspace")
        if not location:
            return
        assert os.path.isfile(location)
        assert location.endswith(".pkl")
        # read every sim in that location
        with open(location, "rb") as f:
            simulations = pickle.load(f)
            simulation: Simulation
            for simulation in simulations:
                self.simulation_manager.add_simulation(simulation)
        # TOOD: make this more elegant
        self.parent.simulation_manager.update()