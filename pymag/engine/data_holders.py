import json
import os
from abc import ABC, abstractclassmethod, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List

import cmtj
import numpy as np
import pandas as pd
from numpy.core.shape_base import vstack
from pydantic import BaseModel
from pydantic.types import Json

from pymag.engine.utils import get_stimulus
from pymag.gui.utils import unicode_subs


class GUIObject(ABC):

    @abstractclassmethod
    def from_gui(cls, **kwargs):
        ...

    @abstractmethod
    def to_gui(self):
        ...


class GenericHolder:

    def to_json(self, json_file) -> None:
        json.dump(self.to_dict(), open(json_file, "w"))

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__

    def to_list(self) -> List:
        asm_list = []
        for el in self.to_dict().values():
            if isinstance(el, np.ndarray):
                asm_list.append(el.tolist())
            else:
                asm_list.append(el)
        return asm_list

    def to_numpy(self) -> np.ndarray:
        return np.array(self.to_dict().values())

    @classmethod
    def from_json(cls, json_file):
        cls.from_dict(json.load(open(json_file, "r")))

    @classmethod
    def from_dict(cls, dict_):
        cls(**dict_)


class ExperimentData(GenericHolder, BaseModel):
    name: str
    H: List[float] = []
    theta: List[float] = []
    phi: List[float] = []
    f: List[float] = []
    Vmix: List[float] = []
    Rx: List[float] = []
    Ry: List[float] = []
    Rz: List[float] = []
    Mx: List[float] = []
    My: List[float] = []
    Mz: List[float] = []
    x: List[float] = []

    @staticmethod
    def from_csv(filename):
        bsn = os.path.basename(filename)
        df: pd.DataFrame = pd.read_csv(filename, sep='\t').astype(float)
        t = df.to_dict(orient='list')
        expr = ExperimentData(name=bsn, **t)
        expr.deduce_change()
        return expr

    def deduce_change(self):
        if len(np.unique(self.H)) <= 1:
            if len(np.unique(self.phi)) > 1:
                self.x = self.phi
            else:
                self.x = self.theta
        else:
            self.x = self.H

    def get_vsd_series(self):
        return self.x, self.Vmix

    def get_m_series(self):
        return self.x, self.Mx, self.My, self.Mz

    def get_r_series(self):
        return self.x, self.Rx, self.Ry, self.Rz

    def get_pimm_series(self):
        return self.x, self.f


@dataclass
class VoltageSpinDiodeData:
    DC: np.ndarray
    FHarmonic: np.ndarray
    SHarmonic: np.ndarray
    FHarmonic_phase: np.ndarray
    SHarmonic_phase: np.ndarray

    def merge_vsd(self, vsd_data: 'VoltageSpinDiodeData', axis: int):
        self.DC = np.concatenate((self.DC, vsd_data.DC), axis=axis)
        self.FHarmonic = np.concatenate((self.FHarmonic, vsd_data.FHarmonic),
                                        axis=axis)
        self.SHarmonic = np.concatenate((self.SHarmonic, vsd_data.SHarmonic),
                                        axis=axis)

        self.FHarmonic_phase = np.concatenate(
            (self.FHarmonic_phase, vsd_data.FHarmonic_phase), axis=axis)
        self.SHarmonic_phase = np.concatenate(
            (self.SHarmonic_phase, vsd_data.SHarmonic_phase), axis=axis)

    def to_csv(self, filename, index: List[str], columns: List[str]):
        for name, values in zip([
                "DC", "First_harmonic", "Second_harmonic",
                "First_harmonic_phase", "Second_harmonic_phase"
        ], [
                self.DC, self.FHarmonic, self.SHarmonic, self.FHarmonic_phase,
                self.SHarmonic_phase
        ]):
            df = pd.DataFrame(data=values, columns=columns, index=index)
            df.to_csv(f"{filename}_{name}.csv", index=True)


