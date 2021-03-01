import pandas as pd
import numpy as np
import data.murray_data_loader as data_loader
import model.storage.objective_hysteresis_model as ohm
from matplotlib import pyplot as plt
import matplotlib.dates as dates
import model.radiation.solar_radiation_calculator as rad
import util.location_util
import util.time_util as time_util
import model.penman_monteith.penman_monteith as penman_monteith
from model.penman_monteith.tuning import learn_parameters
import model.radiation.longwave_radiation as longwave
import pytz
from util.exceptions import ConfigValueNotRecognized
from model.visualization import styles
from model.visualization.plot_filters import Save, SetBottomLegend, TimeFormatXAxis
from model.visualization.line_plot import LinePlot, YData


def get_model_output(config):
    data = data_loader.get_energy_balance_data()
    if config.longwave_model:
        estimate_longwave(config, data)
    estimate_storage(config, data)
    estimate_sensible_and_latent(config, data)
    return data


def estimate_longwave(config, data):
    if config.longwave_model == "burridge_gadd":
        constant_lwr = longwave.burridge_gadd_parameterization()
        data["longwave"] = constant_lwr
    else:
        raise ConfigValueNotRecognized("Unrecognized longwave radiation model: " + config.longwave_model)
    data["net_all_wave"] = data["net_radiation"] + data["longwave"]
    data["net_radiation"] = data["net_all_wave"]


def estimate_storage(config, data):
    radiative_fluxes = data["net_radiation"].to_numpy()
    times = data["time"].to_numpy()
    data["storage"] = ohm.storage_heat_flux(config, radiative_fluxes, time=times)
    data["residual"] = data["net_radiation"] - data["sensible_heat"] - data["latent_heat"]


def estimate_sensible_and_latent(config, data):
    if "tuning_params" in config.penman_monteith_params:
        learn_parameters.auto_tune(config)
    for index, row in data.iterrows():
        estimate_sensible, estimate_latent = penman_monteith.sensible_and_latent_heat(
            config, row["net_radiation"], row["storage"], row["temp"], row["pressure"])
        data.at[index, "model_sensible"] = estimate_sensible
        data.at[index, "model_latent"] = estimate_latent


def make_lumps_chart(config, model_output):
    model_ohm, model_rad, model_times, murray = get_modeled_radiation(config)
    data = model_output

    x_axis = data["time"]
    y_data = [
        YData(model_rad, "Modeled Net Q_s", styles.model.plus(styles.shortwave), x_axis=model_times),
        YData(data["net_solar"], "Net Q_s", styles.observation.plus(styles.shortwave)),
        YData(data["storage"], "Storage from Objective Hysteresis", styles.storage.plus(styles.model)),
        YData(data["residual"], "Storage from Residual", styles.storage.plus(styles.observation)),
        YData(data["sensible_heat"], "Observed Sensible Heat", styles.sensible.plus(styles.observation)),
        YData(data["model_sensible"], "Modeled Sensible Heat", styles.sensible.plus(styles.model)),
        YData(data["latent_heat"], "Observed Latent Heat", styles.latent.plus(styles.observation)),
        YData(data["model_latent"], "Modeled Latent Heat", styles.latent.plus(styles.model))
    ]

    if config.longwave_model:
        y_data.extend([
            YData(data["longwave"], "Modeled Longwave Radiation", styles.longwave.plus(styles.model)),
            YData(data["net_all_wave"], "All-wave Radiation", styles.allwave.plus(styles.model))
        ])

    LinePlot(x_axis, y_data).with_post_filter(
        TimeFormatXAxis(murray.timezone),
        SetBottomLegend(),
        Save(config.output_dir / "full_model.png")
    ).run()



def make_hysteresis_charts(config, model_output):
    model_ohm, model_rad, model_times, murray = get_modeled_radiation(config)
    base_radiation = model_output["net_solar"]
    if config.longwave_model == "burridge_gadd":
        base_radiation = model_output["net_all_wave"]
        model_rad = [x + longwave.burridge_gadd_param for x in model_rad]

    fig, ax = plt.subplots()
    ax.scatter(model_rad, model_ohm, label="From modeled radiation")
    ax.scatter(base_radiation, model_output["storage"], label="From observed radiation")
    plt.legend()
    fig.savefig(config.output_dir / "hysteresis.png")


