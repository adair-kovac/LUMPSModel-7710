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


class TimeFormatXAxis(BaseFilter):
    timezone_string = None

    def __init__(self, timezone_str):
        self.timezone_string = timezone_str

    def apply(self, fig, ax):
        tz = pytz.timezone(self.timezone_string)
        ax.xaxis.set_major_locator(dates.HourLocator(interval=2, tz=tz))
        ax.xaxis.set_major_formatter(dates.DateFormatter('%H', tz=tz))


class SetBottomLegend(BaseFilter):
    chart_scale = .30

    def __init__(self, scale_factor=.30):
        self.chart_scale = scale_factor

    def apply(self, fig, ax):
        chart_scale = .30
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -.1), ncol=2)
        plt.subplots_adjust(bottom=chart_scale)