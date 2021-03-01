from collections import namedtuple
from model.visualization.plot import BasePlot


class YData:
    def __init__(self, data, name, style, x_axis=None):
        self.data = data
        self.name = name
        self.style = style
        self.x_axis = x_axis


class LinePlot(BasePlot):

    def __init__(self, x_axis, y_data):
        BasePlot.__init__(self)
        self.x_axis = x_axis
        self.y_data = y_data

    def plot_data(self, fig, ax):
        for y in self.y_data:
            x = self.x_axis
            if y.x_axis:
                x = y.x_axis
            ax.plot(x, y.data, *y.style.args, label=y.name, **y.style.kwargs)
