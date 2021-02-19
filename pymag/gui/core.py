import pyqtgraph as pg
from pymag.engine.utils import *
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QCheckBox, QComboBox, QLabel
from pyqtgraph.Qt import QtCore, QtGui

ResultsColumns = ['H', 'Mx', 'My', 'Mz', 'Rx', 'Ry', 'Rz']


class LayerTableStimulus():
    def __init__(self, parent):
        layerParameters = parent.layerParameters
        StimulusParameters = parent.StimulusParameters
        self.table_layer_params = pg.TableWidget(editable=True, sortable=False)
        self.table_stimulus_params = pg.TableWidget(editable=True,
                                                    sortable=False)
        self.generate_stimulus_btn = QtWidgets.QPushButton()
        self.add_btn = QtWidgets.QPushButton()
        self.remove_button = QtWidgets.QPushButton()
        self.LoadButton = QtWidgets.QPushButton()
        self.SaveButton = QtWidgets.QPushButton()
        self.add_simulation = QtWidgets.QPushButton()
        self.generate_stimulus_btn.setText("Set stimulus \nfor all")
        self.generate_stimulus_btn.clicked.connect(parent.set_stimulus_for_all)
        self.add_btn.setText("Add new \nlayer")
        self.add_btn.clicked.connect(self.add_layer)
        self.remove_button.setText("Remove selected\n row")
        self.remove_button.clicked.connect(self.remove_layer)
        self.LoadButton.setText("Load params \nfrom file")
        self.LoadButton.clicked.connect(parent.load_param_table)
        self.SaveButton.setText("Save params \nto file")
        self.SaveButton.clicked.connect(parent.save_params)
        self.add_simulation.setText("Add to \nsimulation list")
        self.add_simulation.clicked.connect(parent.add_to_simulation_list)
        self.table_layer_params.setData(layerParameters.to_numpy())
        self.table_layer_params.setHorizontalHeaderLabels(
            layerParameters.columns)
        self.table_stimulus_params.setData(StimulusParameters.to_numpy())
        self.table_stimulus_params.setHorizontalHeaderLabels(
            StimulusParameters.columns)
        self.central_widget = QtGui.QWidget()
        self.central_layout = QtGui.QVBoxLayout()
        self.central_widget.setLayout(self.central_layout)
        self.central_layout.addWidget(self.table_layer_params)
        self.btn_layout = QtGui.QHBoxLayout()
        self.btn_layout.addWidget(self.generate_stimulus_btn)
        self.btn_layout.addWidget(self.add_btn)
        self.btn_layout.addWidget(self.remove_button)
        self.btn_layout.addWidget(self.LoadButton)
        self.btn_layout.addWidget(self.SaveButton)
        self.btn_layout.addWidget(self.add_simulation)
        self.central_layout.addWidget(self.table_stimulus_params)
        self.central_layout.addLayout(self.btn_layout)

    def add_layer(self):
        self.table_layer_params.addRow([
            1, 1.6, 3000, "[1 0 0]", -1e-5, 0.01, 1e-9, "[0 1 0]", 0.02, 0.01,
            0.01, 100, 120, 1
        ])

    def remove_layer(self):
        self.table_layer_params.removeRow(self.table_layer_params.currentRow())


class LayerStructure():
    def __init__(self, sim_num, parent):
        self.plotter = parent
        for val in [
                "Ms", "Ku", "J", "th", "alpha", "AMR", "SMR", "Rx0", "Ry0",
                "w", "l"
        ]:
            setattr(
                self, val,
                np.asarray(
                    self.plotter.simulation_manager.
                    simulations_list["layer_params"][sim_num][val].values,
                    dtype=np.float32))
        self.Kdir = self.get_kdir(
            self.plotter.simulation_manager.simulations_list["layer_params"]
            [sim_num]["Kdir"].values)
        self.Ndemag2 = self.get_Ndemag(
            self.plotter.simulation_manager.simulations_list["layer_params"]
            [sim_num]["N"].values)
        self.number_of_layers = len(self.Ms)

    def get_kdir(self, value):
        listOfParams = []
        for n in range(0, len(value)):
            tmp = value[n]
            tmp = tmp.replace("[", "").replace("]", "")
            v_tmp = (tmp.split(" "))
            res = np.array(list(map(float, v_tmp)))
            res = normalize(res)
            listOfParams.append(res)
        return listOfParams

    def get_Ndemag(self, value):
        tmp = self.plotter.widget_layer_params.table_layer_params.item(
            0, 7).text()
        tmp = tmp.replace("[", "").replace("]", "")
        v_tmp = (tmp.split(" "))
        res = np.array(list(map(float, v_tmp)))
        N = np.array([[res[0], 0, 0], [0, res[1], 0], [0, 0, res[2]]])
        return N


