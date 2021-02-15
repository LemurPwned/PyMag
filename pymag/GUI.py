from PyQt5.QtWidgets import QLabel, QFrame, QComboBox
from PyQt5 import QtWidgets
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtCore import pyqtSlot
import pyqtgraph.console
import PyMagStudio_backends

from backend_utils import *
from PyQt5.QtWidgets import (QCheckBox)
import os

import pandas as pd

ResultsColumns = ['H', 'Mx', 'My', 'Mz', 'Rx', 'Ry', 'Rz']

import pyqtgraph.opengl as gl


class TrajectoryPlot():

    def __init__(self):
        self.w = gl.GLViewWidget()
        self.init_GL_settings()
        self.w.setBackgroundColor('w')

    def init_GL_settings(self):
        self.w.opts['distance'] = 3
        plt = gl.GLLinePlotItem(pos=np.array([[0,0,0],[1,0,0]]), color=pg.glColor([255,0,0]), width=(2), antialias=True)
        self.w.addItem(plt)
        plt = gl.GLLinePlotItem(pos=np.array([[0,0,0],[0,1,0]]), color=pg.glColor([0,255,0]), width=(2), antialias=True)
        self.w.addItem(plt)
        plt = gl.GLLinePlotItem(pos=np.array([[0,0,0],[0,0,1]]), color=pg.glColor([0,0,255]), width=(2), antialias=True)
        self.w.addItem(plt)
        md = gl.MeshData.sphere(rows=20, cols=20)
        m1 = gl.GLMeshItem(meshdata=md, smooth=True, color=(0.7, 0.7, 0.7, 0.7), shader='balloon') #, glOptions='additive'
        m1.translate(0, 0, 0)
        m1.scale(1, 1, 1)
        self.w.addItem(m1)



    def pltTraj(self,traj, colory):

        # pts = traj
        # color = [100,200,250]
        # print(traj)
        plt = gl.GLLinePlotItem(pos=np.array(traj), color=pg.glColor(colory), width=(0 + 1) / 10., antialias=True)
        self.w.addItem(plt)

    def pltPoint(self,x,y,z):

        md = gl.MeshData.sphere(rows=10, cols=10)
        m1 = gl.GLMeshItem(meshdata=md, smooth=True, color=(1, 0, 0, 0.5), shader='balloon', glOptions='additive')
        m1.translate(x,y,z)
        m1.scale(0.05,0.05,0.05)
        self.w.addItem(m1)

    def clear(self):
        for item in self.w.items:
            item._setView(None)
        self.w.items = []

        self.w.update()
        self.init_GL_settings()


class paramsAndStimulus():
    def __init__(self,parent):
        layerParameters = parent.layerParameters
        StimulusParameters = parent.StimulusParameters
        self.table_layer_params = pg.TableWidget(editable=True, sortable=False)
        self.table_stimulus_params = pg.TableWidget(editable=True, sortable=False)
        self.GenerateStimulus = QtWidgets.QPushButton()
        self.AddButton = QtWidgets.QPushButton()
        self.RemoveButton = QtWidgets.QPushButton()
        self.LoadButton = QtWidgets.QPushButton()
        self.SaveButton = QtWidgets.QPushButton()
        self.AddSimulationButton = QtWidgets.QPushButton()
        self.GenerateStimulus.setText("Set stimulus \nfor all")
        self.GenerateStimulus.clicked.connect(parent.setStimulusForALl)
        self.AddButton.setText("Add new \nlayer")
        self.AddButton.clicked.connect(self.addLayer)
        self.RemoveButton.setText("Remove selected\n row")
        self.RemoveButton.clicked.connect(self.removeLayer)
        self.LoadButton.setText("Load params \nfrom file")
        self.LoadButton.clicked.connect(parent.loadParams)
        self.SaveButton.setText("Save params \nto file")
        self.SaveButton.clicked.connect(parent.saveParams)
        self.AddSimulationButton.setText("Add to \nsimulation list")
        self.AddSimulationButton.clicked.connect(parent.addToSimulationList)
        self.table_layer_params.setData(layerParameters.to_numpy())
        self.table_layer_params.setHorizontalHeaderLabels(layerParameters.columns)
        self.table_stimulus_params.setData(StimulusParameters.to_numpy())
        self.table_stimulus_params.setHorizontalHeaderLabels(StimulusParameters.columns)
        self.ctrlWidget = QtGui.QWidget()
        self.ctrLayout = QtGui.QVBoxLayout()
        self.ctrlWidget.setLayout(self.ctrLayout)
        self.ctrLayout.addWidget(self.table_layer_params)
        self.btn_layout = QtGui.QHBoxLayout()
        self.btn_layout.addWidget(self.GenerateStimulus)
        self.btn_layout.addWidget(self.AddButton)
        self.btn_layout.addWidget(self.RemoveButton)
        self.btn_layout.addWidget(self.LoadButton)
        self.btn_layout.addWidget(self.SaveButton)
        self.btn_layout.addWidget(self.AddSimulationButton)
        self.ctrLayout.addWidget(self.table_stimulus_params)
        self.ctrLayout.addLayout(self.btn_layout)

    def addLayer(self):
        self.table_layer_params.addRow([1, 1.6, 3000, "[1 0 0]", -1e-5, 0.01, 1e-9, "[0 1 0]", 0.02, 0.01, 0.01, 100, 120, 1])

    def removeLayer(self):
        self.table_layer_params.removeRow(self.table_layer_params.currentRow())

