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
        
        
        # theta_min = 0
        # theta_max = 180
        # phi_min = 0
        # phi_max = 360
        # H_min = -1e9
        # H_max = 1e9
        # f_min = 0
        # f_max = 1e3
        # I_dc_min = 0
        # I_dc_max = 1000
        # I_RF_min = 0
        # I_RF_max = 1000
        # steps_min = 1
        # steps_max = 1e9
        # LLG_time_min = 1e-15
        # LLG_steps_min = 10
        # LLG_time_max = 1e-3
        # LLG_steps_max = 1e9

        # H_unit = "kA/m"
        # angle_unit = "deg"
        # f_unit = "GHz"
        # I_unit = "uA"
        # V_unit = "V"
        # time_unit = "ns"

        # self.stimulus_layout = QtGui.QGridLayout()
        # self.stimulus_layout.addWidget(QLabel("H sweep mode"), 0, 0)

        # self.stimulus_labels_H = [
        #     ["H start", "H steps", "H stop", "\u03B8", "\u03C6"],
        #     ["H mag", "\u03B8 start", "\u03B8 steps", "\u03B8 stop", "\u03C6"],
        #     ["H mag", "\u03B8", "\u03C6 start", "\u03C6 steps", "\u03C6 stop"]
        # ]
        
        # self.stimulus_labels_generals = [
        #     "LLG time", "LLG steps", "DC current", "RF current", "frequeny min",
        #     "frequency steps", "frequency max"
        # ]
        # self.stimulus_labels_directions = [
        #     "Voltmeter dir", "Current source dir"
        # ]

        # self.stimulus_units_H = [[
        #     H_unit, "int", H_unit, angle_unit, angle_unit
        # ], [H_unit, angle_unit, "int", angle_unit,
        #     angle_unit], [H_unit, angle_unit, angle_unit, "int", angle_unit]]

        # self.stimulus_H_min = [[H_min, steps_min, H_min, theta_min, phi_min],
        #                        [
        #                            H_min, theta_min, steps_min, theta_min,
        #                            phi_min
        #                        ],
        #                        [H_min, theta_min, phi_min, steps_min, phi_min]]
        # self.stimulus_H_max = [[H_max, steps_max, H_max, theta_max, phi_max],
        #                        [
        #                            H_max, theta_max, steps_max, theta_max,
        #                            phi_max
        #                        ],
        #                        [H_max, theta_max, phi_max, steps_max, phi_max]]


        # self.stimulus_general_min = [LLG_time_min, LLG_steps_min, I_dc_min, I_RF_min, f_min, steps_min, f_min]
        # self.stimulus_general_max = [LLG_time_max, LLG_steps_max, I_dc_max, I_RF_max, f_max, steps_max, f_max]
        # self.stimulus_general_units = [time_unit, "int", I_unit, I_unit, f_unit, "int", f_unit]

        # self.stimulus_spinboxes_H = []
        # self.stimulus_labels__ = []

        # for i in range(0, 5):
        #     self.stimulus_labels__.append(QLabel())
        #     self.stimulus_layout.addWidget(self.stimulus_labels__[i], i + 1, 0)
        #     self.stimulus_spinboxes_H.append(QDoubleSpinBox())
        #     self.stimulus_layout.addWidget(self.stimulus_spinboxes_H[i], i + 1,1)



        # self.H_sweep_mode = QComboBox()
        # self.H_sweep_mode.currentIndexChanged.connect(self.H_mode_changed)
        # stimulus_H_modes_names = ["mag", "\u03B8", "\u03C6"]
        # for i in range(0, len(stimulus_H_modes_names)):
        #     self.H_sweep_mode.addItem(stimulus_H_modes_names[i])
        # self.stimulus_layout.addWidget(self.H_sweep_mode, 0, 1)
        # self.H_mode_changed()

        
        # for i in range(0, len(self.stimulus_labels_directions)):
        #     self.stimulus_layout.addWidget(
        #         QLabel(self.stimulus_labels_directions[i]), i, 5)

        # self.stimulus_spinboxes_generals = []

        # for i in range(0, len(self.stimulus_labels_generals)):
        #     self.stimulus_layout.addWidget(QLabel(self.stimulus_labels_generals[i]+ " ("+ self.stimulus_general_units[i] +")"), i, 3)

        #     self.stimulus_spinboxes_generals.append(QDoubleSpinBox())
        #     self.stimulus_layout.addWidget(self.stimulus_spinboxes_generals[i], i,4)
        #     self.stimulus_spinboxes_generals[i].setMinimum(self.stimulus_general_min[i])
        #     self.stimulus_spinboxes_generals[i].setMaximum(self.stimulus_general_max[i])



        # directions = ["x", "y", "z"]
        # self.voltmeter = QComboBox()
        # for i in range(0, len(directions)):
        #     self.voltmeter.addItem(directions[i])
        # self.stimulus_layout.addWidget(self.voltmeter, 0, 6)

        # self.ACDC_source = QComboBox()
        # for i in range(0, len(directions)):
        #     self.ACDC_source.addItem(directions[i])
        # self.stimulus_layout.addWidget(self.ACDC_source, 1, 6)




        # self.w = gl.GLViewWidget()
        # self.w.opts['distance'] = 45.0
        # self.w.opts['fov'] = 60
        # self.w.opts['elevation'] = 10
        # self.w.opts['azimuth'] = 90
        # self.w.setWindowTitle('pyqtgraph example: GLLinePlotItem')
        # self.w.setGeometry(450, 700, 980, 700)
        # # self.w.show()
        # # create the background grids
        # gx = gl.GLGridItem()
        # gx.rotate(90, 0, 1, 0)
        # gx.translate(-10, 0, 0)
        # self.w.addItem(gx)
        # gy = gl.GLGridItem()
        # gy.rotate(90, 1, 0, 0)
        # gy.translate(0, -10, 0)
        # self.w.addItem(gy)
        # gz = gl.GLGridItem()
        # gz.translate(0, 0, -10)
        # self.w.addItem(gz)

        # verts = np.array([(-1.0, -1.0, 0.0), (1.0, -1.0, 0.0),
        #                   (-1.0, 1.0, 0.0), (1.0, 1.0, 0.0), (-2, -3, -4),
        #                   (-2, -3, 0.3), (-2, 3, -4), (-2, 3, 0.3),
        #                   (2, -3, -4), (2, -3, 0.3), (2, 3, -4), (2, 3, 0.3),
        #                   (-1.0, -1.0, 5), (1.0, -1.0, 5), (-1.0, 1.0, 5),
        #                   (1.0, 1.0, 5)])

        # faces = np.array([(1, 2, 0), (1, 3, 2), (5, 6, 4), (7, 10, 6),
        #                   (11, 8, 10), (9, 4, 8), (10, 4, 6), (7, 9, 11),
        #                   (5, 7, 6), (7, 11, 10), (11, 9, 8), (9, 5, 4),
        #                   (10, 8, 4), (7, 5, 9), (13, 14, 12), (13, 15, 14)])

        # colors = np.array([[1, i / 16, 1, 1] for i in range(len(faces))])

        # self.object = gl.GLMeshItem(vertexes=verts,
        #                             faces=faces,
        #                             faceColors=colors,
        #                             smooth=False,
        #                             shader='shaded',
        #                             glOptions='opaque')
        # self.w.addItem(self.object)

        # self.stimulus_layout.addWidget(self.w, 2, 5, 5, 2)

        theta_min = 0
        theta_max = 180
        phi_min = 0
        phi_max = 360
        H_min = -1e9
        H_max = 1e9
        f_min = 0
        f_max = 1e3
        I_dc_min = 0
        I_dc_max = 1000
        I_RF_min = 0
        I_RF_max = 1000
        steps_min = 1
        steps_max = 1e9
        LLG_time_min = 1e-15
        LLG_steps_min = 10
        LLG_time_max = 1e-3
        LLG_steps_max = 1e9

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
                                          minimum=LLG_steps_min,
                                          maximum=LLG_steps_max,
                                          value=10)
        self.fmin = Labeled(label="f AC",
                                          minimum=LLG_steps_min,
                                          maximum=LLG_steps_max,
                                          value=10)
        self.steps = Labeled(label="f AC steps",
                                          minimum=LLG_steps_min,
                                          maximum=LLG_steps_max,
                                          value=10)
        self.fmax = Labeled(label="fmax AC steps",
                                          minimum=LLG_steps_min,
                                          maximum=LLG_steps_max,
                                          value=10)

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
                                            value=50)
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
            value=90)
        self.HThetaMax = Labeled(
            label="Phi",
            minimum=-360,
            maximum=360,
            value=90)

        self.HPhiMin = Labeled(label="(\u03C6)",
                                          minimum=-360,
                                          maximum=360,
                                          value=0.0)
        self.HPhiMax = Labeled(label="(\u03C6)",
                                          minimum=-360,
                                          maximum=360,
                                          value=0.0)
        self.HMode = Labeled(label="Field sweep mode",mode="Combo", item_list=["H","Phi","Theta"])
        self.Idir = Labeled(label="I source",mode="Combo", item_list=["x","y","z"])
        self.Vdir = Labeled(label="Voltmeter",mode="Combo", item_list=["x","y","z"])
        self.stimulus_layout = QtGui.QGridLayout()

        # self.stimulus_layout.addWidget(self.HMode.Value, 0, 0)
        self.LLGError_threshold = Labeled(label="Max dm error",
                                          minimum=-360,
                                          maximum=360,
                                          value=0.0)


        self.stimulus_objests = [[QLabel(" "),self.HMode.Label, self.HMode.Value],
                            [QLabel(" "),     QLabel("Start"),      QLabel("Steps"),        QLabel("Stop"),       QLabel("Value")],
                            [self.HMin.Label,      self.HMin.Value,      self.HSteps.Value,      self.HMax.Value,      self.HBack.Value],
                            [self.HPhiMin.Label,   self.HPhiMin.Value,   self.HPhiSteps.Value,   self.HPhiMax.Value,   self.HPhiBack.Value],
                            [self.HThetaMin.Label, self.HThetaMin.Value, self.HThetaSteps.Value, self.HThetaMax.Value, self.HThetaBack.Value],
                            [QLabel(" "), QLabel("Electrical")],
                            [self.fmin.Label, self.fmin.Value, self.steps.Value, self.fmax.Value],
                            [self.Idir.Label, self.Idir.Value],
                            [self.Vdir.Label, self.Vdir.Value],
                            [self.Idc.Label,self.Idc.Value],
                            [self.Iac.Label,self.Iac.Value],
                            [QLabel(" "), QLabel("Simulation\nparameters")],
                            [self.LLGtime.Label,self.LLGtime.Value],
                            [self.LLGsteps.Label,self.LLGsteps.Value],
                            [self.LLGError_threshold.Label,self.LLGError_threshold.Value]]

        self.HMode.Value.currentIndexChanged.connect(self.H_mode_changed)

        for i in range(0,len(self.stimulus_objests[:])):
            for j in range(0,len(self.stimulus_objests[i])):
                self.stimulus_layout.addWidget(self.stimulus_objests[i][j], i, j)


        self.H_mode_changed()


    # def get_table_data(self, table: pg.TableWidget):
    #     number_of_rows = table.rowCount()
    #     number_of_columns = table.columnCount()
    #     tmp_df = pd.DataFrame()
    #     tmp_col_name = []
    #     for i in range(number_of_columns):
    #         name = table.takeHorizontalHeaderItem(i).text()
    #         if name in inverse_subs:
    #             name = inverse_subs[name]
    #         tmp_col_name.append(name)
    #         for j in range(number_of_rows):
    #             tmp_df.loc[j, i] = table.item(j, i).text()
    #     table.setHorizontalHeaderLabels(tmp_col_name)
    #     tmp_df.columns = tmp_col_name
    #     # d = {'col1': [1, 2], 'col2': [3, 4]}
    #     print(tmp_df)
    #     return tmp_df


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

        self.table_stimulus_params: pg.TableWidget = pg.TableWidget(
            editable=True, sortable=False)
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
        self.add_simulation.clicked.connect(parent.add_to_simulation_list)

        self.table_layer_params.setData(layer_parameters.to_numpy())
        self.table_layer_params.setHorizontalHeaderLabels([
            unicode_subs[c] if c in unicode_subs else c
            for c in layer_parameters.columns
        ])
        self.table_stimulus_params.setData(stimulus_parameters.to_numpy())
        self.table_stimulus_params.setHorizontalHeaderLabels(
            stimulus_parameters.columns)
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

        self.stimulus_GUI = StimulusGUI()
        self.central_layout.addLayout(self.stimulus_GUI.stimulus_layout)

        
        


    def get_all_data(self):
        return self.get_table_data(
            self.table_stimulus_params), self.get_table_data(
                self.table_layer_params)



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
        print(tmp_df)
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








