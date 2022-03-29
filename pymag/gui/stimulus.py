
import json
import os
from typing import List

import numpy as np
from pydantic.types import Json
from PyQt5 import QtWidgets

from pymag.engine.data_holders import StimulusObject
from pymag.engine.utils import SweepMode, get_stimulus

from .utils import Labelled


class StimulusGUI():
    def __init__(self) -> None:
        self.preset_file = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', 'presets', "stimulus.json"))

        self.__dynamic_constructor(preset_file=self.preset_file)
        self.stimulus_layout = QtWidgets.QGridLayout()
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
                                 self.LLGsteps]

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
            setattr(self, obj["name"], Labelled(
                **obj["params"], var_name=obj["name"]))

    def set_stimulus(self, stimulus_json: Json):
        for obj in stimulus_json["stimulus"]:
            _ref = getattr(self, obj["name"])
            if 'value' in obj['params']:
                _ref.setValue(obj['params']['value'])

        self.H_mode_changed()

    def to_json(self):
        output_json = {"stimulus": []}
        obj: Labelled
        for obj in self.stimulus_objects:
            output_json["stimulus"].append(obj.to_json())
        return output_json

    def save_stimulus(self):
        json.dump(self.to_json(), open(self.preset_file, "w"), indent=4)

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
        Calculates the values necessary for calculation while parsing as well.
        """
        mode = self.HMode.Value.currentText()
        if mode == SweepMode.H:
            steps = int(self.HSteps.Value.value())
            back = self.HBack.Value.checkState()
        if mode == SweepMode.PHI:
            steps = int(self.HPhiSteps.Value.value())
            back = self.HPhiBack.Value.checkState()
        if mode == SweepMode.THETA:
            steps = int(self.HThetaSteps.Value.value())
            back = self.HThetaBack.Value.checkState()
        # convert H from kA/m -> A/m
        H_sweep, sweep = get_stimulus(self.H.Value.value()*1e3,
                                      self.HMin.Value.value()*1e3,
                                      self.HMax.Value.value()*1e3,
                                      self.HTheta.Value.value(),
                                      self.HThetaMin.Value.value(),
                                      self.HThetaMax.Value.value(),
                                      self.HPhi.Value.value(),
                                      self.HPhiMin.Value.value(),
                                      self.HPhiMax.Value.value(),
                                      steps, back, mode)
        f_min = self.fmin.Value.value()*1e9
        f_max = self.fmax.Value.value()*1e9
        f_steps = int(self.fsteps.Value.value())
        LLG_steps = int(self.LLGsteps.Value.value())
        LLG_time = self.LLGtime.Value.value()/1e9  # ns -> s
        PIMM_delta_f = 1./LLG_time
        PIMM_freqs = np.arange(0, PIMM_delta_f*LLG_steps, step=PIMM_delta_f)
        SD_freqs = np.linspace(f_min, f_max, f_steps)
        spectrum_len = LLG_steps // 2
        so = StimulusObject(
            mode=mode,
            H_sweep=H_sweep.tolist(),
            sweep=sweep.tolist(),
            LLG_steps=LLG_steps,
            LLG_time=LLG_time,
            frequency_min=f_min,
            frequency_max=f_max,
            frequency_steps=f_steps,
            I_rf=self.Iac.Value.value(),
            I_dc=self.Idc.Value.value(),
            I_dir=self.parse_vector(self.Idir.Value.currentText()),
            V_dir=self.parse_vector(self.Vdir.Value.currentText()),
            # PIMM and VSD
            spectrum_len=spectrum_len,
            SD_freqs=SD_freqs.tolist(),
            PIMM_freqs=PIMM_freqs.tolist(),
            PIMM_delta_f=PIMM_delta_f,
            stimulus_json=self.to_json()
        )
        return so

    def H_mode_changed(self):
        mode = self.HMode.Value.currentText()
        for i in self.stimulus_objects[1:16]:
            i.hide()
        if mode == SweepMode.H:
            for i in [self.HMin, self.HSteps, self.HMax, self.HBack, self.HPhi, self.HTheta]:
                i.show()

        if mode == SweepMode.PHI:
            for i in [self.H, self.HPhiMin, self.HPhiSteps, self.HPhiMax, self.HPhiBack, self.HTheta]:
                i.show()

        if mode == SweepMode.THETA:
            for i in [self.H, self.HPhi, self.HThetaMin, self.HThetaSteps, self.HThetaMax, self.HThetaBack]:
                i.show()
