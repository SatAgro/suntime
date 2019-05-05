#!/usr/bin/env python

from setuptools import setup


setup(name='suntime',
      version='1.2.3',
      description='Simple sunset and sunrise time calculation python library',
      author='Krzysztof Stopa',
      url='https://github.com/SatAgro/suntime',
      copyright='Copyright 2019 SatAgro',
      license='LGPLv3',
      packages=['suntime'],
      install_requires=['python-dateutil']
)