class Res_plot():
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

    def clearPlot(self):
        self.Rx.clear()
        self.Ry.clear()
        self.Rz.clear()

    def setMode(self, mode):
        if mode == "H":
            self.Rz.setLabel('bottom', "Field", units=H_unit)
        elif mode == "phi":
            self.Rz.setLabel('bottom', "Phi angle", units="deg")
        elif mode == "theta":
            self.Rz.setLabel('bottom', "Theta angle", units="deg")

class Line_shape():
    def __init__(self):
        self.plotsLS = pg.GraphicsLayoutWidget()
        self.plotsLS.setGeometry(QtCore.QRect(0, 0, 600, 300))
        self.legenda = 0
        self.LS = self.plotsLS.addPlot()
        self.LS.setLabel('bottom', "Field", units=H_unit)
        self.LS.setLabel('left', "SD voltage with artificial offset", units='V')
        self.LS.enableAutoRange('x', True)
        self.LS.showGrid(x=True, y=True, alpha=0.6)
        ###RAPORT
        # self.a = self.LS.addLegend()
        self.plotsLS.setBackground('w')

    def update(self, spectrogramData, deltaf, H):
        self.spectrogramData = spectrogramData
        self.deltaf = deltaf
        self.H = H
        self.clearPlot()
        offset = 0
        number_of_freqs = spectrogramData.shape[1]
        a= 4
        b = 24
        for ff in range(a, b):
            curr_LS = self.spectrogramData[:, ff]-np.min(self.spectrogramData[:, ff])
            self.LS.plot(self.H, curr_LS + offset, pen={'color': (0,int(((ff-a) / (b-a)) * 255), 255 - int(((ff-a) / (b-a)) * 255), 255), 'width': 2})
            offset = offset + (np.max(curr_LS) - np.min(curr_LS))*1.05

    def update_experimental(self, spectrogramData, deltaf, H):
        df = pd.read_csv("4651_Pymag/8/SD.dat", sep="\t")
        self.spectrogramData = np.array(df.values, dtype=np.float32)
        self.H = np.array(df["H"].values)
        self.deltaf  = 2e9
        self.clearPlot()
        offset = 0
        number_of_freqs = spectrogramData.shape[1]
        a = 0
        b = 24
        for ff in range(a, b):
            curr_LS = self.spectrogramData[:, ff] - np.min(self.spectrogramData[:, ff])
            self.LS.plot(self.H, curr_LS + offset, pen={
                'color': (0, int(((ff - a) / (b - a)) * 255), 255 - int(((ff - a) / (b - a)) * 255), 255),
                'width': 2})
            offset = offset + (np.max(curr_LS) - np.min(curr_LS)) * 1.05

    def setMode(self, mode):
        if mode == "H":
            self.LS.setLabel('bottom', "Field", units=H_unit)
        elif mode == "phi":
            self.LS.setLabel('bottom', "Phi angle", units="deg")
        elif mode == "theta":
            self.LS.setLabel('bottom', "Theta angle", units="deg")

    def clearPlot(self):
        # self.legenda = 0
        self.LS.clear()


