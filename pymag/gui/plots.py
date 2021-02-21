from pymag.engine.utils import H_unit
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore

import numpy as np
import pandas as pd
H_unit = "A/m"


class ResPlot():
    def __init__(self):
        self.plotsRes = pg.GraphicsLayoutWidget()
        self.plotsRes.setGeometry(QtCore.QRect(0, 0, 600, 300))
        self.plotsRes.nextRow()
        self.Rx = self.plotsRes.addPlot()
        self.Rx.setLabel('left', "Rxx", units='\u03A9')
        self.Rx.enableAutoRange('x', True)
        self.Rx.showGrid(x=True, y=True, alpha=0.6)
        self.plotsRes.nextRow()
        self.Ry = self.plotsRes.addPlot()
        self.Ry.setLabel('left', "Rxy", units='\u03A9')
        self.Ry.enableAutoRange('x', True)
        self.Ry.showGrid(x=True, y=True, alpha=0.6)
        self.plotsRes.nextRow()
        self.Rz = self.plotsRes.addPlot()
        self.Rz.setLabel('bottom', "Field", units=H_unit)
        self.Rz.setLabel('left', "Rzz CPP G(T)MR", units='\u03A9')
        self.Rz.enableAutoRange('x', True)
        self.Rz.showGrid(x=True, y=True, alpha=0.6)
        self.Rx.setXLink(self.Ry)
        self.Ry.setXLink(self.Rz)
        self.plotsRes.setBackground('w')

    def clear_plots(self):
        self.Rx.clear()
        self.Ry.clear()
        self.Rz.clear()

    def set_mode(self, mode):
        if mode == "H":
            self.Rz.setLabel('bottom', "Field", units=H_unit)
        elif mode == "phi":
            self.Rz.setLabel('bottom', "Phi angle", units="deg")
        elif mode == "theta":
            self.Rz.setLabel('bottom', "Theta angle", units="deg")


class LineShape():
    def __init__(self):
        self.plotsLS = pg.GraphicsLayoutWidget()
        self.plotsLS.setGeometry(QtCore.QRect(0, 0, 600, 300))
        self.legenda = 0
        self.LS = self.plotsLS.addPlot()
        self.LS.setLabel('bottom', "Field", units=H_unit)
        self.LS.setLabel('left',
                         "SD voltage with artificial offset",
                         units='V')
        self.LS.enableAutoRange('x', True)
        self.LS.showGrid(x=True, y=True, alpha=0.6)
        ###RAPORT
        # self.a = self.LS.addLegend()
        self.plotsLS.setBackground('w')

    def update(self, spectrogramData, deltaf, H):
        self.spectrogramData = spectrogramData
        self.deltaf = deltaf
        self.H = H
        self.clear_plots()
        offset = 0
        a = 4
        b = 24
        for ff in range(a, b):
            curr_LS = self.spectrogramData[:, ff] - np.min(
                self.spectrogramData[:, ff])
            self.LS.plot(self.H,
                         curr_LS + offset,
                         pen={
                             'color': (0, int(
                                 ((ff - a) / (b - a)) * 255), 255 - int(
                                     ((ff - a) / (b - a)) * 255), 255),
                             'width':
                             2
                         })
            offset = offset + (np.max(curr_LS) - np.min(curr_LS)) * 1.05

    def update_experimental(self, spectrogramData, deltaf, H):
        df = pd.read_csv("4651_Pymag/8/SD.dat", sep="\t")
        self.spectrogramData = np.array(df.values, dtype=np.float32)
        self.H = np.array(df["H"].values)
        self.deltaf = 2e9
        self.clear_plots()
        offset = 0
        a = 0
        b = 24
        for ff in range(a, b):
            curr_LS = self.spectrogramData[:, ff] - np.min(
                self.spectrogramData[:, ff])
            self.LS.plot(self.H,
                         curr_LS + offset,
                         pen={
                             'color': (0, int(
                                 ((ff - a) / (b - a)) * 255), 255 - int(
                                     ((ff - a) / (b - a)) * 255), 255),
                             'width':
                             2
                         })
            offset = offset + (np.max(curr_LS) - np.min(curr_LS)) * 1.05

    def set_mode(self, mode):
        if mode == "H":
            self.LS.setLabel('bottom', "Field", units=H_unit)
        elif mode == "phi":
            self.LS.setLabel('bottom', "Phi angle", units="deg")
        elif mode == "theta":
            self.LS.setLabel('bottom', "Theta angle", units="deg")

    def clear_plots(self):
        # self.legenda = 0
        self.LS.clear()


