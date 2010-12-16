#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='storage',
      version='0.1',
      description='spatial storage client',
      packages=find_packages(),
      install_requires=(
          'oauth',
      ),
)
