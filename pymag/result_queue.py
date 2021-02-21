from pymag.gui.trajectory import TrajectoryPlot
from pymag.gui.plots import LineShape, MagPlot, PlotDynamics, ResPlot
from pymag.engine.data_holders import ResultHolder
import queue
import logging


class ResultQueueSynchroniser:
    def __init__(self,
                 magnetisation_plot: MagPlot,
                 resistance_plot: ResPlot,
                 SD_plot: PlotDynamics,
                 SD_lines: LineShape,
                 PIMM_plot: PlotDynamics,
                 trajectory_plot: TrajectoryPlot,
                 progress_bar=None) -> None:
        self.queue_history = []
        self.result_queue = queue.Queue()

        self.magnetisation_plot = magnetisation_plot
        self.resistance_plot = resistance_plot
        self.SD_plot = SD_plot
        self.SD_lines = SD_lines
        self.PIMM_plot = PIMM_plot
        self.trajectory_plot = trajectory_plot
        # self.progress_bar = progress_bar

    def plot_current_queue_result(self, result_holder: ResultHolder):

        self.PIMM_plot.init_setup(Xmin=min(result_holder.H_mag),
                                  Xmax=max(result_holder.H_mag),
                                  Xsteps=len(result_holder.H_mag),
                                  dy=result_holder.PIMM_freqs)
        self.SD_plot.init_setup(Xmin=min(result_holder.H_mag),
                                Xmax=max(result_holder.H_mag),
                                Xsteps=len(result_holder.H_mag),
                                dy=result_holder.SD_freqs[1] -
                                result_holder.SD_freqs[0])

        self.magnetisation_plot.Mx.plot(result_holder.H_mag,
                                        result_holder.m_avg[:, 0],
                                        pen=(255, 0, 0))
        self.magnetisation_plot.My.plot(result_holder.H_mag,
                                        result_holder.m_avg[:, 1],
                                        pen=(0, 255, 0))
        self.magnetisation_plot.Mz.plot(result_holder.H_mag,
                                        result_holder.m_avg[:, 2],
                                        pen=(0, 0, 255))
        self.magnetisation_plot.Mx.setYRange(-1.5, 1.5, padding=0)
        self.magnetisation_plot.My.setYRange(-1.5, 1.5, padding=0)
        self.magnetisation_plot.Mz.setYRange(-1.5, 1.5, padding=0)
        self.magnetisation_plot.set_mode(result_holder.mode)
        self.resistance_plot.Rx.plot(result_holder.H_mag,
                                     result_holder.Rx,
                                     pen=(255, 0, 0))
        self.resistance_plot.Ry.plot(result_holder.H_mag,
                                     result_holder.Ry,
                                     pen=(0, 255, 0))
        self.resistance_plot.Rz.plot(result_holder.H_mag,
                                     result_holder.Rz,
                                     pen=(0, 0, 255))
        self.resistance_plot.set_mode(result_holder.mode)

        self.SD_plot.update(result_holder.SD,
                            result_holder.SD_freqs[1] -
                            result_holder.SD_freqs[0],
                            result_holder.H_mag,
                            rm_bkg=1)
        self.SD_plot.set_mode(result_holder.mode)

        self.PIMM_plot.update(result_holder.PIMM, result_holder.PIMM_freqs,
                              result_holder.H_mag)
        self.PIMM_plot.set_mode(result_holder.mode)

        # self.SD_lines.update(
        #     result_holder.SD,
        #     result_holder.SD_freqs[1] - result_holder.SD_freqs[0],
        #     result_holder.H_mag)
        # self.SD_lines.set_mode(result_holder.mode)

        self.trajectory_plot.plt_traj(result_holder.traj, [
            10 * len(result_holder.H_mag), 255 - 10 * len(result_holder.H_mag),
            255 - 10 * len(result_holder.H_mag)
        ])
        # self.table_results.setData(xp["MR"].astype(np.str))

    def on_new_element_update(self):
        try:
            _, res = self.result_queue.get(block=False)
            self.plot_current_queue_result(ResultHolder(**res))

        except queue.Empty:
            logging.debug("Queue emptied!")