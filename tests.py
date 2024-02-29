
import unittest
from datetime import datetime
from dateutil import tz

from suntime import Sun, SunTimeException

_SF_LAT = 37.7749
_SF_LON = -122.4194

_NORTH_POLE_LAT = 90
_NORTH_POLE_LON = 0


class TestCommonSun(unittest.TestCase):
    """ Test on a location where the sun always rises and sets (i.e. San Francisco) """

    def setUp(self):
        self.sun = Sun(_SF_LAT, _SF_LON)  # Coordinates for San Francisco

    def _test_get_sunrise_time(self):
        # Sunrise in San Francisco
        expected_sunrise = datetime(2024, 3, 11, 14, 26, tzinfo=tz.tzutc())  # 6:26 AM local time
        utc_sunrise = self.sun.get_sunrise_time(datetime(2024, 3, 11))
        local_sunrise = self.sun.get_local_sunrise_time(datetime(2024, 3, 11), tz.gettz('America/Los_Angeles'))
        # Assert time matches 14:40 UTC
        self.assertEqual(utc_sunrise, expected_sunrise)
        self.assertEqual(local_sunrise, expected_sunrise)

    def test_get_sunset_time(self):
        # Test sunset in San Francisco
        expected_sunset = datetime(2024, 3, 11, 2, 14, tzinfo=tz.tzutc())
        utc_sunset = self.sun.get_sunset_time(datetime(2024, 3, 11))
        local_sunset = self.sun.get_local_sunset_time(datetime(2024, 3, 11), tz.gettz('America/Los_Angeles'))
        print(utc_sunset)
        print(local_sunset)
        self.assertEqual(utc_sunset, expected_sunset)
        self.assertEqual(local_sunset, expected_sunset)


class TestNoSun(unittest.TestCase):
    """ Test on a location where the sun never rises or sets (i.e. North Pole) """

    def setUp(self):
        self.sun = Sun(_NORTH_POLE_LAT, _NORTH_POLE_LON)  # Coordinates for North Pole

    def test_get_sunrise_time(self):
        # Test for no sunrise
        with self.assertRaises(SunTimeException):
            self.sun.get_sunrise_time(datetime(2024, 12, 21))  # Winter solstice in the northern hemisphere

    def test_get_sunset_time(self):
        # Test for no sunset
        with self.assertRaises(SunTimeException):
            self.sun.get_sunset_time(datetime(2024, 6, 21))  # Summer solstice in the northern hemisphere


if __name__ == '__main__':
    unittest.main()