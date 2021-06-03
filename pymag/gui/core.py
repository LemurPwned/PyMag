from functools import partial
from typing import ClassVar, List, Tuple, Union

import pandas as pd
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pymag.engine.utils import *
from pymag.gui.exporter import Exporter
from pymag.gui.plot_manager import PlotManager
from pymag.gui.simulation_manager import (ExperimentManager, GeneralManager,
                                          Simulation)
from pymag.gui.utils import LabelledDoubleSpinBox, unicode_subs, inverse_subs
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QComboBox, QDoubleSpinBox, QLabel

from PyQt5.QtGui import QIcon, QPixmap


        # H_unit = "kA/m"
        # angle_unit = "deg"
        # f_unit = "GHz"
        # I_unit = "uA"
        # V_unit = "V"
        # time_unit = "ns"


class Labeled():
    def __init__(self,
                 label="Label",
                 minimum=0,
                 maximum=1,
                 value=0,
                 mode='Double',
                 item_list = ["1", "2", "3"]):
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
        if mode == 'Combo':
            self.Value = QtWidgets.QComboBox()
            self.Value.setObjectName(label)
            for i in range(0, len(item_list)):
                self.Value.addItem(item_list[i])
            





class StimulusGUI():
    def __init__(self) -> None:
        
        theta_min = 0
        theta_max = 180
        phi_min = 0
        phi_max = 360
        H_min = -1e6
        H_max = 1e6
        f_min = 0
        f_max = 1e3
        f_step_min = 1
        f_step_max = 1e3
        I_dc_min = 0
        I_dc_max = 1000
        I_RF_min = 0
        I_RF_max = 1000
        steps_min = 1
        steps_max = 1e6
        LLG_time_min = 0.1
        LLG_steps_min = 10
        LLG_time_max = 1e6
        LLG_steps_max = 1e6

        H_unit = "kA/m"
        angle_unit = "deg"
        f_unit = "GHz"
        I_unit = "uA"
        V_unit = "V"
        time_unit = "ns"

        self.Idc = Labeled(label="I DC",
                                          minimum=I_dc_min,
                                          maximum=I_dc_max,
                                          value=0.01)
        self.Iac = Labeled(label="I AC",
                                          minimum=I_dc_min,
                                          maximum=I_dc_max,
                                          value=0.01)

        self.LLGtime = Labeled(label="LLG time",
                                          minimum=LLG_time_min,
                                          maximum=LLG_time_max,
                                          value=10)
        self.LLGsteps = Labeled(label="LLG steps",
                                          minimum=f_step_min,
                                          maximum=f_step_max,
                                          value=10,
                                            mode='Integer')
        self.fmin = Labeled(label="f AC",
                                          minimum=f_min,
                                          maximum=f_max,
                                          value=0)
        self.fsteps = Labeled(label="f AC steps",
                                          minimum=LLG_steps_min,
                                          maximum=LLG_steps_max,
                                          value=10,
                                          mode='Integer')
        self.fmax = Labeled(label="fmax AC steps",
                                          minimum=f_min,
                                          maximum=f_max,
                                          value=20)

        self.HMin = Labeled(label="H",
                                          minimum=H_min,
                                          maximum=H_max,
                                          value=-1e3)
        self.HMax = Labeled(label="-",
                                          minimum=H_min,
                                          maximum=H_max,
                                          value=1e3)
        self.HSteps = Labeled(label="Steps",
                                            minimum=steps_min,
                                            maximum=steps_max,
                                            value=50,
                                            mode='Integer')
        self.HThetaSteps = Labeled(label="Steps",
                                            minimum=0,
                                            maximum=1e6,
                                            value=50)
        self.HPhiSteps = Labeled(label="Steps",
                                            minimum=0,
                                            maximum=1e6,
                                            value=50)
        self.HBack = Labeled(label="Back",
                                           value=False,
                                           mode='Binary')
        self.HPhiBack = Labeled(label="Back",
                                           value=False,
                                           mode='Binary')
        self.HThetaBack = Labeled(label="Back",
                                           value=False,
                                           mode='Binary')
        self.HThetaMin = Labeled(
            label="Theta",
            minimum=-360,
            maximum=360,
            value=89)
        self.HThetaMax = Labeled(
            label="Phi",
            minimum=-360,
            maximum=360,
            value=89)

        self.HPhiMin = Labeled(label="Phi",
                                          minimum=-360,
                                          maximum=360,
                                          value=1)
        self.HPhiMax = Labeled(label="Phi",
                                          minimum=-360,
                                          maximum=360,
                                          value=1)
        self.HMode = Labeled(label="Field sweep mode",mode="Combo", item_list=["H","Phi","Theta"])
        self.Idir = Labeled(label="I source",mode="Combo", item_list=["x","y","z"])
        self.Vdir = Labeled(label="Voltmeter",mode="Combo", item_list=["x","y","z"])
        self.stimulus_layout = QtGui.QGridLayout()
        self.LLGError_threshold = Labeled(label="Max dm error",
                                          minimum=-360,
                                          maximum=360,
                                          value=0.0)


        self.stimulus_objests = [[QLabel(" "),self.HMode.Label, self.HMode.Value],
                            [QLabel(" "),     QLabel("Start"),      QLabel("Steps"),        QLabel("Stop"),       QLabel("Back")],
                            [self.HMin.Label,      self.HMin.Value,      self.HSteps.Value,      self.HMax.Value,      self.HBack.Value],
                            [self.HPhiMin.Label,   self.HPhiMin.Value,   self.HPhiSteps.Value,   self.HPhiMax.Value,   self.HPhiBack.Value],
                            [self.HThetaMin.Label, self.HThetaMin.Value, self.HThetaSteps.Value, self.HThetaMax.Value, self.HThetaBack.Value],
                            [QLabel(" "), QLabel("Electrical")],
                            [self.fmin.Label, self.fmin.Value, self.fsteps.Value, self.fmax.Value],
                            [self.Idir.Label, self.Idir.Value],
                            [self.Vdir.Label, self.Vdir.Value],
                            [self.Idc.Label,self.Idc.Value],
                            [self.Iac.Label,self.Iac.Value],
                            [QLabel(" "), QLabel("Simulation\nparameters")],
                            [self.LLGtime.Label,self.LLGtime.Value],
                            [self.LLGsteps.Label,self.LLGsteps.Value],
                            [self.LLGError_threshold.Label,self.LLGError_threshold.Value]]

        self.HMode.Value.currentIndexChanged.connect(self.H_mode_changed)


        setup_circuit = QLabel()
        setup_circuit.setPixmap(QPixmap('./pymag/presets/image1.png'))
        setup_circuit.resize(80,80)
        for i in range(0,len(self.stimulus_objests[:])):
            for j in range(0,len(self.stimulus_objests[i])):
                self.stimulus_layout.addWidget(self.stimulus_objests[i][j], i, j)
        self.stimulus_layout.addWidget(setup_circuit, 7,2,8,3)


        self.H_mode_changed()
        self.get_stimulus_data()


    def get_stimulus_data(self):

        mode = self.HMode.Value.currentText()
        if mode == "H":
            tmp_H = {'H': [self.HMin.Value.value(), self.HSteps.Value.value(), self.HMax.Value.value()], 
                    'Hback': [self.HBack.Value.checkState(), "-", "-"],
                    'HTheta': [self.HThetaMin.Value.value(), "-", "-"],
                    'HPhi': [self.HPhiMin.Value.value(), "-", "-"]}
        if mode == "Phi":
            tmp_H = {'H': [self.HMin.Value.value(), "-", "-"], 
                    'Hback': [self.HPhiBack.Value.checkState(), "-", "-"],
                    'HTheta': [self.HThetaMin.Value.value(), "-", "-"],
                    'HPhi': [self.HPhiMin.Value.value(), self.HPhiSteps.Value.value(), self.HPhiMax.Value.value()]}
        if mode == "Theta":
            tmp_H = {'H': [self.HMin.Value.value(), "-", "-"], 
                    'Hback': [self.HThetaBack.Value.checkState(), "-", "-"],
                    'HTheta': [self.HThetaMin.Value.value(), self.HThetaSteps.Value.value(), self.HThetaMax.Value.value()],
                    'HPhi': [self.HPhiMin.Value.value(), "-", "-"]}

        tmp = {'f': [self.fmin.Value.value()*1e9, self.fsteps.Value.value(), self.fmax.Value.value()*1e9], 
                "IAC": [self.Iac.Value.value(), "-", "-"],
                "IDC": [self.Idc.Value.value(), "-", "-"],
                "Idir": ["1 0 0", "-", "-"],
                "Vdir": ["1 0 0", "-", "-"],
                "LLGtime": [self.LLGtime.Value.value()/1e9, "-", "-",],
                "LLGsteps": [self.LLGsteps.Value.value(), "-", "-",]}

        df = pd.concat([pd.DataFrame(tmp_H), pd.DataFrame(tmp)], axis=1)

        return df

    def H_mode_changed(self):

        mode = self.HMode.Value.currentText()

        if mode == "H":

            self.HMax.Value.setEnabled(True)
            self.HSteps.Value.setEnabled(True)
            self.HBack.Value.setEnabled(True)

            self.HPhiSteps.Value.setEnabled(False)
            self.HPhiMax.Value.setEnabled(False)
            self.HPhiBack.Value.setEnabled(False)

            self.HThetaSteps.Value.setEnabled(False)
            self.HThetaMax.Value.setEnabled(False)
            self.HThetaBack.Value.setEnabled(False)

        if mode == "Phi":
            self.HMax.Value.setEnabled(False)
            self.HSteps.Value.setEnabled(False)
            self.HBack.Value.setEnabled(False)

            self.HPhiSteps.Value.setEnabled(True)
            self.HPhiMax.Value.setEnabled(True)
            self.HPhiBack.Value.setEnabled(True)

            self.HThetaSteps.Value.setEnabled(False)
            self.HThetaMax.Value.setEnabled(False)
            self.HThetaBack.Value.setEnabled(False)

        if mode == "Theta":
            self.HMax.Value.setEnabled(False)
            self.HSteps.Value.setEnabled(False)
            self.HBack.Value.setEnabled(False)

            self.HPhiSteps.Value.setEnabled(False)
            self.HPhiMax.Value.setEnabled(False)
            self.HPhiBack.Value.setEnabled(False)

            self.HThetaSteps.Value.setEnabled(True)
            self.HThetaMax.Value.setEnabled(True)
            self.HThetaBack.Value.setEnabled(True)


