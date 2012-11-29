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

from traceback import print_exc

from seecr.test.io import stdout_replaced, stderr_replaced


class IOTest(TestCase):

    def testStdOutReplaced(self):
        with stdout_replaced() as s:
            print 'output'
            self.assertEquals('output\n', s.getvalue())

    def testStdErrReplaced(self):
        with stderr_replaced() as s:
            try:
                raise Exception('xcptn')
            except Exception:
                print_exc()
            result = s.getvalue()
            self.assertTrue('Traceback' in result, result)
            self.assertTrue('Exception: xcptn' in result, result)

