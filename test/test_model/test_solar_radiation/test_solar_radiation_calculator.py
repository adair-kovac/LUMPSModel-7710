import model.solar_radiation.solar_radiation_calculator as calc
import datetime
import unittest
import math
from model.solar_radiation.solar_radiation_calculator import Location
from util.time_util import make_date_time

vancouver = Location(49.25, 123.1, "US/Pacific")


class TestSolarRadiation(unittest.TestCase):

    def test_flux_zero_at_night(self):
        date_time = make_date_time(hour=0)
        flux = calc.calc_radiation_flux(date_time, vancouver)
        self.assertAlmostEqual(flux, 0)

    def test_solar_declination(self):
        date_time = datetime.date(2021, 3, 5)
        solar_declination = calc.get_solar_declination_angle(date_time.timetuple())
        self.assertAlmostEqual(math.degrees(solar_declination), -7.05, places=1)

    def test_elevation_angle(self):
        date_time = make_date_time(month=3, day=5, hour=15, timezone=vancouver.timezone)
        radiation_variables = calc.get_radiation_variables(date_time, vancouver)
        elevation_angle = radiation_variables["elevation_angle"]
        self.assertAlmostEqual(math.degrees(elevation_angle), 22.9, places=1)

    def test_azimuth_angle(self):
        date_time = make_date_time(month=2, day=4, hour=15, timezone=vancouver.timezone)
        radiation_variables = calc.get_radiation_variables(date_time, vancouver)
        azimuth = radiation_variables["solar_azimuth"]
        self.assertAlmostEqual(math.degrees(azimuth), 225.4, places=1)

    def test_to_zenith_angle(self):
        elevation_angle = math.radians(20)
        zenith_angle = calc.to_zenith_angle(elevation_angle)
        self.assertAlmostEqual(math.degrees(zenith_angle), 70)

    def test_get_angle_of_incidence_of_solar_radiation_is_zenith_angle_for_no_slope(self):
        zenith_angle = math.radians(40)
        angle = calc.get_angle_of_incidence_of_solar_radiation(0, 0, math.radians(20), zenith_angle)
        self.assertAlmostEqual(angle, zenith_angle)

    def test_lannemezan_local_apparent_solar_time(self):
        lannemezan = Location(43 + 6/60 + 32.9/360, -21/60 - 32.1/360, "Europe/Paris")
        date_time = make_date_time(month=6, day=25, hour=12, year=2011, timezone=lannemezan.timezone)
        radiation_variables = calc.get_radiation_variables(date_time, lannemezan)
        self.assertAlmostEqual(radiation_variables["local_solar_time"], 9 + 59/60, places=0)


if __name__ == '__main__':
    unittest.main()