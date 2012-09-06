#!/usr/bin/env python2.5
## begin license ##
#
#   Copyright (C) 2010-2011 Seek You Too (CQ2) http://www.cq2.nl
#
#   All rights reserved.
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
