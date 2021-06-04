
import os
from typing import List
import json
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

    def show(self):
        self.Value.show()
        self.Label.show()

    def hide(self):
        self.Value.hide()
        self.Label.hide()


class StimulusGUI():
    def __init__(self) -> None:
        preset_dir = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', 'presets'))
        preset_file = os.path.join(preset_dir,
                                   "stimulus.json")
        self.__dynamic_constructor(preset_file=preset_file)
        self.stimulus_layout = QtGui.QGridLayout()
        self.LLGError_threshold = Labelled(label="Max dm error",
                                           minimum=-360,
                                           maximum=360,
                                           value=0.0)

        self.stimulus_objects = [self.HMode,
                                 self.H,
                                 self.HMin,
                                 self.HSteps,
                                 self.HMax,
                                 self.HBack,
                                 self.HPhi,
                                 self.HPhiMin,
                                 self.HPhiSteps,
                                 self.HPhiMax,
                                 self.HPhiBack,
                                 self.HTheta,
                                 self.HThetaMin,
                                 self.HThetaSteps,
                                 self.HThetaMax,
                                 self.HThetaBack,
                                 self.fmin,
                                 self.fsteps,
                                 self.fmax,
                                 self.Idir,
                                 self.Vdir,
                                 self.Idc,
                                 self.Iac,
                                 self.LLGtime,
                                 self.LLGsteps,
                                 self.LLGError_threshold]

        self.HMode.Value.currentIndexChanged.connect(self.H_mode_changed)

        for i in range(0, len(self.stimulus_objects)):

            self.stimulus_layout.addWidget(
                self.stimulus_objects[i].Label, 0, i)
            self.stimulus_layout.addWidget(
                self.stimulus_objects[i].Value, 1, i)

        self.H_mode_changed()

    def __dynamic_constructor(self, preset_file: str):
        """
        Add Stimulus Boxes given a json specification.
        """
        preset_json = json.load(open(preset_file, "r"))
        for obj in preset_json["stimulus"]:
            setattr(self, obj["name"], Labelled(**obj["params"]))

    def parse_vector(self, vector_str_value) -> List[int]:
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
            steps = int(self.HSteps.Value.value())
            back = bool(self.HThetaBack.Value.checkState())
        if mode == "Phi":
            steps = int(self.HPhiSteps.Value.value())
            back = bool(self.HPhiBack.Value.checkState())
        if mode == "Theta":
            steps = int(self.HThetaSteps.Value.value())
            back = bool(self.HBack.Value.checkState())

        H_sweep, sweep = get_stimulus(float(self.H.Value.value()),
                                      float(self.HMin.Value.value()),
                                      float(self.HMax.Value.value()),
                                      float(self.HTheta.Value.value()),
                                      float(self.HThetaMin.Value.value()),
                                      float(self.HThetaMax.Value.value()),
                                      float(self.HPhi.Value.value()),
                                      float(self.HPhiMin.Value.value()),
                                      float(self.HPhiMax.Value.value()),
                                      steps, back, mode)
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
        return so

    def H_mode_changed(self):

        mode = self.HMode.Value.currentText()
        for i in self.stimulus_objects[1:16]:
            i.hide()
        if mode == "H":
            for i in [self.HMin, self.HSteps, self.HMax, self.HBack, self.HPhi, self.HTheta]:
                i.show()

        if mode == "Phi":
            for i in [self.H, self.HPhiMin, self.HPhiSteps, self.HPhiMax, self.HPhiBack, self.HTheta]:
                i.show()

        if mode == "Theta":
            for i in [self.H, self.HPhi, self.HThetaMin, self.HThetaSteps, self.HThetaMax, self.HThetaBack]:
                i.show()
