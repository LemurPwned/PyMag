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
