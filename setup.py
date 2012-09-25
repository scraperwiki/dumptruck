#!/usr/bin/env python2

# This file is part of DumpTruck.

# DumpTruck is free software: you can redistribute it and/or modify
# it under the terms of the GNU Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# DumpTruck is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Public License for more details.

# You should have received a copy of the GNU Public License
# along with DumpTruck.  If not, see <http://www.gnu.org/licenses/>.

from distutils.core import setup
import dumptruck

setup(name='dumptruck',
    author='Thomas Levine',
    #author_email='perluette@thomaslevine.com',
    author_email='thomas@scraperwiki.com',
    description='Relaxing interface to SQLite',
    url='https://github.com/tlevine/dumptruck',
    #url='http://hacks.thomaslevine.com/dumptruck',
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: SQL',
        'Topic :: Database :: Front-Ends',
    ],
    packages=['dumptruck'],

    # From requests
    version=dumptruck.__version__,
    #long_description=open('README.md').read() + '\n\n' + open('HISTORY.md').read(), #needs to be rst
    #package_data={'': ['LICENSE']},
    #license=open('LICENSE').read(),
    license='GPL',
#   install_requires = open('requirements.txt').read().split('\n')[:-1],
)
