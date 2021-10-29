import pyqtgraph.opengl as gl
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from pyqtgraph.widgets.GraphicsLayoutWidget import GraphicsLayoutWidget


class TrajectoryWidget(GraphicsLayoutWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.trajectory_gl = TrajectoryPlot(parent=self)

        self.addPlot(
            self.trajectory_gl.w, row=0, col=0
        )


class TrajectoryPlot:
    def __init__(self, parent=None):
        self.w = gl.GLViewWidget()
        # g = gl.GLGridItem()
        # self.w.addItem(g)
        self.init_GL_settings()
        # self.w.setBackgroundColor('w')

    def init_GL_settings(self):
        self.w.opts['distance'] = 3
        plt = gl.GLLinePlotItem(pos=np.array([[0, 0, 0], [1, 0, 0]]),
                                color=pg.glColor([255, 0, 0]),
                                width=(2),
                                antialias=True)
        self.w.addItem(plt)
        plt = gl.GLLinePlotItem(pos=np.array([[0, 0, 0], [0, 1, 0]]),
                                color=pg.glColor([0, 255, 0]),
                                width=(2),
                                antialias=True)
        self.w.addItem(plt)
        plt = gl.GLLinePlotItem(pos=np.array([[0, 0, 0], [0, 0, 1]]),
                                color=pg.glColor([0, 0, 255]),
                                width=(2),
                                antialias=True)
        self.w.addItem(plt)
        md = gl.MeshData.sphere(rows=20, cols=20)
        m1 = gl.GLMeshItem(meshdata=md,
                           smooth=True,
                           color=(0.7, 0.7, 0.7, 0.2),
                           shader='balloon', glOptions='additive')
        m1.translate(0, 0, 0)
        m1.scale(1, 1, 1)
        self.w.addItem(m1)

    def draw_trajectory(self, traj, color):
        plt = gl.GLLinePlotItem(pos=np.asarray(traj),
                                color=color,
                                width=5,
                                antialias=True)
        self.w.addItem(plt)

    def draw_point(self, x, y, z):
        md = gl.MeshData.sphere(rows=10, cols=10)
        m1 = gl.GLMeshItem(meshdata=md,
                           smooth=True,
                           color=(1, 0, 0, 0.5),
                           shader='balloon',
                           glOptions='additive')
        m1.translate(x, y, z)
        m1.scale(0.05, 0.05, 0.05)
        self.w.addItem(m1)

    def clear(self):
        for item in self.w.items:
            item._setView(None)
        self.w.items = []
        self.w.update()
        self.init_GL_settings()


RES = "resistance"
MAG = "magnetisation"


class CoordinatePlot:
    def __init__(self) -> None:
        self.plot_type = RES

    def plot_coordinates():
        ...
