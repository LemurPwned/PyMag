import sys

import click
from PyQt6.QtWidgets import QApplication

from pymag import __version__
from pymag.gui.main_window import UIMainWindow


@click.group()
def cli():
    ...


@cli.command(name='run', help='Run Pymag application')
def run_pymag():
    app = QApplication([])
    app.setOrganizationName("PyMag")
    app.setApplicationName(__version__)
    main_window = UIMainWindow()
    # main_window.showMaximized()
    exit_code = app.exec()
    # main_window.save_before_exit()
    sys.exit(exit_code)


if __name__ == "__main__":
    cli()
