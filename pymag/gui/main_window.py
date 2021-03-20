import os
import pickle

from pymag.gui.simulation_manager import Simulation, SimulationManager
from pymag.engine.data_holders import Layer, SimulationInput, Stimulus
from pymag.gui.plot_manager import PlotManager
import queue
import logging
import numpy as np
import pandas as pd
import pyqtgraph as pg
from natsort import natsorted
from pymag.engine.utils import PyMagVersion
from pymag.gui.core import About, AddMenuBar, LayerTableStimulus, ResultsTable
from pymag.gui.plots import MultiplePlot, SpectrogramPlot
from pymag.gui.trajectory import TrajectoryPlot
from PyQt5.QtWidgets import QFileDialog, QMainWindow
from pyqtgraph.dockarea import Dock, DockArea


class UIMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # load defaults
        self.defaultStimulusFile = os.path.join("pymag", "presets",
                                                "defaultStimulus.csv")
        self.defaultParametersFile = os.path.join("pymag", "presets",
                                                  "defaultParameters.csv")
        self.load_defaults()

        # main window properties
        self.setObjectName(PyMagVersion)
        self.setWindowTitle(PyMagVersion)
        self.resize(1200, 900)

        # dock area as a central widget of GUI
        self.area = DockArea()
        self.setCentralWidget(self.area)

        # define classes
        self.window_about = About()

        # self.SD_plot = PlotDynamics()
        self.SD_plot = SpectrogramPlot()
        self.PIMM_plot = SpectrogramPlot()


        
        # self.res_plot = ResPlot()
        self.res_plot = MultiplePlot(left=["Rxx", "Rxy", "Rzz"],
                                     number_of_plots=3)
        # self.mag_plot = MagPlot()
        self.mag_plot = MultiplePlot(left=["Mx", "My", "Mz"],
                                     number_of_plots=3)
        self.traj_plot = TrajectoryPlot()

        self.central_layout = AddMenuBar(self)
        self.central_widget = self.central_layout.central_widget
        self.simulation_manager = ResultsTable(self)
        self.measurement_manager = ResultsTable(self)
        self.widget_layer_params = LayerTableStimulus(self,
                                                      self.layerParameters,
                                                      self.StimulusParameters)

        self.table_results = pg.TableWidget(editable=True, sortable=False)
        self.table_results.setHorizontalHeaderLabels(
            ['H', 'Mx', 'My', 'Mz', 'Rx', 'Ry', 'Rz'])

        self.d = []
        dock_titles = [
            "Control panel", "PIMM-FMR", "Magnetization", "Simulation results",
            "Resistance", "SD-FMR", "Measurement management",
            "Simulation management", "Layer parameters"
        ]

        dock_contents = [
            self.central_widget, self.PIMM_plot.plot_view,
            self.mag_plot.plot_area, self.table_results,
            self.res_plot.plot_area, self.SD_plot.plot_view,
            self.measurement_manager.central_widget,
            self.simulation_manager.central_widget,
            self.widget_layer_params.central_widget
        ]

        for i in range(len(dock_titles)):
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
        self.plot_manager = PlotManager(
            magnetisation_plot=self.mag_plot,
            resistance_plot=self.res_plot,
            SD_plot=self.SD_plot,
            PIMM_plot=self.PIMM_plot,
            trajectory_plot=self.traj_plot,
        )

        self.result_queue = queue.Queue()

        self.global_sim_manager = SimulationManager(
            self.result_queue, self.central_layout.progress)

        self.ports = []
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.on_simulation_data_update)
        self.timer.start(0)
        self.show()

    def load_defaults(self):
        # try:
        self.StimulusParameters = pd.read_csv(self.defaultStimulusFile,delimiter='\t')
        # except:
        #     print("No file with default stimulus was found")
        #     self.StimulusParameters = pd.DataFrame(
        #         np.array([[
        #             -800000, 800000, 50, 0, 89.9, 45, 0, 47e9, 48, 0.01, 0.01,
        #             "[1 0 0]", 0, "[1 0 0]", 4e-9, 2000
        #         ]]),
        #         columns=[
        #             'Hmin', 'Hmax', 'Hsteps', 'Hback', 'HTheta', 'HPhi',
        #             'fmin', 'fmax', 'fsteps', 'IAC', 'IDC', 'Idir', 'fphase',
        #             'Vdir', 'LLGtime', 'LLGsteps'
        #         ])

        # try:
        self.layerParameters = pd.read_csv(self.defaultParametersFile,
                                               delimiter='\t')
        # except:
        #     print("No file with default parameters was found")
        #     self.layerParameters = pd.DataFrame(
        #         np.array([[
        #             1, 1.6, 3000, "[1 0 0]", -1e-5, 0.01, 1e-9, "[0 0 1]",
        #             0.02, 0.01, 0.01, 100, 120
        #         ],
        #                   [
        #                       2, 1.1, 4000, "[1 0 0]", -1e-5, 0.01, 1e-9,
        #                       "[0 0 1]", 0.02, 0.01, 0.01, 100, 120
        #                   ]]),
        #         columns=[
        #             'layer', 'Ms', 'Ku', 'Kdir', 'J', 'alpha', 'th', 'N',
        #             'AMR', 'SMR', 'AHE', 'Rx0', 'Ry0'
        #         ])

    def about(self):
        self.window_about.show()

    def full_screen(self):
        """
            Switch between normal and full screen mode
        """
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

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

    def open_file_dialog(self, extention=".csv"):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(
            self,
            "QFileDialog.getOpenFileName()",
            "",
            "File (*" + extention + ");;CSV (*.csv)",
            options=options)
        return fileName

    def open_dir_dialog(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        fileName, _ = QFileDialog.getOpenFileName(
            self, "QFileDialog.getOpenFileName()", "")
        return fileName

    def save_file_dialog(self, extention=".csv"):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(
            self,
            "QFileDialog.getOpenFileName()",
            "",
            "File (*" + extention + ")",
            options=options)
        return fileName + extention

    def save_params(self, auto=0):
        if auto == 0:
            fileName = self.save_file_dialog()
        else:
            curr_dir = os.path.dirname(os.path.realpath(__file__))
            fileName = curr_dir + "/" + "previous_params.csv"
        if fileName:
            df_generated_data = self.get_df_from_table(
                self.widget_layer_params.table_layer_params)
            df_generated_data.to_csv(fileName,
                                     encoding='utf-8',
                                     index=False,
                                     sep='\t')

    def save_binary(self):
        fileName = self.save_file_dialog(".bin")
        a_file = open(fileName, "wb")
        pickle.dump([
            self.simulation_manager.results_list_JSON,
            self.measurement_manager.results_list_JSON
        ], a_file)
        a_file.close()

    def load_binary(self):
        fileName = self.open_file_dialog(".bin")
        a_file = open(fileName, "rb")
        package1 = pickle.load(a_file)
        self.simulation_manager.results_list_JSON = package1[0]
        self.measurement_manager.results_list_JSON = package1[1]
        a_file.close()
        self.simulation_manager.results_table.setData(
            pd.DataFrame(
                np.array(self.simulation_manager.results_list_JSON["settings"])
            ).to_numpy())
        self.measurement_manager.results_table.setData(
            pd.DataFrame(
                np.array(self.measurement_manager.results_list_JSON["settings"]
                         )).to_numpy())

    def add_to_simulation_list(self):
        df = self.get_df_from_table(
            self.widget_layer_params.table_layer_params)
        df_stimulus = self.get_df_from_table(
            self.widget_layer_params.table_stimulus_params)

        sim_layers = [
            Layer(**df_dict) for df_dict in df.to_dict(orient="records")
        ]
        self.global_sim_manager.add_simulation(
            Simulation(simulation_input=SimulationInput(
                layers=sim_layers, stimulus=Stimulus(df_stimulus))))

        self.simulation_manager.results_list_JSON["results"].append({
            "MR":
            np.array([[0, 0, 0, 0, 0, 0], [1, 0, 0, 0, 0, 0]]),
            "SD_freqs":
            np.array([0, 1]),
            "SD":
            np.array([[0, 0, 0], [0, 0, 0]]),
            "PIMM_freqs":
            1,
            "PIMM":
            np.array([[0, 0]]),
            "traj":
            np.array([[0, 0, 0]])
        })
        self.simulation_manager.results_list_JSON["settings"].append(
            ["X", "from_table", "To be simulated"])
        self.simulation_manager.results_list_JSON["layer_params"].append(df)
        self.simulation_manager.results_list_JSON["simulation_params"].append(
            df_stimulus)
        self.simulation_manager.print_and_color_table()
        # self.simulation_manager.print_and_color_table()

    def load_multiple(self):
        dirName = "/home/sz/Desktop/AGH/PyMag/20 Oct 2020/4651_Pymag"
        listaa = []
        listab = []
        listac = []
        for path, subdirs, files in os.walk(dirName):
            for name in files:
                if os.path.splitext(name)[1] == ".csv":
                    listaa.append(os.path.join(path, name))
                elif os.path.splitext(name)[1] == ".dat" and os.path.splitext(
                        name)[0].find("PO") != -1:
                    listab.append(os.path.join(path, name))
                elif os.path.splitext(name)[1] == ".dat" and os.path.splitext(
                        name)[0].find("ment") != -1:
                    listac.append(os.path.join(path, name))
        for a in natsorted(listaa):
            self.load_param_table(auto=False, filename=a)
        for b in natsorted(listab):
            self.load_results(auto=False, filename=b)
        for c in natsorted(listac):
            self.load_results(auto=False, filename=c)

    def load_param_table(self, dialog=True, auto=True, filename=""):
        if auto == True:
            fileName = self.open_file_dialog()
        else:
            fileName = filename
        if fileName:
            df = pd.read_csv(fileName, delimiter='\t')
            self.widget_layer_params.table_layer_params.setData(np.array(df))
            self.widget_layer_params.table_layer_params.setHorizontalHeaderLabels(
                df.columns)
            simulationName = os.path.basename(fileName).replace(
                ".csv",
                "").replace("_layer_params",
                            "").replace("_layers_params",
                                        "").replace("_layer_param", "")
            self.central_layout.Simulation_Name.setText(simulationName)
            self.simulation_manager.results_list_JSON["results"].append({
                "MR":
                np.array([[0, 0, 0, 0, 0, 0], [1, 0, 0, 0, 0, 0]]),
                "SD_freqs":
                np.array([0, 1]),
                "SD":
                np.array([[0, 0, 0], [0, 0, 0]]),
                "PIMM_freqs":
                1,
                "PIMM":
                np.array([[0, 0]]),
                "traj":
                np.array([[0, 0, 0]])
            })
            self.simulation_manager.results_list_JSON["settings"].append(
                ["X", simulationName, "To be simulated"])
            self.simulation_manager.results_list_JSON["layer_params"].append(
                df)
            df_stimulus = self.get_df_from_table(
                self.widget_layer_params.table_stimulus_params)
            self.simulation_manager.results_list_JSON[
                "simulation_params"].append(df_stimulus)
            self.simulation_manager.print_and_color_table()
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

    def save_results(self):
        fileName = self.save_file_dialog("_MR.csv")
        if fileName:
            df_generated_data = self.get_df_from_table(self.table_results)
            df_generated_data.to_csv(fileName,
                                     encoding='utf-8',
                                     index=False,
                                     sep='\t')

    def export_images(self, num=1):
        self.simulation_manager.active_list = [num]
        self.measurement_manager.active_list = [
            num, num + int(self.simulation_manager.results_table.rowCount())
        ]
        self.replot_results()
        exporter = pg.exporters.ImageExporter(self.res_plot.plotsRes.sceneObj)
        exporter.export('Res' + '.png')
        exporter = pg.exporters.ImageExporter(self.mag_plot.plotsMag.sceneObj)
        exporter.export('Mag' + '.png')
        exporter = pg.exporters.ImageExporter(
            self.SD_plot.plot_dynamics_view.sceneObj)
        exporter.export('SD' + '.png')
        # self.PIMM_plot.export()
        exporter = pg.exporters.ImageExporter(
            self.PIMM_plot.plot_dynamics_view.sceneObj)
        exporter.export('PIMM' + '.png')
        exporter = pg.exporters.ImageExporter(self.SD_lines.plotsLS.sceneObj)
        exporter.export('LS' + '.png')

    def load_results(self, dialog=True, auto=True, filename=""):
        if auto == True:
            fileName = self.open_file_dialog(".dat")
        else:
            fileName = filename
        if fileName:
            df = pd.read_csv(fileName, delimiter='\t')
            self.plot_experimental(
                df,
                os.path.basename(fileName).replace(".dat", ""))

    def plot_experimental(self, df, fileName):
        self.mag_plot.Mx.plot(df['H'],
                              df['Mx'],
                              symbol='o',
                              pen=None,
                              symbolPen=(255, 0, 0, 90),
                              symbolBrush=(255, 0, 0, 50))
        self.mag_plot.My.plot(df['H'],
                              df['My'],
                              symbol='o',
                              pen=None,
                              symbolBrush=(0, 255, 0, 90),
                              symbolPen=(0, 255, 0, 50))

        self.mag_plot.Mz.plot(df['H'],
                              df['Mz'],
                              symbol='o',
                              pen=None,
                              symbolBrush=(0, 0, 255, 90),
                              symbolPen=(0, 0, 255, 50))

        self.res_plot.Rx.plot(df['H'],
                              df['Rx'],
                              symbol='o',
                              pen=None,
                              symbolBrush=(255, 0, 0, 90),
                              symbolPen=(255, 0, 0, 50))

        self.res_plot.Ry.plot(df['H'],
                              df['Ry'],
                              symbol='o',
                              pen=None,
                              symbolBrush=(0, 255, 0, 90),
                              symbolPen=(0, 255, 255, 50))

        self.res_plot.Rz.plot(df['H'],
                              df['Rz'],
                              symbol='o',
                              pen=None,
                              symbolBrush=(0, 0, 255, 90),
                              symbolPen=(0, 0, 255, 50))

        self.measurement_manager.results_list_JSON["settings"].append(
            ["X", "Exp", fileName])
        self.measurement_manager.results_list_JSON["results"].append({
            "H":
            df['H'],
            "f":
            df['f']
        })
        self.measurement_manager.results_list_JSON["layer_params"].append(
            ["X"])
        self.measurement_manager.print_and_color_table()

    def start_simulations(self):
        self.central_layout.progress.setValue(0)
        self.global_sim_manager.simulate_selected()

    def save_dock_state(self):
        global state
        state = self.area.saveState()

    def load_dock_state(self):
        global state
        self.area.restoreState(state)

    def stop_clk(self):
        pass

    def on_simulation_data_update(self):
        try:
            sim_indx, res = self.result_queue.get(block=False)
            # TODO: change this
            self.global_sim_manager.update_simulation_data(sim_indx, res)
            self.plot_manager.plot_result(
                self.global_sim_manager.get_simulation_result(sim_indx))
        except queue.Empty:
            logging.debug("Queue emptied!")

    def replot_experimental(self):
        try:
            for k in self.measurement_manager.active_list:
                xp1 = self.measurement_manager.results_list_JSON["results"][k]
                if "PO" in str(
                        self.measurement_manager.results_list_JSON["settings"]
                    [k][2]):  ###Raport
                    self.PIMM_plot.plots_spectrum.plot(xp1['H'],
                                                       xp1['f'],
                                                       symbol='o',
                                                       pen=None,
                                                       symbolBrush=(255, 0, 0,
                                                                    70),
                                                       symbolPen=(255, 0, 0,
                                                                  70))
                    self.SD_plot.plots_spectrum.plot(xp1['H'],
                                                     xp1['f'],
                                                     symbol='o',
                                                     pen=None,
                                                     symbolBrush=(255, 0, 0,
                                                                  70),
                                                     symbolPen=(255, 0, 0, 70))
                elif "ment" in str(
                        self.measurement_manager.results_list_JSON["settings"]
                    [k][2]):  ###Raport
                    self.PIMM_plot.plots_spectrum.plot(xp1['H'],
                                                       xp1['f'],
                                                       symbol='o',
                                                       pen=None,
                                                       symbolBrush=(0, 255, 0,
                                                                    120),
                                                       symbolPen=(0, 255, 0,
                                                                  120))
                    self.SD_plot.plots_spectrum.plot(xp1['H'],
                                                     xp1['f'],
                                                     symbol='o',
                                                     pen=None,
                                                     symbolBrush=(0, 255, 0,
                                                                  120),
                                                     symbolPen=(0, 255, 0,
                                                                120))
                else:
                    self.PIMM_plot.plots_spectrum.plot(xp1['H'],
                                                       xp1['f'],
                                                       symbol='o',
                                                       pen=None,
                                                       symbolBrush=(255, 0, 0,
                                                                    70),
                                                       symbolPen=(255, 0, 0,
                                                                  70))
                    self.SD_plot.plots_spectrum.plot(xp1['H'],
                                                     xp1['f'],
                                                     symbol='o',
                                                     pen=None,
                                                     symbolBrush=(255, 0, 0,
                                                                  70),
                                                     symbolPen=(255, 0, 0, 70))
        except:
            pass
