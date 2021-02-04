from datetime import datetime
import math
from math import cos, sin, acos, asin

C = 2 * math.pi  # radians in a circle
S_0 = 1366  # W/m^2, solar "constant"


# longitude is positive for west coordinates for some reason
def calc_radiation_flux(date_time, latitude, longitude, slope_angle=0, slope_azimuth=0):
    struct_time = date_time.utctimetuple()
    hour_fraction = get_fractional_hour_of_day(struct_time)
    solar_declination = get_solar_declination_angle(struct_time, latitude)
    elevation_angle = get_elevation_angle(hour_fraction, latitude, longitude, solar_declination)
    zenith_angle = to_zenith_angle(elevation_angle)
    solar_azimuth = get_solar_azimuth_angle(latitude, solar_declination, zenith_angle)
    angle_of_incidence = get_angle_of_incidence_of_solar_radiation(slope_angle, slope_azimuth, solar_azimuth,
                                                                   zenith_angle)
    return flux_at_angle(S_0, angle_of_incidence)


def flux_at_angle(perpendicular_flux, angle_of_incidence):
    return perpendicular_flux * cos(angle_of_incidence)


def get_angle_of_incidence_of_solar_radiation(slope_angle, slope_azimuth, solar_azimuth, zenith_angle):
    return acos(
        cos(slope_angle) * cos(zenith_angle) +
        sin(slope_angle) * sin(zenith_angle) * cos(solar_azimuth - slope_azimuth))


def get_solar_azimuth_angle(latitude, solar_declination, zenith_angle):
    return acos(
        (sin(solar_declination) - sin(latitude) * cos(zenith_angle)) /
        (cos(latitude) * sin(zenith_angle)))


def to_zenith_angle(elevation_angle):
    return C / 4 - elevation_angle


def get_elevation_angle(hour_fraction, latitude, longitude, solar_declination):
    longitude_radians = degrees_to_radians(longitude)
    return asin(
        sin(latitude) * sin(solar_declination) -
        cos(latitude) * cos(solar_declination) * cos(C * hour_fraction / 24 - longitude_radians))


def degrees_to_radians(degrees):
    return C * degrees / 360.


def get_solar_declination_angle(struct_time, latitude):
    julian_day = get_julian_day(struct_time)
    return latitude * cos(C * (julian_day - 173) / 365)


def get_julian_day(struct_time):
    return struct_time.tm_yday


def get_fractional_hour_of_day(struct_time):
    return struct_time.tm_hour + struct_time.tm_min / 60.
