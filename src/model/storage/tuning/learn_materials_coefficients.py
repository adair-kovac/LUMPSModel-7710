import model.penman_monteith.tuning.learn_parameters as pm
import pandas as pd
import numpy as np
from model import lumps


def get_best_model_output(config):
    iterations = config.experiment["tuning_iterations"]

    errors = []
    for i in range(0, iterations):
        print("....Starting iteration " + str(i) + "....\n\n\n")
        config.set_output_dir(config.output_dir / str(i))
        config.penman_monteith_params["disabled"] = True
        best_materials_coefficients = get_best_materials_coefficients(config)
        set_materials(config, best_materials_coefficients)
        best_penman_monteith_params, error = get_best_penman_monteith_params(config)
        print("....Iteration " + str(i) + " error: " + str(error) + "....\n\n\n")
        config.penman_monteith_params.pop("disabled")
        config.penman_monteith_params.update(best_penman_monteith_params)
        print(str(config.surface_data))
        print(str(config.penman_monteith_params))
        config.set_output_dir(config.output_dir.parent)
        if errors and not error < errors[-1]:
            break
        errors.append(error)

    config.set_output_dir(config.output_dir / "best")
    write_best(config, best_materials_coefficients, best_penman_monteith_params, errors)
    model_output = lumps.get_model_output(config)
    model_output.to_csv(config.output_dir / "model_output.csv")
    return model_output


def write_best(config, best_materials_coefficients, best_penman_monteith_params, errors):
    file = open(config.output_dir / "description.txt", "w")
    file.write("Best materials coefficients:\n")
    file.write(str(best_materials_coefficients) + "\n")
    file.write("Best penman monteith params:\n")
    file.write(str(best_penman_monteith_params) + "\n")
    file.write("Average normalized squared error: " + str(errors[-1]))
    file.write("\nError series: " + str(errors))
    file.close()


def get_best_materials_coefficients(config):
    params = config.experiment["surface_materials_tuning_params"]
    errors = pd.DataFrame(columns=["a1", "a2", "a3", "error"])
    for a1 in get_parameter_space(params["a1"]):
        print("\ta1")
        for a2 in get_parameter_space(params["a2"]):
            print("\t\ta2")
            for a3 in get_parameter_space(params["a3"]):
                print("\t\t\ta3")
                set_materials(config, [a1, a2, a3])
                model_output = lumps.get_model_output(config)
                error = pm.calculate_normalized_squared_error(model_output["latent_heat"],
                                                      model_output["sensible_heat"],
                                                      model_output["model_latent"],
                                                      model_output["model_sensible"])
                errors.loc[len(errors.index)] = [a1, a2, a3, error]
                print(errors.iloc[-1])
    min = errors[errors["error"] == errors["error"].min()].iloc[0]
    return [min["a1"], min["a2"], min["a3"]]


def get_parameter_space(param):
    p_range = param["range"]
    number = param["number"]
    return np.linspace(p_range[0], p_range[1], num=number)


def get_best_penman_monteith_params(config):
    params = config.penman_monteith_params["tuning_params"]
    best = pm.auto_tune(config)
    best_params = {"alpha": best["alpha"], "beta": best["beta"]}
    return best_params, best["error"]


def set_materials(config, materials_coefficients):
    config.surface_data = pd.DataFrame(columns=["Surface Type", "Fraction", "a1", "a2", "a3"])
    config.surface_data.loc[len(config.surface_data.index)] = ["learned", 1] + materials_coefficients
