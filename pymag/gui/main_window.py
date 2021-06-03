import logging
import multiprocessing as mp
import os
import queue

import pandas as pd
import pyqtgraph as pg
from pymag import __version__
from pymag.engine.data_holders import Layer, SimulationInput, Stimulus
from pymag.engine.utils import SimulationStatus
from pymag.gui.core import AddMenuBar, ResultsTable, SimulationParameters
from pymag.gui.exporter import Exporter
from pymag.gui.plot_manager import PlotManager
from pymag.gui.plots import MultiplePlot, SpectrogramPlot
from pymag.gui.simulation_manager import (ExperimentManager, Simulation,
                                          SimulationManager)
from PyQt5.QtWidgets import QMainWindow
from pyqtgraph.dockarea import Dock, DockArea


class UIMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setObjectName("PyMag")
        # load defaults
        default_stimulus_file = os.path.join("pymag", "presets",
                                             "defaultStimulus.csv")
        default_layer_parameters_file = os.path.join("pymag", "presets",
                                                     "defaultParameters.csv")
        self.stimulus_parameters, self.layer_parameters = self.load_defaults(
            default_stimulus_file, default_layer_parameters_file)

        # main window properties
        self.setObjectName(__version__)
        self.setWindowTitle(__version__)
        self.resize(1400, 900)

        # dock area as a central widget of GUI
        self.area = DockArea()
        self.setCentralWidget(self.area)

        # define classes
        self.SD_plot = SpectrogramPlot()
        self.PIMM_plot = SpectrogramPlot()

        self.res_plot = MultiplePlot(left=["Rxx", "Rxy", "Rzz"],
                                     number_of_plots=3)

        self.mag_plot = MultiplePlot(left=["Mx", "My", "Mz"],
                                     number_of_plots=3)

        self.plot_manager = PlotManager(magnetisation_plot=self.mag_plot,
                                        resistance_plot=self.res_plot,
                                        SD_plot=self.SD_plot,
                                        PIMM_plot=self.PIMM_plot)
        self.result_queue = mp.Queue()
        self.central_layout = AddMenuBar(parent=self)

        self.global_experiment_manager = ExperimentManager()
        self.global_sim_manager = SimulationManager(
            self.result_queue,
            self.central_layout.progress,
            kill_btn=self.central_layout.start_btn)

        exporter = Exporter(parent=self,
                            simulation_manager=self.global_sim_manager,
                            experiment_manager=self.global_experiment_manager)
        self.central_layout.set_exporter(exporter)

        self.widget_layer_params = SimulationParameters(
            self, self.layer_parameters, self.stimulus_parameters)

        self.simulation_manager = ResultsTable(self.global_sim_manager,
                                               self.plot_manager,
                                               self.widget_layer_params,
                                               exporter)
        self.measurement_manager = ResultsTable(self.global_experiment_manager,
                                                self.plot_manager,
                                                self.widget_layer_params,
                                                exporter)

        self.table_results = pg.TableWidget(editable=True, sortable=False)
        self.table_results.setHorizontalHeaderLabels(
            ['H', 'Mx', 'My', 'Mz', 'Rx', 'Ry', 'Rz'])

        self.d = []
        dock_titles = [
            "Control panel", "PIMM-FMR", "Magnetization", "Simulation results",
            "Resistance", "SD-FMR", "Measurement manager",
            "Simulation manager", "Simulation parameters"
        ]

        self.central_widget = self.central_layout.central_widget
        dock_contents = [
            self.central_widget, self.PIMM_plot.plot_view,
            self.mag_plot.plot_area, self.table_results,
            self.res_plot.plot_area, self.SD_plot.plot_view,
            self.measurement_manager.central_widget,
            self.simulation_manager.central_widget,
            self.widget_layer_params.central_widget
        ]
        # no size here
        for i in range(0, len(dock_titles)):
            self.d.append(Dock(dock_titles[i]))
            self.d[i].addWidget(dock_contents[i])

        dock_pos = [(self.d[0], 'left'), 
                    (self.d[6], 'right', self.d[0]),
                    (self.d[1], 'right', self.d[0]),
                    
                    (self.d[2], 'bottom', self.d[1]),
                    (self.d[3], 'above', self.d[2]),
                    (self.d[4], 'above', self.d[2]),
                    (self.d[5], 'above', self.d[1]),
                    
                    (self.d[7], 'above', self.d[6]),
                    (self.d[8], 'bottom', self.d[0])]
        

        for i in range(len(dock_titles)):
            self.area.addDock(*dock_pos[i])

        self.ports = []
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.on_simulation_data_update)
        self.timer.start(0)
        self.show()

    def load_defaults(self, default_stimulus_file,
                      default_layer_parameter_file):
        """
        Load default parameters: Simulus and Layer Structure
        """
        stimulus_parameters = pd.read_csv(default_stimulus_file,
                                          delimiter='\t')
        layer_parameters = pd.read_csv(default_layer_parameter_file,
                                       delimiter='\t')
        return stimulus_parameters, layer_parameters

    def end_program(self):
        """
        Stimulus and layer params at shutdown
        """
        df_stimulus, df_layers = self.widget_layer_params.get_all_data()
        df_stimulus.to_csv(self.stimulus_parameters,
                           encoding='utf-8',
                           index=False,
                           sep='\t')
        df_layers.to_csv(self.layer_parameters,
                         encoding='utf-8',
                         index=False,
                         sep='\t')
        os._exit(0)

    def add_to_simulation_list(self):
        df_stimulus, df_layers = self.widget_layer_params.get_all_data()
        print(df_layers.to_dict(orient='records')[0])
        sim_layers = [
            Layer.from_gui(**df_dict)
            for df_dict in df_layers.to_dict(orient="records")
        ]
        self.global_sim_manager.add_simulation(
            Simulation(simulation_input=SimulationInput(
                layers=sim_layers, stimulus=Stimulus(df_stimulus))))
        self.simulation_manager.update_list()

    def start_simulations(self):
        self.central_layout.progress.setValue(0)
        self.global_sim_manager.simulate_selected()

    def on_simulation_data_update(self):
        try:
            sim_indx, res, status = self.result_queue.get(block=False)
            if status == SimulationStatus.ALL_DONE:
                self.central_layout.set_btn_start_position()
            elif status == SimulationStatus.DONE:
                self.global_sim_manager.mark_as_done(sim_indx)
            elif status == SimulationStatus.KILLED:
                # now sim_indx is a list of the sim indices that were in the
                # compute backend
                for indx in sim_indx:
                    self.global_sim_manager.reset_simulation_output(indx)
                    self.global_sim_manager.update_status(
                        indx, SimulationStatus.KILLED)
                self.plot_manager.clear_simulation_plots()
            elif status == SimulationStatus.IN_PROGRESS:
                self.global_sim_manager.update_simulation_data(sim_indx, res)
                self.plot_manager.plot_result(
                    self.global_sim_manager.get_simulation(sim_indx))
            else:
                raise ValueError("Unknown simulation status received!")
            self.simulation_manager.update_row(sim_indx)
        except queue.Empty:
            logging.debug("Queue emptied!")
