#!/usr/bin/env python
## begin license ##
# 
# "Seecr Test" provides test tools. 
# 
# Copyright (C) 2010-2011 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2012 Seecr (Seek You Too B.V.) http://seecr.nl
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

from os.path import isfile, abspath, basename
import re
from sys import argv

importLineRe = re.compile("from (?P<filename>.*) import (?P<testname>.*)")
defLineRe = re.compile('def test(?P<defname>.*)\(self\):')

def listTests(fileWithAllTests):
    testFilename = basename(abspath(fileWithAllTests))
    if testFilename.endswith('.sh'):
        testFilename = '_%s.py' % testFilename[:-3]
    for line in open(testFilename):
        match = importLineRe.match(line)
        if match:
            listTestsInFile(**match.groupdict())

def listTestsInFile(filename='', testname=''):
    for testname in (f.strip() for f in testname.split(',')):
        if not testname.endswith('Test'):
            return
        print testname
        for line in open('%s.py' % filename.replace('.', '/')):
            match = defLineRe.search(line)
            if match:
                print '%s.test%s' % (testname, match.groupdict()['defname'])

if __name__ == '__main__':
    if len(argv) == 2:
        listTests(argv[1])
