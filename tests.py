import unittest
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from suntime import Sun, SunTimeException, MidnightSunException, PolarNightException

_SF_LAT = 37.7749
_SF_LON = -122.4194

_TOKYO_LAT = 35.6895
_TOKYO_LON = 139.6917

_SYDNEY_LAT = -33.8688
_SYDNEY_LON = 151.2093

_NORTH_POLE_LAT = 90
_NORTH_POLE_LON = 0

_SOUTH_POLE_LAT = -90
_SOUTH_POLE_LON = 0

_QUITO_LAT = -0.1807
_QUITO_LON = -78.4678


class TestWestSun(unittest.TestCase):
    """Test on a location where the sun always rises and sets (i.e. San Francisco)"""

    def setUp(self):
        self.sun = Sun(_SF_LAT, _SF_LON)  # Coordinates for San Francisco

    def test_get_sunrise_time(self):
        # Sunrise in San Francisco (winter time)
        expected_sunrise = datetime(2024, 3, 11, 14, 25, 48, tzinfo=timezone.utc)  # 6:26 AM local time
        utc_sunrise = self.sun.get_sunrise_time(datetime(2024, 3, 11))
        local_sunrise = self.sun.get_local_sunrise_time(datetime(2024, 3, 11), ZoneInfo("America/Los_Angeles"))
        # Assert time matches 14:40 UTC
        self.assertEqual(utc_sunrise, expected_sunrise)
        self.assertEqual(local_sunrise, expected_sunrise)
        # Sunrise in San Francisco (summer time)
        expected_sunrise = datetime(2024, 6, 20, 12, 48, 0, tzinfo=timezone.utc)
        utc_sunrise = self.sun.get_sunrise_time(datetime(2024, 6, 20))
        local_sunrise = self.sun.get_local_sunrise_time(datetime(2024, 6, 20), ZoneInfo("America/Los_Angeles"))
        # Assert time matches 13:25 UTC
        self.assertEqual(utc_sunrise, expected_sunrise)
        self.assertEqual(local_sunrise, expected_sunrise)

    def test_get_sunset_time(self):
        # Test sunset in San Francisco
        expected_sunset = datetime(2024, 3, 12, 2, 13, 48, tzinfo=timezone.utc)
        utc_sunset = self.sun.get_sunset_time(datetime(2024, 3, 11))
        local_sunset = self.sun.get_local_sunset_time(datetime(2024, 3, 11), ZoneInfo("America/Los_Angeles"))
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
        expected_utc_sunrise = datetime(2024, 3, 10, 20, 57, 36, tzinfo=timezone.utc)
        expected_local_sunrise = datetime(2024, 3, 11, 5, 57, 36, tzinfo=ZoneInfo("Asia/Tokyo"))

        utc_sunrise = self.sun.get_sunrise_time(datetime(2024, 3, 11))
        self.assertEqual(utc_sunrise, expected_utc_sunrise)

        local_time_sunrise = self.sun.get_local_sunrise_time(datetime(2024, 3, 11), time_zone=ZoneInfo("Asia/Tokyo"))
        self.assertEqual(local_time_sunrise, expected_local_sunrise)


class TestSouthSun(unittest.TestCase):
    """Test south hemisphere location where the sun rises and sets (i.e. Sydney)"""

    def setUp(self):
        self.sun = Sun(_SYDNEY_LAT, _SYDNEY_LON)

    def test_get_sunrise_time(self):
        # Sunrise in Sydney
        expected_sunrise = datetime(2024, 3, 11, 6, 51, 36, tzinfo=ZoneInfo("Australia/Sydney"))
        local_sunrise = self.sun.get_sunrise_time(datetime(2024, 3, 11), ZoneInfo("Australia/Sydney"))
        self.assertEqual(expected_sunrise, local_sunrise)

    def test_get_sunset_time(self):
        # Test sunset in Sydney
        expected_sunset = datetime(2024, 3, 11, 19, 18, 0, tzinfo=ZoneInfo("Australia/Sydney"))
        local_sunset = self.sun.get_sunset_time(datetime(2024, 3, 11), ZoneInfo("Australia/Sydney"))
        self.assertEqual(expected_sunset, local_sunset)


class TestNoSun(unittest.TestCase):
    """Test on a location where the sun never rises or sets (i.e. North Pole)"""

    def setUp(self):
        self.sun = Sun(_NORTH_POLE_LAT, _NORTH_POLE_LON)  # Coordinates for North Pole

    def test_get_sunrise_time(self):
        # Test for no sunrise
        # Winter solstice in the northern hemisphere
        d = datetime(2024, 12, 21)
        with self.assertRaisesRegex(SunTimeException, "The sun"):
            self.sun.get_sunrise_time(d)

        # Should throw specific PolarNightException which is derived
        # from SunTimeException
        with self.assertRaisesRegex(PolarNightException, "The sun"):
            self.sun.get_sunrise_time(d)

    def test_get_sunset_time(self):
        # Test for no sunset
        # Summer solstice in the northern hemisphere
        d = datetime(2024, 6, 21)
        with self.assertRaisesRegex(SunTimeException, "The sun"):
            self.sun.get_sunset_time(d)

        # Should throw specific MidnightSunException which is derived
        # from SunTimeException
        with self.assertRaisesRegex(MidnightSunException, "The sun"):
            self.sun.get_sunset_time(d)


