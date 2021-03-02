from experiments.config.config import Config
from model import lumps
from model.storage.tuning.learn_materials_coefficients import get_best_model_output


def main():
    config = Config().load()
    if "surface_materials_tuning_params" not in config.experiment:
        data = lumps.get_model_output(config)
        data.to_csv(config.output_dir / "model_output.csv")
        lumps.make_hysteresis_charts(config, data)
        lumps.make_lumps_chart(config, data)
    else:
        data = get_best_model_output(config)
        lumps.make_lumps_chart(config, data)


if __name__ == "__main__":
    main()