class Mag_plot():
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

    def clearPlot(self):
        self.Mx.clear()
        self.My.clear()
        self.Mz.clear()

    def setMode(self, mode):
        if mode == "H":
            self.Mz.setLabel('bottom', "Field", units=H_unit)
        elif mode == "phi":
            self.Mz.setLabel('bottom', "Phi angle", units="deg")
        elif mode == "theta":
            self.Mz.setLabel('bottom', "Theta angle", units="deg")

class plotDynamics():
    def __init__(self):
        self.plotsDynamics_view = pg.GraphicsLayoutWidget()
        self.plotsDynamics_view.setGeometry(QtCore.QRect(0, 0, 600, 300))
        self.plotsSpectrum = self.plotsDynamics_view.addPlot(title="Spectrum")
        self.plotsSpectrum.setLabel('left', "Frequency", units='Hz')
        self.plotsSpectrum.setLabel('bottom', "Field", units='A/m')
        self.imageViewSpectrum = pg.ImageView()
        self.plotsDynamics_view.setBackground('w')
        self.imageSpectrum = self.imageViewSpectrum.getImageItem()
        self.plotsSpectrum.addItem(self.imageSpectrum)
        self.plotsSpectrum.setYRange(0, 20e9, padding=0)
        self.plotsSpectrum.showGrid(x=True, y=True, alpha=0.6)
        self.imageSpectrum.resetTransform()
        self.imageSpectrum.translate(-20e3, 0)
        self.imageSpectrum.scale((20e3 + 20e3) / 20, 1 / 20e9)
        self.hist_SD = pg.HistogramLUTItem()
        self.hist_SD.setImageItem(self.imageSpectrum)
        self.hist_SD.vb.disableAutoRange()
        colors = [
            (22, 0, 70),
            (47, 0, 135),
            (98, 0, 164),
            (146, 0, 166),
            (186, 47, 138),
            (216, 91, 105),
            (238, 137, 73),
            (246, 189, 39),
            (228, 250, 211)]
        cmap = pg.ColorMap(pos=np.linspace(0.0, 1.0, 9), color=colors)
        self.imageViewSpectrum.setColorMap(cmap)
        self.hist_SD.gradient.setColorMap(cm=cmap)
        self.inf1_SD = pg.InfiniteLine(movable=True, angle=0, label='x={value:0.2f}', pos=[0, 1e9], bounds = [0, 100e9],
                                       labelOpts={'position': 5e9, 'color': (200, 200, 100),
                                                  'fill': (200, 200, 200, 50), 'movable': True})
        self.inf1_SD.sigPositionChanged.connect(self.update_roi_loc)
        self.plotsSpectrum.addItem(self.inf1_SD)
        self.plotsDynamics_view.addItem(self.hist_SD)
        self.hist_SD.setLevels(-0.001, 0.01)
        self.hist_SD.autoHistogramRange()

    def init_setup(self, Xmin, Xmax, Xsteps, dy):
        self.imageSpectrum.clear()
        self.imageSpectrum.resetTransform()
        self.imageSpectrum.translate(Xmin, 0)
        self.imageSpectrum.scale( (Xmax-Xmin)/Xsteps , dy )

    def update(self,spectrogramData,deltaf,H,rm_bkg = 0):
        if rm_bkg == 1:
            self.spectrogramData = spectrogramData
            self.spectrogramData2 = spectrogramData*0
            for ff in range(0, spectrogramData.shape[1]):
                self.spectrogramData2[:, ff] = spectrogramData[:, ff]-np.median(spectrogramData[:, ff])
                self.imageSpectrum.setImage(self.spectrogramData2,autoLevels=False)  # , autoHistogramRange=False,levels=[3, 6])
            del self.spectrogramData2
        else:
            self.spectrogramData = spectrogramData
            self.imageSpectrum.setImage(self.spectrogramData,autoLevels=False)
        self.deltaf= deltaf
        self.H = H
        # self.setMode(mode)
        self.update_roi_loc()

    def setMode(self, mode):
        if mode == "H":
            self.plotsSpectrum.setLabel('bottom', "Field", units=H_unit)
        elif mode == "phi":
            self.plotsSpectrum.setLabel('bottom', "Phi angle", units="deg")
        elif mode == "theta":
            self.plotsSpectrum.setLabel('bottom', "Theta angle", units="deg")

    def update_roi_loc(self):
        try:
            self.plotLineShape.clear()
            self.plotLineShape.plot(self.H ,self.spectrogramData[:, int(self.inf1_SD.value() / self.deltaf)], pen=(255, 255, 255))
        except:
            pass

    def clearPlot(self):
        self.imageSpectrum.clear()
        self.plotsSpectrum.clear() ########
        try:
            self.plotsSpectrum.addItem(self.inf1_SD)
            self.plotsSpectrum.addItem(self.imageSpectrum)
            self.plotLineShape.clear()
        except:
            pass
        try:
            del (self.spectrogramData)
        except:
            pass



