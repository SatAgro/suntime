# SunTime
Simple sunset and sunrise time calculation python library.

## Installation

Download and type:

    python setup.py install


## Usage

You can use the library to get UTC and local time sunrise and sunset times typing:

    import datetime
    import suntime

    latitude = 51.21
    longitude = 21.01

    sun = Sun(latitude, longitude)

    # Get today's sunrise and sunset in UTC
    today_sr = sun.get_sunrise_time()
    today_ss = sun.get_sunset_time()

    # On a special date in your machine's local time zone
    abd = datetime.date(2014,10,3)
    abd_sr = sun.get_local_sunrise_time(abd)
    abd_ss = sun.get_local_sunset_time(abd)

    # Error handling (no sunset or sunrise on given location)
    latitude = 87.87
    longitude = 0.1

    try:
        abd_sr = sun.get_local_sunrise_time(abd)
        abd_ss = sun.get_local_sunset_time(abd)
    except SunTimeException as e:
        print("Error: {0}".format(e))


## License

Copyright © 2017 SatAgro Sp. z o.o.

This file is part of SunTime library for python (SunTime).

SunTime is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.

SunTime is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with CAMS tools. If not, see http://www.gnu.org/licenses/.