class SimulationStimulus():
    def __init__(self, sim_num, parent):
        data = parent.simulation_manager.results_list_JSON[
            "simulation_params"][sim_num]

        # self.theta = np.array(data["HTheta"].values[0], dtype=np.float32)
        self.back = np.array(data["Hback"].values[0], dtype=np.int)
        # self.phi = np.array(data["HPhi"].values[0], dtype=np.float32)

        if data["H"].values[1] != "-" and data["HPhi"].values[
                1] == "-" and data["HTheta"].values[1] == "-":
            self.mode = "H"
            self.STEPS = np.array(data["H"].values[1], dtype=np.float32)
            self.Hmin = np.array(data["H"].values[0], dtype=np.float32)
            self.Hmax = np.array(data["H"].values[2], dtype=np.float32)
            self.ThetaMin = np.array(data["HTheta"].values[0],
                                     dtype=np.float32)
            self.ThetaMax = np.array(data["HTheta"].values[0],
                                     dtype=np.float32)
            self.PhiMin = np.array(data["HPhi"].values[0], dtype=np.float32)
            self.PhiMax = np.array(data["HPhi"].values[0], dtype=np.float32)

        elif data["HPhi"].values[1] != "-" and data["H"].values[
                1] == "-" and data["HTheta"].values[1] == "-":
            self.mode = "phi"
            self.STEPS = np.array(data["HPhi"].values[1], dtype=np.float32)
            self.Hmin = np.array(data["H"].values[0], dtype=np.float32)
            self.Hmax = np.array(data["H"].values[0], dtype=np.float32)
            self.ThetaMin = np.array(data["HTheta"].values[0],
                                     dtype=np.float32)
            self.ThetaMax = np.array(data["HTheta"].values[0],
                                     dtype=np.float32)
            self.PhiMin = np.array(data["HPhi"].values[0], dtype=np.float32)
            self.PhiMax = np.array(data["HPhi"].values[2], dtype=np.float32)
        elif data["HTheta"].values[1] != "-" and data["H"].values[
                1] == "-" and data["HPhi"].values[1] == "-":
            self.mode = "theta"
            self.STEPS = np.array(data["HTheta"].values[1], dtype=np.float32)
            self.Hmin = np.array(data["H"].values[0], dtype=np.float32)
            self.Hmax = np.array(data["H"].values[0], dtype=np.float32)
            self.ThetaMin = np.array(data["HTheta"].values[0],
                                     dtype=np.float32)
            self.ThetaMax = np.array(data["HTheta"].values[2],
                                     dtype=np.float32)
            self.PhiMin = np.array(data["HPhi"].values[0], dtype=np.float32)
            self.PhiMax = np.array(data["HPhi"].values[0], dtype=np.float32)
        else:
            print("Stimulus error")
        self.H_sweep, self.Hmag = get_stimulus2(self.Hmin, self.Hmax,
                                                self.ThetaMin, self.ThetaMax,
                                                self.PhiMin, self.PhiMax,
                                                self.STEPS, self.back,
                                                self.mode)
        self.fmin = np.array(data["f"].values[0], dtype=np.float32)
        self.fsteps = np.array(data["f"].values[1], dtype=np.int)
        self.fmax = np.array(data["f"].values[2], dtype=np.float32)
        self.LLGtime = np.array(data["LLGtime"].values[0], dtype=np.float32)
        self.LLGsteps = int(
            np.array(data["LLGsteps"].values[0], dtype=np.float32))
        self.freqs = np.linspace(self.fmin, self.fmax, self.fsteps)
        self.spectrum_len = (self.LLGsteps) // 2
        self.PIMM_delta_f = 1 / self.LLGtime
        self.fphase = np.array(data["fphase"].values[0], dtype=np.float32)


