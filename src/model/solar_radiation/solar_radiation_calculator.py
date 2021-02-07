from datetime import datetime
import math
from math import cos, sin, acos, asin
from collections import namedtuple

C = 2 * math.pi  # radians in a circle
S_0 = 1366  # W/m^2, solar "constant"

Clouds = namedtuple("CloudCoverage", ["high", "medium", "low"])
# longitude is positive for west coordinates for some reason
Location = namedtuple("Location", ["latitude", "longitude", "timezone"])


def calc_radiation_flux(date_time, location, slope_angle=0, slope_azimuth=0, clouds=Clouds(0,0,0), albedo=0):
    radiation_variables = get_radiation_variables(date_time, location, slope_angle, slope_azimuth, clouds, albedo)
    return radiation_variables["flux"]


def get_radiation_variables(date_time, location, slope_angle=0, slope_azimuth=0, clouds=Clouds(0,0,0), albedo=0):
    radiation_variables = dict()

    longitude = math.radians(location.longitude)
    latitude = math.radians(location.latitude)
    struct_time = date_time.utctimetuple()

    hour_fraction = get_fractional_hour_of_day(struct_time)
    radiation_variables["hour_fraction"] = hour_fraction

    solar_declination = get_solar_declination_angle(struct_time)
    radiation_variables["solar_declination"] = solar_declination

    elevation_angle = get_elevation_angle(hour_fraction, latitude, longitude, solar_declination)
    radiation_variables["elevation_angle"] = elevation_angle

    zenith_angle = to_zenith_angle(elevation_angle)
    radiation_variables["zenith_angle"] = zenith_angle

    solar_azimuth = get_solar_azimuth_angle(latitude, solar_declination, zenith_angle,
                                            check_is_after_solar_noon(hour_fraction, longitude))
    radiation_variables["solar_azimuth"] = solar_azimuth

    angle_of_incidence = get_angle_of_incidence_of_solar_radiation(slope_angle, slope_azimuth, solar_azimuth,
                                                                   zenith_angle)
    radiation_variables["angle_of_incidence"] = angle_of_incidence

    flux_at_angle = get_flux_at_angle(S_0, angle_of_incidence)
    radiation_variables["flux_debug_1_angle"] = flux_at_angle
    flux_with_clouds = get_flux_with_clouds(flux_at_angle, clouds, elevation_angle)
    radiation_variables["flux_debug_2_angle_and_clouds"] = flux_with_clouds
    flux_with_albedo = flux_with_clouds * (1 - albedo)
    radiation_variables["flux_debug_3_angle_clouds_and_albedo"] = flux_with_albedo
    radiation_variables["flux"] = flux_with_albedo

    return radiation_variables


def get_flux_at_angle(perpendicular_flux, angle_of_incidence):
    return perpendicular_flux * cos(angle_of_incidence)


def get_flux_with_clouds(flux, clouds, elevation_angle):
    transmissivity = get_transmissivity(clouds, elevation_angle)
    return transmissivity * flux


def get_transmissivity(clouds, elevation_angle):
    return (0.6 + .2*sin(elevation_angle))*(1-.4*clouds.high)*(1-.7*clouds.medium)*(1-.4*clouds.low)


def get_angle_of_incidence_of_solar_radiation(slope_angle, slope_azimuth, solar_azimuth, zenith_angle):
    return acos(
        cos(slope_angle) * cos(zenith_angle) +
        sin(slope_angle) * sin(zenith_angle) * cos(solar_azimuth - slope_azimuth))


def check_is_after_solar_noon(hour_fraction, longitude):
    local_solar_time = hour_fraction + longitude/C*24
    return local_solar_time > 12


def get_solar_azimuth_angle(latitude, solar_declination, zenith_angle, is_after_solar_noon):
    alpha = acos((sin(solar_declination) - sin(latitude) * cos(zenith_angle)) / (cos(latitude) * sin(zenith_angle)))
    if is_after_solar_noon:
        alpha = C - alpha
    return alpha


def to_zenith_angle(elevation_angle):
    return C / 4 - elevation_angle


def get_elevation_angle(hour_fraction, latitude, longitude, solar_declination):
    return asin(
        sin(latitude) * sin(solar_declination) -
        cos(latitude) * cos(solar_declination) * cos(C * hour_fraction / 24 - longitude))


def degrees_to_radians(degrees):
    return C * degrees / 360.


def get_solar_declination_angle(struct_time):
    julian_day = get_julian_day(struct_time)
    return .409*cos(C * (julian_day - 173) / 365)


def get_julian_day(struct_time):
    return struct_time.tm_yday


def get_fractional_hour_of_day(struct_time):
    return struct_time.tm_hour + struct_time.tm_min / 60.
