from pymag.engine.utils import H_unit
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore

import numpy as np
import pandas as pd

H_unit = "A/m"


class MultiplePlot():
    def __init__(self, left, number_of_plots, y_unit='\u03A9'):
        self.number_of_plots = number_of_plots
        self.plot_area = pg.GraphicsLayoutWidget()
        self.plot_area.setGeometry(QtCore.QRect(0, 0, 600, 300))
        self.plot_area.nextRow()
        self.plot_area.setBackground('w')
        self.plots = []

        for i in range(0, number_of_plots):
            self.plots.append(self.plot_area.addPlot())
            self.plots[i].setLabel('left', left[i], units=y_unit)
            self.plots[i].enableAutoRange('x', True)
            self.plots[i].showGrid(x=True, y=True, alpha=0.6)
            self.plot_area.nextRow()

    def clear_plots(self):
        for i in range(0, self.number_of_plots):
            self.plots[i].clear()

    def set_plots(self, X: list, Y: list, colors: list, left_caption,
                  left_units, bottom_caption, bottom_units):
        for i in range(0, self.number_of_plots):
            self.plots[i].plot(X, Y[i], pen=(colors[i]))
            self.plots[i].setLabel('left',
                                   left_caption[i],
                                   units=left_units[i])
        self.plots[i].setLabel('bottom', bottom_caption, units=bottom_units)

    def set_plot(self, n, X, Y):
        self.plots[n].plot(np.array(X), np.array(Y))


# class LineShape():
#     def __init__(self):
#         self.plotsLS = pg.GraphicsLayoutWidget()
#         self.plotsLS.setGeometry(QtCore.QRect(0, 0, 600, 300))
#         self.legenda = 0
#         self.LS = self.plotsLS.addPlot()
#         self.LS.setLabel('bottom', "Field", units=H_unit)
#         self.LS.setLabel('left',
#                          "SD voltage with artificial offset",
#                          units='V')
#         self.LS.enableAutoRange('x', True)
#         self.LS.showGrid(x=True, y=True, alpha=0.6)
#         ###RAPORT
#         # self.a = self.LS.addLegend()
#         self.plotsLS.setBackground('w')

#     def update(self, spectrogramData, deltaf, H):
#         self.spectrogramData = spectrogramData
#         self.deltaf = deltaf
#         self.H = H
#         self.clear_plots()
#         offset = 0
#         a = 4
#         b = 24
#         for ff in range(a, b):
#             curr_LS = self.spectrogramData[:, ff] - np.min(
#                 self.spectrogramData[:, ff])
#             self.LS.plot(self.H,
#                          curr_LS + offset,
#                          pen={
#                              'color': (0, int(
#                                  ((ff - a) / (b - a)) * 255), 255 - int(
#                                      ((ff - a) / (b - a)) * 255), 255),
#                              'width':
#                              2
#                          })
#             offset = offset + (np.max(curr_LS) - np.min(curr_LS)) * 1.05

#     def update_experimental(self, spectrogramData, deltaf, H):
#         df = pd.read_csv("4651_Pymag/8/SD.dat", sep="\t")
#         self.spectrogramData = np.array(df.values, dtype=np.float32)
#         self.H = np.array(df["H"].values)
#         self.deltaf = 2e9
#         self.clear_plots()
#         offset = 0

#         # TODO FIX A&B
#         a = 0
#         b = 24
#         for ff in range(a, b):
#             curr_LS = self.spectrogramData[:, ff] - np.min(
#                 self.spectrogramData[:, ff])
#             self.LS.plot(self.H,
#                          curr_LS + offset,
#                          pen={
#                              'color': (0, int(
#                                  ((ff - a) / (b - a)) * 255), 255 - int(
#                                      ((ff - a) / (b - a)) * 255), 255),
#                              'width':
#                              2
#                          })
#             # TODO 1.05?
#             offset = offset + (np.max(curr_LS) - np.min(curr_LS)) * 1.05

#     def set_mode(self, mode):
#         if mode == "H":
#             self.LS.setLabel('bottom', "Field", units=H_unit)
#         elif mode == "phi":
#             self.LS.setLabel('bottom', "Phi angle", units="deg")
#         elif mode == "theta":
#             self.LS.setLabel('bottom', "Theta angle", units="deg")

#     def clear_plots(self):
#         # self.legenda = 0
#         self.LS.clear()


class SpectrogramPlot():
    def __init__(self):
        self.plot_view = pg.GraphicsLayoutWidget()
        self.plot_view.setGeometry(QtCore.QRect(0, 0, 600, 300))
        self.plot_image = self.plot_view.addPlot()
        self.image = pg.ImageView()
        self.plot_view.setBackground('w')
        self.image_spectrum = self.image.getImageItem()
        self.plot_image.addItem(self.image_spectrum)
        self.plot_image.showGrid(x=True, y=True, alpha=0.6)
        self.image_spectrum.resetTransform()
        self.histogram_scale = pg.HistogramLUTItem()
        self.histogram_scale.setImageItem(self.image_spectrum)
        self.plot_view.addItem(self.histogram_scale)
        colors = [(22, 0, 70), (47, 0, 135), (98, 0, 164), (146, 0, 166),
                  (186, 47, 138), (216, 91, 105), (238, 137, 73),
                  (246, 189, 39), (228, 250, 211)]
        cmap = pg.ColorMap(pos=np.linspace(0.0, 1.0, 9), color=colors)
        self.image.setColorMap(cmap)
        self.histogram_scale.gradient.setColorMap(cm=cmap)

    def update_axis(self, left_caption, left_units, bottom_caption,
                    bottom_units):
        self.plot_image.setLabel('left', left_caption, units=left_units)
        self.plot_image.setLabel('bottom', bottom_caption, units=bottom_units)

    def update(self, xrange, yrange, values):

        self.image_spectrum.resetTransform()
        self.image_spectrum.translate(min(xrange), min(yrange))
        self.image_spectrum.scale((max(xrange) - min(xrange)) / len(xrange),
                                  (max(yrange) - min(yrange)) / len(yrange))
        self.image_spectrum.setImage(values, autoLevels=False)

        self.image.updateImage()

    def detrend_f_axis(self, values):
        values2 = np.empty(values.shape)
        for f in range(0, values.shape[1]):
            values2[:, f] = values[:, f] - np.median(values[:, f])
        return values2


