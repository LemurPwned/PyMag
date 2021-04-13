from typing import List
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
import numpy as np
from pyqtgraph.graphicsItems.PlotDataItem import PlotDataItem


class MultiplePlot():
    def __init__(self, left, number_of_plots, y_unit='\u03A9'):
        self.number_of_plots = number_of_plots
        self.plot_area = pg.GraphicsLayoutWidget()
        self.plot_area.setGeometry(QtCore.QRect(0, 0, 600, 300))
        self.plot_area.nextRow()
        self.plot_area.setBackground('w')
        self.plots: List[pg.PlotItem] = []
        self.experimental_plots: List[pg.PlotDataItem] = []

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
        self.plots[n].plot(np.asarray(X), np.asarray(Y))

    def set_experimental(self, n, X, Y):
        pointer = self.plots[n].scatterPlot(np.asarray(X),
                                            np.asarray(Y),
                                            pen=pg.mkPen('r', width=1.2),
                                            alpha=0.6)
        self.experimental_plots.append(pointer)

    def clear_experimental(self):
        exp_plot: PlotDataItem
        for i, exp_plot in enumerate(self.experimental_plots):
            self.plots[i].removeItem(exp_plot)
        self.experimental_plots.clear()


class SpectrogramPlot():
    def __init__(self):
        self.plot_view = pg.GraphicsLayoutWidget()
        self.plot_view.setGeometry(QtCore.QRect(0, 0, 600, 300))
        self.plot_image: pg.PlotItem = self.plot_view.addPlot()
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
        self.inf_line = pg.InfiniteLine(movable=True,
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
        self.plot_image.addItem(self.inf_line)

        self.experimental_overlay = pg.PlotCurveItem()
        self.image.addItem(self.experimental_overlay)

        self.plot_view.nextRow()
        self.cross_section = self.plot_view.addPlot(title="SD/STO vs H")
        self.cross_section.setLabel('bottom', "Field", units="A/m")
        self.cross_section.setLabel('left', "Udc")
        self.cross_section.showGrid(x=True, y=True, alpha=0.6)

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

    def update_plot(self, x, y):
        self.plot_image.scatterPlot(x,
                                    y,
                                    pen=pg.mkPen('r', width=1.2),
                                    alpha=0.6)

    def detrend_f_axis(self, values):
        values2 = np.empty(values.shape)
        for f in range(0, values.shape[1]):
            values2[:, f] = values[:, f] - np.median(values[:, f])
        return values2

    def clear_plots(self):
        self.image_spectrum.clear()
        self.cross_section.clear()
        # self.plot_image.clear()
        return
