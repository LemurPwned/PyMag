from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import sys
import setuptools
import os

__version__ = '0.0.1'



setup(
    name='pymag',
    version=__version__,
    author='AGH',
    description='Python GUI for magnetics',
    long_description='',
    zip_safe=False,
)