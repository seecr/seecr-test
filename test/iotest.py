## begin license ##
#
# "Seecr Test" provides test tools.
#
# Copyright (C) 2012-2013, 2017 Seecr (Seek You Too B.V.) http://seecr.nl
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

from StringIO import StringIO
from traceback import print_exc

from seecr.test.io import stdout_replaced, stderr_replaced, stdin_replaced, stdin_replaced_decorator


class IOTest(TestCase):
    def testStdInReplaced_withGivenStream(self):
        idStdin = id(sys.stdin)

        _in = StringIO('string\nio\n')
        with stdin_replaced(_in) as s:
            self.assertNotEqual(idStdin, id(sys.stdin))
            self.assertEquals(['string\n', 'io\n'], sys.stdin.readlines())

        self.assertEquals(idStdin, id(sys.stdin))

        _in = StringIO('string\nio\n')
        @stdin_replaced_decorator(_in) # Cannot reuse same fn because decoration needs to be distinguishable from args-usage.
        def f():
            self.assertNotEqual(idStdin, id(sys.stdin))
            self.assertEquals(['string\n', 'io\n'], sys.stdin.readlines())
        self.assertEquals(idStdin, id(sys.stdin))

    def testStdInReplaced_withEmptyStream(self):
        idStdin = id(sys.stdin)

        with stdin_replaced() as s:
            s.write('li')
            s.write('ne1\nline2\n')
            s.seek(0)
            self.assertNotEqual(idStdin, id(sys.stdin))
            self.assertEquals(['line1\n', 'line2\n'], sys.stdin.readlines())

        self.assertEquals(idStdin, id(sys.stdin))

        @stdin_replaced_decorator() # Cannot reuse same fn because decoration needs to be distinguishable from args-usage.
        def f():
            sys.stdin.write('li') # Won't normally work, but - long live mocking
            sys.stdin.write('ne1\nline2\n')
            sys.stdin.seek(0)
            self.assertEquals(StringIO, type(sys.stdin))
            self.assertNotEqual(idStdin, id(sys.stdin))
            self.assertEquals(['string\n', 'io\n'], sys.stdin.readlines())
        self.assertEquals(idStdin, id(sys.stdin))
        self.assertRaises(IOError, lambda: sys.stdin.write('x'))

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
