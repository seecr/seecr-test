## begin license ##
# 
# "Seecr Test" provides test tools. 
# 
# Copyright (C) 2005-2009 Seek You Too (CQ2) http://www.cq2.nl
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

from seecr.test import SeecrTestCase

class SeecrTestCaseTest(SeecrTestCase):

    def checkAssertEqualsWSFails(self, s1, s2):
        try:
            self.assertEqualsWS(s1, s2)
        except AssertionError, e:
            return
        self.fail("%s should not equal %s" % (s1, s2))

    def testWhiteSpace(self):
        self.assertEqualsWS('', '')
        self.assertEqualsWS('aa', '  aa')
        self.assertEqualsWS('bb', 'bb  ')
        self.assertEqualsWS('c c ', ' c c ')
        self.checkAssertEqualsWSFails('', 'a')
        self.checkAssertEqualsWSFails('asdf', 'fdsa')

