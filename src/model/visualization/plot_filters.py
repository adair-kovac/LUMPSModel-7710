from model.visualization.plot import BaseFilter
from matplotlib import pyplot as plt
import pytz
import matplotlib.dates as dates


class Save(BaseFilter):
    path = None

    def __init__(self, in_path):
        self.path = in_path

    def apply(self, fig, ax):
        fig.savefig(self.path)
        plt.close(fig)


class TimeFormatXAxis(BaseFilter):
    timezone_string = None

    def __init__(self, timezone_str):
        self.timezone_string = timezone_str

    def apply(self, fig, ax):
        tz = pytz.timezone(self.timezone_string)
        ax.xaxis.set_major_locator(dates.HourLocator(interval=2, tz=tz))
        ax.xaxis.set_major_formatter(dates.DateFormatter('%H', tz=tz))


class SetBottomLegend(BaseFilter):

    def __init__(self, scale_factor=.30, anchor_start=0.5, anchor_end=-.1):
        self.chart_scale = scale_factor
        self.anchor_start = anchor_start
        self.anchor_end = anchor_end

    def apply(self, fig, ax):
        chart_scale = .30
        ax.legend(loc='upper center', bbox_to_anchor=(self.anchor_start, self.anchor_end), ncol=2)
        plt.subplots_adjust(bottom=chart_scale)