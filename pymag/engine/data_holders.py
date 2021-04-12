import json
import os
from re import M

from pymag.engine.utils import get_stimulus
from typing import Any, Dict, List, Union
import numpy as np
import pandas as pd

from abc import ABC, abstractclassmethod, abstractmethod
import cmtj


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


class ExperimentData(GenericHolder):
    def __init__(self, name: str, H: Union[List[float], np.ndarray],
                 f: Union[List[float], np.ndarray]) -> None:
        self.H = H
        self.f = f
        self.name = name

    @classmethod
    def from_csv(cls, filename):
        bsn = os.path.basename(filename)
        df = pd.read_csv(filename, sep='\t')
        return cls(name=bsn, H=df['H'], f=df['f'])


class ResultHolder(GenericHolder):
    def __init__(self, mode, H_mag, m_avg, m_traj, PIMM, PIMM_freqs, SD,
                 SD_freqs, Rx, Ry, Rz) -> None:
        self.mode = mode
        self.H_mag = H_mag
        self.m_avg = np.expand_dims(m_avg, axis=0)

        self.Rx = [Rx]
        self.Ry = [Ry]
        self.Rz = [Rz]

        self.SD = np.asarray(SD).reshape(-1, len(SD_freqs))
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
        :param filename
        Save results:
        Dynamics
        Spin Diode
        PIMM 
        to a file
        """
        print(self.PIMM.shape, len(self.PIMM_freqs[:]))
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
            spin_diode.to_csv(filename + "_SD.csv", index=False)
        except Exception as e:
            print(f"Failed to export spin diode: {e}")
        try:
            pimm = pd.DataFrame(data=self.PIMM,
                                columns=self.PIMM_freqs[:self.PIMM.shape[1]],
                                index=self.H_mag)
            pimm.to_csv(filename + "_PIMM.csv", index=False)
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

    def to_cmtj(self) -> cmtj.Layer:
        N = [
            cmtj.CVector(self.N[0], 0, 0),
            cmtj.CVector(0, self.N[1], 0),
            cmtj.CVector(0, 0, self.N[2])
        ]
        clayer = cmtj.Layer(
            id=str(self.layer),
            mag=cmtj.CVector(*self.mag),
            anis=cmtj.CVector(*self.Kdir.tolist()),
            Ms=self.Ms,
            thickness=self.th,
            cellSurface=0,
            temperature=0,
            dipoleTensor=[cmtj.CVector(*self.dipole[i]) for i in range(3)],
            demagTensor=N,
            includeSTT=0,
            damping=self.alpha)
        clayer.setAnisotropyDriver(cmtj.ScalarDriver.getConstantDriver(
            self.Ku))
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
                 mag=[0, 0, 1],
                 dipole=[[0, 0, 0], [0, 0, 0], [0, 0, 0]]):
        parsed_Kdir = Layer.parse_list(Kdir)
        parsed_N = Layer.parse_list(N)
        return cls(layer, alpha, parsed_Kdir, Ku, Ms, J, parsed_N, th, AMR,
                   SMR, AHE, Rx0, Ry0, w, l, mag, dipole)

    def to_gui(self):
        headers = [
            "layer",
            "Ms",
            "Ku",
            "Kdir",
            "J",
            "alpha",
            "N",
            "th",
            "AMR",
            "SMR",
            "AHE",
            "Rx0",
            "Ry0",
            "w",
            "l",
        ]
        res = {}
        for itm in headers:
            _itm = getattr(self, itm)
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


class Stimulus(GenericHolder, GUIObject):
    def __init__(self, data):
        self.org_data = data
        self.back = np.array(data["Hback"].values[0], dtype=np.int)
        if data["H"].values[1] != "-" and data["HPhi"].values[
                1] == "-" and data["HTheta"].values[1] == "-":
            self.mode = "H"
            self.STEPS = np.array(data["H"].values[1], dtype=np.float32)
            self.Hmin = np.array(data["H"].values[0], dtype=np.float32)
            self.Hmax = np.array(data["H"].values[2], dtype=np.float32)
            self.ThetaMin = np.array(data["HTheta"].values[0],
                                     dtype=np.float32)
            self.ThetaMax = np.array(data["HTheta"].values[0],
                                     dtype=np.float32)
            self.PhiMin = np.array(data["HPhi"].values[0], dtype=np.float32)
            self.PhiMax = np.array(data["HPhi"].values[0], dtype=np.float32)

        elif data["HPhi"].values[1] != "-" and data["H"].values[
                1] == "-" and data["HTheta"].values[1] == "-":
            self.mode = "phi"
            self.STEPS = np.array(data["HPhi"].values[1], dtype=np.float32)
            self.Hmin = np.array(data["H"].values[0], dtype=np.float32)
            self.Hmax = np.array(data["H"].values[0], dtype=np.float32)
            self.ThetaMin = np.array(data["HTheta"].values[0],
                                     dtype=np.float32)
            self.ThetaMax = np.array(data["HTheta"].values[0],
                                     dtype=np.float32)
            self.PhiMin = np.array(data["HPhi"].values[0], dtype=np.float32)
            self.PhiMax = np.array(data["HPhi"].values[2], dtype=np.float32)
        elif data["HTheta"].values[1] != "-" and data["H"].values[
                1] == "-" and data["HPhi"].values[1] == "-":
            self.mode = "theta"
            self.STEPS = np.array(data["HTheta"].values[1], dtype=np.float32)
            self.Hmin = np.array(data["H"].values[0], dtype=np.float32)
            self.Hmax = np.array(data["H"].values[0], dtype=np.float32)
            self.ThetaMin = np.array(data["HTheta"].values[0],
                                     dtype=np.float32)
            self.ThetaMax = np.array(data["HTheta"].values[2],
                                     dtype=np.float32)
            self.PhiMin = np.array(data["HPhi"].values[0], dtype=np.float32)
            self.PhiMax = np.array(data["HPhi"].values[0], dtype=np.float32)
        else:
            print("Stimulus error")
        self.H_sweep, self.Hmag = get_stimulus(self.Hmin, self.Hmax,
                                               self.ThetaMin, self.ThetaMax,
                                               self.PhiMin, self.PhiMax,
                                               self.STEPS, self.back,
                                               self.mode)
        self.fmin = np.array(data["f"].values[0], dtype=np.float32)
        self.fsteps = np.array(data["f"].values[1], dtype=np.int)
        self.fmax = np.array(data["f"].values[2], dtype=np.float32)
        self.LLG_time = np.array(data["LLGtime"].values[0], dtype=np.float32)
        self.LLG_steps = int(
            np.array(data["LLGsteps"].values[0], dtype=np.float32))
        self.SD_freqs = np.linspace(self.fmin, self.fmax, self.fsteps)
        self.spectrum_len = (self.LLG_steps) // 2
        self.PIMM_delta_f = 1 / self.LLG_time

        self.PIMM_freqs = np.arange(0,
                                    self.PIMM_delta_f * self.LLG_steps,
                                    step=self.PIMM_delta_f)
        self.fphase = np.array(data["fphase"].values[0], dtype=np.float32)

    def to_dict(self) -> Dict[str, Any]:
        return {
            # "f": self.
            "H_sweep": self.H_sweep,
            "SD_freqs": self.SD_freqs,
            "LLG_steps": self.LLG_steps,
            "LLG_time": self.LLG_time,
            "PIMM_delta_f": self.PIMM_delta_f,
            "H_mag": self.Hmag,
            "spectrum_len": self.spectrum_len,
            "mode": self.mode
        }

    def to_gui(self) -> List:
        return self.org_data.to_dict(orient="records")

    @classmethod
    def from_gui(cls, **kwargs):
        return super().from_gui(**kwargs)


class SimulationInput(GenericHolder):
    def __init__(self, layers: List[Layer], stimulus: Stimulus) -> None:
        self.layers = layers
        self.stimulus = stimulus