class SimulationParameters():
    """
    Don't pass parent -- pass Layer & Stimulus
    """
    def __init__(self, parent, layer_parameters, stimulus_parameters):
        self.table_layer_params = pg.TableWidget(editable=True, sortable=False)
        header = self.table_layer_params.horizontalHeader()
        # also QtWidgets.QHeaderView.Stretch is good
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        # self.table_stimulus_params: pg.TableWidget = pg.TableWidget(
        #     editable=True, sortable=False)
        # stimulus_header = self.table_stimulus_params.horizontalHeader()
        # stimulus_header.setSectionResizeMode(
        #     QtWidgets.QHeaderView.ResizeToContents)
        self.add_btn = QtWidgets.QPushButton()
        self.remove_button = QtWidgets.QPushButton()
        self.add_simulation = QtWidgets.QPushButton()

        self.add_btn.setText("Add new \nlayer")
        self.add_btn.clicked.connect(self.add_layer)
        self.remove_button.setText("Remove selected\n layer")
        self.remove_button.clicked.connect(self.remove_layer)
        self.add_simulation.setText("Add to \nsimulation list")
        self.add_simulation.clicked.connect(parent.add_to_simulation_list)

        self.table_layer_params.setData(layer_parameters.to_numpy())
        self.table_layer_params.setHorizontalHeaderLabels([
            unicode_subs[c] if c in unicode_subs else c
            for c in layer_parameters.columns
        ])
        # self.table_stimulus_params.setData(stimulus_parameters.to_numpy())
        # self.table_stimulus_params.setHorizontalHeaderLabels(
        #     stimulus_parameters.columns)
        self.central_widget = QtGui.QWidget()
        self.central_layout = QtGui.QVBoxLayout()
        self.central_widget.setLayout(self.central_layout)
        self.central_layout.addWidget(self.table_layer_params)
        self.btn_layout = QtGui.QHBoxLayout()
        self.btn_layout.addWidget(self.add_btn)
        self.btn_layout.addWidget(self.remove_button)
        self.btn_layout.addWidget(self.add_simulation)
        # self.central_layout.addWidget(self.table_stimulus_params)
        self.central_layout.addLayout(self.btn_layout)

        self.stimulus_GUI = StimulusGUI()
        self.central_layout.addLayout(self.stimulus_GUI.stimulus_layout)

        
        


    # def get_all_data(self):
    #     return self.get_table_data(
    #         self.table_stimulus_params), self.get_table_data(
    #             self.table_layer_params)




    def get_all_data(self):
        return self.stimulus_GUI.get_stimulus_data(), self.get_table_data(self.table_layer_params)


    def get_table_data(self, table: pg.TableWidget):
        number_of_rows = table.rowCount()
        number_of_columns = table.columnCount()
        tmp_df = pd.DataFrame()
        tmp_col_name = []
        for i in range(number_of_columns):
            name = table.takeHorizontalHeaderItem(i).text()
            if name in inverse_subs:
                name = inverse_subs[name]
            tmp_col_name.append(name)
            for j in range(number_of_rows):
                tmp_df.loc[j, i] = table.item(j, i).text()
        table.setHorizontalHeaderLabels(tmp_col_name)
        tmp_df.columns = tmp_col_name
        # d = {'col1': [1, 2], 'col2': [3, 4]}
        # print(tmp_df)
        return tmp_df

    def add_layer(self):
        self.table_layer_params.addRow([
            1, 1.6, 3000, "[1 0 0]", -1e-5, 0.01, 1e-9, "[0 1 0]", 0.02, 0.01,
            0.01, 100, 120, 1, [0, 0, 0], 0, 0, 0
        ])

    def remove_layer(self):
        self.table_layer_params.removeRow(self.table_layer_params.currentRow())

    def update_simulation_input_table(self, simulation: Simulation):
        sim_input = simulation.get_simulation_input()
        layer_params = [layer.to_gui() for layer in sim_input.layers]
        stimulus_params = sim_input.stimulus.to_gui()
        self.table_layer_params.setData(layer_params)
        self.table_stimulus_params.setData(stimulus_params)


