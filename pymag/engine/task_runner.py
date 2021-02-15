import json
import time as tm
from typing import Callable

import matplotlib.pyplot as plt
import numpy as np
import requests


def submit_task(task: dict) -> dict:
    """
    Submit a task to the server
    :param task
        a dictionary of parameters that define a task
    """
    url = f"http://localhost:8080/queue"
    payload = json.dumps(task)
    headers = {'Content-Type': 'application/json'}
    response = requests.request("POST", url, headers=headers,
                                data=payload).json()
    uuid = response['uuid']
    return receive(uuid)


def receive(task_uuid: str) -> dict:
    while True:
        url = f"http://localhost:8080/task?uuid={task_uuid}"
        response = requests.request("GET", url).json()
        if response['code'] != 404:
            return response
        tm.sleep(0.5)


def compose_vsd_spectrogram(data: dict, task_def: dict):
    """
    Given a vsd task, it composes a spectrogram and
    saves it to a file. X axis -- field, Y axis -- frequency
    ** WARNING ** Only works when frequencies % threads == 0!
    Otheriwse, there will be artefacts and other functions must be used
    :param data
        result from the CTMJ server
    """
    # fetch all the data from the dict
    f = data['frequencies']
    h = data[task_def['parameters']['mode']]
    fsteps = data['fsteps']
    hsteps = data['steps']
    Vmix = data['Vmix']

    # sort, since threads may return in various orders
    f, h, Vmix = zip(*sorted(zip(f, h, Vmix), reverse=False))
    f = np.asarray(f).reshape(hsteps, -1)
    h = np.asarray(h).reshape(hsteps, -1)
    Vmix = np.asarray(Vmix).reshape(fsteps, -1)
    return Vmix, f, h


# def compose_max_PIM(data: dict, task_def: dict):
#     """
#     Creates PIM dispersion relation
#     :param data
#         result from the CTMJ server do domu!
#     """
#     fields, max_frequencies = [], []
#     freqs = data['frequencies']
#     for r in data['pim']:
#         fields.append(r[task_def['parameters']['mode']])
#         indx = np.argmax(r['amplitude'])
#         max_frequencies.append(freqs[indx])
#
#     fields, max_frequencies = zip(*sorted(zip(fields, max_frequencies)))
#     # fig, ax = plt.subplots()
#     # ax.plot(fields, max_frequencies, 'd-', color='r')
#     # ax.set_xlabel("H [A/m]")
#     # ax.set_ylabel("Max f [Hz]")
#     # fig.savefig("PIM.png")


def compose_max_PIM(data: dict, task_def: dict):
    """
    Creates PIM dispersion relation
    :param data
        result from the CTMJ server
    """
    fields, z_free, z_bottom = [], [], []
    res, mag1, mag2 = [], [], []
    freqs = data['frequencies']
    for r in data['pim']:
        fields.append(r[task_def['parameters']['mode']])
        z_free.append(r['free_mz_amplitude'])  # vektor amplitud dla H = x
        z_bottom.append(r['free_mz_amplitude'])
        res.append(r['res'])
        mag1.append(r['mags'][:3])
        mag2.append(r['mags'][3:6])

    fields, z_free, z_bottom, res, mag1, mag2 = zip(
        *sorted(zip(fields, z_free, z_bottom, res, mag1, mag2)))
    return np.asarray(fields), np.asarray(freqs), np.asarray(
        z_free), np.asarray(z_bottom), np.asarray(res), np.asarray(
            mag1), np.asarray(mag2)


def run_task(task_file: str, task_fn: Callable):
    """
    Run a task file and then produce some result
    """
    task = json.load(open(task_file, 'r'))
    result = submit_task(task)
    if result['code'] != 200:
        raise ValueError(f"Invalid task: {result}")

    task_fn(result['result'], task)


def run_task_json(json_data, task_fn: Callable):
    """
    Run a task file and then produce some result
    """
    task = json_data
    result = submit_task(task)
    if result['code'] != 200:
        raise ValueError(f"Invalid task: {result}")

    return task_fn(result['result'], task)


if __name__ == "__main__":
    run_task("./vsd_task.json", compose_vsd_spectrogram)
    # run_task("./pim_task.json", compose_max_PIM)