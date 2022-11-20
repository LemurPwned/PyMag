# Welcome to PyMag documentation

This is a frontend GUI for some of the `cmtj` functionalities. It's possible that you will be able to simulate most of your experiments here if you use:

- SD-FMR
- Harmonic Hall voltage
- PIMM

techniques for your expeirments.

## Requirements

- Python 3.6 or higher
- PyQt6 (`pip install pyqt6`) -- installing `PyMag` should automatically install `PyQt6` as well
- `cmtj` -- installing `PyMag` should automatically install `cmtj` as well

## Quickstart

For quick installation you only need to install the package first:

- From Github repository

```bash
git clone https://github.com/LemurPwned/PyMag
cd PyMag
pip3 install .
```

### Example

You can find a sample simulation description in [docs/example.md](./example.md).

## Running

You can launch anywhere with a simple command

```bash
python3 -m pymag run
```

It's possible to `alias` that for a quicker run:

```bash
alias pymag "python3 -m pymag run"
```

For persistence add this to your `.bashrc` if you're on Linux. On Windows you may simply create a shortcut.

---

## Parameters

Here's an explanation of the parameters in the table:
| Parameter                   | Meaning                               |
| --------------------------- | ------------------------------------- |
| $\mu_0 M_\mathrm{s}$        | Magnetisation saturation              |
| $J_1$                       | IEC value                             |
| $J_2$                       | IEC value (quadratic term)            |
| $K_{u}$                     | Anisotropy value                      |
| $\mathbf{K}_{dir}$          | Anisotropy axis                       |
| $\alpha_\mathrm{G}$         | Gilbert damping parameter             |
| $\mathbf{N}_\mathrm{demag}$ | diagonal of demagnetisation tensor    |
| $t_\mathrm{FM}$             | thickness of a FM layer               |
| $w$                         | width of a sample                     |
| $l$                         | length of the sample                  |
| $H_\mathrm{DL}$             | magnitude of the damping-like torque  |
| $H_\mathrm{FL}$             | magnitude of the field-like torque    |
| $H_\mathrm{Oe}$             | magnitude of the Oersted field in 1/m |
| $\mathbf{p}$                | polarisation vector                   |

The Oersted field value is multiplied by the current value in the code, hence the unit is 1/m (1/m \* A = A/m).

## Resistance

For the interpretation of the remaining resistance, please refer to the supplementary material of the paper [Kim et al. (2016), _Spin Hall Magnetoresistance in Metallic Bilayers_, Phys. Rev. Let. 116, 9, 097201](https://link.aps.org/doi/10.1103/PhysRevLett.116.097201):

- $R_\mathrm{XX0}$
- $R_\mathrm{XY0}$
- $R_\mathrm{AMR}$
- $R_\mathrm{SMR}$
- $R_\mathrm{AHE}$
