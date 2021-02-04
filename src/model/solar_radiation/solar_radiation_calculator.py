from datetime import datetime
import math
from math import cos, sin, acos, asin

C = 2 * math.pi  # radians in a circle
S_0 = 1366  # W/m^2, solar "constant"


# longitude is positive for west coordinates for some reason
def calc_radiation_flux(date_time, latitude, longitude, slope_angle=0, slope_azimuth=0):
    struct_time = date_time.utctimetuple()
    julian_day = struct_time.tm_yday
    hour_fraction = struct_time.tm_hour + struct_time.tm_min/60.
    solar_declination = latitude * cos(C*(julian_day - 173)/365)
    longitude_radians = C * longitude/360.
    elevation_angle = asin(
        sin(latitude) * sin(solar_declination) -
        cos(latitude) * cos(solar_declination) * cos(C*hour_fraction/24 - longitude_radians))
    zenith_angle = C/4 - elevation_angle
    solar_azimuth = acos(
        (sin(solar_declination) - sin(latitude)*cos(zenith_angle)) /
        (cos(latitude) * sin(zenith_angle)))
    angle_of_incidence = acos(
        cos(slope_angle) * cos(zenith_angle) +
        sin(slope_angle) * sin(zenith_angle) * cos(solar_azimuth-slope_azimuth))
    return S_0 * cos(angle_of_incidence)