class addMenuBar():

    def __init__(self,parent):
        self.menubar = QtWidgets.QMenuBar()
        self.File_menu = self.menubar.addMenu("File")

        self.File_menu.addAction("Save layer params").triggered.connect(parent.saveParams)
        self.File_menu.addAction("Load layer params").triggered.connect(parent.loadParams)
        self.File_menu.addAction("Load multiple layer params").triggered.connect(parent.loadMultipleLayerParams)
        self.File_menu.addSeparator()
        self.File_menu.addAction("Open results from csv").triggered.connect(parent.loadResults)
        self.File_menu.addAction("Save results as csv").triggered.connect(parent.saveResults)

        self.File_menu.addAction("Save simulation report as docx").triggered.connect(parent.saveReport)
        self.File_menu.addAction("Append results to pptx").triggered.connect(parent.appendPptx)
        self.File_menu.addAction("Save all to binary file").triggered.connect(parent.saveBinary)
        self.File_menu.addAction("Load all from binary file").triggered.connect(parent.loadBinary)
        self.File_menu.addSeparator()
        self.exitButton = self.File_menu.addAction("Exit").triggered.connect(parent.endProgram)

        self.SettingsMenu = self.menubar.addMenu("Settings")
        self.SettingsMenu.addAction("Change Settings").triggered.connect(parent.newSettings)
        self.SettingsMenu.addSeparator()
        self.WindowMenu = self.menubar.addMenu("Window")
        self.WindowMenu.addAction("Switch full/normal screen").triggered.connect(parent.fullScreenMode)
        self.WindowMenu.addAction("Save dock state").triggered.connect(parent.saveDockState)
        self.WindowMenu.addAction("Load dock state").triggered.connect(parent.loadDockState)
        self.HelpMenu = self.menubar.addMenu("Help")
        self.HelpMenu.addAction("About").triggered.connect(parent.newAbout)


        self.Simulation_Name_Label = QLabel("Simulation\nName:")
        self.Simulation_Name = QtWidgets.QLineEdit()

        self.startButton = QtWidgets.QPushButton()
        self.stopButton = QtWidgets.QPushButton()
        self.startButton.setText("Start")
        self.stopButton.setText("Stop")
        self.stopButton.setText("Stop")
        self.startButton.clicked.connect(parent.btn_clk)
        self.stopButton.clicked.connect(parent.stop_clk)

        self.MultiprocessingLabel = QLabel("MP")
        self.Backend_choose = QComboBox()

        self.Backend_choose.addItem("C++")
        self.Backend_choose.addItem("Docker")
        self.Backend_choose.addItem("Python")
        self.BackEndLabel = QLabel("Backend:")

        self.MultiprocessingCheckBox = QCheckBox()
        self.MultiprocessingCheckBox.setObjectName("Multiprocessing")
        self.MultiprocessingCheckBox.setChecked(True)

        self.progress = QtWidgets.QProgressBar()
        self.progress.setGeometry(0, 0, 300, 25)
        self.progress.setMaximum(100)

        self.ctrlWidget = QtGui.QWidget()
        self.ctrLayout = QtGui.QVBoxLayout()
        self.ctrlWidget.setLayout(self.ctrLayout)
        self.ctrLayout.addWidget(self.menubar)
        self.ctrLayout.addWidget(self.progress)


        self.btn_layout = QtGui.QHBoxLayout()


        self.btn_layout.addWidget(self.startButton)
        self.btn_layout.addWidget(self.Simulation_Name_Label)
        self.btn_layout.addWidget(self.Simulation_Name)


        self.btn_layout.addWidget(self.stopButton)
        # self.btn_layout.addWidget(self.clearPlotButton)
        self.btn_layout.addWidget(self.MultiprocessingLabel)
        self.btn_layout.addWidget(self.MultiprocessingCheckBox)
        self.btn_layout.addWidget(self.BackEndLabel)
        self.btn_layout.addWidget(self.Backend_choose)

        self.ctrLayout.addLayout(self.btn_layout)








