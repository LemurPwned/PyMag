import pyqtgraph as pg
from pymag.engine.utils import *
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QCheckBox, QComboBox, QLabel
from pyqtgraph.Qt import QtGui

ResultsColumns = ['H', 'Mx', 'My', 'Mz', 'Rx', 'Ry', 'Rz']


class LayerTableStimulus():
    """
    Don't pass parent -- pass Layer & Stimulus
    """
    def __init__(self, parent):
        layerParameters = parent.layerParameters
        StimulusParameters = parent.StimulusParameters
        self.table_layer_params = pg.TableWidget(editable=True, sortable=False)
        self.table_stimulus_params = pg.TableWidget(editable=True,
                                                    sortable=False)
        self.add_btn = QtWidgets.QPushButton()
        self.remove_button = QtWidgets.QPushButton()
        self.load_button = QtWidgets.QPushButton()
        self.save_button = QtWidgets.QPushButton()
        self.add_simulation = QtWidgets.QPushButton()

        self.add_btn.setText("Add new \nlayer")
        self.add_btn.clicked.connect(self.add_layer)
        self.remove_button.setText("Remove selected\n row")
        self.remove_button.clicked.connect(self.remove_layer)
        self.load_button.setText("Load params \nfrom file")
        self.load_button.clicked.connect(parent.load_param_table)
        self.save_button.setText("Save params \nto file")
        self.save_button.clicked.connect(parent.save_params)
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
        self.btn_layout.addWidget(self.add_btn)
        self.btn_layout.addWidget(self.remove_button)
        self.btn_layout.addWidget(self.load_button)
        self.btn_layout.addWidget(self.save_button)
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


class ResultsTable():
    """
    To be changed & renamed -- must use Simulation Manager
    """
    def __init__(self, parent):
        self.main_window = parent
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
        self.main_window.global_sim_manager.remove_selected()
        for n in self.active_list:
            self.results_list_JSON["settings"].pop(n)
            self.results_list_JSON["results"].pop(n)
            self.results_list_JSON["layer_params"].pop(n)
            self.results_list_JSON["simulation_params"].pop(n)
            self.results_table.setData(self.results_list_JSON["settings"])
        self.active_list = []
        self.main_window.replot_results()
        self.print_and_color_table()

    def export_selected(self):
        self.main_window.replot_results(self.active_highlighted, save=1)

    def clicked2x(self, row_number: int, column_number: int):
        # self.main_window.global_sim_manager.swap_simulation_status(row_number)
        print("Index number", row_number)
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
        self.main_window.replot_results()

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
        self.start_btn.clicked.connect(parent.start_simulations)
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
