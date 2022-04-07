"""
Setup script for PaperCollector

Install:
[shell] python setup.py install
Develop:
[shell] python setpy.py develop
Call module:
[python] import papercollector
"""

from setuptools import setup, find_packages

setup(
    name="papercollector",
    version="1.0",
    author="ChiahsinChu",
    author_email="xmuchiahsin@gmail.com",
    packages=find_packages('papercollector'),
    exclude_package_date={'': ['.gitignore']},
)
