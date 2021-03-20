from pymag.gui.trajectory import TrajectoryPlot
from pymag.gui.plots import MultiplePlot, SpectrogramPlot
from pymag.engine.data_holders import ResultHolder
from pymag.gui.simulation_manager import Simulation
import queue
from typing import List


class PlotManager:
    """
    Plot Manager manages all plot updates in the dock
    """
    def __init__(self, magnetisation_plot: MultiplePlot,
                 resistance_plot: MultiplePlot, SD_plot: SpectrogramPlot,
                 PIMM_plot: SpectrogramPlot,
                 trajectory_plot: TrajectoryPlot) -> None:
        """
        :param magnetisation_plot
        :param resistance_plot
        :param SD_plot
        :param SD_lines
        :param PIMM_plot
        :param trajectory_plot
        Plot manager requires all individual plots
        """
        self.queue_history = []
        self.result_queue = queue.Queue()

        self.magnetisation_plot = magnetisation_plot
        self.resistance_plot = resistance_plot
        self.SD_plot = SD_plot
        # self.SD_lines = SD_lines
        self.PIMM_plot = PIMM_plot
        self.trajectory_plot = trajectory_plot

    def clear_all_plots(self):
        """
            Clear all plots
        """
        self.resistance_plot.clear_plots()
        self.magnetisation_plot.clear_plots()
        self.PIMM_plot.clear_plots()
        self.SD_plot.clear_plots()

    def plot_active_results(self, simulation_list: List[Simulation]):
        """
        :param simulation_list
            Plot active simulations 
        """
        self.clear_all_plots()
        for simulation in simulation_list:
            self.plot_result(simulation.simulation_result)

    def plot_result(self, result_holder: ResultHolder):
        """
        :param result_holder
            Holds partial result of the simulation
        Update the plots with freshly updated queue value
        """

        if not result_holder:
            return
        lim = result_holder.update_count
        if lim == 1:
            return
        # self.PIMM_plot.init_setup(Xmin=min(result_holder.H_mag[:lim]),
        #                           Xmax=max(result_holder.H_mag[:lim]),
        #                           Xsteps=len(result_holder.H_mag[:lim]),
        #                           dy=result_holder.PIMM_delta_f)
        # self.SD_plot.init_setup(Xmin=min(result_holder.H_mag[:lim]),
        #                         Xmax=max(result_holder.H_mag[:lim]),
        #                         Xsteps=len(result_holder.H_mag[:lim]),
        #                         dy=result_holder.SD_freqs[1] -
        #                         result_holder.SD_freqs[0])

        units_SI = {"H": "A/m", "theta": "deg", "phi": "deg"}
        units = units_SI

        self.magnetisation_plot.set_plots(result_holder.H_mag[:lim], [
            result_holder.m_avg[:, 0], result_holder.m_avg[:, 1],
            result_holder.m_avg[:, 2]
        ], [[255, 0, 0], [0, 255, 0], [0, 0, 255]], ["Mx", "My", "Mz"],
                                          ["norm.", "norm.", "norm."],
                                          str(result_holder.mode),
                                          units[str(result_holder.mode)])

        self.resistance_plot.set_plots(
            result_holder.H_mag[:lim],
            [result_holder.Rx, result_holder.Ry, result_holder.Rz],
            [[255, 0, 0], [0, 255, 0], [0, 0, 255]],
            ["Rxx", "Rxy", "Rzz"], ["\u03A9", "\u03A9", "\u03A9"],
            str(result_holder.mode), units[str(result_holder.mode)])

        if lim >= 2:
            # two updates of frequencies
            self.SD_plot.update(result_holder.H_mag[:lim],
                                result_holder.SD_freqs,
                                self.SD_plot.detrend_f_axis(result_holder.SD))

            self.SD_plot.update_axis(left_caption="SD-FMR Frequency",
                                     left_units="Hz",
                                     bottom_caption="Magnetic Field",
                                     bottom_units="A/m")

            self.PIMM_plot.update(result_holder.H_mag[:lim],
                                  result_holder.PIMM_delta_f,
                                  result_holder.PIMM)

            self.PIMM_plot.update_axis(left_caption="PIMM-FMR Frequency",
                                       left_units="Hz",
                                       bottom_caption="Magnetic Field",
                                       bottom_units="A/m")

            # self.SD_plot.update(result_holder.SD,
            #                     result_holder.SD_freqs[1] -
            #                     result_holder.SD_freqs[0],
            #                     result_holder.H_mag[:lim],
            #                     rm_bkg=1)
            # self.SD_plot.set_mode(result_holder.mode)
            # self.SD_lines.update(
            #     result_holder.SD,
            #     result_holder.SD_freqs[1] - result_holder.SD_freqs[0],
            #     result_holder.H_mag[:lim])
            # self.SD_lines.set_mode(result_holder.mode)

        # self.PIMM_plot.update(result_holder.PIMM, result_holder.PIMM_delta_f,result_holder.H_mag[:lim])
        # self.PIMM_plot.set_mode(result_holder.mode)

        # self.trajectory_plot.plt_traj(result_holder.traj, [
        #     10 * len(result_holder.H_mag[:lim]), 255 - 10 * len(result_holder.H_mag[:lim]),
        #     255 - 10 * len(result_holder.H_mag[:lim])
        # ])
        # self.table_results.setData(xp["MR"].astype(np.str))
