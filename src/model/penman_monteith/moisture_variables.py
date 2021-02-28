import math
import numpy as np
from matplotlib import pyplot as plt

L_v = 2.5e6  # J/kg
R_v = 461  # J/K/kg
T_0 = 273.15  # K
e_0 = 6.113  # hPa
c_p = 1004 #J/K/kg
epsilon = 0.622 #kg/kg


def get_psychrometric_constant(pressure):
    # We could use a variable c_p depending on moisture content of air, but I don't think we have that info
    return c_p/L_v * pressure / epsilon


def clausius_clapeyron_e_s(T, is_C=True):
    if is_C:
        T = as_kelvin(T)
    return e_0 * math.exp(L_v/R_v*(1/T_0 - 1/T)) #hPa * e^(J/kg/(J/kg/K) * 1/K) = hPa * unitless^unitless = hPa


def slope_e_s(T, is_C=True):
    if is_C:
        T = as_kelvin(T)
    return L_v/R_v * 1/(T*T) * clausius_clapeyron_e_s(T, is_C=False)


def as_kelvin(temp_in_C):
    return temp_in_C + 273.15


def plot_sat_vapor_pressure_and_slope():
    """
        Test to see if the slope equation is correct by comparing to finite difference.
    """
    temps = np.linspace(0, 40, num=100)
    delta_T = 40/100
    e_s = [clausius_clapeyron_e_s(temp) for temp in temps]
    finite_difference_delta = finite_difference(e_s, delta_T)
    delta = [slope_e_s(temp) for temp in temps]

    fig, ax = plt.subplots()

    ax.plot(temps, e_s, 'y', label="e_S")
    ax.plot(temps, delta, 'r', label="d(e_s)/dT")
    ax.plot(temps[0:-1], finite_difference_delta, 'g', label="Finite difference")
    plt.legend()

    fig.savefig("sat_vapor_pressure_and_slope.png")


def finite_difference(series, delta):
    brackets = zip(series[0:-1], series[1:])
    return [(top - bottom)/delta for (bottom, top) in brackets]


plot_sat_vapor_pressure_and_slope()
