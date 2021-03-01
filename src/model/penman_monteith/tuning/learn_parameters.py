import data.murray_data_loader as data_loader
from data import util
import model.penman_monteith.penman_monteith as penman_monteith
import model.storage.objective_hysteresis_model as ohm
from collections import namedtuple
import numpy as np
import pandas as pd
import seaborn as seaborn
import matplotlib.pyplot as plt


def auto_tune(config):
    params = config.penman_monteith_params["tuning_params"]
    alpha_range = (params["alpha"][0], params["alpha"][1])
    beta_range = (params["beta"][0], params["beta"][1])
    number = params["number"]
    file_root = config.output_dir / "pm_autotune"
    best = optimize(alpha_range, beta_range, number, file_root)
    config.penman_monteith_params["alpha"] = best["alpha"]
    config.penman_monteith_params["beta"] = best["beta"]
    best.to_csv(file_root / "final_params.csv")


def main():
    alpha_range = (0, 1.5)
    beta_range = (0, 30)
    number = 40
    file_name = "".join(["error_a_", str(alpha_range), "_b_", str(beta_range), "_n_", str(number)])
    file_name = util.get_project_root() / "src/model/penman_monteith/tuning" / file_name
    print(file_name)
    optimize(alpha_range, beta_range, number, file_name)


def optimize(alpha_range, beta_range, number, file_root):
    file_root.mkdir(parents=True, exist_ok=True)
    errors = get_errors(alpha_range, beta_range, number)
    errors.to_csv(file_root / "errors.csv")
    # errors = pd.read_csv(file_root, index_col=0)
    best = errors[errors["error"] == errors["error"].min()].iloc[0]
    print(best)
    errors = errors.round(decimals=3)
    pivoted = errors.pivot(index="beta", columns="alpha")
    fig, ax = plt.subplots(figsize=(7, 10))
    seaborn.heatmap(pivoted)
    fig.savefig(file_root / "heatmap.png")
    return best


def get_errors(alpha_range, beta_range, number):
    alphas = np.linspace(alpha_range[0], alpha_range[1], num=number)
    betas = np.linspace(beta_range[0], beta_range[1], num=number)
    error_matrix = pd.DataFrame(columns=["alpha", "beta", "error"])
    for alpha in alphas:
        for beta in betas:
            error = calculate_error(alpha, beta)
            error_matrix.loc[len(error_matrix.index)] = [alpha, beta, error]
    return error_matrix


def calculate_error(alpha, beta):
    data = get_observations()
    sensible_stats = get_statistical_vars("sensible_heat")
    latent_stats = get_statistical_vars("latent_heat")
    error_total = 0
    for row in data.iterrows():
        error = calculate_error_row(alpha, beta, row[1], latent_stats, sensible_stats)
        error_total = error_total + error
    average_error = error_total/len(data.index)
    print("a:" + str(alpha) + " b:" + str(beta) + "\terror: " + str(average_error))
    return average_error


def calculate_error_row(alpha, beta, observation_row, latent_stats, sensible_stats):
    estimate_sensible, estimate_latent = penman_monteith.calc_sensible_and_latent_heat(
        alpha, beta, observation_row["net_radiation"], observation_row["storage"],
        observation_row["temp"], observation_row["pressure"])
    actual_sensible, actual_latent = observation_row["sensible_heat"], observation_row["latent_heat"]
    sensible_error = calculate_error_component(sensible_stats, estimate_sensible, actual_sensible)
    latent_error = calculate_error_component(latent_stats, estimate_latent, actual_latent)
    error = (sensible_error + latent_error)/2
    return error


def calculate_error_component(stats, estimated, actual):
    estimated = normalize(stats, estimated)
    actual = normalize(stats, actual)
    difference = estimated - actual
    return difference * difference


def normalize(stats, value):
    centered = value - stats.mean
    scaled = centered/stats.std
    return scaled

Vars = namedtuple("vars", ["mean", "std"])

def get_statistical_vars(column_name):
    data = get_observations()
    mean = data[column_name].mean()
    standard_deviation = data[column_name].std()
    return Vars(mean, standard_deviation)


def get_observations():
    data = data_loader.get_energy_balance_data()
    materials = data_loader.get_surface_data()
    radiative_fluxes = data["net_radiation"].to_numpy()
    times = data["time"].to_numpy()
    data["storage"] = ohm.calculate_storage_heat_flux(materials, radiative_fluxes, time=times)
    return data


if __name__ == "__main__":
    main()