class Stimulus(QtGui.QDialog):
    def __init__(self, parent):
        super(Stimulus, self).__init__()

        self.settings = QtCore.QSettings("Stimulus_settings.ini",
                                         QtCore.QSettings.IniFormat)
        # print(self.settings.fileName())

        self.setWindowTitle(PyMagVersion + " - New stimulus")

        self.setFixedSize(650, 600)
        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)

        self.OKButton = QtWidgets.QPushButton()

        self.table_stimulus = pg.TableWidget(editable=True, sortable=False)
        data = np.zeros((4, 1))
        columns = ['Hext (A/m)']
        self.table_stimulus.setData(data)
        self.table_stimulus.setHorizontalHeaderLabels(['Hx', 'Hy', 'Hz'])

        self.LLGparams = QtGui.QGridLayout()
        self.LLGparamsLabel = QLabel("LLG simulation parameters:")
        self.LLGSteps = LabelledDoubleSpinBox(label="Simulation steps of LLG",
                                              minimum=10,
                                              maximum=1e6,
                                              value=1000)
        self.LLGTime = LabelledDoubleSpinBox(
            label="Simulation time of LLG [ns]",
            minimum=0.001,
            maximum=1e3,
            value=5)
        self.LLGparams.addWidget(self.LLGparamsLabel, 0, 0)
        self.LLGparams.addWidget(self.LLGTime.Label, 1, 0)
        self.LLGparams.addWidget(self.LLGTime.Value, 1, 1)
        self.LLGparams.addWidget(self.LLGSteps.Label, 2, 0)
        self.LLGparams.addWidget(self.LLGSteps.Value, 2, 1)

        self.FieldLayout = QtGui.QGridLayout()
        self.FieldLayoutLabel = QLabel("Field H simulation parameters:")
        self.HMin = LabelledDoubleSpinBox(label="HMin (A/m)",
                                          minimum=-1e9,
                                          maximum=1e9,
                                          value=-1e3)
        self.HMax = LabelledDoubleSpinBox(label="HMax (A/m)",
                                          minimum=-1e9,
                                          maximum=1e9,
                                          value=1e3)
        self.HSteps = LabelledDoubleSpinBox(label="Steps",
                                            minimum=0,
                                            maximum=1e6,
                                            value=50)
        self.HBack = LabelledDoubleSpinBox(label="Back",
                                           value=False,
                                           mode='Binary')
        self.HTheta = LabelledDoubleSpinBox(
            label="Out of plane angle \u03B8\n 0-out of plane, 90 - in plane",
            minimum=-360,
            maximum=360,
            value=90)
        self.HPhi = LabelledDoubleSpinBox(label="In plane angle (\u03C6)",
                                          minimum=-360,
                                          maximum=360,
                                          value=0.0)

        self.FieldLayout.addWidget(self.FieldLayoutLabel, 0, 0)
        self.FieldLayout.addWidget(self.HMin.Label, 1, 0)
        self.FieldLayout.addWidget(self.HMin.Value, 1, 1)
        self.FieldLayout.addWidget(self.HMax.Label, 2, 0)
        self.FieldLayout.addWidget(self.HMax.Value, 2, 1)
        self.FieldLayout.addWidget(self.HSteps.Label, 3, 0)
        self.FieldLayout.addWidget(self.HSteps.Value, 3, 1)
        self.FieldLayout.addWidget(self.HBack.Label, 4, 0)
        self.FieldLayout.addWidget(self.HBack.Value, 4, 1)
        self.FieldLayout.addWidget(self.HTheta.Label, 5, 0)
        self.FieldLayout.addWidget(self.HTheta.Value, 5, 1)
        self.FieldLayout.addWidget(self.HPhi.Label, 6, 0)
        self.FieldLayout.addWidget(self.HPhi.Value, 6, 1)

        self.SpinDiodeLayout = QtGui.QGridLayout()
        self.SpinDiodeLayoutLabel = QLabel("Spin diode simulation parameters:")
        self.IAC = LabelledDoubleSpinBox(label="I(AC) [A]",
                                         minimum=0,
                                         maximum=1,
                                         value=0.01)
        self.IDC = LabelledDoubleSpinBox(label="I(DC) [A]",
                                         minimum=0,
                                         maximum=1,
                                         value=0)
        self.IACphi = LabelledDoubleSpinBox(label="Phase shift psi [deg]",
                                            minimum=0,
                                            maximum=360,
                                            value=0)
        self.fMin = LabelledDoubleSpinBox(label="fMin [GHz]",
                                          minimum=0,
                                          maximum=100,
                                          value=0)
        self.fMax = LabelledDoubleSpinBox(label="fMax [GHz]",
                                          minimum=0,
                                          maximum=100,
                                          value=12)
        self.fSteps = LabelledDoubleSpinBox(label="fSteps",
                                            minimum=0,
                                            maximum=1000,
                                            value=12,
                                            mode='Integer')

        self.SpinDiodeLayout.addWidget(self.SpinDiodeLayoutLabel, 0, 0)

        self.SpinDiodeLayout.addWidget(self.IAC.Label, 1, 0)
        self.SpinDiodeLayout.addWidget(self.IAC.Value, 1, 1)
        self.SpinDiodeLayout.addWidget(self.IDC.Label, 2, 0)
        self.SpinDiodeLayout.addWidget(self.IDC.Value, 2, 1)
        self.SpinDiodeLayout.addWidget(self.IACphi.Label, 3, 0)
        self.SpinDiodeLayout.addWidget(self.IACphi.Value, 3, 1)
        self.SpinDiodeLayout.addWidget(self.fMin.Label, 4, 0)
        self.SpinDiodeLayout.addWidget(self.fMin.Value, 4, 1)
        self.SpinDiodeLayout.addWidget(self.fSteps.Label, 5, 0)
        self.SpinDiodeLayout.addWidget(self.fSteps.Value, 5, 1)
        self.SpinDiodeLayout.addWidget(self.fMax.Label, 6, 0)
        self.SpinDiodeLayout.addWidget(self.fMax.Value, 6, 1)

        self.btn_layout = QtWidgets.QVBoxLayout()

        self.btn_layout.addLayout(self.FieldLayout)
        self.btn_layout.addLayout(self.SpinDiodeLayout)
        self.btn_layout.addLayout(self.LLGparams)
        self.layout.addLayout(self.btn_layout)
        self.layout.addWidget(self.table_stimulus)
        self.btn_layout.addWidget(self.OKButton)
        self.OKButton.setText("OK")

        self.OKButton.clicked.connect(self.generateStimulus)

        self.HMin.Value.valueChanged.connect(self.Stimulus_update)
        self.HMax.Value.valueChanged.connect(self.Stimulus_update)
        self.HSteps.Value.valueChanged.connect(self.Stimulus_update)
        self.HPhi.Value.valueChanged.connect(self.Stimulus_update)
        self.HTheta.Value.valueChanged.connect(self.Stimulus_update)
        self.HBack.Value.stateChanged.connect(self.Stimulus_update)
