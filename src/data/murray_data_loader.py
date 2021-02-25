import pandas as pd
import numpy as np
import dateutil
albedo = .18


def get_radiation_data():
    """

    :return: NumPy array of (intensity W/m^2, date_time) in (float, np.datetime64)
    :rtype: np.ndarray
    """
    data = pd.read_csv("../../data/raw/murray_solar.csv", header=6, skiprows=[7], parse_dates=["Date_Time"])
    return (data["Date_Time"].to_numpy(), data["solar_radiation_set_1"].to_numpy()*(1-albedo))


def get_surface_data():
    data = pd.read_csv("../../data/processed/surface_types.csv", usecols=range(0,5))
    return data


def get_weather_data():
    date_parser = lambda time: dateutil.parser.parse("2005-08-20 " + time + ":00 MDT")
    data = pd.read_csv("../../data/processed/murray_weather.txt", sep="\t", parse_dates=["time"],
                       date_parser=date_parser)
    return data
