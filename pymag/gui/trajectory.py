import pyqtgraph.opengl as gl
import numpy as np
import pyqtgraph as pg


class TrajectoryPlot():
    def __init__(self):
        self.w = gl.GLViewWidget()
        self.init_GL_settings()
        self.w.setBackgroundColor('w')

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
                           color=(0.7, 0.7, 0.7, 0.7),
                           shader='balloon')  #, glOptions='additive'
        m1.translate(0, 0, 0)
        m1.scale(1, 1, 1)
        self.w.addItem(m1)

    def plt_traj(self, traj, colory):
        plt = gl.GLLinePlotItem(pos=np.array(traj),
                                color=pg.glColor(colory),
                                width=(0 + 1) / 10.,
                                antialias=True)
        self.w.addItem(plt)

    def plt_point(self, x, y, z):
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