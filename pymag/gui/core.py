from pymag.gui.exporter import Exporter
import pyqtgraph as pg
from pymag.engine.utils import *
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QCheckBox, QComboBox, QLabel
from pyqtgraph.Qt import QtGui

# ResultsColumns = ['H', 'Mx', 'My', 'Mz', 'Rx', 'Ry', 'Rz']


class SimulationParameters():
    """
    Don't pass parent -- pass Layer & Stimulus
    """
    def __init__(self, parent, layerParameters, StimulusParameters):

        self.table_layer_params = pg.TableWidget(editable=True, sortable=False)
        self.table_stimulus_params = pg.TableWidget(editable=True,
                                                    sortable=False)
        self.add_btn = QtWidgets.QPushButton()
        self.remove_button = QtWidgets.QPushButton()
        self.add_simulation = QtWidgets.QPushButton()

        self.add_btn.setText("Add new \nlayer")
        self.add_btn.clicked.connect(self.add_layer)
        self.remove_button.setText("Remove selected\n layer")
        self.remove_button.clicked.connect(self.remove_layer)
        self.add_simulation.setText("Add to \nsimulation list")
        self.add_simulation.clicked.connect(
            parent.add_to_simulation_list
        )  #zastanawiam się jak zrobić to najbardziej elegancko

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
    def __init__(self, global_sim_manager, plot_manager):

        self.plot_manager = plot_manager
        self.global_sim_manager = global_sim_manager
        self.results_table = pg.TableWidget(editable=False, sortable=False)
        self.remove_btn = QtWidgets.QPushButton()
        self.remove_btn.setText("Remove selected result")
        self.remove_btn.clicked.connect(self.remove_layer)
        self.export_btn = QtWidgets.QPushButton()
        self.export_btn.setText("Export selected to .csv")
        self.export_btn.clicked.connect(self.export_selected)
        self.central_widget = QtGui.QWidget()
        self.central_layout = QtGui.QGridLayout()
        self.central_widget.setLayout(self.central_layout)
        self.central_layout.addWidget(self.results_table)
        self.central_layout.addWidget(self.remove_btn)
        self.central_layout.addWidget(self.export_btn)
        self.results_table.cellDoubleClicked.connect(self.clicked2x)

    def remove_layer(self):
        self.global_sim_manager.remove_selected()
        self.update()

    def export_selected(self):
        self.replot_results(self.active_highlighted, save=1)

    def clicked2x(self, row_number: int, column_number: int):
        self.global_sim_manager.swap_simulation_status(row_number)
        self.update()

    def update(self):
        results_to_plot = self.global_sim_manager.get_selected_simulations()
        self.plot_manager.plot_active_results(results_to_plot)
        self.print_and_color_table()

    def print_and_color_table(self):
        active = self.global_sim_manager.selected_simulation_indices
        num_of_sim = len(self.global_sim_manager.simulations)
        self.results_table.setData(
            self.global_sim_manager.get_simulation_names())

        for i in range(0, num_of_sim):
            if i in active:
                self.results_table.item(i, 0).setBackground(
                    QtGui.QColor(255, 0, 0))
            else:
                self.results_table.item(i, 0).setBackground(
                    QtGui.QColor(255, 255, 255))


class AddMenuBar():
    def __init__(self, parent: 'UIMainWindow'):
        """
        still to do: remove parent
        """
        self.parent = parent
        self.menubar = QtWidgets.QMenuBar()
        self.window_about = About()
        self.window_menu = self.menubar.addMenu("Window")
        self.window_menu.addAction(
            "Switch full/normal screen").triggered.connect(self.full_screen)

        self.help_menu = self.menubar.addMenu("Help")
        self.help_menu.addAction("About").triggered.connect(self.about)

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

    def set_exporter(self, exporter: 'Exporter'):
        self.exporter = exporter
        self.file_menu = self.menubar.addMenu("File")

        self.file_menu.addAction("Save workspace").triggered.connect(
            self.exporter.export_workspace_binary)
        self.file_menu.addAction("Load workspace").triggered.connect(
            self.exporter.load_workspace_binary)
        self.file_menu.addSeparator()
        self.exit_btn = self.file_menu.addAction("Exit").triggered.connect(
            self.parent.end_program)

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


class About(QtGui.QDialog):
    def __init__(self):
        super(About, self).__init__()
        self.setWindowTitle("About pyMag")
        self.setFixedSize(300, 300)
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.about_label = QtWidgets.QLabel(
            "Used open source libaries: pyQT5, pyGtGraph ...\n Authors: SZ,JM,WS\n To cite: \narxiv,\ngit:"
        )
        self.layout.addWidget(self.about_label)
        self.close()