class ResultHolder(GenericHolder):

    def __init__(self, mode, H_mag, m_avg, m_traj, PIMM, PIMM_freqs, SD_freqs,
                 Rx, Ry, Rz, L2convergence_dm, Rxx_vsd: VoltageSpinDiodeData,
                 Rxy_vsd: VoltageSpinDiodeData) -> None:
        self.mode = mode
        self.H_mag = H_mag
        self.m_avg = np.expand_dims(m_avg, axis=0)

        self.Rx = [Rx]
        self.Ry = [Ry]
        self.Rz = [Rz]
        self.SD_freqs = SD_freqs
        self.PIMM = np.asarray(PIMM).reshape(1, -1)
        self.PIMM_freqs = PIMM_freqs
        # make place for next ones
        self.m_traj = np.expand_dims(m_traj, axis=0)
        self.update_count = 1
        self.Rxx_vsd = Rxx_vsd
        self.Rxy_vsd = Rxy_vsd
        self.L2convergence_dm = [L2convergence_dm]

    def merge_result(self, result: 'ResultHolder'):
        self.PIMM = np.concatenate((self.PIMM, np.asarray(result.PIMM)),
                                   axis=0)
        self.m_avg = np.concatenate((self.m_avg, np.asarray(result.m_avg)),
                                    axis=0)
        self.m_traj = np.concatenate((self.m_traj, result.m_traj), axis=0)
        # take 0 because Rx is an expanding list
        self.Rx.append(result.Rx[0])
        self.Ry.append(result.Ry[0])
        self.Rz.append(result.Rz[0])
        self.L2convergence_dm.append(result.L2convergence_dm[0])
        self.Rxx_vsd.merge_vsd(result.Rxx_vsd, axis=0)
        self.Rxy_vsd.merge_vsd(result.Rxy_vsd, axis=0)
        self.update_count += result.update_count

    def to_csv(self, filename) -> None:
        """
        :param filename:
        Save results:
        Dynamics
        Spin Diode
        PIMM
        to a file
        """
        try:
            dynamics = pd.DataFrame.from_dict({
                "mx": self.m_avg[:, 0],
                "my": self.m_avg[:, 0],
                "mz": self.m_avg[:, 0],
                "Rx": self.Rx,
                "Ry": self.Ry,
                "Rz": self.Rz,
                "H": self.H_mag
            })
            dynamics.to_csv(filename + "_dynamics.csv", index=False)
        except Exception as e:
            print(f"Failed to export dynamics: {e}")

        try:
            self.Rxx_vsd.to_csv(filename=filename + "SD_Rxx",
                                index=self.H_mag,
                                columns=self.SD_freqs)
        except Exception as e:
            print(f"Failed to export Rxx spin diode: {e}")
        try:
            self.Rxy_vsd.to_csv(filename=filename + "SD_Rxx",
                                index=self.H_mag,
                                columns=self.SD_freqs)
        except Exception as e:
            print(f"Failed to export Rxy spin diode: {e}")
        try:
            pimm = pd.DataFrame(data=self.PIMM,
                                columns=self.PIMM_freqs[:self.PIMM.shape[1]],
                                index=self.H_mag)
            pimm.to_csv(filename + "_PIMM.csv", index=True)
        except Exception as e:
            print(f"Failed to export PIMM: {e}")


