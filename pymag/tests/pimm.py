import cProfile
import io
import pstats
import time as tm

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable
from pymag.engine.data_holders import Layer
from pymag.engine.solver import Solver
from pymag.engine.utils import get_stimulus
from scipy.fft import fft

l1 = Layer(0,
           alpha=0.01,
           Ku=305e3,
           Kdir=[0, -0.0871557, 0.996195],
           N=[0, 0, 1],
           th=1e-9,
           Ms=1.07,
           J=4e-5,
           AMR=0,
           SMR=0,
           AHE=0,
           Rx0=0,
           Ry0=0,
           w=0,
           l=0)

l2 = Layer(1,
           alpha=0.01,
           Ku=728e3,
           Kdir=[0.34071865, -0.08715574, 0.936116],
           N=[0, 0, 1],
           th=1e-9,
           Ms=1.07,
           J=0,
           AMR=0,
           SMR=0,
           AHE=0,
           Rx0=0,
           Ry0=0,
           w=0,
           l=0)

layers = [l1, l2]
Hmin = -800e3
Hmax = 800e3
hsteps = 100
frequency = 0
LLG_steps = 2000
LLG_time = 8e-9
theta = 89.9
phi = 45
H, _ = get_stimulus(Hmin=Hmin,
                    Hmax=Hmax,
                    ThetaMin=theta,
                    ThetaMax=theta,
                    PhiMin=phi,
                    PhiMax=phi,
                    STEPS=hsteps,
                    back=False,
                    mode="H")


def profile_PIMM():
    pr = cProfile.Profile()
    pr.enable()
    for Hval in reversed(H):
        _, _, _, _, _, _, _, _ = Solver.calc_trajectoryRK45(
            layers=layers,
            m_init=[[1, 1, 0], [1, 1, 0]],
            Hext=Hval,
            f=frequency,
            I_amp=0,
            LLG_time=LLG_time,
            LLG_steps=LLG_steps)
    pr.disable()
    s = io.StringIO()
    sortby = pstats.SortKey.CUMULATIVE
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())


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

    final_PIMM = []
    m = None
    start = tm.time()
    for Hval in reversed(H):
        m, _, _, _, _, _, _, PIMM_ = Solver.calc_trajectoryRK45(
            layers=layers,
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
