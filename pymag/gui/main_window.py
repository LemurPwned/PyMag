import os
import pickle
import queue as Queue
from threading import Thread

import numpy as np
import pandas as pd
import pyqtgraph as pg
from natsort import natsorted
from pymag.engine.solver import SimulationRunner
from pymag.engine.utils import PyMagVersion
from pymag.gui.core import About, AddMenuBar, LayerTableStimulus, ResultsTable
from pymag.gui.plots import LineShape, MagPlot, PlotDynamics, ResPlot
from pymag.gui.trajectory import TrajectoryPlot
from PyQt5.QtWidgets import QFileDialog, QMainWindow
from pyqtgraph.dockarea import Dock, DockArea


class UIMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.runner = SimulationRunner(self)
        #load defaults
        # TODO: CHANGE PATHS HERE
        self.defaultStimulusFile =   os.path.join("pymag","presets","defaultStimulus.csv")
        self.defaultParametersFile = os.path.join("pymag","presets","defaultParameters.csv")
        self.load_defaults()

        #Main window properties
        self.setObjectName(PyMagVersion)
        self.setWindowTitle(PyMagVersion)
        self.resize(1200, 900)

        #dock area as a central widget of GUI
        self.area = DockArea()
        self.setCentralWidget(self.area)

        # define classes
        self.window_about = About(self)

        self.SD_lines = LineShape()
        self.SD_plot = PlotDynamics()
        self.PIMM_plot = PlotDynamics()
        self.res_plot = ResPlot()
        self.mag_plot = MagPlot()
        self.central_layout = AddMenuBar(self)
        self.central_widget = self.central_layout.central_widget
        self.traj_plot = TrajectoryPlot()
        self.simulation_manager = ResultsTable(self)
        self.measurement_manager = ResultsTable(self)
        self.widget_layer_params = LayerTableStimulus(self)
        self.table_results = pg.TableWidget(editable=True, sortable=False)
        self.table_results.setHorizontalHeaderLabels(
            ['H', 'Mx', 'My', 'Mz', 'Rx', 'Ry', 'Rz'])

        #define dock area structure
        self.d1 = Dock("Control panel", size=(300, 50))
        self.d2 = Dock("PIMM-FMR", size=(300, 300))
        self.d7 = Dock("SD-FMR", size=(300, 300))
        self.d3 = Dock("Magnetization", size=(300, 300))
        self.d4 = Dock("Simulation results", size=(300, 200))
        self.d6 = Dock("Resistance", size=(300, 300))
        self.d10 = Dock("Trajectory", size=(200, 200))
        self.d11 = Dock("SD lines", size=(300, 300))
        self.d20 = Dock("Layer parameters", size=(100, 200))
        self.d13 = Dock("Python console", size=(200, 200))
        self.d14 = Dock("Simulation management", size=(200, 200))
        self.d15 = Dock("Measurement management", size=(200, 200))

        self.area.addDock(self.d1, 'left')
        self.area.addDock(self.d2, 'right')
        self.area.addDock(self.d3, 'bottom', self.d1)
        self.area.moveDock(self.d15, 'right', self.d2)
        self.area.moveDock(self.d14, 'above', self.d15)
        self.area.addDock(self.d4, 'above', self.d3)
        self.area.addDock(self.d6, 'above', self.d3)
        self.area.addDock(self.d7, 'above', self.d2)
        self.area.addDock(self.d10, 'above', self.d7)
        self.area.addDock(self.d11, 'above', self.d7)
        self.area.moveDock(self.d20, 'top', self.d2)

        self.d20.addWidget(self.widget_layer_params.central_widget)
        self.d14.addWidget(self.simulation_manager.central_widget)
        self.d15.addWidget(self.measurement_manager.central_widget)
        self.d11.addWidget(self.SD_lines.plotsLS)
        self.d7.addWidget(self.SD_plot.plot_dynamics_view)
        self.d2.addWidget(self.PIMM_plot.plot_dynamics_view)
        self.d6.addWidget(self.res_plot.plotsRes)
        self.d3.addWidget(self.mag_plot.plotsMag)
        self.d4.addWidget(self.table_results)
        self.d1.addWidget(self.central_widget)
        self.d10.addWidget(self.traj_plot.w)

        self.ports = []
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(0)
        self.show()
        self.p = Thread(target=self.runner.run_scheduled_simulations)
        self.p.start()

    def load_defaults(self):
        try:
            self.StimulusParameters = pd.read_csv(self.defaultStimulusFile,
                                                  delimiter='\t')
        except:
            print("No file with default stimulus was found")
            self.StimulusParameters = pd.DataFrame(
                np.array([[
                    -800000, 800000, 50, 0, 89.9, 45, 0, 47e9, 48, 0.01, 0.01,
                    "[1 0 0]", 0, "[1 0 0]", 4e-9, 2000
                ]]),
                columns=[
                    'Hmin', 'Hmax', 'Hsteps', 'Hback', 'HTheta', 'HPhi',
                    'fmin', 'fmax', 'fsteps', 'IAC', 'IDC', 'Idir', 'fphase',
                    'Vdir', 'LLGtime', 'LLGsteps'
                ])

        try:
            self.layerParameters = pd.read_csv(self.defaultParametersFile,
                                               delimiter='\t')
        except:
            print("No file with default parameters was found")
            self.layerParameters = pd.DataFrame(
                np.array([[
                    1, 1.6, 3000, "[1 0 0]", -1e-5, 0.01, 1e-9, "[0 0 1]",
                    0.02, 0.01, 0.01, 100, 120
                ],
                          [
                              2, 1.1, 4000, "[1 0 0]", -1e-5, 0.01, 1e-9,
                              "[0 0 1]", 0.02, 0.01, 0.01, 100, 120
                          ]]),
                columns=[
                    'layer', 'Ms', 'Ku', 'Kdir', 'J', 'alpha', 'th', 'N',
                    'AMR', 'SMR', 'AHE', 'Rx0', 'Ry0'
                ])

    def about(self):
        self.window_about.show()

    def full_screen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def end_program(self):
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

    def set_stimulus_for_all(self):
        df_stimulus = self.get_df_from_table(
            self.widget_layer_params.table_stimulus_params)
        for n in range(self.simulation_manager.results_table.rowCount()):
            self.simulation_manager.results_list_JSON["simulation_params"][
                n] = df_stimulus
        self.replot_results()

    def clear_plots(self):
        self.res_plot.clear_plots()
        self.mag_plot.clear_plots()
        self.PIMM_plot.clear_plots()
        self.SD_plot.clear_plots()
        self.SD_lines.clear_plots()
        self.traj_plot.clear()

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
        self.simulation_manager.print_and_color_table()

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
        try:
            self.mag_plot.Mx.plot(df['H'],
                                  df['Mx'],
                                  symbol='o',
                                  pen=None,
                                  symbolPen=(255, 0, 0, 90),
                                  symbolBrush=(255, 0, 0, 50))
        except:
            pass
        try:
            self.mag_plot.My.plot(df['H'],
                                  df['My'],
                                  symbol='o',
                                  pen=None,
                                  symbolBrush=(0, 255, 0, 90),
                                  symbolPen=(0, 255, 0, 50))
        except:
            pass
        try:
            self.mag_plot.Mz.plot(df['H'],
                                  df['Mz'],
                                  symbol='o',
                                  pen=None,
                                  symbolBrush=(0, 0, 255, 90),
                                  symbolPen=(0, 0, 255, 50))
        except:
            pass
        try:
            self.res_plot.Rx.plot(df['H'],
                                  df['Rx'],
                                  symbol='o',
                                  pen=None,
                                  symbolBrush=(255, 0, 0, 90),
                                  symbolPen=(255, 0, 0, 50))
        except:
            pass
        try:
            self.res_plot.Ry.plot(df['H'],
                                  df['Ry'],
                                  symbol='o',
                                  pen=None,
                                  symbolBrush=(0, 255, 0, 90),
                                  symbolPen=(0, 255, 255, 50))
        except:
            pass
        try:
            self.res_plot.Rz.plot(df['H'],
                                  df['Rz'],
                                  symbol='o',
                                  pen=None,
                                  symbolBrush=(0, 0, 255, 90),
                                  symbolPen=(0, 0, 255, 50))
        except:
            pass
        try:
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
        except:
            pass

    def btn_clk(self):
        self.central_layout.progress.setValue(0)
        global stop
        stop = 0

    def stop_clk(self):
        global stop
        print(stop)
        stop = 1

    def save_dock_state(self):
        global state
        state = self.area.saveState()

    def load_dock_state(self):
        global state
        self.area.restoreState(state)

    def get_queue(self):
        q = Queue.Queue()
        self.ports.append((q))
        return q

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

    def replot_all(self, xp, plot_realtime=0, save=0):
        try:
            mode = xp["mode"]
            H = xp["MR"][:, 0]
            Mx = xp["MR"][:, 1]
            My = xp["MR"][:, 2]
            Mz = xp["MR"][:, 3]
            Rx = xp["MR"][:, 4]
            Ry = xp["MR"][:, 5]
            Rz = xp["MR"][:, 6]
            SD_freqs = xp["SD_freqs"]
            PIMM_delta_f = xp["PIMM_freqs"]
            if plot_realtime == 0:
                self.PIMM_plot.init_setup(Xmin=min(H),
                                          Xmax=max(H),
                                          Xsteps=len(H),
                                          dy=PIMM_delta_f)
                self.SD_plot.init_setup(Xmin=min(H),
                                        Xmax=max(H),
                                        Xsteps=len(H),
                                        dy=SD_freqs[1] - SD_freqs[0])
            self.mag_plot.Mx.plot(H, Mx, pen=(255, 0, 0))
            self.mag_plot.My.plot(H, My, pen=(0, 255, 0))
            self.mag_plot.Mz.plot(H, Mz, pen=(0, 0, 255))
            self.mag_plot.Mx.setYRange(-1.5, 1.5, padding=0)
            self.mag_plot.My.setYRange(-1.5, 1.5, padding=0)
            self.mag_plot.Mz.setYRange(-1.5, 1.5, padding=0)
            self.mag_plot.set_mode(mode)
            self.res_plot.Rx.plot(H, Rx, pen=(255, 0, 0))
            self.res_plot.Ry.plot(H, Ry, pen=(0, 255, 0))
            self.res_plot.Rz.plot(H, Rz, pen=(0, 0, 255))
            self.res_plot.set_mode(mode)

            self.SD_plot.update(xp["SD"],
                                SD_freqs[1] - SD_freqs[0],
                                H,
                                rm_bkg=1)
            self.SD_plot.set_mode(mode)

            self.PIMM_plot.update(xp["PIMM"], PIMM_delta_f, H)
            self.PIMM_plot.set_mode(mode)

            self.SD_lines.update(xp["SD"], SD_freqs[1] - SD_freqs[0], H)
            self.SD_lines.set_mode(mode)

            self.traj_plot.plt_traj(
                xp["traj"],
                [10 * len(H), 255 - 10 * len(H), 255 - 10 * len(H)])
            self.table_results.setData(xp["MR"].astype(np.str))
            if save == 1:
                fileName = self.save_file_dialog("")
                if fileName:
                    pd.DataFrame(
                        xp["SD"].T,
                        columns=np.array(H)).set_index(SD_freqs).to_csv(
                            fileName + "_SD.csv",
                            encoding='utf-8',
                            index=True,
                            sep='\t')
        except:
            pass

    def replot_results(self, plot_realtime=0, save=0):
        plot_realtime = 0
        self.clear_plots()
        n = self.simulation_manager.active_list
        if not n and plot_realtime == 0:
            self.replot_experimental()
            return 0
        elif plot_realtime == 1:
            return
        else:
            for n in self.simulation_manager.active_list:
                xp = self.simulation_manager.results_list_JSON["results"][n]
                self.widget_layer_params.table_layer_params.setData(
                    self.simulation_manager.results_list_JSON["layer_params"]
                    [n].to_numpy())
                self.widget_layer_params.table_layer_params.setHorizontalHeaderLabels(
                    self.simulation_manager.results_list_JSON["layer_params"]
                    [n].columns)
                self.widget_layer_params.table_stimulus_params.setData(
                    self.simulation_manager.
                    results_list_JSON["simulation_params"][n].to_numpy())
                self.widget_layer_params.table_stimulus_params.setHorizontalHeaderLabels(
                    self.simulation_manager.
                    results_list_JSON["simulation_params"][n].columns)
                self.replot_all(xp, save=save)
        self.replot_experimental()

    def update(self):
        for q in self.ports:
            try:
                prog, self.exp = q.get(block=False)
                self.central_layout.progress.setValue(prog)
                self.replot_results(plot_realtime=1)
            except Queue.Empty:
                pass

    def simple_update(self):
        try:
            self.replot_results(plot_realtime=1)
        except Queue.Empty:
            pass
