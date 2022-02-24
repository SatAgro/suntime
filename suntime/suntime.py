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

    def get_sunrise_sunset_time(self, date=None):
        """
        Calculate the sunrise time for given date.
        :param lat: Latitude
        :param lon: Longitude
        :param date: Reference date. Today if not provided.
        :return: UTC sunrise datetime
        :raises: SunTimeException when there is no sunrise and sunset on given location and date
        """
        date = datetime.date.today() if date is None else date
        sr, ss = self._calc_suns_time(date)
        return sr, ss

    def get_sunrise_time(self, date=None):
        """
        Calculate the sunrise time for given date.
        :param lat: Latitude
        :param lon: Longitude
        :param date: Reference date. Today if not provided.
        :return: UTC sunrise datetime
        :raises: SunTimeException when there is no sunrise and sunset on given location and date
        """
        date = datetime.date.today() if date is None else date
        sr = self._calc_sun_time(date, f1=_f1_sunrise, f2=_f2_sunrise)
        if sr is None:
            raise SunTimeException('The sun never rises on this location (on the specified date)')
        else:
            return sr

    def get_sunset_time(self, date=None):
        """
        Calculate the sunset time for given date.
        :param lat: Latitude
        :param lon: Longitude
        :param date: Reference date. Today if not provided.
        :return: UTC sunset datetime
        :raises: SunTimeException when there is no sunrise and sunset on given location and date.
        """
        date = datetime.date.today() if date is None else date
        ss = self._calc_sun_time(date, f1=_f1_sunset, f2=_f2_sunset)
        if ss is None:
            raise SunTimeException('The sun never sets on this location (on the specified date)')
        else:
            return ss

    # TODO: local is buggy (sunset before sunrise) 
    # def get_local_sunrise_time(self, date=None, local_time_zone=tz.tzlocal()):
    #     """
    #     Get sunrise time for local or custom time zone.
    #     :param date: Reference date. Today if not provided.
    #     :param local_time_zone: Local or custom time zone.
    #     :return: Local time zone sunrise datetime
    #     """
    #     date = datetime.date.today() if date is None else date
    #     sr = self._calc_sun_time(date, True)
    #     if sr is None:
    #         raise SunTimeException('The sun never rises on this location (on the specified date)')
    #     else:
    #         return sr.astimezone(local_time_zone)

    # def get_local_sunset_time(self, date=None, local_time_zone=tz.tzlocal()):
    #     """
    #     Get sunset time for local or custom time zone.
    #     :param date: Reference date
    #     :param local_time_zone: Local or custom time zone.
    #     :return: Local time zone sunset datetime
    #     """
    #     date = datetime.date.today() if date is None else date
    #     ss = self._calc_sun_time(date, False)
    #     if ss is None:
    #         raise SunTimeException('The sun never sets on this location (on the specified date)')
    #     else:
    #         return ss.astimezone(local_time_zone)

    def _calc_suns_time(self, date, zenith=90.8):
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
        t_sr, t_ss = _f1_sunrise(N, self.lngHour), _f1_sunset(N, self.lngHour)

        # 3. get sun true longitude 
        L_sr, L_ss = self._get_true_longitude(t_sr), self._get_true_longitude(t_ss)

        # 4. get cosH
        cosH_sr, cosH_ss = self._get_cosH(L_sr, zenith=zenith), self._get_cosH(L_ss, zenith=zenith)

        # 5. finish calculating H and convert into hours, get hour and minute
        if -1 < cosH_sr < 1:
            H_sr = _f2_sunrise(cosH_sr) / 15
            time_delta_sr = self._get_time_delta(t_sr, L_sr, H_sr)
            date_sr = datetime.datetime.combine(date, datetime.time(0, 0, tzinfo=UTC)) + time_delta_sr
        else:
            date_sr = None

        if -1 < cosH_ss < 1:
            H_ss = _f2_sunset(cosH_ss) / 15
            time_delta_ss = self._get_time_delta(t_ss, L_ss, H_ss)
            date_ss = datetime.datetime.combine(date, datetime.time(0, 0, tzinfo=UTC)) + time_delta_ss
        else:
            date_ss = None

        return date_sr, date_ss

    def _calc_sun_time(self, date, f1, f2, zenith=90.8):
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

        # 5. finish calculating H and convert into hours
        H = f2(cosH)
        H = H / 15

        # 6. get hour and minute
        time_delta = self._get_time_delta(t, L, H)

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

    def _get_time_delta(self, t, L, H):
        # 5a. calculate the Sun's right ascension
        RA = (1/TO_RAD) * math.atan(0.91764 * math.tan(TO_RAD*L))
        RA = _force_range(RA, 360) #NOTE: RA adjusted into the range [0,360)

        # 5b. right ascension value needs to be in the same quadrant as L
        Lquadrant  = (math.floor(L/90)) * 90
        RAquadrant = (math.floor(RA/90)) * 90
        RA = RA + (Lquadrant - RAquadrant)

        # 5c. right ascension value needs to be converted into hours
        RA = RA / 15

        # 7. calculate local mean time of rising/setting
        T = H + RA - (0.06571 * t) - 6.622

        # 8. adjust back to UTC
        UT = T - self.lngHour
        print(round(UT, 1))
        return datetime.timedelta(hours=round(UT, 1))

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
    # from suntime import Sun
    # from datetime import datetime
    # from suntime import Sun, SunTimeException
    # latitude = 56.49771
    # longitude = 82.0475315

    # sun = Sun(latitude, longitude)
    # print(sun.get_sunrise_sunset_time())
    # print(sun.get_sunrise_time())
    # print(sun.get_sunset_time())

    # day = datetime(2021, 4, 24)
    # print(sun.get_sunrise_sunset_time(day))
    # print(sun.get_sunrise_time(day))
    # print(sun.get_sunset_time(day))

    # day = datetime(2021, 4, 25)
    # print(sun.get_sunrise_sunset_time(day))
    # print(sun.get_sunrise_time(day))
    # print(sun.get_sunset_time(day))

    # sun = Sun(85.0, 21.00)
    # try:
    #     print(sun.get_sunrise_time())
    #     print(sun.get_sunset_time())
    #     # print(sun.get_local_sunrise_time())
    #     # print(sun.get_local_sunset_time())

    # # On a special date in UTC

    #     abd = datetime.date(2014, 1, 3)
    #     print(sun.get_sunrise_time(abd))
    #     print(sun.get_sunset_time(abd))
    #     # print(sun.get_local_sunrise_time(abd))
    #     # print(sun.get_local_sunset_time(abd))
    # except SunTimeException as e:
    #     print("Error: {0}".format(e))
