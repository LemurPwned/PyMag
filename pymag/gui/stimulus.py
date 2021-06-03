

import pandas as pd
import numpy as np
from pymag.engine.utils import get_stimulus
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel
from pymag.engine.data_holders import StimulusObject


class Labelled():
    def __init__(self,
                 label="Label",
                 minimum=0,
                 maximum=1,
                 value=0,
                 mode='Double',
                 item_list=["1", "2", "3"]):
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
        H_min = -1e9
        H_max = 1e9
        f_min = 0
        f_max = 1e3
        f_step_min = 1
        f_step_max = 1e9
        I_dc_min = 0
        I_dc_max = 1000
        I_RF_min = 0
        I_RF_max = 1000
        steps_min = 1
        steps_max = 1e9
        LLG_time_min = 1e-15
        LLG_steps_min = 10
        LLG_time_max = 1e6
        LLG_steps_max = 1e9

        H_unit = "kA/m"
        angle_unit = "deg"
        f_unit = "GHz"
        I_unit = "uA"
        V_unit = "V"
        time_unit = "ns"

        self.Idc = Labelled(label="I DC",
                            minimum=I_dc_min,
                            maximum=I_dc_max,
                            value=0.01)
        self.Iac = Labelled(label="I AC",
                            minimum=I_dc_min,
                            maximum=I_dc_max,
                            value=0.01)

        self.LLGtime = Labelled(label="LLG time",
                                minimum=LLG_time_min,
                                maximum=LLG_time_max,
                                value=10)
        self.LLGsteps = Labelled(label="LLG steps",
                                 minimum=f_step_min,
                                 maximum=f_step_max,
                                 value=10,
                                 mode='Integer')
        self.fmin = Labelled(label="f AC",
                             minimum=f_min,
                             maximum=f_max,
                             value=0)
        self.fsteps = Labelled(label="f AC steps",
                               minimum=LLG_steps_min,
                               maximum=LLG_steps_max,
                               value=10,
                               mode='Integer')
        self.fmax = Labelled(label="fmax AC steps",
                             minimum=f_min,
                             maximum=f_max,
                             value=20)

        self.HMin = Labelled(label="H",
                             minimum=H_min,
                             maximum=H_max,
                             value=-1e3)
        self.HMax = Labelled(label="-",
                             minimum=H_min,
                             maximum=H_max,
                             value=1e3)
        self.HSteps = Labelled(label="Steps",
                               minimum=steps_min,
                               maximum=steps_max,
                               value=50,
                               mode='Integer')
        self.HThetaSteps = Labelled(label="Steps",
                                    minimum=0,
                                    maximum=1e6,
                                    value=50)
        self.HPhiSteps = Labelled(label="Steps",
                                  minimum=0,
                                  maximum=1e6,
                                  value=50)
        self.HBack = Labelled(label="Back",
                              value=False,
                              mode='Binary')
        self.HPhiBack = Labelled(label="Back",
                                 value=False,
                                 mode='Binary')
        self.HThetaBack = Labelled(label="Back",
                                   value=False,
                                   mode='Binary')
        self.HThetaMin = Labelled(
            label="Theta",
            minimum=-360,
            maximum=360,
            value=89)
        self.HThetaMax = Labelled(
            label="Phi",
            minimum=-360,
            maximum=360,
            value=89)

        self.HPhiMin = Labelled(label="Phi",
                                minimum=-360,
                                maximum=360,
                                value=1)
        self.HPhiMax = Labelled(label="Phi",
                                minimum=-360,
                                maximum=360,
                                value=1)
        self.HMode = Labelled(label="Field sweep mode",
                              mode="Combo", item_list=["H", "Phi", "Theta"])
        self.Idir = Labelled(label="I source", mode="Combo",
                             item_list=["x", "y", "z"])
        self.Vdir = Labelled(label="Voltmeter", mode="Combo",
                             item_list=["x", "y", "z"])
        self.stimulus_layout = QtGui.QGridLayout()
        self.LLGError_threshold = Labelled(label="Max dm error",
                                           minimum=-360,
                                           maximum=360,
                                           value=0.0)

        self.stimulus_objects = [[QLabel(" "), self.HMode.Label, self.HMode.Value],
                                 [QLabel(" "),
                                 QLabel("Start"),
                                 QLabel("Steps"),
                                 QLabel("Stop"), QLabel("Back")],
                                 [self.HMin.Label, self.HMin.Value,
                                 self.HSteps.Value,
                                  self.HMax.Value, self.HBack.Value],
                                 [self.HPhiMin.Label,
                                 self.HPhiMin.Value,
                                 self.HPhiSteps.Value,
                                  self.HPhiMax.Value,
                                  self.HPhiBack.Value],
                                 [self.HThetaMin.Label,
                                 self.HThetaMin.Value, self.HThetaSteps.Value,
                                  self.HThetaMax.Value, self.HThetaBack.Value],
                                 [QLabel(" "), QLabel("Electrical")],
                                 [self.fmin.Label, self.fmin.Value,
                                     self.fsteps.Value, self.fmax.Value],
                                 [self.Idir.Label, self.Idir.Value],
                                 [self.Vdir.Label, self.Vdir.Value],
                                 [self.Idc.Label, self.Idc.Value],
                                 [self.Iac.Label, self.Iac.Value],
                                 [QLabel(" "), QLabel(
                                     "Simulation parameters")],
                                 [self.LLGtime.Label, self.LLGtime.Value],
                                 [self.LLGsteps.Label, self.LLGsteps.Value],
                                 [self.LLGError_threshold.Label, self.LLGError_threshold.Value]]

        self.HMode.Value.currentIndexChanged.connect(self.H_mode_changed)

        pixmap = QPixmap('./pymag/presets/image1.png')
        label = QLabel()
        # label.resize(200,200)
        label.setPixmap(pixmap)

        for i in range(0, len(self.stimulus_objects[:])):
            for j in range(0, len(self.stimulus_objects[i])):
                self.stimulus_layout.addWidget(
                    self.stimulus_objects[i][j], i, j)
        self.stimulus_layout.addWidget(label, 7, 2, 8, 3)

        self.H_mode_changed()
        # self.get_stimulus_data()

    def parse_vector(self, vector_str_value):
        if vector_str_value == "x":
            return [1, 0, 0]
        elif vector_str_value == "y":
            return [0, 1, 0]
        elif vector_str_value == "z":
            return [0, 0, 1]
        else:
            raise ValueError('Invalid vector value: {vector_str_value}')

    def get_stimulus_object(self) -> StimulusObject:
        """
        Parse the GUI object to the corresponding backend 
        object. 
        Calculates the values necessary for calculation while parsing as well
        """
        mode = self.HMode.Value.currentText()
        if mode == "H":
            tmp_H = {'H': [self.HMin.Value.value(), self.HSteps.Value.value(), self.HMax.Value.value()],
                     'Hback': [self.HBack.Value.checkState(), "-", "-"],
                     'HTheta': [self.HThetaMin.Value.value(), "-", "-"],
                     'HPhi': [self.HPhiMin.Value.value(), "-", "-"]}
            steps = int(self.HSteps.Value.value())
        if mode == "Phi":
            tmp_H = {'H': [self.HMin.Value.value(), "-", "-"],
                     'Hback': [self.HPhiBack.Value.checkState(), "-", "-"],
                     'HTheta': [self.HThetaMin.Value.value(), "-", "-"],
                     'HPhi': [self.HPhiMin.Value.value(), self.HPhiSteps.Value.value(), self.HPhiMax.Value.value()]}
            steps = int(self.HPhiSteps.Value.value())
        if mode == "Theta":
            tmp_H = {'H': [self.HMin.Value.value(), "-", "-"],
                     'Hback': [self.HThetaBack.Value.checkState(), "-", "-"],
                     'HTheta': [self.HThetaMin.Value.value(), self.HThetaSteps.Value.value(), self.HThetaMax.Value.value()],
                     'HPhi': [self.HPhiMin.Value.value(), "-", "-"]}
            steps = int(self.HThetaSteps.Value.value())
        tmp = {'f': [self.fmin.Value.value()*1e9, self.fsteps.Value.value(), self.fmax.Value.value()*1e9],
               "IAC": [self.Iac.Value.value(), "-", "-"],
               "IDC": [self.Idc.Value.value(), "-", "-"],
               "Idir": ["1 0 0", "-", "-"],
               "Vdir": ["1 0 0", "-", "-"],
               "LLGtime": [self.LLGtime.Value.value()/1e9, "-", "-", ],
               "LLGsteps": [self.LLGsteps.Value.value(), "-", "-", ]}

        H_sweep, sweep = get_stimulus(float(self.HMin.Value.value()),
                                      float(self.HMax.Value.value()),
                                      float(self.HThetaMin.Value.value()),
                                      float(self.HThetaMax.Value.value()),
                                      float(self.HPhiMin.Value.value()),
                                      float(self.HPhiMax.Value.value()),
                                      steps,
                                      bool(self.HThetaBack.Value.checkState()) or bool(
                                          self.HPhiBack.Value.checkState()) or bool(self.HBack.Value.checkState()),
                                      mode)
        f_min = float(self.fmin.Value.value()*1e9)
        f_max = float(self.fmax.Value.value()*1e9)
        f_steps = int(self.fsteps.Value.value())
        LLG_steps = int(self.LLGsteps.Value.value())
        PIMM_delta_f = 1./LLG_steps
        PIMM_freqs = np.arange(0, PIMM_delta_f*LLG_steps, step=PIMM_delta_f)
        SD_freqs = np.linspace(f_min, f_max, f_steps)
        spectrum_len = LLG_steps // 2
        so = StimulusObject(
            mode=mode,
            H_sweep=H_sweep.tolist(),
            sweep=sweep.tolist(),
            LLG_steps=LLG_steps,
            LLG_time=float(self.LLGtime.Value.value()/1e9),
            frequency_min=f_min,
            frequency_max=f_max,
            frequency_steps=f_steps,
            I_rf=float(self.Iac.Value.value()),
            I_dc=float(self.Idc.Value.value()),
            I_dir=self.parse_vector(self.Idir.Value.currentText()),
            V_dir=self.parse_vector(self.Vdir.Value.currentText()),
            # PIMM and VSD
            spectrum_len=spectrum_len,
            SD_freqs=SD_freqs.tolist(),
            PIMM_freqs=PIMM_freqs.tolist(),
            PIMM_delta_f=PIMM_delta_f
        )
        # print(so.dict())
        # df = pd.concat([pd.DataFrame(tmp_H), pd.DataFrame(tmp)], axis=1)
        return so

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
