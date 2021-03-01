from matplotlib import pyplot as plt


class BasePlot:

    def __init__(self):
        self.pre_filters = []
        self.post_filters = []

    def plot_data(self, fig, ax):
        pass

    def with_pre_filter(self, *args):
        self.pre_filters.extend(args)
        return self

    def with_post_filter(self, *args):
        self.post_filters.extend(args)
        return self

    def run(self):
        fig, ax = plt.subplots()
        ax.clear()
        for pre_filter in self.pre_filters:
            pre_filter.apply(fig, ax)
        self.plot_data(fig, ax)
        for post_filter in self.post_filters:
            post_filter.apply(fig, ax)


class BaseFilter:

    def apply(self, fig, ax):
        pass
