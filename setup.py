#!/usr/bin/env python2

# This file is part of DumpTruck.

# Copyright (C) 2012 ScraperWiki Ltd. and other contributors
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to the following
# conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies
# or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

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
        'License :: OSI Approved :: MIT License',
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
    license='MIT',
#   install_requires = open('requirements.txt').read().split('\n')[:-1],
)
