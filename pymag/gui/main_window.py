import os
from pymag.gui.exporter import Exporter

from pymag.gui.simulation_manager import ExperimentManager, Simulation, SimulationManager
from pymag.engine.data_holders import Layer, SimulationInput, Stimulus
from pymag.gui.plot_manager import PlotManager
import queue
import logging
import pandas as pd
import pyqtgraph as pg
import multiprocessing as mp
from pymag.engine.utils import PyMagVersion, SimulationStatus
from pymag.gui.core import AddMenuBar, SimulationParameters, ResultsTable
from pymag.gui.plots import MultiplePlot, SpectrogramPlot
from PyQt5.QtWidgets import QMainWindow
from pyqtgraph.dockarea import Dock, DockArea


class UIMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setObjectName("PyMag")
        # load defaults
        self.defaultStimulusFile = os.path.join("pymag", "presets",
                                                "defaultStimulus.csv")
        self.defaultParametersFile = os.path.join("pymag", "presets",
                                                  "defaultParameters.csv")
        self.load_defaults()

        # main window properties
        self.setObjectName(PyMagVersion)
        self.setWindowTitle(PyMagVersion)
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

        self.simulation_manager = ResultsTable(self.global_sim_manager,
                                               self.plot_manager)
        self.measurement_manager = ResultsTable(self.global_experiment_manager,
                                                self.plot_manager)

        self.widget_layer_params = SimulationParameters(
            self, self.layerParameters, self.StimulusParameters)

        self.table_results = pg.TableWidget(editable=True, sortable=False)
        self.table_results.setHorizontalHeaderLabels(
            ['H', 'Mx', 'My', 'Mz', 'Rx', 'Ry', 'Rz'])

        self.d = []
        dock_titles = [
            "Control panel", "PIMM-FMR", "Magnetization", "Simulation results",
            "Resistance", "SD-FMR", "Measurement management",
            "Simulation management", "Layer parameters"
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
        self.d.append(Dock(dock_titles[0]))
        self.d[0].addWidget(dock_contents[0])
        for i in range(1, len(dock_titles)):
            self.d.append(Dock(dock_titles[i], size=(300, 50)))
            self.d[i].addWidget(dock_contents[i])

        dock_pos = [(self.d[0], 'left'), (self.d[1], 'right'),
                    (self.d[2], 'bottom', self.d[0]),
                    (self.d[3], 'above', self.d[2]),
                    (self.d[4], 'above', self.d[2]),
                    (self.d[5], 'above', self.d[1]),
                    (self.d[6], 'right', self.d[1]),
                    (self.d[7], 'above', self.d[6]),
                    (self.d[8], 'top', self.d[1])]

        for i in range(len(dock_titles)):
            self.area.addDock(*dock_pos[i])

        # MAIN OBJECTS
        # REPLOTTTER == "PLOT MANAGER"

        self.ports = []
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.on_simulation_data_update)
        self.timer.start(0)
        self.show()

    def load_defaults(self):
        """
        Load default parameters: Simulus and Layer Structure
        """
        self.StimulusParameters = pd.read_csv(self.defaultStimulusFile,
                                              delimiter='\t')
        self.layerParameters = pd.read_csv(self.defaultParametersFile,
                                           delimiter='\t')

    def end_program(self):
        """
            stimulus and layer params are saved when exit
        """
        self.get_df_from_table(
            self.widget_layer_params.table_stimulus_params).to_csv(
                self.defaultStimulusFile,
                encoding='utf-8',
                index=False,
                sep='\t')
        self.get_df_from_table(
            self.widget_layer_params.table_layer_params).to_csv(
                self.defaultParametersFile,
                encoding='utf-8',
                index=False,
                sep='\t')
        os._exit(0)

    def save_params(self, auto=0):
        ...

    def add_to_simulation_list(self):
        df = self.get_df_from_table(
            self.widget_layer_params.table_layer_params)
        df_stimulus = self.get_df_from_table(
            self.widget_layer_params.table_stimulus_params)

        sim_layers = [
            Layer.create_layer_from_gui(**df_dict)
            for df_dict in df.to_dict(orient="records")
        ]
        self.global_sim_manager.add_simulation(
            Simulation(simulation_input=SimulationInput(
                layers=sim_layers, stimulus=Stimulus(df_stimulus))))
        self.simulation_manager.print_and_color_table()

    def get_df_from_table(self, table):
        number_of_rows = table.rowCount()
        number_of_columns = table.columnCount()
        tmp_df = pd.DataFrame()
        tmp_col_name = []
        for i in range(number_of_columns):
            tmp_col_name.append(table.takeHorizontalHeaderItem(i).text())
            for j in range(number_of_rows):
                tmp_df.loc[j, i] = table.item(j, i).text()
        table.setHorizontalHeaderLabels(tmp_col_name)
        tmp_df.columns = tmp_col_name
        return tmp_df

    def start_simulations(self):
        self.central_layout.progress.setValue(0)
        self.global_sim_manager.simulate_selected()

    def on_simulation_data_update(self):
        try:
            sim_indx, res, status = self.result_queue.get(block=False)
            if status == SimulationStatus.DONE:
                self.global_sim_manager.mark_as_done(sim_indx)
                return
            elif status == SimulationStatus.KILLED:
                # now sim_indx is a list of the sim indices that were in the
                # compute backend
                for indx in sim_indx:
                    self.global_sim_manager.reset_simulation_output(indx)
                self.plot_manager.clear_all_plots()
            elif status == SimulationStatus.IN_PROGRESS:
                self.global_sim_manager.update_simulation_data(sim_indx, res)
                self.plot_manager.plot_result(
                    self.global_sim_manager.get_simulation(sim_indx))
            else:
                raise ValueError("Unknown simulation status received!")
        except queue.Empty:
            logging.debug("Queue emptied!")