class TestSouthPoleNoSun(unittest.TestCase):
    """Mirror of TestNoSun for the southern polar location, to guard the exception
    branches against a hemisphere-specific regression."""

    def setUp(self):
        self.sun = Sun(_SOUTH_POLE_LAT, _SOUTH_POLE_LON)

    def test_get_sunset_time_polar_night(self):
        # Winter in the southern hemisphere: sun never rises above the horizon
        d = datetime(2024, 6, 21)
        with self.assertRaisesRegex(PolarNightException, "The sun"):
            self.sun.get_sunset_time(d)

    def test_get_sunrise_time_midnight_sun(self):
        # Summer in the southern hemisphere: sun never sets
        d = datetime(2024, 12, 21)
        with self.assertRaisesRegex(MidnightSunException, "The sun"):
            self.sun.get_sunrise_time(d)


class TestEquatorSun(unittest.TestCase):
    """Near the equator sunrise/sunset should stay close to 6 AM/6 PM local time
    with little seasonal variation."""

    def setUp(self):
        self.sun = Sun(_QUITO_LAT, _QUITO_LON)

    def test_get_sunrise_time(self):
        expected_sunrise = datetime(2024, 3, 20, 11, 18, 0, tzinfo=timezone.utc)
        utc_sunrise = self.sun.get_sunrise_time(datetime(2024, 3, 20))
        self.assertEqual(utc_sunrise, expected_sunrise)

    def test_get_sunset_time(self):
        expected_sunset = datetime(2024, 3, 20, 23, 24, 0, tzinfo=timezone.utc)
        utc_sunset = self.sun.get_sunset_time(datetime(2024, 3, 20))
        self.assertEqual(utc_sunset, expected_sunset)


class TestUtcDayOffset(unittest.TestCase):
    """CLAUDE.md calls out utc_day_offset as a past source of bugs: a western
    longitude's sunset can land on the following UTC calendar date, and an eastern
    longitude's sunrise can land on the previous one. Pin that invariant explicitly."""

    def test_west_sunset_rolls_to_next_utc_day(self):
        sun = Sun(_SF_LAT, _SF_LON)
        requested = datetime(2024, 3, 11)
        utc_sunset = sun.get_sunset_time(requested)
        self.assertEqual(utc_sunset.date(), requested.date() + timedelta(days=1))

    def test_east_sunrise_rolls_to_previous_utc_day(self):
        sun = Sun(_TOKYO_LAT, _TOKYO_LON)
        requested = datetime(2024, 3, 11)
        utc_sunrise = sun.get_sunrise_time(requested)
        self.assertEqual(utc_sunrise.date(), requested.date() - timedelta(days=1))


class TestCustomZenith(unittest.TestCase):
    """get_sun_timedelta accepts a custom zenith (e.g. for civil twilight); a wider
    zenith angle should produce an earlier rise / later set than the default 90.8."""

    def setUp(self):
        self.sun = Sun(_SF_LAT, _SF_LON)

    def test_civil_twilight_precedes_standard_sunrise(self):
        at_date = datetime(2024, 3, 11)
        standard_rise = self.sun.get_sun_timedelta(at_date, timezone.utc, is_rise_time=True)
        civil_twilight_rise = self.sun.get_sun_timedelta(at_date, timezone.utc, is_rise_time=True, zenith=96)
        self.assertLess(civil_twilight_rise, standard_rise)


class TestNoneTimezone(unittest.TestCase):
    """time_zone=None falls back to the machine's local timezone (see CLAUDE.md)."""

    def test_get_sunrise_time_matches_explicit_local_offset(self):
        sun = Sun(_SF_LAT, _SF_LON)
        at_date = datetime(2024, 3, 11)
        utc_sunrise = sun.get_sunrise_time(at_date, time_zone=timezone.utc)
        local_offset = datetime.now().astimezone().utcoffset()
        expected_naive_local = (utc_sunrise + local_offset).replace(tzinfo=None)

        result = sun.get_sunrise_time(at_date, time_zone=None)

        self.assertIsNone(result.tzinfo)
        self.assertEqual(result, expected_naive_local)


class TestDeprecatedWrappers(unittest.TestCase):
    """get_local_sunrise_time/get_local_sunset_time are deprecated but must keep
    warning and delegating to the non-deprecated methods with identical results."""

    def setUp(self):
        self.sun = Sun(_SF_LAT, _SF_LON)

    def test_get_local_sunrise_time_warns_and_matches(self):
        at_date = datetime(2024, 3, 11)
        with self.assertWarns(DeprecationWarning):
            deprecated_result = self.sun.get_local_sunrise_time(at_date, ZoneInfo("America/Los_Angeles"))
        direct_result = self.sun.get_sunrise_time(at_date, ZoneInfo("America/Los_Angeles"))
        self.assertEqual(deprecated_result, direct_result)

    def test_get_local_sunset_time_warns_and_matches(self):
        at_date = datetime(2024, 3, 11)
        with self.assertWarns(DeprecationWarning):
            deprecated_result = self.sun.get_local_sunset_time(at_date, ZoneInfo("America/Los_Angeles"))
        direct_result = self.sun.get_sunset_time(at_date, ZoneInfo("America/Los_Angeles"))
        self.assertEqual(deprecated_result, direct_result)


class TestSunConstructor(unittest.TestCase):
    def test_stores_lat_lon_and_computes_lngHour(self):
        sun = Sun(_SF_LAT, _SF_LON)
        self.assertEqual(sun._lat, _SF_LAT)
        self.assertEqual(sun._lon, _SF_LON)
        self.assertAlmostEqual(sun.lngHour, _SF_LON / 15)

    def test_computes_lngHour_for_eastern_longitude(self):
        sun = Sun(_TOKYO_LAT, _TOKYO_LON)
        self.assertAlmostEqual(sun.lngHour, _TOKYO_LON / 15)


if __name__ == "__main__":
    unittest.main()