class ResultsTable():
    """
    To be changed & renamed -- must use Simulation Manager
    """
    def __init__(self, manager: GeneralManager, plot_manager: PlotManager,
                 param_table: SimulationParameters, exporter: Exporter):

        self.plot_manager = plot_manager
        self.manager = manager
        self.parameter_table = param_table
        self.exporter = exporter
        self.results_table = pg.TableWidget(editable=False, sortable=False)

        if isinstance(manager, ExperimentManager):
            self.results_table.setColumnCount(1)
            self.results_table.setHorizontalHeaderLabels(["Name"])
        else:
            self.results_table.setColumnCount(2)
            self.results_table.setHorizontalHeaderLabels(["Name", "Status"])
        header = self.results_table.horizontalHeader()
        # also QtWidgets.QHeaderView.Stretch is good
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.remove_btn = QtWidgets.QPushButton()
        self.remove_btn.setText("Remove selected")
        self.remove_btn.clicked.connect(self.remove_selected)
        self.export_btn = QtWidgets.QPushButton()
        self.export_btn.setText("Export selected to .csv")
        self.export_btn.clicked.connect(self.export_selected)
        self.central_widget = QtGui.QWidget()
        self.central_layout = QtGui.QVBoxLayout()
        self.central_widget.setLayout(self.central_layout)
        self.central_layout.addWidget(self.results_table)
        self.central_layout.addWidget(self.remove_btn)
        self.central_layout.addWidget(self.export_btn)
        self.results_table.currentItemChanged.connect(
            self.on_item_selection_changed)

        self.results_table_itms: List[Tuple[QtWidgets.QTableWidgetItem,
                                            QtWidgets.QTableWidgetItem]] = []

    def on_item_selection_changed(self, current: QtWidgets.QTableWidgetItem,
                                  _: QtWidgets.QTableWidgetItem):

        if current is None:
            # everything was deselected
            return
        self.manager.set_highlighted_index(current.row())
        highlighted = self.manager.get_highlighted_item()
        self.plot_manager.plot_active_results([highlighted])
        if isinstance(highlighted, Simulation):
            self.parameter_table.update_simulation_input_table(highlighted)

    def remove_selected(self):
        highlighted = self.manager.get_highlighted_item()
        if highlighted in self.manager.get_selected_items():
            self.plot_manager.clear_simulation_plots()
            if isinstance(highlighted, Simulation):
                self.plot_manager.clear_simulation_plots()
            else:
                self.plot_manager.clear_experiment_plots()
        self.manager.remove_selected()
        self.update()

    def export_selected(self):
        self.exporter.export_simulations_csv()

    def update(self):
        self.update_list()

    def item_checked(self, item: QtWidgets.QTableWidgetItem,
                     status_item: QtWidgets.QTableWidgetItem):
        row = item.row()
        # name was changed
        self.manager.items[row].name = item.text()
        itm = self.manager.get_item(row)
        if status_item:
            status_item.setText(itm.status)
        if item.checkState() == QtCore.Qt.Checked:
            self.manager.add_to_selected(row)
        else:
            self.manager.remove_from_selected(row)

    def update_row(self, indx: Union[int, List[int]]):
        if isinstance(indx, int):
            indx = [indx]
        for sindex in indx:
            sim = self.manager.get_item(sindex)
            _, status_itm = self.results_table_itms[sindex]
            status_itm.setText(sim.status)

    def update_list(self):
        active = self.manager.selected_indices
        items = self.manager.get_items()
        self.results_table.setRowCount(len(items))
        self.results_table_itms.clear()
        for i, sim in enumerate(items):
            # main item
            sim_name = sim.name
            chbx_itm = QtWidgets.QTableWidgetItem(sim_name)
            if i in active:
                chbx_itm.setCheckState(QtCore.Qt.Checked)
            else:
                chbx_itm.setCheckState(QtCore.Qt.Unchecked)
            # for some reason there's an attrubute error
            # we don't want to trigger on first add
            chbx_itm.itemChanged = lambda:...
            self.results_table.setItem(i, 0, chbx_itm)

            status_itm = None
            if isinstance(sim, Simulation):
                # status item
                status_itm = QtWidgets.QTableWidgetItem(sim.status)
                status_itm.itemChanged = lambda:...
                status_itm.setFlags(status_itm.flags()
                                    & ~QtCore.Qt.ItemIsEditable
                                    & ~QtCore.Qt.ItemIsSelectable)
                self.results_table.setItem(i, 1, status_itm)

            chbx_itm.itemChanged = partial(self.item_checked, chbx_itm,
                                           status_itm)
            self.results_table_itms.append((chbx_itm, status_itm))


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

        self.start_btn = QtWidgets.QPushButton("Start")
        self.start_btn.setCheckable(True)
        self.start_btn.setStyleSheet("background-color : lightgreen")
        self.kill_fn = lambda:...  # empty function
        self.start_btn.clicked.connect(self.btn_toggle)

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
        self.start_btn.setChecked(False)
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








