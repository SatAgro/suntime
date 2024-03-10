#!/usr/bin/env python

from setuptools import setup
from suntime import __version__, __author__, __license__

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

setup(name='suntime',
      version=__version__,
      description='Simple sunset and sunrise time calculation python library',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author=__author__,
      url='https://github.com/SatAgro/suntime',
      copyright='Copyright 2024 SatAgro',
      license=__license__,
      packages=['suntime'],
      install_requires=['python-dateutil'])
