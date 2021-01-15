## begin license ##
#
# "Seecr Test" provides test tools.
#
# Copyright (C) 2012-2013, 2017, 2019-2021 Seecr (Seek You Too B.V.) https://seecr.nl
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



from unittest import TestCase

import sys

from io import StringIO
from traceback import print_exc

from seecr.test.io import stdout_replaced, stderr_replaced, stdin_replaced


class IOTest(TestCase):
    def testStdInReplaced_withGivenStream(self):
        idStdin = id(sys.stdin)

        _in = StringIO('string\nio\n')
        with stdin_replaced(_in) as s:
            self.assertNotEqual(idStdin, id(sys.stdin))
            self.assertEqual(['string\n', 'io\n'], sys.stdin.readlines())

        self.assertEqual(idStdin, id(sys.stdin))

        _in = StringIO('string\nio\n')
        @stdin_replaced(_in)
        def f():
            self.assertNotEqual(idStdin, id(sys.stdin))
            self.assertEqual(['string\n', 'io\n'], sys.stdin.readlines())
        self.assertEqual(idStdin, id(sys.stdin))

    def testStdInReplaced_withEmptyStream(self):
        idStdin = id(sys.stdin)

        with stdin_replaced() as s:
            s.write('li')
            s.write('ne1\nline2\n')
            s.seek(0)
            self.assertNotEqual(idStdin, id(sys.stdin))
            self.assertEqual(['line1\n', 'line2\n'], sys.stdin.readlines())

        self.assertEqual(idStdin, id(sys.stdin))

        @stdin_replaced()
        def f():
            sys.stdin.write('li') # Won't normally work, but - long live mocking
            sys.stdin.write('ne1\nline2\n')
            sys.stdin.seek(0)
            self.assertEqual(StringIO, type(sys.stdin))
            self.assertNotEqual(idStdin, id(sys.stdin))
            self.assertEqual(['string\n', 'io\n'], sys.stdin.readlines())
        self.assertEqual(idStdin, id(sys.stdin))
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

        self.assertEqual(idStderr, id(sys.stderr))

        @stderr_replaced
        def f():
            self.assertNotEqual(idStderr, id(sys.stderr))
            raise Exception()
        self.assertEqual(idStderr, id(sys.stderr))

    def testStdOutReplaced(self):
        idStdout = id(sys.stdout)
        idStderr = id(sys.stderr)
        with stdout_replaced() as s:
            self.assertNotEqual(idStdout, id(sys.stdout))
            self.assertEqual(idStderr, id(sys.stderr))
            print('output_as_contextmanager')
            self.assertEqual('output_as_contextmanager\n', s.getvalue())
        self.assertEqual(idStdout, id(sys.stdout))

        called = []
        @stdout_replaced
        def decoratedFunction(arg1, *args, **kwargs):
            self.assertNotEqual(idStdout, id(sys.stdout))
            called.append((arg1, args, kwargs))
            print('output_as_decorator')
            return 'retval'

        with stdout_replaced() as s:
            outerMockId = id(sys.stdout)
            self.assertNotEqual(idStdout, outerMockId)

            result = decoratedFunction('arg1', 'anotherarg', key='wordedArg')

            self.assertEqual('retval', result)
            self.assertEqual(outerMockId, id(sys.stdout))
            self.assertEqual('', s.getvalue())

        self.assertEqual(idStdout, id(sys.stdout))
        self.assertEqual([('arg1', ('anotherarg',), {'key': 'wordedArg'})], called)

    def testStdOutReplacedNoSideEffectsOnException(self):
        idStdout = id(sys.stdout)
        def f():
            with stdout_replaced() as s:
                raise Exception()
        self.assertRaises(Exception, lambda: f())
        self.assertEqual(idStdout, id(sys.stdout))

        @stdout_replaced
        def f():
            raise Exception()
        self.assertRaises(Exception, lambda: f())
        self.assertEqual(idStdout, id(sys.stdout))