class Layer(GenericHolder, GUIObject):

    def __init__(self,
                 layer,
                 alpha,
                 Kdir,
                 Ku,
                 Ms,
                 J,
                 J2,
                 N,
                 th,
                 AMR,
                 SMR,
                 AHE,
                 Rx0,
                 Ry0,
                 w,
                 l,
                 p,
                 h_dl,
                 h_fl,
                 Hoe,
                 Hoedir,
                 T=0.0,
                 mag=[0, 0, 1],
                 dipole=[[0, 0, 0], [0, 0, 0], [0, 0, 0]]) -> None:
        super().__init__()
        self.layer = int(layer)
        self.mag = mag
        self.Kdir = Kdir
        self.Kdir = np.asarray(self.Kdir) / np.linalg.norm(self.Kdir)
        self.Ku = float(Ku)
        self.J = float(J)
        self.J2 = float(J2)
        self.Ms = float(Ms)
        self.th = float(th)
        self.N = np.asarray(N)
        self.dipole = dipole
        self.alpha = float(alpha)
        self.AMR = float(AMR)
        self.SMR = float(SMR)
        self.AHE = float(AHE)
        self.Rx0 = float(Rx0)
        self.Ry0 = float(Ry0)
        self.w = float(w)
        self.l = float(l)
        if any(p):
            self.p = np.asarray(p) / np.linalg.norm(p)
            self.p = self.p.tolist()
        else:
            self.p = p
        self.h_dl = float(h_dl)
        self.h_fl = float(h_fl)
        self.T = float(T)
        self.Hoe = float(Hoe)
        self.Hoedir = [int(x) for x in Hoedir]

    def to_cmtj(self) -> cmtj.Layer:
        N = [
            cmtj.CVector(self.N[0], 0, 0),
            cmtj.CVector(0, self.N[1], 0),
            cmtj.CVector(0, 0, self.N[2])
        ]

        stt_params = {}
        if self.h_dl or self.h_fl:
            stt_params = {
                "fieldLikeTorque": self.h_fl,
                "dampingLikeTorque": self.h_dl
            }
        clayer = cmtj.Layer.createSOTLayer(
            id=str(self.layer),
            mag=cmtj.CVector(*self.mag),
            anis=cmtj.CVector(*self.Kdir.tolist()),
            Ms=self.Ms,
            thickness=self.th,
            cellSurface=10e-18,
            demagTensor=N,
            damping=self.alpha,
            **stt_params)
        clayer.setAnisotropyDriver(cmtj.ScalarDriver.getConstantDriver(
            self.Ku))
        clayer.setReferenceLayer(cmtj.CVector(*self.p))
        return clayer

    @classmethod
    def from_gui(cls,
                 layer,
                 alpha,
                 Kdir,
                 Ku,
                 Ms,
                 J,
                 J2,
                 N,
                 th,
                 AMR,
                 SMR,
                 AHE,
                 Rx0,
                 Ry0,
                 w,
                 l,
                 p,
                 h_dl,
                 h_fl,
                 Hoe,
                 Hoedir,
                 T=0.0,
                 mag=[0, 0, 1],
                 dipole=[[0, 0, 0], [0, 0, 0], [0, 0, 0]]):
        parsed_Kdir = Layer.parse_list(Kdir)
        parsed_N = Layer.parse_list(N)
        parsed_p = Layer.parse_list(p)
        parsed_Hoedir = Layer.parse_list(Hoedir)
        return cls(layer=layer,
                   alpha=alpha,
                   Kdir=parsed_Kdir,
                   Ku=Ku,
                   Ms=Ms,
                   J=J,
                   J2=J2,
                   N=parsed_N,
                   th=th,
                   AMR=AMR,
                   SMR=SMR,
                   AHE=AHE,
                   Rx0=Rx0,
                   Ry0=Ry0,
                   w=w,
                   l=l,
                   p=parsed_p,
                   h_dl=h_dl,
                   h_fl=h_fl,
                   Hoe=Hoe,
                   Hoedir=parsed_Hoedir,
                   T=T,
                   mag=mag,
                   dipole=dipole)

    def to_gui(self):
        headers = [
            "layer", "Ms", "Ku", "Kdir", "J", "J2", "alpha", "N", "th", "AMR",
            "SMR", "AHE", "Rx0", "Ry0", "w", "l", "p", "h_dl", "h_fl", "Hoe",
            "Hoedir"
        ]
        res = {}
        for itm in headers:
            _itm = getattr(self, itm)
            if itm in unicode_subs:
                itm = unicode_subs[itm]
            if isinstance(_itm, np.ndarray):
                res[itm] = _itm.tolist()
            else:
                res[itm] = _itm
        return res

    @staticmethod
    def parse_list(str_list: str):
        actual_list = [
            float(i) for i in str_list.strip().replace("[", "").replace(
                "]", "").replace(",", "").split(" ")
        ]
        return actual_list


class StimulusObject(BaseModel):
    mode: str
    sweep: List[float]
    H_sweep: List[List[float]]

    LLG_steps: int
    LLG_time: float

    I_dc: float
    I_dir: List[int]
    V_dir: List[int]

    I_rf: float
    frequency_min: float
    frequency_max: float
    frequency_steps: int

    PIMM_delta_f: float
    PIMM_freqs: List[float]

    spectrum_len: int
    SD_freqs: List[float]

    stimulus_json: Dict[str, Any]

    def to_gui(self) -> Dict[str, Any]:
        return self.stimulus_json


class SimulationInput(GenericHolder):

    def __init__(self, layers: List[Layer], stimulus: StimulusObject) -> None:
        self.layers = layers
        self.stimulus = stimulus