class LabeledDoubleSpinBox():
    def __init__(self,label = "Label", minimum=0, maximum=1, value=0, mode = 'Double'):
        self.Label = QLabel(label)
        if mode == 'Double':
            self.Value = QtWidgets.QDoubleSpinBox()
            self.Value.setMinimum(minimum)
            self.Value.setMaximum(maximum)
            self.Value.setValue(value)
            self.Value.setObjectName(label)
        elif mode == 'Integer':
            self.Value = QtWidgets.QSpinBox()
            self.Value.setMinimum(minimum)
            self.Value.setMaximum(maximum)
            self.Value.setValue(value)
            self.Value.setObjectName(label)

        if mode == 'Binary':
            self.Value = QtWidgets.QCheckBox()
            self.Value.setObjectName(label)
            self.Value.setChecked(value)


class Settings(QtGui.QDialog):
    signal = QtCore.pyqtSignal(float, float, int, bool, float, float)

    def __init__(self, parent):
        super(Settings, self).__init__()
        self.setWindowTitle(PyMagVersion + " - Settings")

        self.setFixedSize(650, 400)
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.MHCheckBox = QtWidgets.QCheckBox()
        self.MHCheckLabel = QtWidgets.QLabel("M(H)")
        self.RHCheckBox = QtWidgets.QCheckBox()
        self.RHCheckLabel = QtWidgets.QLabel("R(H)")
        self.SDCheckBox = QtWidgets.QCheckBox()
        self.SDCheckBox.setChecked(True)
        self.SDCheckLabel = QtWidgets.QLabel("SD(H,f)")
        self.STOCheckBox = QtWidgets.QCheckBox()

        self.STOCheckLabel = QtWidgets.QLabel("STO(H,f)")

        self.CheckBoxLayout = QtWidgets.QHBoxLayout()
        self.CheckBoxLayout.addWidget(self.MHCheckLabel)
        self.CheckBoxLayout.addWidget(self.MHCheckBox)
        self.CheckBoxLayout.addWidget(self.RHCheckLabel)
        self.CheckBoxLayout.addWidget(self.RHCheckBox)
        self.CheckBoxLayout.addWidget(self.SDCheckLabel)
        self.CheckBoxLayout.addWidget(self.SDCheckBox)
        self.CheckBoxLayout.addWidget(self.STOCheckLabel)
        self.CheckBoxLayout.addWidget(self.STOCheckBox)
        self.layout.addLayout(self.CheckBoxLayout)

        self.close()

class About(QtGui.QDialog):
    def __init__(self, parent):
        super(About, self).__init__()
        self.setWindowTitle(PyMagVersion + " - About")
        self.setFixedSize(200, 100)
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.AboutLabel = QtWidgets.QLabel(PyMagVersion + "\n" + PyMagDate)
        self.layout.addWidget(self.AboutLabel)
        self.close()


