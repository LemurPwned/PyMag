from pymag.engine.data_holders import VoltageSpinDiodeData
from typing import List
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
from PyQt5.QtWidgets import QAction, QActionGroup
from PyQt5.QtWidgets import QWidget, QSpinBox


class MultiplePlot(QWidget):
    def __init__(self, left, number_of_plots, y_unit='\u03A9'):
        QWidget.__init__(self, None)
        self.number_of_plots = number_of_plots
        self.plot_area = pg.GraphicsLayoutWidget()
        self.plot_area.setGeometry(QtCore.QRect(0, 0, 600, 300))
        self.plot_area.nextRow()
        self.plot_area.setBackground('w')
        self.plots: List[pg.PlotItem] = []
        self.experimental_plots: List[pg.PlotDataItem] = []
        self.plots_to_clear: List[pg.PlotDataItem] = []

        for i in range(number_of_plots):
            self.plots.append(self.plot_area.addPlot())
            self.plots[i].setLabel('left', left[i], units=y_unit)
            self.plots[i].enableAutoRange('x', True)
            self.plots[i].showGrid(x=True, y=True, alpha=0.6)
            self.plot_area.nextRow()
            self.plots_to_clear.append(None)
            self.experimental_plots.append(None)

    def clear_plots(self):
        for i in range(self.number_of_plots):
            self.plots[i].removeItem(self.plots_to_clear[i])

    def nuke_plots(self):
        for i in range(self.number_of_plots):
            self.plots[i].clear()

    def set_plots(self, X: list, Y: list, colors: list, left_caption,
                  left_units, bottom_caption, bottom_units):
        for i in range(self.number_of_plots):
            pointer = self.plots[i].plot(X, Y[i], pen=(colors[i]))
            self.plots_to_clear[i] = pointer
            self.plots[i].setLabel('left',
                                   left_caption[i],
                                   units=left_units[i])
        self.plots[i].setLabel('bottom', bottom_caption, units=bottom_units)

    def set_plot(self, n, X, Y):
        pointer = self.plots[n].plot(np.asarray(X), np.asarray(Y))
        self.plots_to_clear[n] = pointer

    def set_experimental(self, n, X, Y):
        pointer = self.plots[n].scatterPlot(np.asarray(X),
                                            np.asarray(Y),
                                            pen=pg.mkPen('r', width=1.2),
                                            alpha=0.6)
        self.experimental_plots[n] = pointer

    def clear_experimental(self):
        for i in range(self.number_of_plots):
            self.plots[i].removeItem(self.experimental_plots[i])


