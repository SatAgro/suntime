#!/usr/bin/env python

from distutils.core import setup
import suntime

setup(name='suntime',
      version=suntime.__version__,
      description='Simple sunset and sunrise time calculation python library',
      author=suntime.__author__,
      author_email=suntime.__email__,
      url='https://github.com/SatAgro/suntime',
      copyright='Copyright 2017 SatAgro',
      packages=['suntime'], requires=['dateutil']
      )
