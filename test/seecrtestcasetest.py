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

from StringIO import StringIO

# TODO:
#   lxmltostring stuff ...
from lxml.etree import parse, tostring


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

    def checkAssertEqualsLxmlFails(self, x1, x2, message):
        try:
            self.assertEqualsLxml(expected=x1, result=x2)
        except AssertionError, e:
            self.assertEquals(message, str(e))
            return
        self.fail("Fail!\n%s should not equal:\n%s" % (tostring(x1, encoding='UTF-8', pretty_print=True), tostring(x2, encoding='UTF-8', pretty_print=True)))

    def testAssertEqualsLxml(self):
        xml = parseString('<xml/>')
        self.assertEqualsLxml(xml, xml)
        self.assertEqualsLxml(xml, parseString('<xml/>'))

        # (root) tag
        self.checkAssertEqualsLxmlFails(
            parseString('<aap/>'),
            parseString('<xml/>'),
            "Tags do not match 'aap' != 'xml' at location: ''")
        # (root) tag - NS diff
        self.checkAssertEqualsLxmlFails(
            parseString('<xml/>'),
            parseString('<xml xmlns="urn:something"/>'),
            "Tags do not match 'xml' != '{urn:something}xml' at location: ''")
        # attrs right
        self.checkAssertEqualsLxmlFails(
            parseString('<xml/>'),
            parseString('<xml attr="" anotherattr="zz"/>'),
            "Unexpected attributes 'attr', 'anotherattr' at location: 'xml'")
        # attrs left
        self.checkAssertEqualsLxmlFails(
            parseString('<xml a="" z=""/>'),
            parseString('<xml/>'),
            "Missing attributes 'a', 'z' at location: 'xml'")
        # attrs value
        self.checkAssertEqualsLxmlFails(
            parseString('<xml attr="a"/>'),
            parseString('<xml attr="b"/>'),
            "Attribute 'attr' has a different value ('a' != 'b') at location: 'xml'")
        # attrs NS
        self.checkAssertEqualsLxmlFails(
            parseString('<xml attr="a"/>'),
            parseString('<xml a:attr="b" xmlns:a="urn:something"/>'),
            "Missing attributes 'attr' at location: 'xml'")

        # subtag #nr difference
        self.checkAssertEqualsLxmlFails(
            parseString('<xml><subtag/><another.tag/></xml>'),
            parseString('<xml><another.tag/></xml>'),
            "Number of children not equal (expected -- result):\n\
    'subtag' -- 'another.tag'\n\
    'another.tag' -- no|tag\n\
\n\
At location: 'xml'")

        self.fail("Continue here")

        # subtag tagname difference
        self.checkAssertEqualsLxmlFails(
            parseString('<xml><subtag/></xml>'),
            parseString('<xml><subgat/></xml>'),
            "?")

        # subtag tail difference
        self.checkAssertEqualsLxmlFails(
            parseString('<xml><subtag/></xml>'),
            parseString('<xml><subtag/> tail </xml>'),
            "?")



        # TODO: Test this!
        #   deeper nested xml (for correct (non-)recusion and CompareXml.xpathToHere testing)
        #   xpathToHere correct for tail's, and other more complex structures
        #   breadth first not depth first (i.e. not intuitive "first error" in test may not be first error in xml-serialisation)
        #   fail on str's, ... not lxml'ish
        #   fail-or-retree Node's iso Tree.


def parseString(s):
    return parse(StringIO(s))

