## begin license ##
# 
# "Seecr Test" provides test tools. 
# 
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

from __future__ import with_statement

from unittest import TestCase

from seecr.test.io import stdout_replaced
from seecr.test.timing import T
from seecr.test.utils import ignoreLineNumbers, sleepWheel

from time import time, sleep


class UtilsTest(TestCase):
    def testIgnoreLineNumber(self):
        theTraceback = """Traceback (most recent call last):
  File "../some/file.py", line 104, in aFunction
    for _var  in vars:
  File "some/other/file.py", line 249, in anotherFuntion
    raise Exception('xcptn')
Exception: xcptn\n"""

        expected = """Traceback (most recent call last):
  File "../some/file.py", line [#], in aFunction
    for _var  in vars:
  File "some/other/file.py", line [#], in anotherFuntion
    raise Exception('xcptn')
Exception: xcptn\n"""

        self.assertEquals(expected, ignoreLineNumbers(theTraceback))

    def testSleepWheelNoCallback(self):
        t0 = time()
        with stdout_replaced():
            retval = sleepWheel(0.01, interval=0.001)
        t1 = time()
        delta = t1 - t0
        self.assertTrue(0.01 < delta < max(0.02, (0.02 * T_ADJUSTMENT * T)), delta)
        self.assertEquals(False, retval)

    def testSleepWheelCallbackFalsy(self):
        calls = []
        def callback():
            calls.append(True)
        t0 = time()
        with stdout_replaced() as out:
            retval = sleepWheel(0.01, interval=0.001, callback=callback)
            t1 = time()
            self.assertEquals('\\\x08|\x08/\x08-\x08\\\x08|\x08/\x08-\x08\\\x08|\x08', out.getvalue())
        delta = t1 - t0
        self.assertTrue(0.01 < delta < max(0.02, (0.02 * T_ADJUSTMENT * T)), delta)
        self.assertEquals(10, len(calls))
        self.assertEquals(False, retval)

    def testSleepWheelCallbackTruthy(self):
        calls = []
        def callback():
            calls.append(True)
            return True
        t0 = time()
        with stdout_replaced() as out:
            retval = sleepWheel(0.01, interval=0.001, callback=callback)
            t1 = time()
            self.assertEquals('\\\x08', out.getvalue())
        delta = t1 - t0
        self.assertTrue(0.001 < delta < max(0.002, (0.002 * T_ADJUSTMENT * T)), delta)
        self.assertEquals(1, len(calls))
        self.assertEquals(True, retval)

T_ADJUSTMENT = 1.5
