

class Style:

    def __init__(self, *args, **kwargs):
        self.args = []
        self.kwargs = dict()
        self.args.extend(args)
        self.kwargs.update(kwargs)

    def plus(self, other):
        new_args = self.args + other.args
        new_kwargs = dict(self.kwargs, **other.kwargs)
        return Style(*new_args, **new_kwargs)


model = Style(dashes=[5, 2])
observation = Style()

shortwave = Style("y")
longwave = Style("tab:gray")
storage = Style("r")
sensible = Style("g")
latent = Style("b")
allwave = Style("tab:orange")
