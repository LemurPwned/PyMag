import numpy as np
from scipy.signal import butter, lfilter
from numpy.linalg import norm

PyMagVersion = "PyMag v. 2.1"
PyMagDate = "28 Oct 2020"
H_unit = "A/m"

gamma = 1.76e11  # 1/(Ts)
mu0 = 1.255e-6  # N/A^2
mu0_x_gamma = gamma * mu0
Am_to_Oe = 79.57


class SimulationStatus:
    KILLED = "KILLED"
    IN_PROGRESS = "IN PROGRESS"
    DONE = "DONE"
    NOT_STARTED = "NOT STARTED"
    ALL_DONE = "ALL_DONE"


class SweepMode:
    H = "H"
    PHI = "Phi"
    THETA = "Theta"


def get_stimulus(H, Hmin, Hmax, theta, ThetaMin, ThetaMax, phi, PhiMin, PhiMax, STEPS, back,
                 mode):
    st = np.sin(np.deg2rad(theta))
    ct = np.cos(np.deg2rad(theta))
    sp = np.sin(np.deg2rad(phi))
    cp = np.cos(np.deg2rad(phi))
    if mode == SweepMode.H:
        steps = int(STEPS)
        x_versor = st * cp
        y_versor = st * sp
        z_versor = ct
        Hmag = np.linspace(Hmin, Hmax, steps)
        Hx = np.around(Hmag * x_versor, decimals=2)
        Hy = np.around(Hmag * y_versor, decimals=2)
        Hz = np.around(Hmag * z_versor, decimals=2)

    elif mode == SweepMode.PHI:
        steps = int(STEPS)
        phi = np.linspace(PhiMin, PhiMax, steps)
        Hx = H * st * cp
        Hy = H * st * sp
        Hz = H * ct + phi * 0 #???
        Hmag = phi

    elif mode == SweepMode.THETA:
        steps = int(STEPS)
        theta = np.linspace(ThetaMin, ThetaMax, steps)
        Hx = H * st * cp
        Hy = H * st * sp
        Hz = H * ct
        Hmag = theta
    else:
        raise ValueError(f"Invalid mode: {mode}")

    if (back != 0):
        Hx = np.append(Hx, -Hx)
        Hy = np.append(Hy, -Hy)
        Hz = np.append(Hz, -Hz)
        Hmag = np.append(Hmag, -Hmag)
    return np.vstack((Hx, Hy, Hz)).T, Hmag


def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a


def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data, zi=None)
    return y


def cos_between_arrays(vec1, vec2):
    return np.dot(np.array(vec1), np.array(vec2)) / (norm(
        np.array(vec1) * norm(np.array(vec2))))


def normalize(vector):
    return vector / (vector[0]**2 + vector[1]**2 + vector[2]**2)**0.5
