import unittest
from datetime import datetime
from dateutil import tz

from suntime import Sun, SunTimeException, MidnightSunException, PolarNightException

_SF_LAT = 37.7749
_SF_LON = -122.4194

_TOKYO_LAT = 35.6895
_TOKYO_LON = 139.6917

_SYDNEY_LAT = -33.8688
_SYDNEY_LON = 151.2093

_NORTH_POLE_LAT = 90
_NORTH_POLE_LON = 0


class TestWestSun(unittest.TestCase):
    """ Test on a location where the sun always rises and sets (i.e. San Francisco) """

    def setUp(self):
        self.sun = Sun(_SF_LAT, _SF_LON)  # Coordinates for San Francisco

    def test_get_sunrise_time(self):
        # Sunrise in San Francisco (winter time)
        expected_sunrise = datetime(2024, 3, 11, 14, 25, 48, tzinfo=tz.UTC)  # 6:26 AM local time
        utc_sunrise = self.sun.get_sunrise_time(datetime(2024, 3, 11))
        local_sunrise = self.sun.get_local_sunrise_time(datetime(2024, 3, 11), tz.gettz('America/Los_Angeles'))
        # Assert time matches 14:40 UTC
        self.assertEqual(utc_sunrise, expected_sunrise)
        self.assertEqual(local_sunrise, expected_sunrise)
        # Sunrise in San Francisco (summer time)
        expected_sunrise = datetime(2024, 6, 20, 12, 48, 0, tzinfo=tz.UTC)
        utc_sunrise = self.sun.get_sunrise_time(datetime(2024, 6, 20))
        local_sunrise = self.sun.get_local_sunrise_time(datetime(2024, 6, 20), tz.gettz('America/Los_Angeles'))
        # Assert time matches 13:25 UTC
        self.assertEqual(utc_sunrise, expected_sunrise)
        self.assertEqual(local_sunrise, expected_sunrise)

    def test_get_sunset_time(self):
        # Test sunset in San Francisco
        expected_sunset = datetime(2024, 3, 12, 2, 13, 48, tzinfo=tz.tzutc())
        utc_sunset = self.sun.get_sunset_time(datetime(2024, 3, 11))
        local_sunset = self.sun.get_local_sunset_time(datetime(2024, 3, 11), tz.gettz('America/Los_Angeles'))
        self.assertEqual(utc_sunset, expected_sunset)
        self.assertEqual(local_sunset, expected_sunset)
        # Check with no params
        utc_default_sunrise = self.sun.get_sunrise_time()
        local_default_sunrise = self.sun.get_local_sunrise_time()
        self.assertEqual(utc_default_sunrise.date(), datetime.now().date())
        self.assertEqual(local_default_sunrise.date(), datetime.now().date())


class TestEastSun(unittest.TestCase):

    def setUp(self):
        self.sun = Sun(_TOKYO_LAT, _TOKYO_LON)

    def test_get_sunrise_time(self):
        # Sunrise in Tokyo
        expected_sunrise = datetime(2024, 3, 11, 20, 57, 36, tzinfo=tz.UTC)
        utc_sunrise = self.sun.get_sunrise_time(datetime(2024, 3, 11))
        self.assertEqual(utc_sunrise, expected_sunrise)


class TestSouthSun(unittest.TestCase):
    """ Test south hemisphere location where the sun rises and sets (i.e. Sydney)"""

    def setUp(self):
        self.sun = Sun(_SYDNEY_LAT, _SYDNEY_LON)

    def test_get_sunrise_time(self):
        # Sunrise in Sydney
        expected_sunrise = datetime(2024, 3, 11, 6, 51, 36, tzinfo=tz.gettz('Australia/Sydney'))
        local_sunrise = self.sun.get_sunrise_time(datetime(2024, 3, 11), tz.gettz('Australia/Sydney'))
        self.assertEqual(expected_sunrise, local_sunrise)

    def test_get_sunset_time(self):
        # Test sunset in Sydney
        expected_sunset = datetime(2024, 3, 11, 19, 18, 0, tzinfo=tz.gettz('Australia/Sydney'))
        local_sunset = self.sun.get_sunset_time(datetime(2024, 3, 11), tz.gettz('Australia/Sydney'))
        self.assertEqual(expected_sunset, local_sunset)


class TestNoSun(unittest.TestCase):
    """ Test on a location where the sun never rises or sets (i.e. North Pole) """

    def setUp(self):
        self.sun = Sun(_NORTH_POLE_LAT, _NORTH_POLE_LON)  # Coordinates for North Pole

    def test_get_sunrise_time(self):
        # Test for no sunrise
        # Winter solstice in the northern hemisphere
        d = datetime(2024, 12, 21)
        with self.assertRaisesRegex(SunTimeException, 'The sun'):
            self.sun.get_sunrise_time(d)

        # Should throw specific PolarNightException which is derived
        # from SunTimeException
        with self.assertRaisesRegex(PolarNightException, 'The sun'):
            self.sun.get_sunrise_time(d)

    def test_get_sunset_time(self):
        # Test for no sunset
        # Summer solstice in the northern hemisphere
        d = datetime(2024, 6, 21)
        with self.assertRaisesRegex(SunTimeException, 'The sun'):
            self.sun.get_sunset_time(d)

        # Should throw specific MidnightSunException which is derived
        # from SunTimeException
        with self.assertRaisesRegex(MidnightSunException, 'The sun'):
            self.sun.get_sunset_time(d)


if __name__ == '__main__':
    unittest.main()
