import pandas as pd
import numpy as np
import data.murray_data_loader as data_loader
import model.storage.objective_hysteresis_model as ohm
from matplotlib import pyplot as plt
import matplotlib.dates as dates
import model.solar_radiation.solar_radiation_calculator as rad
import util.time_util as time_util

materials = data_loader.get_surface_data()
times, radiative_fluxes = data_loader.get_radiation_data()
ohm_output = ohm.calculate_storage_heat_flux(materials, radiative_fluxes, time=times)

murray = rad.Location(40.67250, 111.80220, "US/Mountain") # Mountain Daylight Time is UTC+6
hours = range(0, 24)
minutes = range(0, 60)
model_times = [pd.Timestamp(
    time_util.make_date_time(year=2005, month=8, day=20, hour=hour, minute=minute, timezone=murray.timezone))
         for hour in hours
         for minute in minutes]

model_rad = [rad.calc_radiation_flux(date_time, murray, albedo=data_loader.albedo) for date_time in model_times]
model_ohm = ohm.calculate_storage_heat_flux(materials, np.array(model_rad), time=np.array(model_times))


tz = times[0].tz
fig, ax = plt.subplots()

ax.plot(model_times, model_rad, 'y', dashes=[5, 2], label="Modeled Net Q_s")
ax.plot(model_times, model_ohm, 'r', dashes=[5, 2], label="Storage from Modeled Radiation")
ax.plot(times, radiative_fluxes, 'y', label="Net Q_s")
ax.plot(times, ohm_output, 'r', label="Storage from Observed Radiation")
ax.xaxis.set_major_locator(dates.HourLocator(interval=2, tz=tz))
ax.xaxis.set_major_formatter(dates.DateFormatter('%H', tz=tz))
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -.1), ncol=2)
plt.subplots_adjust(bottom=.20)


fig.savefig("radiation_over_time.png")

ax.clear()

ax.scatter(model_rad, model_ohm, label="From modeled radiation")
ax.scatter(radiative_fluxes, ohm_output, label="From observed radiation")
plt.legend()
fig.savefig("hysteresis.png")