def get_modeled_radiation(config):
    # The way this is currently written, it only uses half the available datapoints (because
    # the passed model_output has already downsampled the radiation data to match the lower
    # resolution of the weather data).
    murray = util.location_util.Location(40.67250, 111.80220, "US/Mountain")  # Mountain Daylight Time is UTC+6
    model_rad, model_times = get_model_radiation(murray)
    model_ohm = ohm.storage_heat_flux(config, np.array(model_rad), time=np.array(model_times))
    return model_ohm, model_rad, model_times, murray


def get_model_radiation(murray):
    model_times = make_day_time_series(murray)
    model_rad = [rad.calc_radiation_flux(date_time, murray, albedo=data_loader.albedo) for date_time in model_times]
    return model_rad, model_times


def make_day_time_series(location):
    hours = range(0, 24)
    minutes = range(0, 60)
    model_times = [pd.Timestamp(
        time_util.make_date_time(year=2005, month=8, day=20, hour=hour, minute=minute, timezone=location.timezone))
        for hour in hours
        for minute in minutes]
    return model_times


def main():
    data = data_loader.get_energy_balance_data()
    materials = data_loader.get_surface_data()
    radiative_fluxes = data["net_radiation"].to_numpy()
    times = data["time"].to_numpy()
    data["storage"] = ohm.calculate_storage_heat_flux(materials, radiative_fluxes, time=times)

    alpha = 0.473684
    beta = 10.0
    for index, row in data.iterrows():
        estimate_sensible, estimate_latent = penman_monteith.calc_sensible_and_latent_heat(
            alpha, beta, row["net_radiation"], row["storage"], row["temp"], row["pressure"])
        data.at[index, "model_sensible"] = estimate_sensible
        data.at[index, "model_latent"] = estimate_latent

    data["residual"] = data["net_radiation"] - data["sensible_heat"] - data["latent_heat"]
    fig, ax = plot_radiation_and_ohm()

    ax.plot(times, data["storage"], 'r', dashes=[5, 2], label="Storage from Objective Hysteresis")
    ax.plot(times, data["residual"], 'r', label="Storage from Observed Residual")
    ax.plot(times, data["sensible_heat"], 'g', label="Observed Sensible Heat")
    ax.plot(times, data["model_sensible"], 'g', dashes=[5, 2], label="Model Sensible Heat")
    ax.plot(times, data["latent_heat"], 'b', label="Observed Latent Heat")
    ax.plot(times, data["model_latent"], 'b', dashes=[5, 2], label="Model Latent Heat")

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -.1), ncol=2)
    plt.subplots_adjust(bottom=.30)

    fig.savefig("full_model.png")


def plot_radiation_and_ohm(just_ohm=False):
    materials = data_loader.get_surface_data()
    times, radiative_fluxes = data_loader.get_radiation_data()
    ohm_output = ohm.calculate_storage_heat_flux(materials, radiative_fluxes, time=times)

    murray = util.location_util.Location(40.67250, 111.80220, "US/Mountain") # Mountain Daylight Time is UTC+6
    hours = range(0, 24)
    minutes = range(0, 60)
    model_times = [pd.Timestamp(
        time_util.make_date_time(year=2005, month=8, day=20, hour=hour, minute=minute, timezone=murray.timezone))
             for hour in hours
             for minute in minutes]

    model_rad = [rad.calc_radiation_flux(date_time, murray, albedo=data_loader.albedo) for date_time in model_times]
    model_ohm = ohm.calculate_storage_heat_flux(materials, np.array(model_rad), time=np.array(model_times))

    fig, ax = plt.subplots()

    tz = times[0].tz
    ax.plot(model_times, model_rad, 'y', dashes=[5, 2], label="Modeled Net Q_s")
    ax.plot(times, radiative_fluxes, 'y', label="Net Q_s")
    if just_ohm:
        ax.plot(model_times, model_ohm, 'r', dashes=[5, 2], label="Storage from Modeled Radiation")
        ax.plot(times, ohm_output, 'r', label="Storage from Observed Radiation")

    ax.xaxis.set_major_locator(dates.HourLocator(interval=2, tz=tz))
    ax.xaxis.set_major_formatter(dates.DateFormatter('%H', tz=tz))

    if just_ohm:
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -.1), ncol=2)
        plt.subplots_adjust(bottom=.20)
        fig.savefig("radiation_over_time.png")

        ax.clear()

        ax.scatter(model_rad, model_ohm, label="From modeled radiation")
        ax.scatter(radiative_fluxes, ohm_output, label="From observed radiation")
        plt.legend()
        fig.savefig("hysteresis.png")

    return fig, ax


if __name__ == "__main__":
    main()