class SpectrogramPlot():
    def __init__(self, spectrum_enabled=False):
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
        # that's a frequency view -- horizontal line
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
        # designate vertical position of H field
        self.inf_line_H = pg.InfiniteLine(movable=True,
                                          angle=90,
                                          label='x={value:0.2f}',
                                          pos=[0, 0],
                                          bounds=[-800e3, 800e3],
                                          labelOpts={
                                              'position': 5e9,
                                              'color': (200, 200, 100),
                                              'fill': (200, 200, 200, 50),
                                              'movable': True
                                          })
        self.plot_image.addItem(self.inf_line)
        self.plot_image.addItem(self.inf_line_H)

        self.experimental_overlay = pg.PlotCurveItem()
        self.image.addItem(self.experimental_overlay)

        self.plot_view.nextRow()
        self.cross_section = self.plot_view.addPlot(title="SD/STO vs H")
        self.cross_section.setLabel('bottom', "Field", units="A/m")
        self.cross_section.setLabel('left', "Udc")
        self.cross_section.showGrid(x=True, y=True, alpha=0.6)
        self.xrange = None
        self.yrange = None

        # only for VSD
        self.Rxx_holder: VoltageSpinDiodeData = None
        self.Rxy_holder: VoltageSpinDiodeData = None

        # starting values
        self.resistance_mode = "Rxx"
        self.current_action = "DC"
        self.construct_qmenu(spectrum_enabled)

    def construct_qmenu(self, spectrum_enabled):
        menu = self.plot_image.vb.menu
        for action in menu.actions():
            action.setVisible(False)
        if spectrum_enabled:
            """
            This is just for the VSD plots
            """
            submenu = menu.addMenu("Spectrum")
            harmonic_group = QActionGroup(submenu)
            harmonic_group.setExclusive(True)

            for n, ac in zip(["DC", "1st harmonic", "2nd harmonic",
                              "1st harmonic phase",
                              "2nd harmonic phase"],
                             ["DC", "FHarmonic", "SHarmonic",
                             "FHarmonic_phase", "SHarmonic_phase"]):

                a = harmonic_group.addAction(QAction(
                    n, submenu, checkable=True))
                a.triggered.connect(self.action_menu_generator(ac))
                submenu.addAction(a)
            harmonic_group.actions()[0].setChecked(True)

            submenu_rxx_rxy = menu.addMenu("Resistance")
            resistance_group = QActionGroup(submenu_rxx_rxy)
            resistance_group.setExclusive(True)
            for n, ac in zip(["Rxx", "Rxy"],
                             [self.on_Rxx_selected, self.on_Rxy_selected]):
                a = resistance_group.addAction(QAction(
                    n, submenu_rxx_rxy, checkable=True))
                a.triggered.connect(ac)
                submenu_rxx_rxy.addAction(a)
                resistance_group.actions()[0].setChecked(True)

    def on_Rxx_selected(self):
        self.resistance_mode = "Rxx"
        if self.current_action:
            self.action_menu_generator(self.current_action)()

    def on_Rxy_selected(self):
        self.resistance_mode = "Rxy"
        if self.current_action:
            self.action_menu_generator(self.current_action)()

    def set_VSD_holders(self, Rxx_holder: VoltageSpinDiodeData,
                        Rxy_holder: VoltageSpinDiodeData):
        self.Rxx_holder = Rxx_holder
        self.Rxy_holder = Rxy_holder

    def update_action(self, action):
        self.current_action = action

    def action_menu_generator(self, property):
        def menu_action():
            holder = getattr(self, self.resistance_mode + "_holder")
            if holder:
                vals = self.detrend_f_axis(
                    getattr(holder, property)
                )
                self.image_spectrum.setImage(
                    vals, autoLevels=False
                )
                mean, std = self.compute_histogram_fadeout(vals)
                self.image.getHistogramWidget().setLevels(
                    mean-0.6*std, mean+0.6*std)
                self.image.updateImage()
                self.update_roi()
                self.update_action(property)
        return menu_action

    def update_axis(self, left_caption, left_units, bottom_caption,
                    bottom_units):
        self.plot_image.setLabel('left', left_caption, units=left_units)
        self.plot_image.setLabel(
            'bottom', bottom_caption, units=bottom_units)

    def update_roi(self):
        if not (self.xrange is None):
            cross_section = int(self.inf_line.value() / self.deltaf)
            if cross_section >= self.image_spectrum.image.shape[
                    1] or cross_section < 0:
                return
            self.cross_section.clear()
            self.cross_section.plot(
                self.xrange,
                self.image_spectrum.image[:,
                                          int(self.inf_line.value() /
                                              self.deltaf)],
                pen=pg.mkPen('b', width=5))

    def get_current_field_cross_section(self):
        return self.inf_line_H.value()

    def update(self, xrange, yrange, values, deltaf):
        """ 
        PIMM update
        """
        self.xrange = xrange
        self.yrange = yrange
        self.deltaf = deltaf

        self.image_spectrum.resetTransform()
        self.image_spectrum.translate(min(xrange), min(yrange))
        self.image_spectrum.scale((max(xrange) - min(xrange)) / len(xrange),
                                  (max(yrange) - min(yrange)) / len(yrange))
        self.image_spectrum.setImage(values, autoLevels=False)
        _, std = self.compute_histogram_fadeout(values)
        self.image.getHistogramWidget().setLevels(
            0, 0.6*std)  # is not symmetric -- due to FFT
        self.image.updateImage()

    def compute_histogram_fadeout(self, values):
        """ 
        We need to construct the histogram of values for the image 
        and then discount for least interesting
        """
        # try with the quantiles as well
        values = np.asarray(values) - np.mean(values)
        hist, bins = np.histogram(values)
        # return np.mean(values), np.quantile(hist, 0.25)
        return np.mean(values), np.std(values)

    def update_image(self, xrange, yrange, deltaf):
        """
        Voltage spin diode update
        """
        self.xrange = xrange
        self.yrange = yrange
        self.deltaf = deltaf
        self.image_spectrum.resetTransform()
        self.image_spectrum.translate(min(xrange), min(yrange))
        self.image_spectrum.scale((max(xrange) - min(xrange)) / len(xrange),
                                  (max(yrange) - min(yrange)) / len(yrange))
        self.action_menu_generator(self.current_action)()
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
        return
