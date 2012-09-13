from setuptools import setup, find_packages
import sys, os

version = '0.0'

setup(name='IPyMongo',
      version=version,
      description="IPython extension and wrapper for using with MongoDB",
      long_description="""This module installs the ipymongo script and IPython
extension, which allows you to use the following new magic commands in IPython:

 - use <database>
 - connect [ <mongodb uri> ]
 - login [ <username> <password> ]

You also get access to the following global variables:

 - db (current database)
 - conn (current mongodb connection)

Your prompt is also updated to show the current database name.

The ipymongo command takes an optional mongodb:// uri. If not supplied, it will
connect to mongodb://localhost:27017/test.
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Rick Copeland',
      author_email='rick@arborian.com',
      url='',
      license='Apache',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      scripts=['scripts/ipymongo'],
      install_requires=[
        'ipython',
        'pymongo'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
