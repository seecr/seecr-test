#!/usr/bin/env python
## begin license ##
#
# "Seecr Test" provides test tools.
#
# Copyright (C) 2012-2013, 2015, 2020 Seecr (Seek You Too B.V.) https://seecr.nl
#
# This file is part of "Seecr Test"
#
# "Seecr Test" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "Seecr Test" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "Seecr Test"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from distutils.core import setup
from os import walk
from os.path import join

scripts = []
for path, dirs, files in walk('bin'):
    for file in files:
        scripts.append(join(path, file))

setup(
    name='seecr-test',
    version='%VERSION%',
    packages=[
        'seecr',     # DO_NOT_DISTRIBUTE
        'seecr.test',
    ],
    scripts=scripts,
    url='http://www.seecr.nl',
    author='Seecr',
    author_email='info@seecr.nl',
    description='Seecr Test provides test tools',
    long_description='Seecr Test provides test tools for: unittesting, integrationtesting etc.',
    platforms=['linux'],
)

