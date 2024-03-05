# SunTime
Simple sunset and sunrise time calculation python library.

## Installation

Using pip:

    pip3 install suntime
    
Or download and type:

    python3 setup.py install

## Usage

You can use the library to get UTC and local time sunrise and sunset times typing:

```python3
import datetime
from dateutil import tz
from suntime import Sun, SunTimeException

warsaw_lat = 51.21
warsaw_lon = 21.01

sun = Sun(warsaw_lat, warsaw_lon)

# Get today's sunrise and sunset in UTC
today_sr = sun.get_sunrise_time()
today_ss = sun.get_sunset_time()
print('Today at Warsaw the sun raised at {} and get down at {} UTC'.
      format(today_sr.strftime('%H:%M'), today_ss.strftime('%H:%M')))

# On a special date in your machine's local time zone
abd = datetime.date(2014, 10, 3)
abd_sr = sun.get_sunrise_time(abd, tz.gettz('Europe/Warsaw'))
abd_ss = sun.get_sunset_time(abd, tz.gettz('Europe/Warsaw'))
print('On {} the sun at Warsaw raised at {} and get down at {}.'.
      format(abd, abd_sr.strftime('%H:%M'), abd_ss.strftime('%H:%M')))

# Error handling (no sunset or sunrise on given location)
latitude = 87.55
longitude = 0.1
sun = Sun(latitude, longitude)
try:
    abd_sr = sun.get_sunrise_time(abd)
    abd_ss = sun.get_sunset_time(abd)
    print('On {} at somewhere in the north the sun raised at {} and get down at {}.'.
          format(abd, abd_sr.strftime('%H:%M'), abd_ss.strftime('%H:%M')))
except SunTimeException as e:
    print("Error: {0}.".format(e))
```

## License

Copyright © 2024 [SatAgro Sp. z o.o.](https://satagro.pl) and our awesome contributors:

* Andrey Kobyshev ([yokotoka](https://github.com/yokotoka))
* Hadrien Bertrand ([hbertrand](https://github.com/hbertrand))
* Ingo Randolf ([i-n-g-o](https://github.com/i-n-g-o))
* John Vandenberg ([jayvdb](https://github.com/jayvdb))
* Krzysztof Stopa ([kstopa](https://github.com/kstopa))
* Matthias ([palto42](https://github.com/plato42))
* Muhammad Yasirroni ([yasirroni](https://github.com/yasirroni))

This file is part of SunTime library for python (SunTime).

SunTime is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.

SunTime is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with CAMS tools. If not, see http://www.gnu.org/licenses/.
