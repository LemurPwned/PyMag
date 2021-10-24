import sys
from pydantic import main
from pyqtgraph.Qt import QtGui
from pymag.gui.main_window import UIMainWindow
import click

from pymag import __version__


@click.group()
def cli():
    ...


@cli.command(name='run', help='Run Pymag application')
def run_pymag():
    app = QtGui.QApplication([])
    app.setOrganizationName("PyMag")
    app.setApplicationName(__version__)
    main_window = UIMainWindow()
    # main_window.showMaximized()
    exit_code = app.exec_()
    main_window.save_before_exit()
    sys.exit(exit_code)


if __name__ == "__main__":
    cli()
