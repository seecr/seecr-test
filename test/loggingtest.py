## begin license ##
#
# "Seecr Test" provides test tools.
#
# Copyright (C) 2019 Seecr (Seek You Too B.V.) http://seecr.nl
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

from seecr.test import SeecrTestCase
from seecr.test.loggingtest import readTestFile, formatTestname
from os.path import join, dirname, abspath

class LoggingTest(SeecrTestCase):
    def testReadFromFile(self):
        f = readTestFile('data', 'example-testresults.txt')
        self.assertEqual([
                {'classname': 'calltracetest.CallTraceTest', 'testname': 'testCallTraceAsMethod', 'status': 'ok'},
                {'classname': 'calltracetest.CallTraceTest', 'testname': 'testCallWithArguments', 'status': 'ok'},
                {'classname': 'utilstest.UtilsTest', 'testname': 'testParseHtmlAsXml', 'status': 'ok'},
            ], f['tests'])
        self.assertTrue('timestamp' in f)


    def testFormatTestname(self):
        self.assertEqual('Call trace as method', formatTestname('testCallTraceAsMethod'))
