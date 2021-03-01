import math
from math import cos, sin, acos, asin

from util.location_util import Clouds

C = 2 * math.pi  # radians in a circle
S_0 = 1366  # W/m^2, solar "constant"

# Returns R_s down
def calc_radiation_flux(date_time, location, slope_angle=0, slope_azimuth=0, clouds=Clouds(0, 0, 0), albedo=0):
    radiation_variables = get_radiation_variables(date_time, location, slope_angle, slope_azimuth, clouds, albedo)
    return radiation_variables["flux"]


def get_radiation_variables(date_time, location, slope_angle=0, slope_azimuth=0, clouds=Clouds(0, 0, 0), albedo=0):
    radiation_variables = dict()

    longitude = math.radians(location.longitude)
    latitude = math.radians(location.latitude)
    slope_angle = math.radians(slope_angle)
    slope_azimuth = math.radians(slope_azimuth)
    struct_time = get_utc_timetuple(date_time)

    hour_fraction = get_hour_float(struct_time)
    radiation_variables["hour_fraction"] = hour_fraction

    solar_declination = get_solar_declination_angle(struct_time)
    radiation_variables["solar_declination"] = solar_declination

    elevation_angle = get_elevation_angle(hour_fraction, latitude, longitude, solar_declination)
    radiation_variables["elevation_angle"] = elevation_angle

    zenith_angle = to_zenith_angle(elevation_angle)
    radiation_variables["zenith_angle"] = zenith_angle

    local_solar_time = get_local_apparent_solar_time(hour_fraction, longitude)
    radiation_variables["local_solar_time"] = local_solar_time

    solar_azimuth = get_solar_azimuth_angle(latitude, solar_declination, zenith_angle,
                                            local_solar_time)
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


def get_utc_timetuple(date_time):
    # Workaround for Pandas issue 32174
    # https://github.com/pandas-dev/pandas/issues/32174
    import pandas
    if type(date_time) == pandas.Timestamp:
        date_time = date_time.to_pydatetime()
    return date_time.utctimetuple()


def get_flux_at_angle(perpendicular_flux, angle_of_incidence):
    if cos(angle_of_incidence) < 0:
        return 0
    return perpendicular_flux * cos(angle_of_incidence)


def get_flux_with_clouds(flux, clouds, elevation_angle):
    transmissivity = get_transmissivity(clouds, elevation_angle)
    return transmissivity * flux


def get_transmissivity(clouds, elevation_angle):
    return (0.6 + .2*sin(elevation_angle))*(1-.4*clouds.high)*(1-.7*clouds.medium)*(1-.4*clouds.low)


def get_angle_of_incidence_of_solar_radiation(slope_angle, slope_azimuth, solar_azimuth, zenith_angle):
    if cos(zenith_angle) < 0:
        return zenith_angle
    return acos(
        cos(slope_angle) * cos(zenith_angle) +
        sin(slope_angle) * sin(zenith_angle) * cos(solar_azimuth - slope_azimuth))


def get_local_apparent_solar_time(hour_fraction, longitude):
    local_solar_time = (hour_fraction - longitude/C*24)  # technically needs an equation of time correction
    return local_solar_time


def get_solar_azimuth_angle(latitude, solar_declination, zenith_angle, local_apparent_solar_time):
    h = C/24 * (12-local_apparent_solar_time)
    cos_alpha = (sin(solar_declination) * cos(latitude) -
                  cos(solar_declination) * sin(latitude)) * cos(h) / sin(zenith_angle)
    if cos_alpha > 1:
        cos_alpha = 1
    if cos_alpha < -1:
        cos_alpha = -1
    alpha = acos(cos_alpha)
    if local_apparent_solar_time > 12:
        alpha = C - alpha
    return alpha


def to_zenith_angle(elevation_angle):
    return C / 4 - elevation_angle


def get_elevation_angle(hour_fraction, latitude, longitude, solar_declination):
    return asin(
        sin(latitude) * sin(solar_declination) -
        cos(latitude) * cos(solar_declination) * cos(C * hour_fraction / 24 - longitude))


def get_solar_declination_angle(struct_time):
    julian_day = get_julian_day(struct_time)
    return .409*cos(C * (julian_day - 173) / 365)


# Python calls this the yearday, some sources use day of year, but Stull calls it the Julian day
def get_julian_day(struct_time):
    return struct_time.tm_yday


def get_hour_float(struct_time):
    return struct_time.tm_hour + struct_time.tm_min / 60.
