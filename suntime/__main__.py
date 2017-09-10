
import math
import datetime
from dateutil import tz


class Sun:
    """
    Approximated calculation of sunrise and sunset datetimes. Adapted from:
    https://stackoverflow.com/questions/19615350/calculate-sunrise-and-sunset-times-for-a-given-gps-coordinate-within-postgresql
    """
    def __init__(self, lat, lon):
        self._lat = lat
        self._lon = lon

    def get_sunrise_time(self, date=datetime.date.today()):
        """
        Calculate the sunrise time for given date.
        :param lat: Latitude
        :param lon: Longitude
        :param date: Reference date
        :return: UTC sunrise datetime
        """
        return self._calc_sun_time(date, True)


    def get_local_sunrise_time(self, date=datetime.date.today(), local_time_zone=tz.tzlocal()):
        return self.get_sunrise_time(date).astimezone(local_time_zone)

    def get_sunset_time(self, date=datetime.date.today()):
        """
        Calculate the sunset time for given date.
        :param lat: Latitude
        :param lon: Longitude
        :param date: Reference date
        :return: UTC sunset datetime
        """
        return self._calc_sun_time(date, False)

    def get_local_sunset_time(self, date=datetime.date.today(), local_time_zone=tz.tzlocal()):
        return self.get_sunset_time(date).astimezone(local_time_zone)

    def _calc_sun_time(self, date=datetime.date.today(), isRiseTime=True, zenith=90.8):
        # isRiseTime == False, returns sunsetTime
        day = date.day
        month = date.month
        year = date.year

        TO_RAD = math.pi/180.0

        # 1. first calculate the day of the year
        N1 = math.floor(275 * month / 9)
        N2 = math.floor((month + 9) / 12)
        N3 = (1 + math.floor((year - 4 * math.floor(year / 4) + 2) / 3))
        N = N1 - (N2 * N3) + day - 30

        # 2. convert the longitude to hour value and calculate an approximate time
        lngHour = self._lon / 15

        if isRiseTime:
            t = N + ((6 - lngHour) / 24)
        else: #sunset
            t = N + ((18 - lngHour) / 24)

        # 3. calculate the Sun's mean anomaly
        M = (0.9856 * t) - 3.289

        # 4. calculate the Sun's true longitude
        L = M + (1.916 * math.sin(TO_RAD*M)) + (0.020 * math.sin(TO_RAD * 2 * M)) + 282.634
        L = self._force_range(L, 360 ) #NOTE: L adjusted into the range [0,360)

        # 5a. calculate the Sun's right ascension

        RA = (1/TO_RAD) * math.atan(0.91764 * math.tan(TO_RAD*L))
        RA = self._force_range(RA, 360 ) #NOTE: RA adjusted into the range [0,360)

        # 5b. right ascension value needs to be in the same quadrant as L
        Lquadrant  = (math.floor( L/90)) * 90
        RAquadrant = (math.floor(RA/90)) * 90
        RA = RA + (Lquadrant - RAquadrant)

        # 5c. right ascension value needs to be converted into hours
        RA = RA / 15

        # 6. calculate the Sun's declination
        sinDec = 0.39782 * math.sin(TO_RAD*L)
        cosDec = math.cos(math.asin(sinDec))

        # 7a. calculate the Sun's local hour angle
        cosH = (math.cos(TO_RAD*zenith) - (sinDec * math.sin(TO_RAD*self._lat))) / (cosDec * math.cos(TO_RAD*self._lat))

        # TODO Raise exceptions
        if cosH > 1:
            return {'status': False, 'msg': 'the sun never rises on this location (on the specified date)'}

        if cosH < -1:
            return {'status': False, 'msg': 'the sun never sets on this location (on the specified date)'}

        # 7b. finish calculating H and convert into hours

        if isRiseTime:
            H = 360 - (1/TO_RAD) * math.acos(cosH)
        else: #setting
            H = (1/TO_RAD) * math.acos(cosH)

        H = H / 15

        #8. calculate local mean time of rising/setting
        T = H + RA - (0.06571 * t) - 6.622

        #9. adjust back to UTC
        UT = T - lngHour
        UT = self._force_range(UT, 24)   # UTC time in decimal format (e.g. 23.23)

        #10. Return
        hr = self._force_range(int(UT), 24)
        min = round((UT - int(UT))*60, 0)
        if min == 60:
            hr += 1
            min = 0

        return datetime.datetime(year, month, day, hr, int(min), tzinfo=tz.tzutc())

    @staticmethod
    def _force_range(v, max):
        # force v to be >= 0 and < max
        if v < 0:
            return v + max
        elif v >= max:
            return v - max

        return v


if __name__ == '__main__':
    sun = Sun(52.234, 21.00)
    print(sun.get_local_sunrise_time())
    print(sun.get_local_sunset_time())

    # On a special date in UTC
    abd = datetime.date(2014, 10, 3)
    print("Ada")
    abd_sr = sun.get_local_sunrise_time(abd)
    abd_ss = sun.get_local_sunset_time(abd)
    print(abd_sr)
    print(abd_ss)
