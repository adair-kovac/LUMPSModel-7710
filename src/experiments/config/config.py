import yaml
import pandas as pd


class Config:
    config = None
    experiment_name = None
    penman_monteith_params = None
    longwave_model = None
    surface_materials = None

    def load(self):
        with open("config.yaml") as config:
            self.config = yaml.load(config, Loader=yaml.FullLoader)
        conf = self.config
        self.experiment_name = conf["active_experiment"]
        print(self.experiment_name)
        experiment = conf["experiments"][self.experiment_name]
        print(experiment)
        self.penman_monteith_params = experiment["penman_monteith_params"]
        self.load_surface_materials(experiment["surface_materials_mapping"])

    def load_surface_materials(self, mapping):
        sm_conf = self.config["surface_materials"]



Config().load()