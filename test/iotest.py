## begin license ##
# 
# "Seecr Test" provides test tools. 
# 
# Copyright (C) 2012-2013 Seecr (Seek You Too B.V.) http://seecr.nl
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

import sys

from traceback import print_exc

from seecr.test.io import stdout_replaced, stderr_replaced


class IOTest(TestCase):

    def testStdErrReplaced(self):
        idStderr = id(sys.stderr)

        with stderr_replaced() as s:
            self.assertNotEqual(idStderr, id(sys.stderr))
            try:
                raise Exception('xcptn')
            except Exception:
                print_exc()
            result = s.getvalue()
            self.assertTrue('Traceback' in result, result)
            self.assertTrue('Exception: xcptn' in result, result)

        self.assertEquals(idStderr, id(sys.stderr))

        @stderr_replaced
        def f():
            self.assertNotEqual(idStderr, id(sys.stderr))
            raise Exception()
        self.assertEquals(idStderr, id(sys.stderr))

    def testStdOutReplaced(self):
        idStdout = id(sys.stdout)
        idStderr = id(sys.stderr)
        with stdout_replaced() as s:
            self.assertNotEqual(idStdout, id(sys.stdout))
            self.assertEquals(idStderr, id(sys.stderr))
            print 'output_as_contextmanager'
            self.assertEquals('output_as_contextmanager\n', s.getvalue())
        self.assertEquals(idStdout, id(sys.stdout))

        called = []
        @stdout_replaced
        def decoratedFunction(arg1, *args, **kwargs):
            self.assertNotEqual(idStdout, id(sys.stdout))
            called.append((arg1, args, kwargs))
            print 'output_as_decorator'
            return 'retval'

        with stdout_replaced() as s:
            outerMockId = id(sys.stdout)
            self.assertNotEqual(idStdout, outerMockId)

            result = decoratedFunction('arg1', 'anotherarg', key='wordedArg')

            self.assertEquals('retval', result)
            self.assertEquals(outerMockId, id(sys.stdout))
            self.assertEquals('', s.getvalue())

        self.assertEquals(idStdout, id(sys.stdout))
        self.assertEquals([('arg1', ('anotherarg',), {'key': 'wordedArg'})], called)

    def testStdOutReplacedNoSideEffectsOnException(self):
        idStdout = id(sys.stdout)
        def f():
            with stdout_replaced() as s:
                raise Exception()
        self.assertRaises(Exception, lambda: f())
        self.assertEquals(idStdout, id(sys.stdout))

        @stdout_replaced
        def f():
            raise Exception()
        self.assertRaises(Exception, lambda: f())
        self.assertEquals(idStdout, id(sys.stdout))

