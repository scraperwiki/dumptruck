#!/usr/bin/env python2

from distutils.core import setup

setup(name='DumpTruck',
      version='0.1',
      description='Relaxing interface to SQLite',
      author='Thomas Levine',
      author_email='thomas@scraperwiki.com',
      url='http://hacks.thomaslevine.com/dumptruck',
      packages=['src'],
     )

#['sqlite3', 're', 'json', 'datetime', 'pickle', 'copy'],
