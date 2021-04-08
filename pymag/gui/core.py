import pyqtgraph as pg
from scipy.signal.spectral import check_COLA
from pymag.engine.utils import *
from pymag.gui.exporter import Exporter
from pymag.gui.simulation_manager import GeneralManager
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QCheckBox, QComboBox, QLabel
from pyqtgraph.Qt import QtGui

from functools import partial


class SimulationParameters():
    """
    Don't pass parent -- pass Layer & Stimulus
    """
    def __init__(self, parent, layerParameters, StimulusParameters):

        self.table_layer_params = pg.TableWidget(editable=True, sortable=False)
        header = self.table_layer_params.horizontalHeader()
        # also QtWidgets.QHeaderView.Stretch is good
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        self.table_stimulus_params = pg.TableWidget(editable=True,
                                                    sortable=False)
        stimulus_header = self.table_stimulus_params.horizontalHeader()
        stimulus_header.setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeToContents)
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
    def __init__(self, manager: GeneralManager, plot_manager):

        self.plot_manager = plot_manager
        self.manager = manager
        self.results_table = pg.TableWidget(editable=False, sortable=False)
        self.results_table.setColumnCount(1)
        header = self.results_table.horizontalHeader()
        # also QtWidgets.QHeaderView.Stretch is good
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.remove_btn = QtWidgets.QPushButton()
        self.remove_btn.setText("Remove selected result")
        self.remove_btn.clicked.connect(self.remove_layer)
        self.export_btn = QtWidgets.QPushButton()
        self.export_btn.setText("Export selected to .csv")
        self.export_btn.clicked.connect(self.export_selected)
        self.central_widget = QtGui.QWidget()
        self.central_layout = QtGui.QVBoxLayout()
        self.central_widget.setLayout(self.central_layout)
        self.central_layout.addWidget(self.results_table)
        self.central_layout.addWidget(self.remove_btn)
        self.central_layout.addWidget(self.export_btn)

    def remove_layer(self):
        self.manager.remove_selected()
        self.update()

    def export_selected(self):
        self.replot_results(self.active_highlighted, save=1)

    def update(self):
        self.print_and_color_table()
        results_to_plot = self.manager.get_selected_items()
        self.plot_manager.plot_active_results(results_to_plot)

    def item_checked(self, item: QtWidgets.QTableWidgetItem):
        row = item.row()
        # name was changed
        self.manager.items[row].name = item.text()
        if item.checkState() == QtCore.Qt.Checked:
            self.manager.add_to_selected(row)
            results_to_plot = self.manager.get_selected_items()
            self.plot_manager.plot_active_results(results_to_plot)
        else:
            self.manager.remove_from_selected(row)

    def print_and_color_table(self):
        active = self.manager.selected_indices
        names = self.manager.get_item_names()
        self.results_table.setRowCount(len(names))
        self.chkbox_list.clear()
        for i, sim_name in enumerate(names):
            chbx_itm = QtWidgets.QTableWidgetItem(sim_name)
            if i in active:
                chbx_itm.setCheckState(QtCore.Qt.Checked)
            else:
                chbx_itm.setCheckState(QtCore.Qt.Unchecked)
            # for some reason there's an attrubute error
            # we don't want to trigger on first add
            chbx_itm.itemChanged = lambda:...
            self.results_table.setItem(i, 0, chbx_itm)
            chbx_itm.itemChanged = partial(self.item_checked, chbx_itm)


class AddMenuBar():
    def __init__(self, parent: 'UIMainWindow'):
        """
        still to do: remove parent
        """
        self.parent: 'UIMainWindow' = parent
        self.menubar = QtWidgets.QMenuBar()
        self.window_about = About()
        self.window_menu = self.menubar.addMenu("Window")

        self.help_menu = self.menubar.addMenu("Help")
        self.help_menu.addAction("About").triggered.connect(self.about)

        self.simulation_name_label = QLabel("Simulation\nName:")
        self.simulation_name = QtWidgets.QLineEdit()

        self.start_btn = QtWidgets.QPushButton("Start")
        self.start_btn.setCheckable(True)
        self.start_btn.setStyleSheet("background-color : lightgreen")
        self.kill_fn = lambda:...  # empty function
        self.start_btn.clicked.connect(self.btn_toggle)

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

        self.btn_layout.addWidget(self.multiprocessing_label)
        self.btn_layout.addWidget(self.multiprocessing_select)
        self.btn_layout.addWidget(self.back_end_label)
        self.btn_layout.addWidget(self.backend_select)

        self.central_layout.addLayout(self.btn_layout)
        self.central_layout.addStretch()

    def set_exporter(self, exporter: 'Exporter'):
        self.exporter = exporter
        self.file_menu = self.menubar.addMenu("File")

        self.file_menu.addAction("Add experiment data").triggered.connect(
            self.exporter.load_experimental_data)
        self.file_menu.addAction("Save workspace").triggered.connect(
            self.exporter.save_workspace_binary)
        self.file_menu.addAction("Load workspace").triggered.connect(
            self.exporter.load_workspace_binary)
        self.file_menu.addAction(
            "Export active simulations to csv").triggered.connect(
                self.exporter.export_simulations_csv)
        self.file_menu.addSeparator()
        self.exit_btn = self.file_menu.addAction("Exit").triggered.connect(
            self.parent.end_program)

    def about(self):
        self.window_about.show()

    def btn_toggle(self):
        if self.start_btn.isChecked():
            if not len(self.parent.global_sim_manager.get_selected_items()):
                self.start_btn.toggle()
                return
            # refresh the clicked if there were sims before
            self.set_btn_simulation_position()
            # the simulation is running
            self.parent.start_simulations()
        else:
            # reconnect
            self.set_btn_start_position()

    def set_btn_simulation_position(self):
        self.start_btn.disconnect()
        self.start_btn.clicked.connect(self.btn_toggle)
        self.start_btn.setStyleSheet("background-color : red")
        self.start_btn.setText("Cancel")

    def set_btn_start_position(self):
        self.start_btn.setText("Start")
        self.start_btn.setStyleSheet("background-color : lightgreen")


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