class SimulationResults():
    def __init__(self, Stimulus, SpinDevice):
        self.H = []
        self.Rx = []
        self.Ry = []
        self.Rz = []
        self.Hmag_out = []
        self.Mlayers = np.empty((0, SpinDevice.number_of_layers, 3), float)
        self.M_avg = np.empty((0, 3), float)
        self.R_net = np.empty((0, 3), float)
        self.Spectrogram_data = np.empty((0, Stimulus.spectrum_len), float)
        self.Spectrogram_VSD = np.empty((0, len(Stimulus.freqs)), float)


class ResultsTable():
    def __init__(self, parent):
        self.plotter = parent
        self.active_highlighted = None
        self.active_list = []
        self.results_table = pg.TableWidget(editable=False, sortable=False)
        self.results_list_JSON = {
            "results": [],
            "settings": [],
            "layer_params": [],
            "simulation_params": []
        }
        self.remove_btn = QtWidgets.QPushButton()
        self.remove_btn.setText("Remove selected result")
        self.remove_btn.clicked.connect(self.remove_layer)
        self.remove_btn.setEnabled(False)
        self.export_btn = QtWidgets.QPushButton()
        self.export_btn.setText("Export selected to .csv")
        self.export_btn.clicked.connect(self.export_selected)
        self.export_btn.setEnabled(False)
        self.central_widget = QtGui.QWidget()
        self.central_layout = QtGui.QGridLayout()
        self.central_widget.setLayout(self.central_layout)
        self.central_layout.addWidget(self.results_table)
        self.central_layout.addWidget(self.remove_btn)
        self.central_layout.addWidget(self.export_btn)
        self.results_table.cellDoubleClicked.connect(self.clicked2x)

    def remove_layer(self):
        for n in self.active_list:
            self.results_list_JSON["settings"].pop(n)
            self.results_list_JSON["results"].pop(n)
            self.results_list_JSON["layer_params"].pop(n)
            self.results_list_JSON["simulation_params"].pop(n)
            self.results_table.setData(self.results_list_JSON["settings"])
        self.active_list = []
        self.plotter.replot_results()
        self.print_and_color_table()

    def export_selected(self):
        self.plotter.replot_results(self.active_highlighted, save=1)

    def clicked2x(self, parent):
        n = self.results_table.currentRow()
        m = int(self.results_table.rowCount())
        if n in self.active_list:
            self.active_list.remove(n)
        else:
            self.active_list.append(n)
        if not self.active_list:
            self.remove_btn.setEnabled(False)
            self.export_btn.setEnabled(False)
        else:
            self.remove_btn.setEnabled(True)
            self.export_btn.setEnabled(True)

        for i in range(0, m):
            if i in self.active_list:
                self.results_list_JSON["settings"][i][0] = "V"
            else:
                self.results_list_JSON["settings"][i][0] = "X"
        self.print_and_color_table()
        self.plotter.replot_results()

    def print_and_color_table(self):
        m = int(self.results_table.rowCount())
        self.results_table.setData(self.results_list_JSON["settings"])
        self.results_table.setHorizontalHeaderLabels(
            ["Select", "Type", "Timestamp"])
        for i in range(0, m):
            if i in self.active_list:
                self.results_table.item(i, 0).setBackground(
                    QtGui.QColor(255, 0, 0))  ##dosnt work!
            else:
                self.results_table.item(i, 0).setBackground(
                    QtGui.QColor(255, 255, 255))


