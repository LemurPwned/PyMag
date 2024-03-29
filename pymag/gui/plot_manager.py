import colorsys
from typing import List, Union

import numpy as np

from pymag.engine.data_holders import ExperimentData, ResultHolder
from pymag.gui.plots import MultiplePlot, SpectrogramPlot
from pymag.gui.simulation_manager import Simulation
from pymag.gui.trajectory import TrajectoryPlot

N = 5
HSV_tuples = [(x / N, 0.5, 0.5) for x in range(N)]
RGB_tuples = list(map(lambda x: (*colorsys.hsv_to_rgb(*x), 0.4), HSV_tuples))


class PlotManager:
    """
    Plot Manager manages all plot updates in the dock
    """

    def __init__(self, magnetisation_plot: MultiplePlot,
                 resistance_plot: MultiplePlot, convergence_plot: MultiplePlot,
                 SD_plot: SpectrogramPlot, PIMM_plot: SpectrogramPlot,
                 trajectory_components: SpectrogramPlot,
                 trajectory_plot: TrajectoryPlot) -> None:
        """
        :param magnetisation_plot
        :param resistance_plot
        :param convergence_plot
        :param SD_plot
        :param SD_lines
        :param PIMM_plot
        :param trajectory_plot
        Plot manager requires all individual plots
        """
        self.trajectory_plot = trajectory_plot
        self.magnetisation_plot = magnetisation_plot
        self.convergence_plot = convergence_plot
        self.resistance_plot = resistance_plot
        self.trajectory_components = trajectory_components
        self.SD_plot = SD_plot
        self.SD_plot.inf_line.sigPositionChanged.connect(
            self.SD_update_roi_loc)

        self.PIMM_plot = PIMM_plot
        self.PIMM_plot.inf_line.sigPositionChanged.connect(
            self.PIMM_update_roi_loc)

        self.PIMM_plot.inf_line_H.sigPositionChanged.connect(
            self.H_update_roi_loc)

        units_SI = {"H": "A/m", "Theta": "deg", "Phi": "deg", "f": "Hz"}
        self.units = units_SI
        self.H = None
        self.SD_deltaf = 0
        self.PIMM_deltaf = 0

        self.H_select = 0
        self.trajectory_store = None

    def PIMM_update_roi_loc(self):
        self.PIMM_plot.update_roi()

    def SD_update_roi_loc(self):
        self.SD_plot.update_roi()

    def H_update_roi_loc(self):
        if self.H is not None:
            H_select_val = self.PIMM_plot.get_current_field_cross_section()
            self.H_select = np.abs(np.asarray(self.H) - H_select_val).argmin()
            self.plot_trajectory(self.trajectory_store)

    def clear_simulation_plots(self):
        self.resistance_plot.clear_plots()
        self.magnetisation_plot.clear_plots()
        self.convergence_plot.clear_plots()
        self.PIMM_plot.clear_plots()
        self.SD_plot.clear_plots()

    def clear_experiment_plots(self):
        self.SD_plot.plot_image.clearPlots()
        self.PIMM_plot.plot_image.clearPlots()
        self.resistance_plot.clear_experimental()
        self.magnetisation_plot.clear_experimental()

    def plot_active_results(self, obj_list: List[Union[Simulation,
                                                       ExperimentData]]):
        """
        :param simulation_list
            Plot active simulations
        """
        for plotable_obj in obj_list:
            self.plot_result(plotable_obj)

    def plot_result(self, plot_input: Union[Simulation, ExperimentData]):
        """
        Delegates plotting depending on the item type
        :param plot_input Union[Simulation, ExperimentData]
            item to be plotted
        """
        if isinstance(plot_input, ExperimentData):
            self.clear_experiment_plots()
            self.plot_experiment(plot_input)
        else:
            self.clear_simulation_plots()
            self.plot_simulation(plot_input.get_simulation_result())

    def plot_experiment(self, data: ExperimentData):
        """
        Plot the experimental data if it exists
        """
        x, f = data.get_pimm_series()

        self.PIMM_plot.update_plot(np.asarray(x), np.asarray(f))
        self.SD_plot.update_plot(np.asarray(x), np.asarray(f))

        x, Rx, Ry, Rz = data.get_r_series()
        for i, R in enumerate((Rx, Ry, Rz)):
            if R:
                self.resistance_plot.set_experimental(i, x, R)

        x, Mx, My, Mz = data.get_m_series()
        for i, M in enumerate((Mx, My, Mz)):
            if M:
                self.magnetisation_plot.set_experimental(i, x, M)

    def plot_trajectory(self, m_trajectories: np.ndarray):
        """
        Update the trajectory on the OpenGL widget
        """
        if self.trajectory_store is None:
            # happens at first call
            return

        t = np.arange(m_trajectories.shape[-1])

        self.trajectory_plot.clear()
        self.trajectory_components.nuke_plots()
        for i in range(m_trajectories.shape[1]):  # iterate over layers
            X = m_trajectories[self.H_select, i, :, :]
            c = RGB_tuples[i]
            cplot = [[p * 255 for p in RGB_tuples[i][:-1]] for _ in range(3)]
            self.trajectory_plot.draw_trajectory(
                X.transpose().squeeze(),
                color=c  # (1, 0, 0, 1)
            )
            self.trajectory_components.set_plots(t, X, cplot,
                                                 ["m_x", "m_y", "m_z"],
                                                 [None, None, None],
                                                 'Iterations', None)
        self.trajectory_plot.w.update()

    def plot_simulation(self, result_holder: ResultHolder):
        """
        :param result_holder
            Holds partial result of the simulations
        Update the plots with freshly updated queue value
        """
        if not result_holder:
            return
        lim = result_holder.update_count
        if lim == 1:
            return
        # save for update ROI
        self.H = result_holder.H_mag[:lim]
        self.PIMM_plot.inf_line_H.setBounds((min(self.H), max(self.H)))
        self.trajectory_store = result_holder.m_traj

        # adapt PIMM bounds
        self.PIMM_deltaf = result_holder.PIMM_freqs[
            1] - result_holder.PIMM_freqs[0]

        self.magnetisation_plot.set_plots(result_holder.H_mag[:lim], [
            result_holder.m_avg[:, 0], result_holder.m_avg[:, 1],
            result_holder.m_avg[:, 2]
        ], [[255, 0, 0], [0, 255, 0], [0, 0, 255]], ["Mx", "My", "Mz"],
                                          [None, None, None],
                                          str(result_holder.mode),
                                          self.units[str(result_holder.mode)])

        self.resistance_plot.set_plots(
            result_holder.H_mag[:lim],
            [result_holder.Rx, result_holder.Ry, result_holder.Rz],
            [[255, 0, 0], [0, 255, 0], [0, 0, 255]],
            ["Rxx", "Rxy", "Rzz"], ["\u03A9", "\u03A9", "\u03A9"],
            str(result_holder.mode), self.units[str(result_holder.mode)])

        self.convergence_plot.set_plots(result_holder.H_mag[:lim],
                                        [result_holder.L2convergence_dm],
                                        [[0, 0, 0]], ["L2 convergence"],
                                        ["a.u."], str(result_holder.mode),
                                        self.units[str(result_holder.mode)])

        if lim >= 2:
            self.PIMM_plot.update(result_holder.H_mag[:lim],
                                  result_holder.PIMM_freqs, result_holder.PIMM,
                                  self.PIMM_deltaf)

            self.PIMM_plot.update_axis(left_caption="PIMM-FMR Frequency",
                                       left_units="Hz",
                                       bottom_caption=str(result_holder.mode),
                                       bottom_units=self.units[str(
                                           result_holder.mode)])

            self.PIMM_update_roi_loc()
            if len(result_holder.SD_freqs) > 1:
                self.SD_deltaf = result_holder.SD_freqs[1] - \
                    result_holder.SD_freqs[0]
                self.SD_plot.set_VSD_holders(result_holder.Rxx_vsd,
                                             result_holder.Rxy_vsd)
                self.SD_plot.update_image(result_holder.H_mag[:lim],
                                          result_holder.SD_freqs,
                                          self.SD_deltaf)
                self.SD_plot.update_axis(
                    left_caption="SD-FMR Frequency",
                    left_units="Hz",
                    bottom_caption=str(result_holder.mode),
                    bottom_units=self.units[str(result_holder.mode)])
                self.SD_update_roi_loc()
