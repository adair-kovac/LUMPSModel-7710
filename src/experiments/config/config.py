import yaml
import pandas as pd
from data.util import get_project_root


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
        experiment = conf["experiments"][self.experiment_name]

        self.penman_monteith_params = experiment["penman_monteith_params"]
        self.load_surface_materials(experiment["surface_materials_mapping"])

    def load_surface_materials(self, mapping_name):
        sm_conf = self.config["surface_materials"]
        print(sm_conf)
        coverage = pd.read_csv(get_project_root() / sm_conf["coverage_data"])
        materials = pd.read_csv(get_project_root() / sm_conf["materials_data"])
        mapping = sm_conf["mappings"][mapping_name]

        surface_materials = pd.DataFrame(columns=["Surface Type", "Fraction",
                                                  "a1", "a2", "a3"])
        for surface, material in mapping.items():
            idx = len(surface_materials.index)
            surface_materials.loc[idx] = coverage[coverage["Surface Type"] == surface][0] + materials[""]



Config().load()