class paramsAndStimulus():
    def __init__(self, parent):
        layerParameters = parent.layerParameters
        StimulusParameters = parent.StimulusParameters
        self.table_layer_params = pg.TableWidget(editable=True, sortable=False)
        self.table_stimulus_params = pg.TableWidget(editable=True,
                                                    sortable=False)
        self.GenerateStimulus = QtWidgets.QPushButton()
        self.AddButton = QtWidgets.QPushButton()
        self.RemoveButton = QtWidgets.QPushButton()
        self.LoadButton = QtWidgets.QPushButton()
        self.SaveButton = QtWidgets.QPushButton()
        self.AddSimulationButton = QtWidgets.QPushButton()
        self.GenerateStimulus.setText("Set stimulus \nfor all")
        self.GenerateStimulus.clicked.connect(parent.setStimulusForALl)
        self.AddButton.setText("Add new \nlayer")
        self.AddButton.clicked.connect(self.addLayer)
        self.RemoveButton.setText("Remove selected\n row")
        self.RemoveButton.clicked.connect(self.removeLayer)
        self.LoadButton.setText("Load params \nfrom file")
        self.LoadButton.clicked.connect(parent.loadParams)
        self.SaveButton.setText("Save params \nto file")
        self.SaveButton.clicked.connect(parent.saveParams)
        self.AddSimulationButton.setText("Add to \nsimulation list")
        self.AddSimulationButton.clicked.connect(parent.addToSimulationList)
        self.table_layer_params.setData(layerParameters.to_numpy())
        self.table_layer_params.setHorizontalHeaderLabels(
            layerParameters.columns)
        self.table_stimulus_params.setData(StimulusParameters.to_numpy())
        self.table_stimulus_params.setHorizontalHeaderLabels(
            StimulusParameters.columns)
        self.ctrlWidget = QtGui.QWidget()
        self.ctrLayout = QtGui.QVBoxLayout()
        self.ctrlWidget.setLayout(self.ctrLayout)
        self.ctrLayout.addWidget(self.table_layer_params)
        self.btn_layout = QtGui.QHBoxLayout()
        self.btn_layout.addWidget(self.GenerateStimulus)
        self.btn_layout.addWidget(self.AddButton)
        self.btn_layout.addWidget(self.RemoveButton)
        self.btn_layout.addWidget(self.LoadButton)
        self.btn_layout.addWidget(self.SaveButton)
        self.btn_layout.addWidget(self.AddSimulationButton)
        self.ctrLayout.addWidget(self.table_stimulus_params)
        self.ctrLayout.addLayout(self.btn_layout)

    def addLayer(self):
        self.table_layer_params.addRow([
            1, 1.6, 3000, "[1 0 0]", -1e-5, 0.01, 1e-9, "[0 1 0]", 0.02, 0.01,
            0.01, 100, 120, 1
        ])

    def removeLayer(self):
        self.table_layer_params.removeRow(self.table_layer_params.currentRow())


class AddMenuBar():
    def __init__(self, parent):
        self.menubar = QtWidgets.QMenuBar()
        self.file_menu = self.menubar.addMenu("File")

        self.file_menu.addAction("Save layer params").triggered.connect(
            parent.save_params)
        self.file_menu.addAction("Load layer params").triggered.connect(
            parent.load_param_table)
        self.file_menu.addAction(
            "Load multiple layer params").triggered.connect(
                parent.load_multiple)
        self.file_menu.addSeparator()
        self.file_menu.addAction("Open results from csv").triggered.connect(
            parent.load_results)
        self.file_menu.addAction("Save results as csv").triggered.connect(
            parent.save_results)

        self.file_menu.addAction("Save all to binary file").triggered.connect(
            parent.save_binary)
        self.file_menu.addAction(
            "Load all from binary file").triggered.connect(parent.load_binary)
        self.file_menu.addSeparator()
        self.exit_btn = self.file_menu.addAction("Exit").triggered.connect(
            parent.end_program)

        self.window_menu = self.menubar.addMenu("Window")
        self.window_menu.addAction(
            "Switch full/normal screen").triggered.connect(parent.full_screen)
        self.window_menu.addAction("Save dock state").triggered.connect(
            parent.save_dock_state)
        self.window_menu.addAction("Load dock state").triggered.connect(
            parent.load_dock_state)
        self.help_menu = self.menubar.addMenu("Help")
        self.help_menu.addAction("About").triggered.connect(parent.about)

        self.simulation_name_label = QLabel("Simulation\nName:")
        self.simulation_name = QtWidgets.QLineEdit()

        self.start_btn = QtWidgets.QPushButton()
        self.stop_btn = QtWidgets.QPushButton()
        self.start_btn.setText("Start")
        self.stop_btn.setText("Stop")
        self.stop_btn.setText("Stop")
        self.start_btn.clicked.connect(parent.btn_clk)
        self.stop_btn.clicked.connect(parent.stop_clk)

        self.multiprocessing_label = QLabel("MP")
        self.backend_select = QComboBox()

        self.backend_select.addItem("C++")
        self.backend_select.addItem("Docker")
        self.backend_select.addItem("Python")
        self.back_end_label = QLabel("Backend:")

        self.multiprocessing_select = QCheckBox()
        self.multiprocessing_select.setObjectName("Multiprocessing")
        self.multiprocessing_select.setChecked(True)

        self.progress = QtWidgets.QProgressBar()
        self.progress.setGeometry(0, 0, 300, 25)
        self.progress.setMaximum(100)

        self.central_widget = QtGui.QWidget()
        self.central_layout = QtGui.QVBoxLayout()
        self.central_widget.setLayout(self.central_layout)
        self.central_layout.addWidget(self.menubar)
        self.central_layout.addWidget(self.progress)

        self.btn_layout = QtGui.QHBoxLayout()
        self.btn_layout.addWidget(self.start_btn)
        self.btn_layout.addWidget(self.simulation_name_label)
        self.btn_layout.addWidget(self.simulation_name)

        self.btn_layout.addWidget(self.stop_btn)
        # self.btn_layout.addWidget(self.clear_plotsButton)
        self.btn_layout.addWidget(self.multiprocessing_label)
        self.btn_layout.addWidget(self.multiprocessing_select)
        self.btn_layout.addWidget(self.back_end_label)
        self.btn_layout.addWidget(self.backend_select)

        self.central_layout.addLayout(self.btn_layout)


