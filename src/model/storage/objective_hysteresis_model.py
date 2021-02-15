import pandas as pd
import numpy as np
import util.exceptions as ex


def calculate_storage_heat_flux(materials, net_forcing, d_net_forcing_d_t=None, time=None):
    """
    Estimates the heat storage term of the surface energy balance equation as a partition of Q* (net shortwave and
    infrared radiation) with a hysteresis effect. Pass either d_net_forcing_d_t (rate of change of flux corresponding to
    each Q* given) or the time of each Q* observation.

    :param materials: Description of each material. Columns should be:
        "fraction" - float, the coverage fraction. Doesn't have to sum to 1.
        "a1" - coefficient of Q_* term
        "a2" - coefficient of d_Q_* term
        "a3" - coefficient of constant term
    :type materials: pd.DataFrame
    :param net_forcing: np.array of float, Q* estimates ordered by time
    :type net_forcing: np.array
    :param d_net_forcing_d_t: np.array of float, time rate of change co-indexed with net_forcing
    :type d_net_forcing_d_t: np.array
    :param time: np.array of np.datetime64, array of times for each net_forcing value
    :type time: np.array
    :return: np.array of float, estimated delta_Q_s (heat storage) at each time
    :rtype: np.array
    """

    if not time and not d_net_forcing_d_t:
        raise ex.InvalidArgumentError("Must provide either time or d_net_forcing_d_t")

    if not d_net_forcing_d_t:
        d_net_forcing_d_t = get_rate_of_change(net_forcing, time)

    array_estimate_storage = np.vectorize(estimate_storage, excluded=[2])
    return array_estimate_storage(net_forcing, d_net_forcing_d_t, materials)


def estimate_storage(net_forcing, d_net_forcing_d_t, materials):
    """
    Applies the Objective Hysteresis Model calculation to a single data point to estimate storage flux.

    :param net_forcing: Q*
    :type net_forcing: float
    :param d_net_forcing_d_t: Time rate of change of Q*
    :type d_net_forcing_d_t: float
    :param materials: materials dataframe from calculate_storage_heat_flux
    :type materials: pd.DataFrame
    """
    normalization_factor = materials["fraction"].sum()
    # We don't want to assume the fractions add up to 1 since the material type of the whole area might not be known

    weight = materials["fraction"]/normalization_factor
    components = weight*(materials["a1"]*net_forcing + materials["a2"]*d_net_forcing_d_t + materials["a3"])

    return components.sum()


def get_rate_of_change(net_forcing, time):
    array_to_seconds = np.vectorize(to_seconds)
    time_delta = array_to_seconds(get_delta(time))
    forcing_delta = get_delta(net_forcing)
    return forcing_delta/time_delta


def to_seconds(time_delta):
    return time_delta/np.timedelta64(1, 's')


def get_delta(array):
    array = repeat_ends_of_array(array)
    array_end = array[2:len(array)]
    array_beginning = array[0:len(array)-2]
    return array_end - array_beginning


def repeat_ends_of_array(array):
    beginning = array[0:1]
    end = array[len(array):len(array)+1]
    return np.concatenate([beginning, array, end])