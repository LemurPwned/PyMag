from pymag.engine.utils import get_stimulus2
from typing import final
import matplotlib.pyplot as plt
from pymag.engine.solver import Solver
import numpy as np
from scipy.fft import fft
from mpl_toolkits.axes_grid1 import make_axes_locatable
import time as tm

def run_PIMM():
    device = {
        "Ms": [1.07, 1.07],
        "Ku": [305e3, 728e3],
        "J": [4e-5, 0],
        "th": [1e-9, 1e-9],
        "Kdir": [[0, -0.0871557, 0.996195],
                 [0.34071865, -0.08715574, 0.936116]],
        "Ndemag": [[0, 0, 0], [0, 0, 0], [0, 0, 1]],
        "alpha": [0.01, 0.01],
        "number_of_layers": 2
    }

    #     CVector(0.00022708623583019705, 0., 0.),
    # CVector(0., 0.0011629799534817735, 0.),
    # CVector(0., 0., 0.99861)
    Hmin = -800e3
    Hmax = 800e3
    hsteps = 100
    frequency = 0
    LLG_steps = 2000
    LLG_time = 8e-9
    theta = 90
    phi = 45
    H, _ = get_stimulus2(Hmin=Hmin,
                         Hmax=Hmax,
                         ThetaMin=theta,
                         ThetaMax=theta,
                         PhiMin=phi,
                         PhiMax=phi,
                         STEPS=hsteps,
                         back=False,
                         mode="H")
    final_PIMM = []
    m = None
    start = tm.time()
    for Hval in H:
        m, _, _, _, _, _, _, PIMM_ = Solver.calc_trajectoryRK45(
            device["Ku"],
            device["Ms"],
            device["J"],
            device["th"],
            device["Kdir"],
            np.asarray(device["Ndemag"]),
            device["alpha"],
            device["number_of_layers"],
            m_init=m if m is not None else [[1, 1, 0], [1, 1, 0]],
            Hext=Hval,
            f=frequency,
            I_amp=0,
            LLG_time=LLG_time,
            LLG_steps=LLG_steps)
        yf = np.abs(fft(PIMM_))
        final_PIMM.append(yf[:len(yf) // 2])
    final_PIMM = np.asarray(final_PIMM)
    stop = tm.time()
    print(f"Time: {stop-start:.2f}")
    fig, ax = plt.subplots(figsize=(10, 10))
    im = ax.imshow(final_PIMM.T,
                   origin='lower',
                   vmin=np.min(final_PIMM),
                   vmax=np.mean(final_PIMM) + np.std(final_PIMM))
    divider = make_axes_locatable(ax)
    cax = divider.append_axes('right', size='5%', pad=0.05)
    fig.colorbar(im, cax=cax, orientation='vertical')
    print(np.asarray(final_PIMM).shape)
    print(final_PIMM.dtype)
    fig.savefig("PIMM.png")
