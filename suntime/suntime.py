import calendar
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
        Calculate the sunrise time for given date.
        :param lat: Latitude
        :param lon: Longitude
        :param date: Reference date. Today if not provided.
        :return: UTC sunrise datetime
        :raises: SunTimeException when there is no sunrise and sunset on given location and date
        """
        date = datetime.datetime.now() if date is None else date
        sr = self._calc_sun_time(date, tz=tz, f1=_f1_sunrise, f2=_f2_sunrise)
        if sr is None:
            raise SunTimeException('The sun never rises on this location (on the specified date)')
        else:
            return sr

    def get_sunset_time(self, date=None, tz=None):
        """
        Calculate the sunset time for given date.
        :param lat: Latitude
        :param lon: Longitude
        :param date: Reference date. Today if not provided.
        :return: UTC sunset datetime
        :raises: SunTimeException when there is no sunrise and sunset on given location and date.
        """
        date = datetime.datetime.now() if date is None else date
        ss = self._calc_sun_time(date, tz=tz, f1=_f1_sunset, f2=_f2_sunset)
        if ss is None:
            raise SunTimeException('The sun never sets on this location (on the specified date)')
        else:
            return ss

    def _calc_sun_time(self, date, tz, f1, f2, zenith=90.8):
        """
        Calculate sunrise or sunset date.
        :param date: Reference date
        :param isRiseTime: True if you want to calculate sunrise time.
        :param zenith: Sun reference zenith
        :return: UTC sunset or sunrise datetime
        :raises: SunTimeException when there is no sunrise and sunset on given location and date
        """

        # 1. first get the day of the year
        N = date.timetuple().tm_yday

        # 2. convert the longitude to hour value and calculate an approximate time
        t = f1(N, self.lngHour)

        # 3. get sun true longitude 
        L = self._get_true_longitude(t)

        # 4. get cosH
        cosH = self._get_cosH(L, zenith=zenith)

        if cosH > 1:
            return None     # The sun never rises on this location (on the specified date)
        if cosH < -1:
            return None     # The sun never sets on this location (on the specified date)

        # 4c. finish calculating H and convert into hours
        H = f2(cosH)
        H = H / 15

        # 5. get local mean time
        T = self._get_local_mean_time(t, L, H)
        
        # 7a. adjust back to UTC
        UT = T - self.lngHour
        
        if tz:
            # 7b. adjust back to local time
            UT += tz.utcoffset(day).total_seconds()/3600

            # 7c. rounding and impose range bounds
            UT = _force_range(round(UT, 1), 24)
            time_delta = datetime.timedelta(hours=round(UT, 1))
            
            return datetime.datetime.combine(date, datetime.time(0, 0, tzinfo=tz)) + time_delta
        else:
            # 7c. rounding and impose range bounds
            UT = _force_range(round(UT, 1), 24)
            time_delta = datetime.timedelta(hours=round(UT, 1))

            return datetime.datetime.combine(date, datetime.time(0, 0, tzinfo=UTC)) + time_delta

    @staticmethod
    def _get_true_longitude(t):
        # 3a. calculate the Sun's mean anomaly
        M = (0.9856 * t) - 3.289

        # 3b. calculate the Sun's true longitude
        L = M + (1.916 * math.sin(TO_RAD*M)) + (0.020 * math.sin(TO_RAD * 2 * M)) + 282.634
        return _force_range(L, 360) #NOTE: L adjusted into the range [0,360)
        
    def _get_cosH(self, L, zenith=90.8):
        # 4a. calculate the Sun's declination
        sinDec = 0.39782 * math.sin(TO_RAD*L)
        cosDec = math.cos(math.asin(sinDec))

        # 4b. calculate the Sun's local hour angle
        return (math.cos(TO_RAD*zenith) - (sinDec * math.sin(TO_RAD*self._lat))) / (cosDec * math.cos(TO_RAD*self._lat))

    def _get_local_mean_time(self, t, L, H):
        # 5a. calculate the Sun's right ascension
        RA = (1/TO_RAD) * math.atan(0.91764 * math.tan(TO_RAD*L))
        RA = _force_range(RA, 360) #NOTE: RA adjusted into the range [0,360)

        # 5b. right ascension value needs to be in the same quadrant as L
        Lquadrant  = (math.floor(L/90)) * 90
        RAquadrant = (math.floor(RA/90)) * 90
        RA = RA + (Lquadrant - RAquadrant)

        # 5c. right ascension value needs to be converted into hours
        RA = RA / 15

        # 6. calculate local mean time of rising/setting
        T = H + RA - (0.06571 * t) - 6.622

        return T
        # return datetime.timedelta(hours=round(UT, 1))

def _f1_sunrise(N, lngHour):
    return N + ((6 - lngHour) / 24)

def _f1_sunset(N, lngHour):
    return N + ((18 - lngHour) / 24)

def _f2_sunrise(cosH):
    return 360 - (1/TO_RAD) * math.acos(cosH)

def _f2_sunset(cosH):
    return (1/TO_RAD) * math.acos(cosH)

def _force_range(v, max):
    # force v to be >= 0 and < max
    if v < 0:
        return v + max
    elif v >= max:
        return v - max

    return v

# if __name__ == '__main__':
    import datetime
    import pytz
    from suntime import Sun, SunTimeException
    
    latitude = 7.7956
    longitude = 110.3695
    tz = pytz.timezone("Asia/Jakarta")

    day = datetime.datetime(2022, 4, 24)
    print(day)
    print(tz.utcoffset(day))

    sun = Sun(latitude, longitude)
    try:
        print("")

        # print(sun.get_sunrise_sunset_time())
        print(sun.get_sunrise_time())
        print(sun.get_sunset_time())
        print("")
        print(sun.get_sunrise_time(tz=tz))
        print(sun.get_sunset_time(tz=tz))

        # On a special date in UTC
        print(sun.get_sunrise_time(day))
        print(sun.get_sunset_time(day))
        print("")
        print(sun.get_sunrise_time(tz=tz))
        print(sun.get_sunset_time(tz=tz))
    except SunTimeException as e:
        print("Error: {0}".format(e))
