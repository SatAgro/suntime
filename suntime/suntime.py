import math
import warnings
from datetime import datetime, timedelta, time, timezone


# CONSTANT
TO_RAD = math.pi/180.0


class SunTimeException(Exception):
    pass


class MidnightSunException(SunTimeException):
    """
    Sun is always up (24h of daylight)
    """
    pass


class PolarNightException(SunTimeException):
    """
    Sun is always down (0h of daylight)
    """
    pass


class Sun:
    """
    Approximated calculation of sunrise and sunset datetimes. Adapted from:
    https://stackoverflow.com/questions/19615350/calculate-sunrise-and-sunset-times-for-a-given-gps-coordinate-within-postgresql
    """
    def __init__(self, lat, lon):
        self._lat = lat
        self._lon = lon

        self.lngHour = self._lon / 15

    def get_sunrise_time(self, at_date=datetime.now(), time_zone=timezone.utc):
        """
        :param at_date: Reference date. datetime.now() if not provided.
        :param time_zone: pytz object with .tzinfo() or None
        :return: sunrise datetime.
        :raises: SunTimeException when there is no sunrise and sunset on given location and date.
        """
        time_delta = self.get_sun_timedelta(at_date, time_zone=time_zone, is_rise_time=True)
        return datetime.combine(at_date, time(tzinfo=time_zone)) + time_delta

    def get_sunset_time(self, at_date=datetime.now(), time_zone=timezone.utc):
        """
        Calculate the sunset time for given date.
        :param at_date: Reference date. datetime.now() if not provided.
        :param time_zone: pytz object with .tzinfo() or None
        :return: sunset datetime.
        :raises: SunTimeException when there is no sunrise and sunset on given location and date.
        """
        time_delta = self.get_sun_timedelta(at_date, time_zone=time_zone, is_rise_time=False)
        return datetime.combine(at_date, time(tzinfo=time_zone)) + time_delta

    def get_local_sunrise_time(self, at_date=datetime.now(), time_zone=None):
        """ DEPRECATED: Use get_sunrise_time() instead. """
        warnings.warn("get_local_sunrise_time is deprecated and will be removed in future versions."
                      "Use get_sunrise_time with proper time zone", DeprecationWarning)

        return self.get_sunrise_time(at_date, time_zone)

    def get_local_sunset_time(self, at_date=datetime.now(), time_zone=None):
        """ DEPRECATED: Use get_sunset_time() instead. """
        warnings.warn("get_local_sunset_time is deprecated and will be removed in future versions."
                      "Use get_sunset_time with proper time zone.", DeprecationWarning)
        return self.get_sunset_time(at_date, time_zone)

    def get_sun_timedelta(self, at_date, time_zone, is_rise_time=True, zenith=90.8):
        """
        Calculate sunrise or sunset date.
        :param at_date: Reference date
        :param time_zone: pytz object with .tzinfo() or None
        :param is_rise_time: True if you want to calculate sunrise time.
        :param zenith: Sun reference zenith
        :return: timedelta showing hour, minute, and second of sunrise or sunset
        """

        # If not set get local timezone from datetime
        if time_zone is None:
            time_zone = datetime.now().tzinfo

        # 1. first get the day of the year
        N = at_date.timetuple().tm_yday

        # 2. convert the longitude to hour value and calculate an approximate time
        if is_rise_time:
            t = N + ((6 - self.lngHour) / 24)
        else:   # sunset
            t = N + ((18 - self.lngHour) / 24)

        # 3a. calculate the Sun's mean anomaly
        M = (0.9856 * t) - 3.289

        # 3b. calculate the Sun's true longitude
        L = M + (1.916 * math.sin(TO_RAD*M)) + (0.020 * math.sin(TO_RAD * 2 * M)) + 282.634
        L = self._force_range(L, 360)   # NOTE: L adjusted into the range [0,360)

        # 4a. calculate the Sun's declination
        sinDec = 0.39782 * math.sin(TO_RAD*L)
        cosDec = math.cos(math.asin(sinDec))

        # 4b. calculate the Sun's local hour angle
        cosH = (math.cos(TO_RAD*zenith) - (sinDec * math.sin(TO_RAD*self._lat))) / (cosDec * math.cos(TO_RAD*self._lat))

        if cosH > 1:
            raise PolarNightException("The sun is always down on this location on the specified date")
        if cosH < -1:
            raise MidnightSunException("The sun is always up on this location on the specified date")

        # 4c. finish calculating H and convert into hours
        if is_rise_time:
            H = 360 - (1/TO_RAD) * math.acos(cosH)
        else:   # setting
            H = (1/TO_RAD) * math.acos(cosH)
        H = H / 15

        # 5a. calculate the Sun's right ascension
        RA = (1/TO_RAD) * math.atan(0.91764 * math.tan(TO_RAD*L))
        RA = self._force_range(RA, 360)     # NOTE: RA adjusted into the range [0,360)

        # 5b. right ascension value needs to be in the same quadrant as L
        Lquadrant = (math.floor(L/90)) * 90
        RAquadrant = (math.floor(RA/90)) * 90
        RA = RA + (Lquadrant - RAquadrant)

        # 5c. right ascension value needs to be converted into hours
        RA = RA / 15

        # 6. calculate local mean time of rising/setting
        T = H + RA - (0.06571 * t) - 6.622

        # 7a. adjust back to UTC
        UT = T - self.lngHour

        if time_zone:
            # 7b. adjust back to local time
            UT += time_zone.utcoffset(at_date).total_seconds() / 3600

        # 7c. rounding and impose range bounds
        UT = round(UT, 2)
        if is_rise_time:
            UT = self._force_range(UT, 24)

        # 8. return timedelta
        return timedelta(hours=UT)

    @staticmethod
    def _force_range(v, max):
        # force v to be >= 0 and < max
        if v < 0:
            return v + max
        elif v >= max:
            return v - max
        return v
