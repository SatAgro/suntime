#!/usr/bin/env python

from setuptools import setup
import suntime

setup(name='suntime',
      version=suntime.__version__,
      description='Simple sunset and sunrise time calculation python library',
      author=suntime.__author__,
      author_email=suntime.__email__,
      url='https://github.com/SatAgro/suntime',
      copyright='Copyright 2019 SatAgro',
      license='LGPLv3',
      packages=['suntime'],
      install_requires=['python-dateutil']
)
