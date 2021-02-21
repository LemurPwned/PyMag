import json
from typing import List
import cmtj
from cmtj import CVector


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
    def __init__(
        self,
        mode,
        H_mag,
        m_avg,
        traj,
        PIMM,
        PIMM_freqs,
        SD,
        SD_freqs,
        Rx,
        Ry,
        Rz,
    ) -> None:
        self.mode = mode
        self.H_mag = H_mag
        self.m_avg = m_avg
        self.Rx = Rx
        self.Ry = Ry
        self.Rz = Rz

        self.SD = SD
        self.SD_freqs = SD_freqs
        self.PIMM = PIMM
        self.PIMM_freqs = PIMM_freqs
        self.traj = traj

    def update_result(self):
        pass


class Layer(GenericHolder):
    def __init__(self,
                 mag,
                 kdir,
                 Ku,
                 Ms,
                 J,
                 th,
                 demag,
                 dipole=[[0, 0, 0], [0, 0, 0], [0, 0, 0]]) -> None:
        super().__init__()
        self.mag = mag
        self.kdir = kdir
        self.Ku = Ku
        self.J = J
        self.Ms = Ms
        self.th = th
        self.dipole = dipole
        self.demag = demag

    def to_cmtj(self, id: str) -> cmtj.Layer:
        return cmtj.Layer("0", cmtj.CVector(*self.mag),
                          cmtj.CVector(*self.kdir), self.Ku, self.Ms, self.J,
                          self.th, self.demag, self.dipole, 0, False)


class Stimulus(GenericHolder):
    def __init__(self):
        pass


class SimulationInput(GenericHolder):
    def __init__(self, layers: List[Layer], stimulus: Stimulus) -> None:
        self.layers = layers
        self.stimulus = stimulus
         