# class PlotDynamics():
#     """
#     TODO: Rename SpectrogramPlot?
#     """
#     def __init__(self):
#         self.plot_dynamics_view = pg.GraphicsLayoutWidget()
#         self.plot_dynamics_view.setGeometry(QtCore.QRect(0, 0, 600, 300))
#         self.plots_spectrum = self.plot_dynamics_view.addPlot(title="Spectrum")
#         self.plots_spectrum.setLabel('left', "Frequency", units='Hz')
#         self.plots_spectrum.setLabel('bottom', "Field", units='A/m')
#         self.image_view_spectrum = pg.ImageView()
#         self.plot_dynamics_view.setBackground('w')
#         self.image_spectrum = self.image_view_spectrum.getImageItem()
#         self.plots_spectrum.addItem(self.image_spectrum)
#         self.plots_spectrum.setYRange(0, 20e9, padding=0)
#         self.plots_spectrum.showGrid(x=True, y=True, alpha=0.6)
#         self.image_spectrum.resetTransform()
#         self.image_spectrum.translate(-20e3, 0)
#         self.image_spectrum.scale((20e3 + 20e3) / 20, 1 / 20e9)

#         # TODO RENAME Because PIMM uses that too
#         self.hist_SD = pg.HistogramLUTItem()
#         self.hist_SD.setImageItem(self.image_spectrum)
#         self.hist_SD.vb.disableAutoRange()
#         colors = [(22, 0, 70), (47, 0, 135), (98, 0, 164), (146, 0, 166),
#                   (186, 47, 138), (216, 91, 105), (238, 137, 73),
#                   (246, 189, 39), (228, 250, 211)]
#         cmap = pg.ColorMap(pos=np.linspace(0.0, 1.0, 9), color=colors)
#         self.image_view_spectrum.setColorMap(cmap)
#         self.hist_SD.gradient.setColorMap(cm=cmap)
#         self.inf1_SD = pg.InfiniteLine(movable=True,
#                                        angle=0,
#                                        label='x={value:0.2f}',
#                                        pos=[0, 1e9],
#                                        bounds=[0, 100e9],
#                                        labelOpts={
#                                            'position': 5e9,
#                                            'color': (200, 200, 100),
#                                            'fill': (200, 200, 200, 50),
#                                            'movable': True
#                                        })
#         self.inf1_SD.sigPositionChanged.connect(self.update_roi_loc)
#         self.plots_spectrum.addItem(self.inf1_SD)
#         self.plot_dynamics_view.addItem(self.hist_SD)
#         self.hist_SD.setLevels(-0.001, 0.01)
#         self.hist_SD.autoHistogramRange()

#     def init_setup(self, Xmin, Xmax, Xsteps, dy):
#         self.image_spectrum.clear()
#         self.image_spectrum.resetTransform()
#         self.image_spectrum.translate(Xmin, 0)
#         self.image_spectrum.scale((Xmax - Xmin) / Xsteps, dy)

#     def update(self, spectrogramData, deltaf, H, rm_bkg=0):
#         if rm_bkg == 1:
#             self.spectrogramData = spectrogramData
#             self.spectrogramData2 = spectrogramData * 0
#             for ff in range(0, spectrogramData.shape[1]):
#                 self.spectrogramData2[:,
#                                       ff] = spectrogramData[:, ff] - np.median(
#                                           spectrogramData[:, ff])
#                 self.image_spectrum.setImage(
#                     self.spectrogramData2, autoLevels=False
#                 )  # , autoHistogramRange=False,levels=[3, 6])
#             del self.spectrogramData2
#         else:
#             self.spectrogramData = spectrogramData
#             self.image_spectrum.setImage(self.spectrogramData,
#                                          autoLevels=False)
#         self.deltaf = deltaf
#         self.H = H
#         # self.set_mode(mode)
#         self.update_roi_loc()

#     def set_mode(self, mode):
#         if mode == "H":
#             self.plots_spectrum.setLabel('bottom', "Field", units=H_unit)
#         elif mode == "phi":
#             self.plots_spectrum.setLabel('bottom', "Phi angle", units="deg")
#         elif mode == "theta":
#             self.plots_spectrum.setLabel('bottom', "Theta angle", units="deg")

#     def update_roi_loc(self):
#         try:
#             # TODO: plotLineShape this does not exist
#             self.plotLineShape.clear()
#             self.plotLineShape.plot(
#                 self.H,
#                 self.spectrogramData[:,
#                                      int(self.inf1_SD.value() / self.deltaf)],
#                 pen=(255, 255, 255))
#         except:
#             pass

#     def clear_plots(self):
#         self.image_spectrum.clear()
#         self.plots_spectrum.clear()
#         # TODO: remove try exepct
#         try:
#             self.plots_spectrum.addItem(self.inf1_SD)
#             self.plots_spectrum.addItem(self.image_spectrum)
#             self.plotLineShape.clear()
#         except:
#             pass
#         try:
#             del (self.spectrogramData)
#         except:  # except ValueErrror as ex
#             # logging.exception(ex)
#             pass
