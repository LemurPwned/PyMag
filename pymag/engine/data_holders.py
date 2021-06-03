import json
import os
from abc import ABC, abstractclassmethod, abstractmethod
from typing import Any, Dict, List

import cmtj
import numpy as np
import pandas as pd
from pydantic import BaseModel
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


class ResultHolder(GenericHolder):
    def __init__(self, mode, H_mag, m_avg, m_traj, PIMM, PIMM_freqs, SD,
                 SD_freqs, Rx, Ry, Rz) -> None:
        self.mode = mode
        self.H_mag = H_mag
        self.m_avg = np.expand_dims(m_avg, axis=0)

        self.Rx = [Rx]
        self.Ry = [Ry]
        self.Rz = [Rz]
        if len(SD):
            self.SD = np.asarray(SD).reshape(-1, len(SD_freqs))
        else:
            self.SD = np.asarray(SD)
        self.SD_freqs = SD_freqs
        self.PIMM = np.asarray(PIMM).reshape(1, -1)
        self.PIMM_freqs = PIMM_freqs
        self.m_traj = m_traj
        self.update_count = 1

    def merge_result(self, result: 'ResultHolder'):
        self.SD = np.concatenate((self.SD, np.asarray(result.SD)), axis=0)
        self.PIMM = np.concatenate((self.PIMM, np.asarray(result.PIMM)),
                                   axis=0)
        self.m_avg = np.concatenate((self.m_avg, np.asarray(result.m_avg)),
                                    axis=0)

        # take 0 because Rx is an expanding list
        self.Rx.append(result.Rx[0])
        self.Ry.append(result.Ry[0])
        self.Rz.append(result.Rz[0])
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
            spin_diode = pd.DataFrame(data=self.SD,
                                      columns=self.SD_freqs,
                                      index=self.H_mag)
            spin_diode.to_csv(filename + "_SD.csv", index=True)
        except Exception as e:
            print(f"Failed to export spin diode: {e}")
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
                 lam,
                 beta,
                 eng,
                 Hoe,
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
        self.p = p
        self.p = np.asarray(self.p) / np.linalg.norm(self.p)
        self.lam = float(lam)
        self.beta = float(beta)
        self.eng = float(eng)
        self.T = float(T)
        self.Hoe = float(Hoe)

    def to_cmtj(self) -> cmtj.Layer:
        N = [
            cmtj.CVector(self.N[0], 0, 0),
            cmtj.CVector(0, self.N[1], 0),
            cmtj.CVector(0, 0, self.N[2])
        ]
        if self.beta == 0 and self.eng == 0 and self.lam == 0:
            stt_params = {'includeSTT': False}
        else:
            stt_params = {
                "SlonczewskiSpacerLayerParameter": self.lam,
                "includeSTT": True,
                "beta": self.beta,
                "spinPolarisation": self.eng
            }
        clayer = cmtj.Layer(
            id=str(self.layer),
            mag=cmtj.CVector(*self.mag),
            anis=cmtj.CVector(*self.Kdir.tolist()),
            Ms=self.Ms,
            thickness=self.th,
            cellSurface=0,
            temperature=self.T,
            dipoleTensor=[cmtj.CVector(*self.dipole[i]) for i in range(3)],
            demagTensor=N,
            damping=self.alpha,
            **stt_params)
        clayer.setAnisotropyDriver(cmtj.ScalarDriver.getConstantDriver(
            self.Ku))
        clayer.setReferenceLayer(cmtj.CVector(*self.p.tolist()))
        return clayer

    @classmethod
    def from_gui(cls,
                 layer,
                 alpha,
                 Kdir,
                 Ku,
                 Ms,
                 J,
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
                 lam,
                 beta,
                 eng,
                 Hoe,
                 T=0.0,
                 mag=[0, 0, 1],
                 dipole=[[0, 0, 0], [0, 0, 0], [0, 0, 0]]):
        parsed_Kdir = Layer.parse_list(Kdir)
        parsed_N = Layer.parse_list(N)
        parsed_p = Layer.parse_list(p)
        return cls(layer=layer,
                   alpha=alpha,
                   Kdir=parsed_Kdir,
                   Ku=Ku,
                   Ms=Ms,
                   J=J,
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
                   lam=lam,
                   beta=beta,
                   eng=eng,
                   Hoe=Hoe,
                   T=T,
                   mag=mag,
                   dipole=dipole)

    def to_gui(self):
        headers = [
            "layer", "Ms", "Ku", "Kdir", "J", "alpha", "N", "th", "AMR", "SMR",
            "AHE", "Rx0", "Ry0", "w", "l", "p", "lam", "beta", "eng", "Hoe"
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


class SimulationInput(GenericHolder):
    def __init__(self, layers: List[Layer], stimulus: StimulusObject) -> None:
        self.layers = layers
        self.stimulus = stimulus