class About(QtGui.QDialog):
    def __init__(self, parent):
        super(About, self).__init__()
        self.setWindowTitle(PyMagVersion + " - About")
        self.setFixedSize(200, 100)
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.about_label = QtWidgets.QLabel(PyMagVersion + "\n" + PyMagDate)
        self.layout.addWidget(self.about_label)
        self.close()


class LabeledDoubleSpinBox():
    def __init__(self,
                 label="Label",
                 minimum=0,
                 maximum=1,
                 value=0,
                 mode='Double'):
        self.Label = QLabel(label)
        if mode == 'Double':
            self.Value = QtWidgets.QDoubleSpinBox()
            self.Value.setMinimum(minimum)
            self.Value.setMaximum(maximum)
            self.Value.setValue(value)
            self.Value.setObjectName(label)
        elif mode == 'Integer':
            self.Value = QtWidgets.QSpinBox()
            self.Value.setMinimum(minimum)
            self.Value.setMaximum(maximum)
            self.Value.setValue(value)
            self.Value.setObjectName(label)

        if mode == 'Binary':
            self.Value = QtWidgets.QCheckBox()
            self.Value.setObjectName(label)
            self.Value.setChecked(value)


class Settings(QtGui.QDialog):
    signal = QtCore.pyqtSignal(float, float, int, bool, float, float)

    def __init__(self, parent):
        super(Settings, self).__init__()
        self.setWindowTitle(PyMagVersion + " - Settings")

        self.setFixedSize(650, 400)
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.MHCheckBox = QtWidgets.QCheckBox()
        self.MHCheckLabel = QtWidgets.QLabel("M(H)")
        self.RHCheckBox = QtWidgets.QCheckBox()
        self.RHCheckLabel = QtWidgets.QLabel("R(H)")
        self.SDCheckBox = QtWidgets.QCheckBox()
        self.SDCheckBox.setChecked(True)
        self.SDCheckLabel = QtWidgets.QLabel("SD(H,f)")
        self.STOCheckBox = QtWidgets.QCheckBox()

        self.STOCheckLabel = QtWidgets.QLabel("STO(H,f)")

        self.CheckBoxLayout = QtWidgets.QHBoxLayout()
        self.CheckBoxLayout.addWidget(self.MHCheckLabel)
        self.CheckBoxLayout.addWidget(self.MHCheckBox)
        self.CheckBoxLayout.addWidget(self.RHCheckLabel)
        self.CheckBoxLayout.addWidget(self.RHCheckBox)
        self.CheckBoxLayout.addWidget(self.SDCheckLabel)
        self.CheckBoxLayout.addWidget(self.SDCheckBox)
        self.CheckBoxLayout.addWidget(self.STOCheckLabel)
        self.CheckBoxLayout.addWidget(self.STOCheckBox)
        self.layout.addLayout(self.CheckBoxLayout)

        self.close()
