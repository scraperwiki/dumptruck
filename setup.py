#!/usr/bin/env python2

from distutils.core import setup

setup(name='DumpTruck',
      author='Thomas Levine',
      author_email='thomas@scraperwiki.com',
      url='https://github.com/tlevine/dumptruck',
      description='Relaxing interface to SQLite',
      url='http://hacks.thomaslevine.com/dumptruck',
      classifiers=[
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: SQL',
          'Topic :: Database',
          'Topic :: Database :: Front-Ends',
          'Operating System :: MacOS',
          'Operating System :: Microsoft',
          'Operating System :: POSIX',
      ],
      packages=['dumptruck'],

      # From requests
    version=requests.__version__,
    long_description=open('README.md').read() + '\n\n' + open('HISTORY.md').read(),
      package_data={'': ['LICENSE']},
      license=open('LICENSE').read(),
     )
