from experiments.config.config import Config
from model import lumps
from model.storage.tuning.learn_materials_coefficients import get_best_model_output
from model.penman_monteith.tuning.learn_parameters import calculate_normalized_squared_error


def evaluate_model(model_output):
    actual_latent = model_output["latent_heat"]
    actual_sensible = model_output["sensible_heat"]
    estimate_latent = model_output["model_latent"]
    estimate_sensible = model_output["model_sensible"]
    return calculate_normalized_squared_error(actual_latent, actual_sensible, estimate_latent, estimate_sensible)


def write_anse(error, file):
    file = open(file, "w")
    file.write("Average normalized squared error: " + str(error))
    file.close()


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
    write_anse(evaluate_model(data), config.output_dir / "anse")


if __name__ == "__main__":
    main()
