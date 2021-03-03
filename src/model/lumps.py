import pandas as pd
import numpy as np
import data.murray_data_loader as data_loader
import model.storage.objective_hysteresis_model as ohm
from matplotlib import pyplot as plt
import model.radiation.solar_radiation_calculator as rad
import util.location_util
import util.time_util as time_util
import model.penman_monteith.penman_monteith as penman_monteith
from model.penman_monteith.tuning import learn_parameters
import model.radiation.longwave_radiation as longwave

from model.storage.residual import set_residual
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
    set_residual(data)


def estimate_sensible_and_latent(config, data):
    storage_column = "storage"
    if "storage_source" in config.experiment:
        storage_column = config.experiment["storage_source"] # used to set it to residual
    if "tuning_params" in config.penman_monteith_params and "disabled" not in config.penman_monteith_params:
        learn_parameters.auto_tune(config, storage_column)
    for index, row in data.iterrows():
        estimate_sensible, estimate_latent = penman_monteith.sensible_and_latent_heat(
            config, row["net_radiation"], row[storage_column], row["temp"], row["pressure"])
        data.at[index, "model_sensible"] = estimate_sensible
        data.at[index, "model_latent"] = estimate_latent

def make_pure_observations_chart():
    data = data_loader.get_energy_balance_data()
    x_axis = data["time"]
    y_data = [
        YData(data["net_solar"], "Net Q_s", styles.observation.plus(styles.shortwave)),
        YData(data["sensible_heat"], "Observed Sensible Heat", styles.sensible.plus(styles.observation)),
        YData(data["latent_heat"], "Observed Latent Heat", styles.latent.plus(styles.observation)),
    ]
    import model.visualization.plot as plot_base
    class Format(plot_base.BaseFilter):
        def apply(self, fig, ax):
            ax.set_xlabel("Time")
            ax.set_ylabel("Flux (W/m^2)")
            ax.set_title("Murray Aug 20, 2005 Observations")

    LinePlot(x_axis, y_data).with_post_filter(
        TimeFormatXAxis("US/Mountain"),
        SetBottomLegend(scale_factor=.2, anchor_end=-.2),
        Format(),
        Save("observations.png")
    ).run()

make_pure_observations_chart()


def make_lumps_chart(config, model_output):
    model_rad, model_times, murray = get_modeled_shortwave_radiation()
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

    if "line_chart" in config.experiment:
        keep_columns = config.experiment["line_chart"]["keep_columns"]
        new_y_data = [column for column in y_data if column.name in keep_columns]
        y_data = new_y_data

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

    fig, ax = plt.subplots()
    ax.scatter(model_rad, model_ohm, label="From modeled radiation")
    ax.scatter(base_radiation, model_output["storage"], label="From observed radiation")
    ax.set_xlabel("Net Radiation (W/m^2)")
    ax.set_ylabel("Storage (W/m^2)")
    plt.legend()
    fig.savefig(config.output_dir / "hysteresis.png")


def get_modeled_radiation(config):
    # The way this is currently written, it only uses half the available datapoints (because
    # the passed model_output has already downsampled the radiation data to match the lower
    # resolution of the weather data).
    model_rad, model_times, murray = get_modeled_shortwave_radiation()
    if config.longwave_model == "burridge_gadd":
        model_rad = [x + longwave.burridge_gadd_param for x in model_rad]

    model_ohm = ohm.storage_heat_flux(config, np.array(model_rad), time=np.array(model_times))
    return model_ohm, model_rad, model_times, murray


def get_modeled_shortwave_radiation():
    murray = util.location_util.Location(40.67250, 111.80220, "US/Mountain")  # Mountain Daylight Time is UTC+6
    model_rad, model_times = get_model_radiation(murray)
    return model_rad, model_times, murray


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


