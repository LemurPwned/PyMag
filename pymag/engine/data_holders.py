import json

from pyqtgraph.metaarray.MetaArray import axis
from pymag.engine.utils import get_stimulus
from typing import Any, Dict, List
import cmtj
from cmtj import CVector
import numpy as np


class GenericHolder:
    def __init__(self) -> None:
        pass

    def to_json(self, json_file) -> None:
        json.dump(self.to_dict(), open(json_file, "w"))

    def to_dict(self) -> dict:
        return self.__dict__

    @classmethod
    def from_json(cls, json_file):
        cls.from_dict(json.load(open(json_file, "r")))

    @classmethod
    def from_dict(cls, dict_):
        cls(**dict_)


class ResultHolder(GenericHolder):
    def __init__(self, mode, H_mag, m_avg, m_traj, PIMM, PIMM_delta_f, SD,
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
        self.PIMM_delta_f = PIMM_delta_f
        self.m_traj = m_traj
        self.update_count = 1

    def merge_partial_result(self, partial_result: Dict[str, Any]):
        self.SD = np.concatenate((self.SD, np.asarray(partial_result['SD'])),
                                 axis=0)
        self.PIMM = np.concatenate(
            (self.SD, np.asarray(partial_result['PIMM'])), axis=0)
        self.m_avg = np.concatenate(
            (self.m_avg, np.asarray(partial_result['m_avg'])), axis=0)
        for key in ["Rx", "Ry", "Rz"]:
            getattr(self, key).append(partial_result[key])

        self.PIMM_freqs = partial_result['PIMM_freqs']
        self.SD_freqs = partial_result['SD_freqs']

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


class Layer(GenericHolder):
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
        self.Kdir = self.parse_list(Kdir)
        self.Kdir = self.Kdir / np.linalg.norm(self.Kdir)
        self.Ku = float(Ku)
        self.J = float(J)
        self.Ms = float(Ms)
        self.th = float(th)
        self.N = self.parse_list(N)
        self.dipole = dipole
        self.alpha = float(alpha)
        self.AMR = float(AMR)
        self.SMR = float(SMR)
        self.AHE = float(AHE)
        self.Rx0 = float(Rx0)
        self.Ry0 = float(Ry0)
        self.w = float(w)
        self.l = float(l)

    def parse_list(self, str_list: str):
        actual_list = [
            float(i)
            for i in str_list.replace("[", "").replace("]", "").split(" ")
        ]
        return actual_list


class Stimulus():
    def __init__(self, data):
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

    def to_dict(self):
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


class SimulationInput(GenericHolder):
    def __init__(self, layers: List[Layer], stimulus: Stimulus) -> None:
        self.layers = layers
        self.stimulus = stimulus
