import math
import datetime
from dateutil.tz import UTC

# CONSTANT
TO_RAD = math.pi/180.0

class SunTimeException(Exception):

    def __init__(self, message):
        super(SunTimeException, self).__init__(message)

class Sun:
    """
    Approximated calculation of sunrise and sunset datetimes. Adapted from:
    https://stackoverflow.com/questions/19615350/calculate-sunrise-and-sunset-times-for-a-given-gps-coordinate-within-postgresql
    """
    def __init__(self, lat, lon):
        self._lat = lat
        self._lon = lon

        self.lngHour = self._lon / 15

    def get_sunrise_time(self, date=None, tz=None):
        """
        :param date: Reference date. datetime.now() if not provided.
        :param tz: pytz object with .tzinfo() or None
        :return: sunrise datetime.
        :raises: SunTimeException when there is no sunrise and sunset on given location and date.
        """
        date = datetime.datetime.now() if date is None else date
        time_delta = self.get_sun_timedelta(date, tz=tz, isRiseTime=True)
        if time_delta is None:
            raise SunTimeException('The sun never rises on this location (on the specified date)')
        else:
            if tz:
                return datetime.datetime.combine(date, datetime.time(0, 0, tzinfo=tz)) + time_delta
            else:
                return datetime.datetime.combine(date, datetime.time(0, 0, tzinfo=UTC)) + time_delta

    def get_sunset_time(self, date=None, tz=None):
        """
        Calculate the sunset time for given date.
        :param date: Reference date. datetime.now() if not provided.
        :param tz: pytz object with .tzinfo() or None
        :return: sunset datetime.
        :raises: SunTimeException when there is no sunrise and sunset on given location and date.
        """
        date = datetime.datetime.now() if date is None else date
        time_delta = self.get_sun_timedelta(date, tz=tz, isRiseTime=False)
        if time_delta is None:
            raise SunTimeException('The sun never rises on this location (on the specified date)')
        else:
            if tz:
                return datetime.datetime.combine(date, datetime.time(0, 0, tzinfo=tz)) + time_delta
            else:
                return datetime.datetime.combine(date, datetime.time(0, 0, tzinfo=UTC)) + time_delta

    def get_sun_timedelta(self, date, tz, isRiseTime=True, zenith=90.8):
        """
        Calculate sunrise or sunset date.
        :param date: Reference date
        :param tz: pytz object with .tzinfo() or None
        :param isRiseTime: True if you want to calculate sunrise time.
        :param zenith: Sun reference zenith
        :return: timedelta showing hour, minute, and second of sunrise or sunset
        """

        # 1. first get the day of the year
        N = date.timetuple().tm_yday

        # 2. convert the longitude to hour value and calculate an approximate time
        if isRiseTime:
            t = N + ((6 - self.lngHour) / 24)
        else: #sunset
            t = N + ((18 - self.lngHour) / 24)

        # 3a. calculate the Sun's mean anomaly
        M = (0.9856 * t) - 3.289

        # 3b. calculate the Sun's true longitude
        L = M + (1.916 * math.sin(TO_RAD*M)) + (0.020 * math.sin(TO_RAD * 2 * M)) + 282.634
        L = self._force_range(L, 360) #NOTE: L adjusted into the range [0,360)

        # 4a. calculate the Sun's declination
        sinDec = 0.39782 * math.sin(TO_RAD*L)
        cosDec = math.cos(math.asin(sinDec))

        # 4b. calculate the Sun's local hour angle
        cosH =  (math.cos(TO_RAD*zenith) - (sinDec * math.sin(TO_RAD*self._lat))) / (cosDec * math.cos(TO_RAD*self._lat))

        if cosH > 1:
            return None     # The sun never rises on this location (on the specified date)
        if cosH < -1:
            return None     # The sun never sets on this location (on the specified date)

        # 4c. finish calculating H and convert into hours
        if isRiseTime:
            H = 360 - (1/TO_RAD) * math.acos(cosH)
        else: #setting
            H = (1/TO_RAD) * math.acos(cosH)
        H = H / 15

        # 5a. calculate the Sun's right ascension
        RA = (1/TO_RAD) * math.atan(0.91764 * math.tan(TO_RAD*L))
        RA = self._force_range(RA, 360) #NOTE: RA adjusted into the range [0,360)

        # 5b. right ascension value needs to be in the same quadrant as L
        Lquadrant  = (math.floor(L/90)) * 90
        RAquadrant = (math.floor(RA/90)) * 90
        RA = RA + (Lquadrant - RAquadrant)

        # 5c. right ascension value needs to be converted into hours
        RA = RA / 15

        # 6. calculate local mean time of rising/setting
        T = H + RA - (0.06571 * t) - 6.622
        
        # 7a. adjust back to UTC
        UT = T - self.lngHour
        
        if tz:
            # 7b. adjust back to local time
            UT += tz.utcoffset(date).total_seconds()/3600

        # 7c. rounding and impose range bounds
        UT = self._force_range(round(UT, 2), 24)
        
        # 8. return timedelta
        return datetime.timedelta(hours=UT)

    @staticmethod
    def _force_range(v, max):
        # force v to be >= 0 and < max
        if v < 0:
            return v + max
        elif v >= max:
            return v - max
        return v

if __name__ == '__main__':
    import datetime
    import pytz
    from suntime import Sun, SunTimeException
    
    latitude = 7.7956
    longitude = 110.3695
    tz = pytz.timezone("Asia/Jakarta")

    day = datetime.datetime(2022, 4, 24)
    print(tz.utcoffset(day))

    sun = Sun(latitude, longitude)
    try:
        print("")
        print(datetime.datetime.now())
        print()
        print(sun.get_sunrise_time())
        print(sun.get_sunset_time())
        print("")
        print(sun.get_sunrise_time(tz=tz))
        print(sun.get_sunset_time(tz=tz))
        print("")
        print(day)
        print("")
        print(sun.get_sunrise_time(day))
        print(sun.get_sunset_time(day))
        print("")
        print(sun.get_sunrise_time(day, tz=tz))
        print(sun.get_sunset_time(day, tz=tz))
    except SunTimeException as e:
        print("Error: {0}".format(e))
