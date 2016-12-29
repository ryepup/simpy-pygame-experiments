# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='simpygame',
    version='0.1.0',
    description='Tools for visualizing simpy simulations via pygame',
    long_description=readme,
    author='Ryan Davis',
    author_email='ryepup@gmail.com',
    url='https://github.com/ryepup/simpy-pygame-experiments',
    license=license,
    install_requires=['pygame', 'simpy'],
    packages=find_packages(exclude=('tests', 'docs'))
)