class MagPlot():
    def __init__(self):
        self.plotsMag = pg.GraphicsLayoutWidget()
        self.plotsMag.setGeometry(QtCore.QRect(0, 0, 600, 300))
        self.plotsMag.nextRow()
        self.Mx = self.plotsMag.addPlot()
        self.Mx.setLabel('left', "Mx", units='T')
        self.Mx.enableAutoRange('x', True)
        self.Mx.showGrid(x=True, y=True, alpha=0.6)
        self.plotsMag.nextRow()
        self.My = self.plotsMag.addPlot()
        self.My.setLabel('left', "My", units='T')
        self.My.enableAutoRange('x', True)
        self.My.showGrid(x=True, y=True, alpha=0.6)
        self.plotsMag.nextRow()
        self.Mz = self.plotsMag.addPlot()
        self.Mz.setLabel('bottom', "Field", units=H_unit)
        self.Mz.setLabel('left', "Mz", units='T')
        self.Mz.enableAutoRange('x', True)
        self.Mz.showGrid(x=True, y=True, alpha=0.6)
        self.Mx.setXLink(self.My)
        self.My.setXLink(self.Mz)
        self.plotsMag.setBackground('w')

    def clear_plots(self):
        self.Mx.clear()
        self.My.clear()
        self.Mz.clear()

    def set_mode(self, mode):
        if mode == "H":
            self.Mz.setLabel('bottom', "Field", units=H_unit)
        elif mode == "phi":
            self.Mz.setLabel('bottom', "Phi angle", units="deg")
        elif mode == "theta":
            self.Mz.setLabel('bottom', "Theta angle", units="deg")


class PlotDynamics():
    def __init__(self):
        self.plot_dynamics_view = pg.GraphicsLayoutWidget()
        self.plot_dynamics_view.setGeometry(QtCore.QRect(0, 0, 600, 300))
        self.plots_spectrum = self.plot_dynamics_view.addPlot(title="Spectrum")
        self.plots_spectrum.setLabel('left', "Frequency", units='Hz')
        self.plots_spectrum.setLabel('bottom', "Field", units='A/m')
        self.image_view_spectrum = pg.ImageView()
        self.plot_dynamics_view.setBackground('w')
        self.image_spectrum = self.image_view_spectrum.getImageItem()
        self.plots_spectrum.addItem(self.image_spectrum)
        self.plots_spectrum.setYRange(0, 20e9, padding=0)
        self.plots_spectrum.showGrid(x=True, y=True, alpha=0.6)
        self.image_spectrum.resetTransform()
        self.image_spectrum.translate(-20e3, 0)
        self.image_spectrum.scale((20e3 + 20e3) / 20, 1 / 20e9)
        self.hist_SD = pg.HistogramLUTItem()
        self.hist_SD.setImageItem(self.image_spectrum)
        self.hist_SD.vb.disableAutoRange()
        colors = [(22, 0, 70), (47, 0, 135), (98, 0, 164), (146, 0, 166),
                  (186, 47, 138), (216, 91, 105), (238, 137, 73),
                  (246, 189, 39), (228, 250, 211)]
        cmap = pg.ColorMap(pos=np.linspace(0.0, 1.0, 9), color=colors)
        self.image_view_spectrum.setColorMap(cmap)
        self.hist_SD.gradient.setColorMap(cm=cmap)
        self.inf1_SD = pg.InfiniteLine(movable=True,
                                       angle=0,
                                       label='x={value:0.2f}',
                                       pos=[0, 1e9],
                                       bounds=[0, 100e9],
                                       labelOpts={
                                           'position': 5e9,
                                           'color': (200, 200, 100),
                                           'fill': (200, 200, 200, 50),
                                           'movable': True
                                       })
        self.inf1_SD.sigPositionChanged.connect(self.update_roi_loc)
        self.plots_spectrum.addItem(self.inf1_SD)
        self.plot_dynamics_view.addItem(self.hist_SD)
        self.hist_SD.setLevels(-0.001, 0.01)
        self.hist_SD.autoHistogramRange()

    def init_setup(self, Xmin, Xmax, Xsteps, dy):
        self.image_spectrum.clear()
        self.image_spectrum.resetTransform()
        self.image_spectrum.translate(Xmin, 0)
        self.image_spectrum.scale((Xmax - Xmin) / Xsteps, dy)

    def update(self, spectrogramData, deltaf, H, rm_bkg=0):
        if rm_bkg == 1:
            self.spectrogramData = spectrogramData
            self.spectrogramData2 = spectrogramData * 0
            for ff in range(0, spectrogramData.shape[1]):
                self.spectrogramData2[:,
                                      ff] = spectrogramData[:, ff] - np.median(
                                          spectrogramData[:, ff])
                self.image_spectrum.setImage(
                    self.spectrogramData2, autoLevels=False
                )  # , autoHistogramRange=False,levels=[3, 6])
            del self.spectrogramData2
        else:
            self.spectrogramData = spectrogramData
            self.image_spectrum.setImage(self.spectrogramData,
                                         autoLevels=False)
        self.deltaf = deltaf
        self.H = H
        # self.set_mode(mode)
        self.update_roi_loc()

    def set_mode(self, mode):
        if mode == "H":
            self.plots_spectrum.setLabel('bottom', "Field", units=H_unit)
        elif mode == "phi":
            self.plots_spectrum.setLabel('bottom', "Phi angle", units="deg")
        elif mode == "theta":
            self.plots_spectrum.setLabel('bottom', "Theta angle", units="deg")

    def update_roi_loc(self):
        try:
            self.plotLineShape.clear()
            self.plotLineShape.plot(
                self.H,
                self.spectrogramData[:,
                                     int(self.inf1_SD.value() / self.deltaf)],
                pen=(255, 255, 255))
        except:
            pass

    def clear_plots(self):
        self.image_spectrum.clear()
        self.plots_spectrum.clear()  ########
        try:
            self.plots_spectrum.addItem(self.inf1_SD)
            self.plots_spectrum.addItem(self.image_spectrum)
            self.plotLineShape.clear()
        except:
            pass
        try:
            del (self.spectrogramData)
        except:
            pass