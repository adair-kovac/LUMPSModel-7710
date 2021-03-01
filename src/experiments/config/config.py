import yaml
import pandas as pd
from data.util import get_project_root


class Config:
    config = None
    experiment_name = None
    penman_monteith_params = None
    longwave_model = None
    surface_data = None
    output_dir = None

    def load(self):
        with open(get_project_root() / "src/experiments/config/config.yaml") as config:
            self.config = yaml.load(config, Loader=yaml.FullLoader)
        conf = self.config

        self.experiment_name = conf["active_experiment"]
        self.output_dir = get_project_root() / conf["output_root_dir"] / str(self.experiment_name)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        experiment = conf["experiments"][self.experiment_name]

        self.penman_monteith_params = experiment["penman_monteith_params"]

        if "longwave_model" in experiment:
            self.longwave_model = experiment["longwave_model"]

        self.load_surface_data(experiment["surface_materials_mapping"])
        return self

    def load_surface_data(self, mapping_name):
        sm_conf = self.config["surface_materials"]
        coverage = pd.read_csv(get_project_root() / sm_conf["coverage_data"])
        materials = pd.read_csv(get_project_root() / sm_conf["materials_data"])
        mapping = sm_conf["mappings"][mapping_name]

        surface_materials = pd.DataFrame(columns=["Surface Type", "Material"])
        for surface, material in mapping.items():
            surface_materials.loc[len(surface_materials.index)] = [surface, material]

        # This is an inner join - if a type isn't mapped in the config, it's skipped
        joined = coverage.merge(surface_materials, on="Surface Type").merge(materials, on="Material")
        self.surface_data = joined
