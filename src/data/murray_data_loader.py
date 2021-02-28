import pandas as pd
import numpy as np
import dateutil
from pathlib import Path

albedo = .18


def get_radiation_data():
    """

    :return: NumPy array of (intensity W/m^2, date_time) in (float, np.datetime64)
    :rtype: np.ndarray
    """
    data = pd.read_csv(get_project_root() / "data/raw/murray_solar.csv", header=6, skiprows=[7],
                       parse_dates=["Date_Time"])
    return (data["Date_Time"].to_numpy(), data["solar_radiation_set_1"].to_numpy()*(1-albedo))


def get_surface_data():
    data = pd.read_csv(get_project_root() / "data/processed/surface_types.csv", usecols=range(0,5))
    return data


def get_weather_data():
    date_parser = lambda time: dateutil.parser.parse("2005-08-20 " + time + ":00 MDT")
    data = pd.read_csv(get_project_root() / "data/processed/murray_weather.txt", sep="\t", parse_dates=["time"],
                       date_parser=date_parser)
    return data


def get_energy_balance_data():
    data = get_weather_data()
    data = data[["time", "pressure", "temp", "sensible_heat", "latent_heat"]]
    radiation_data = get_radiation_data()[1]
    #This is hacky, would be easier to do a join if it breaks.
    radiation_on_half_hours = [x for index, x in enumerate(radiation_data) if index % 2 == 0][:-1]
    data["net_radiation"] = radiation_on_half_hours
    return data


def get_project_root() -> Path:
    return Path(__file__).parent.parent.parent


