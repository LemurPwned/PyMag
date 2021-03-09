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


def get_stimulus2(Hmin, Hmax, ThetaMin, ThetaMax, PhiMin, PhiMax, STEPS, back,
                  mode):

    if mode == "H":
        theta = ThetaMin
        phi = PhiMin
        steps = int(STEPS)
        x_versor = np.sin(np.deg2rad(theta)) * np.cos(np.deg2rad(phi))
        y_versor = np.sin(np.deg2rad(theta)) * np.sin(np.deg2rad(phi))
        z_versor = np.cos(np.deg2rad(theta))
        Hx = np.around(np.linspace(Hmin, Hmax, steps) * x_versor, decimals=2)
        Hy = np.around(np.linspace(Hmin, Hmax, steps) * y_versor, decimals=2)
        Hz = np.around(np.linspace(Hmin, Hmax, steps) * z_versor, decimals=2)
        Hmag = (Hx**2 + Hy**2 + Hz**2)**0.5 * np.sign(
            np.cos(np.arctan2(Hx, Hy)))

    elif mode == "phi":
        theta = ThetaMin
        H = Hmin
        steps = int(STEPS)
        phi = np.linspace(PhiMin, PhiMax, steps)
        Hx = H * np.sin(np.deg2rad(theta)) * np.cos(np.deg2rad(phi))
        Hy = H * np.sin(np.deg2rad(theta)) * np.sin(np.deg2rad(phi))
        Hz = H * np.cos(np.deg2rad(theta)) + phi * 0
        Hmag = phi

    elif mode == "theta":
        phi = PhiMin
        H = Hmin
        steps = int(STEPS)
        theta = np.linspace(ThetaMin, ThetaMax, steps)
        Hx = H * np.sin(np.deg2rad(theta)) * np.cos(np.deg2rad(phi))
        Hy = H * np.sin(np.deg2rad(theta)) * np.sin(np.deg2rad(phi))
        Hz = H * np.cos(np.deg2rad(theta))
        Hmag = theta

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
    y = lfilter(b, a, data)
    return y


def cos_between_arrays(vec1, vec2):
    return np.dot(np.array(vec1), np.array(vec2)) / (norm(
        np.array(vec1) * norm(np.array(vec2))))


def normalize(vector):
    return vector / (vector[0]**2 + vector[1]**2 + vector[2]**2)**0.5
