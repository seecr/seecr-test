# -*- coding: utf-8 -*-
## begin license ##
#
# "Seecr Test" provides test tools.
#
# Copyright (C) 2005-2009 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2012-2013, 2016-2017, 2019-2021 Seecr (Seek You Too B.V.) https://seecr.nl
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

from io import StringIO
import re

# TODO:
#   lxmltostring stuff ...
from lxml.etree import parse, tostring, XMLParser

# whiteboxing:
from seecr.test.seecrtestcase import CompareXml, refindLxmlNodeCallback


class SeecrTestCaseTest(SeecrTestCase):
    longMessage = True
    maxDiff = None

    def checkAssertEqualsWSFails(self, s1, s2):
        try:
            self.assertEqualsWS(s1, s2)
        except AssertionError:
            return
        self.fail("%s should not equal %s" % (s1, s2))

    def testWhiteSpace(self):
        self.assertEqualsWS('', '')
        self.assertEqualsWS('aa', '  aa')
        self.assertEqualsWS('bb', 'bb  ')
        self.assertEqualsWS('c c ', ' c c ')
        self.checkAssertEqualsWSFails('', 'a')
        self.checkAssertEqualsWSFails('asdf', 'fdsa')

    def checkAssertEqualsLxmlFails(self, x1, x2, message, showContext=False):
        try:
            self.assertEqualsLxml(expected=x1, result=x2, showContext=showContext)
        except AssertionError as e:
            self.assertMultiLineEqual(message, stripColor(str(e)))
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
        # (root) tag - prefix diff
        self.checkAssertEqualsLxmlFails(
            parseString('<a:xml xmlns:a="urn:something" />'),
            parseString('<b:xml xmlns:b="urn:something" />'),
            "Prefix difference a != b for namespace: 'urn:something'\nAt location: '{urn:something}xml'")
        # attrs right
        self.checkAssertEqualsLxmlFails(
            parseString('<xml/>'),
            parseString('<xml attr="" anotherattr="zz"/>'),
            "Unexpected attributes 'anotherattr', 'attr' at location: 'xml'")
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

        # (root) tag text difference
        self.checkAssertEqualsLxmlFails(
            parseString('<xml></xml>'),
            parseString('<xml>TeXT</xml>'),
            "Text difference: >no|text< != 'TeXT'\nAt location: 'xml'")
        self.checkAssertEqualsLxmlFails(
            parseString('<xml>OtHer</xml>'),
            parseString('<xml>TeXT</xml>'),
            "Text difference: 'OtHer' != 'TeXT'\nAt location: 'xml'")
        self.checkAssertEqualsLxmlFails(
            parseString('<xml>Xet</xml>'),
            parseString('<xml></xml>'),
            "Text difference: 'Xet' != >no|text<\nAt location: 'xml'")

        # subtag tagname difference
        self.checkAssertEqualsLxmlFails(
            parseString('<xml><subtag/></xml>'),
            parseString('<xml><subgat/></xml>'),
            "Tags do not match 'subtag' != 'subgat' at location: 'xml'")

        # subtag tagname prefix difference
        self.checkAssertEqualsLxmlFails(
            parseString('<xml><a:subtag xmlns:a="aaa"/></xml>'),
            parseString('<xml><b:subtag xmlns:b="aaa"/></xml>'),
            "Prefix difference a != b for namespace: 'aaa'\nAt location: 'xml/{aaa}subtag'")

        # subtag attrs left and right
        self.checkAssertEqualsLxmlFails(
            parseString('<xml><subtag a="" z=""/></xml>'),
            parseString('<xml><subtag a="" m=""/></xml>'),
            "Missing attributes 'z' at location: 'xml/subtag'")
        # subtag attrs value
        self.checkAssertEqualsLxmlFails(
            parseString('<xml><subtag attr="a"/></xml>'),
            parseString('<xml><subtag attr="b"/></xml>'),
            "Attribute 'attr' has a different value ('a' != 'b') at location: 'xml/subtag'")

        # sub-subtag #nr difference
        self.checkAssertEqualsLxmlFails(
            parseString('<xml><ml><subtag/><another.tag/></ml></xml>'),
            parseString('<xml><ml><another.tag/></ml></xml>'),
            "Number of children not equal (expected -- result):\n\
    'subtag' -- 'another.tag'\n\
    'another.tag' -- no|tag\n\
\n\
At location: 'xml/ml'")

        # subtag text difference
        self.checkAssertEqualsLxmlFails(
            parseString('<xml><subtag/></xml>'),
            parseString('<xml> TeXT <subtag/></xml>'),
            "Text difference: >no|text< != ' TeXT '\nAt location: 'xml'")

        # subtag tail difference
        self.checkAssertEqualsLxmlFails(
            parseString('<xml><subtag/></xml>'),
            parseString('<xml><subtag/> tail </xml>'),
            "Tail difference (text after closing of tag): >no|tail< != ' tail '\nAt location: 'xml/subtag'")

    def testAssertEqualsLxmlPrefixMatchingCanBeDisabled(self):
        # (root) tag - Prefix diff
        args = (parseString('<a:xml xmlns:a="urn:something" />'),
            parseString('<b:xml xmlns:b="urn:something" />'))

        try:
            self.assertEqualsLxml(matchPrefixes=True, *args)
        except AssertionError as e:
            self.assertTrue(str(e).startswith('Prefix difference'), str(e))
        else:
            self.fail()

        self.assertEqualsLxml(matchPrefixes=False, *args)

    def testAssertEqualsLxmlsXpathToHereWithCommentNodes(self):
        xml = '''\
<!-- 1st Comment -->
<!-- Pre-Root Comment -->
<a xmlns="n:s/#">
    <!-- 1st Comment inside -->
    <!-- 2nd Comment inside -->
    <b/>
</a>
<!-- Post-Root Comment -->
<!-- last Comment -->'''
        lxml = parseString(xml)
        _pre_root = lxml.getroot().getprevious()
        _1st = _pre_root.getprevious()
        _post_root = lxml.getroot().getnext()
        _last = _post_root.getnext()
        _1st_inside = lxml.getroot().getchildren()[0]
        _2nd_inside = lxml.getroot().getchildren()[1]

        c = CompareXml(expectedNode=lxml, resultNode=lxml)

        self.assertEqual('{n:s/#}a', c.xpathToHere(_1st_inside))
        self.assertEqual('{n:s/#}a', c.xpathToHere(_2nd_inside))
        self.assertEqual('{n:s/#}a/comment()[1]', c.xpathToHere(_1st_inside, includeCurrent=True))
        self.assertEqual('{n:s/#}a/comment()[2]', c.xpathToHere(_2nd_inside, includeCurrent=True))

        self.assertEqual('', c.xpathToHere(_1st))
        self.assertEqual('', c.xpathToHere(_pre_root))
        self.assertEqual('comment()[1]', c.xpathToHere(_1st, includeCurrent=True))
        self.assertEqual('comment()[2]', c.xpathToHere(_pre_root, includeCurrent=True))

        self.assertEqual('', c.xpathToHere(_post_root))
        self.assertEqual('', c.xpathToHere(_last))
        self.assertEqual('comment()[3]', c.xpathToHere(_post_root, includeCurrent=True))
        self.assertEqual('comment()[4]', c.xpathToHere(_last, includeCurrent=True))

    def testAssertEqualsLxmlsXpathToHereWithProcessingInstructions(self):
        xml = '''\
<?pro cessing instruction?>
<a xmlns="n:s/#">
    <?php ...?>
    <?notphp Intermezzo?>
    <?php just kidding!?>
    <b/>
</a>
<?xml-stylesheet href="what.css" type="text/ever"?>
<?pro with
newlines?>'''
        lxml = parseString(xml)
        _pro_cessing = lxml.getroot().getprevious()
        _xml_style = lxml.getroot().getnext()
        _pro_newline = _xml_style.getnext()
        _inside_1_php = lxml.getroot().getchildren()[0]
        _inside_2_notphp = lxml.getroot().getchildren()[1]
        _inside_3_php = lxml.getroot().getchildren()[2]

        c = CompareXml(expectedNode=lxml, resultNode=lxml)

        self.assertEqual("{n:s/#}a", c.xpathToHere(_inside_1_php))
        self.assertEqual("{n:s/#}a", c.xpathToHere(_inside_2_notphp))
        self.assertEqual("{n:s/#}a", c.xpathToHere(_inside_3_php))
        self.assertEqual("{n:s/#}a/processing-instruction('php')[1]", c.xpathToHere(_inside_1_php, includeCurrent=True))
        self.assertEqual("{n:s/#}a/processing-instruction('notphp')", c.xpathToHere(_inside_2_notphp, includeCurrent=True))
        self.assertEqual("{n:s/#}a/processing-instruction('php')[2]", c.xpathToHere(_inside_3_php, includeCurrent=True))

        self.assertEqual("", c.xpathToHere(_pro_cessing))
        self.assertEqual("", c.xpathToHere(_xml_style))
        self.assertEqual("", c.xpathToHere(_pro_newline))
        self.assertEqual("processing-instruction('pro')[1]", c.xpathToHere(_pro_cessing, includeCurrent=True))
        self.assertEqual("processing-instruction('xml-stylesheet')", c.xpathToHere(_xml_style, includeCurrent=True))
        self.assertEqual("processing-instruction('pro')[2]", c.xpathToHere(_pro_newline, includeCurrent=True))

    def testAssertEqualsLxmlsXpathToHereWithEntityNodes(self):
        # For a (possible) use-case of this parsing method, see: http://lxml.de/FAQ.html#how-do-i-use-lxml-safely-as-a-web-service-endpoint
        parser = XMLParser(resolve_entities=False)  # Otherwise, no entity nodes remain.
        xml = '''\
<!DOCTYPE root [
    <!ENTITY self "sefl">
    <!ENTITY otherself "ohtersefl">
]>
<r>&#1234;  &self;  &otherself;<a>&self;</a></r>
'''
        lxml = parse(StringIO(xml), parser=parser)
        _inside_self = lxml.getroot().getchildren()[0]
        _inside_otherself = lxml.getroot().getchildren()[1]
        _insideA_self = lxml.getroot().getchildren()[2].getchildren()[0]

        c = CompareXml(expectedNode=lxml, resultNode=lxml)

        self.assertEqual("r", c.xpathToHere(_inside_self))
        self.assertEqual("r", c.xpathToHere(_inside_otherself))
        self.assertEqual("r/a", c.xpathToHere(_insideA_self))
        self.assertEqual("r/?[1]", c.xpathToHere(_inside_self, includeCurrent=True))
        self.assertEqual("r/?[2]", c.xpathToHere(_inside_otherself, includeCurrent=True))
        self.assertEqual("r/a/?", c.xpathToHere(_insideA_self, includeCurrent=True))

    def testAssertEqualsLxmlCommentNodes(self):
        # In(-root)-tag comment existence
        self.checkAssertEqualsLxmlFails(
            parseString('<r></r>'),
            parseString('<r><!-- Comment --></r>'),
            "Number of children not equal (expected -- result):\n    no|tag -- comment|node\n\nAt location: 'r'")

        # In(-root)-tag comment difference
        self.checkAssertEqualsLxmlFails(
            parseString('<r><!-- Tnemmoc --></r>'),
            parseString('<r><!-- Comment --></r>'),
            "Text difference: ' Tnemmoc ' != ' Comment '\nAt location: 'r/comment()'")

        # Pre-root-tag comment existence
        self.checkAssertEqualsLxmlFails(
            parseString('<r/>'),
            parseString('<!-- Comment --><r/>'),
            "Number of children not equal (expected -- result):\n    'r' -- comment|node\n    no|tag -- 'r'\n\nAt location: ''")

        # Pre-root-tag comment difference
        self.checkAssertEqualsLxmlFails(
            parseString('<!-- ign --><!-- X --><r/><!-- ign. -->'),
            parseString('<!-- ign --><!-- Y --><r/><!-- ign. -->'),
            "Text difference: ' X ' != ' Y '\nAt location: 'comment()[2]'")

        # Post-root-tag comment existence
        self.checkAssertEqualsLxmlFails(
            parseString('<!-- ign. --><r/><!-- same --><!-- different -->'),
            parseString('<!-- ign. --><r/><!-- same -->'),
            "Number of children not equal (expected -- result):\n    comment|node -- comment|node\n    'r' -- 'r'\n    comment|node -- comment|node\n    comment|node -- no|tag\n\nAt location: ''")

    def testAssertEqualsLxmlPINodes(self):
        # In(-root)-tag PI existence
        self.checkAssertEqualsLxmlFails(
            parseString('<r></r>'),
            parseString('<r><?pro cessing?></r>'),
            "Number of children not equal (expected -- result):\n    no|tag -- processing-instruction('pro')|node\n\nAt location: 'r'")

        # In(-root)-tag PI difference; data
        self.checkAssertEqualsLxmlFails(
            parseString('<r><?pro gnissec?></r>'),
            parseString('<r><?pro cessing?></r>'),
            "Text difference: 'gnissec' != 'cessing'\nAt location: 'r/processing-instruction('pro')'")

        # In(-root)-tag PI difference; target
        self.checkAssertEqualsLxmlFails(
            parseString('<r><?pre cessing?></r>'),
            parseString('<r><?pro cessing?></r>'),
            "Processing-Instruction targets do not match 'pre' != 'pro' at location: 'r'")

        # Pre-root-tag PI existence
        self.checkAssertEqualsLxmlFails(
            parseString('<?pro x?><?pro cessing?><r/>'),
            parseString('<?pro x?><r/>'),
            "Number of children not equal (expected -- result):\n    processing-instruction('pro')|node -- processing-instruction('pro')|node\n    processing-instruction('pro')|node -- 'r'\n    'r' -- no|tag\n\nAt location: ''")

        # Pre-root-tag PI difference; data
        self.checkAssertEqualsLxmlFails(
            parseString('<?pro x?><?pro cessing?><r/>'),
            parseString('<?pro x?><?pro gnissec?><r/>'),
            "Text difference: 'cessing' != 'gnissec'\nAt location: 'processing-instruction('pro')[2]'")

        # Pre-root-tag PI difference; target
        self.checkAssertEqualsLxmlFails(
            parseString('<?pro x?><?pro cessing?><r/>'),
            parseString('<?pro x?><?am ignored?><r/>'),
            "Processing-Instruction targets do not match 'pro' != 'am' at location: ''")

        # Post-root-tag PI difference; target
        self.checkAssertEqualsLxmlFails(
            parseString('<?sa me?><r/><?diff?>'),
            parseString('<?sa me?><r/><?errent?>'),
            "Processing-Instruction targets do not match 'diff' != 'errent' at location: ''")

    def testAssertEqualsLxmlEntityNodes(self):
        # For a (possible) use-case of this parsing method, see: http://lxml.de/FAQ.html#how-do-i-use-lxml-safely-as-a-web-service-endpoint
        parser = XMLParser(resolve_entities=False)  # Otherwise, no entity nodes remain.
        def parseStringUnres(s):
            return parse(StringIO(s), parser=parser)

        xml = '''\
<!DOCTYPE root [
    <!ENTITY self "sefl">
    <!ENTITY otherself "ohtersefl">
]>
<r>%s</r>
'''

        # In(-root)-tag Entity existence
        self.checkAssertEqualsLxmlFails(
            parseStringUnres(xml % '&self;'),
            parseStringUnres(xml % ''),
            "Number of children not equal (expected -- result):\n    entity|node -- no|tag\n\nAt location: 'r'")

        # In(-root)-tag Entity difference
        self.checkAssertEqualsLxmlFails(
            parseStringUnres(xml % '&self;'),
            parseStringUnres(xml % '&otherself;'),
            "Text difference: '&self;' != '&otherself;'\nAt location: 'r/?'")

        # In(-root)-tag Entity - tail diff
        self.checkAssertEqualsLxmlFails(
            parseStringUnres(xml % '&self;'),
            parseStringUnres(xml % '&self; TAIL '),
            "Tail difference (text after closing of tag): >no|tail< != ' TAIL '\nAt location: 'r/?'")

    def testAssertEqualsLxmlWithContext(self):
        # No difference, no context
        self.assertEqualsLxml(parseString('<x/>'), parseString('<x/>'))

        # Small diff, expected sourceline
        self.checkAssertEqualsLxmlFails(
            parseString('\n\n<r>%s\n  <x/>\n</r>' % ('\n'*8)),
            parseString('<r>\n  <y/>\n</r>'),
            """Tags do not match 'x' != 'y' at location: 'r'
=== expected (line 10, sourceline 12) ===
 9-SPACE
10:   <x/>
11- </r>
=== result (line 2) ===
1- <r>
2:   <y/>
3- </r>
=======================\n""".replace('SPACE', ' '), showContext=1)

        # Small diff, with ANSI Color stuff
        try:
            self.assertEqualsLxml(
                parseString('\n\n<r>%s\n  <x/>\n</r>' % ('\n'*8)),
                parseString('<r>\n  <y/>\n</r>')
                , showContext=1)
        except AssertionError as e:
            self.assertMultiLineEqual("""\
Tags do not match 'x' != 'y' at location: 'r'
=== expected (line 10, sourceline 12) ===
 9-SPACE
\033[31m10:   <x/>\033[0m
11- </r>
=== result (line 2) ===
1- <r>
\033[32m2:   <y/>\033[0m
3- </r>
=======================\n""".replace('SPACE', ' '), str(e))
        else:
            self.fail()

        # Small diff, result sourceline
        self.checkAssertEqualsLxmlFails(
            parseString('<r>\n  <y/>\n</r>'),
            parseString('\n\n<r>\n  <x/>\n%s</r>' % ('\n'*8)),
            """\
Tags do not match 'y' != 'x' at location: 'r'
=== expected (line 2) ===
1- <r>
2:   <y/>
3- </r>
=== result (line 2, sourceline 4) ===
1- <r>
2:   <x/>
3-SPACE
=====================================
""".replace('SPACE', ' '), showContext=1)

        # Pre-root diff
        self.checkAssertEqualsLxmlFails(
            parseString('<!-- Text -->\n<r>\n  <sub/>\n</r>'),
            parseString('<r/>'),
            """\
Number of children not equal (expected -- result):
    comment|node -- 'r'
    'r' -- no|tag

At location: ''
=== expected (line 1, sourceline 2) ===
1: <!-- Text --><r>
2-   <sub/>
3- </r>
=== result (line 1) ===
1: <r/>
=======================
""", showContext=10)

        # Odd namespaces still ok
        self.checkAssertEqualsLxmlFails(
            parseString('''\
<r>
  <sub xmlns="uri:1">
    <sub2 xmlns="uri:2">
      <s:sub3 xmlns:s="uri:1">
        <s:sub4 xmlns:s="uri:2">TextDiff</s:sub4>
      </s:sub3>
    </sub2>
  </sub>
</r>
'''),
            parseString('''\
<r>
  <sub xmlns="uri:1">
    <sub2 xmlns="uri:2">
      <s:sub3 xmlns:s="uri:1">
        <s:sub4 xmlns:s="uri:2">Different Text</s:sub4>
      </s:sub3>
    </sub2>
  </sub>
</r>
'''),
            """\
Text difference: 'TextDiff' != 'Different Text'
At location: 'r/{uri:1}sub/{uri:2}sub2/{uri:1}sub3/{uri:2}sub4'
=== expected (line 5) ===
1- <r>
2-   <sub xmlns="uri:1">
3-     <sub2 xmlns="uri:2">
4-       <s:sub3 xmlns:s="uri:1">
5:         <s:sub4 xmlns:s="uri:2">TextDiff</s:sub4>
6-       </s:sub3>
7-     </sub2>
8-   </sub>
9- </r>
=== result (line 5) ===
1- <r>
2-   <sub xmlns="uri:1">
3-     <sub2 xmlns="uri:2">
4-       <s:sub3 xmlns:s="uri:1">
5:         <s:sub4 xmlns:s="uri:2">Different Text</s:sub4>
6-       </s:sub3>
7-     </sub2>
8-   </sub>
9- </r>
=======================
""", showContext=10)

    def testAssertEqualsLxmlNodeOrTreeBothWork(self):
        # Same node, same parentage
        self.assertEqualsLxml(
            parseString('<x/>'),
            parseString('<x/>').getroot()
        )

        # Same node, different parentage
        self.assertEqualsLxml(
            parseString('<x/>'),
            parseString('<r><x/></r>').getroot().getchildren()[0]
        )

        # Root-siblings ONLY when root is at roottree/ElementTree level.
        self.checkAssertEqualsLxmlFails(
            parseString('<!-- Comment --><x/>'),
            parseString('<r><!-- Comment --><x/></r>').getroot().getchildren()[1],
            """\
Number of children not equal (expected -- result):
    comment|node -- 'x'
    'x' -- no|tag

At location: ''
=== expected (line 1) ===
1: <!-- Comment --><x/>
=== result (line 1) ===
1: <x/>
=======================
""", showContext=10)

        # Root-siblings ONLY when root is at roottree/ElementTree level.
        self.checkAssertEqualsLxmlFails(
            parseString('<x/><!-- Comment -->'),
            parseString('<r><x/><!-- Comment --></r>').getroot().getchildren()[0],
            """\
Number of children not equal (expected -- result):
    'x' -- 'x'
    comment|node -- no|tag

At location: ''""", showContext=False)

        # Root-siblings ONLY when root is at roottree/ElementTree level.
        self.checkAssertEqualsLxmlFails(
            parseString('<!-- Comment --><x/>'),
            parseString('<r><x/></r>').getroot().getchildren()[0],
            """\
Number of children not equal (expected -- result):
    comment|node -- 'x'
    'x' -- no|tag

At location: ''
=== expected (line 1) ===
1: <!-- Comment --><x/>
=== result (line 1) ===
1: <x/>
=======================
""", showContext=10)

    def testRefindLxmlNodeCallback(self):
        xml = '''\
<!-- pre1 -->
<!-- pre2 -->
<r>
  <sub xmlns="uri:1">
    <sub2 xmlns="uri:2">
      <s:sub3 xmlns:s="uri:1">
        <s:sub4 xmlns:s="uri:2">Different Text</s:sub4>
      </s:sub3>
      <n:notFirstChild xmlns:n="uri:n" />
    </sub2>
  </sub>
</r>
<?post?>
'''
        lxml1 = parseString(xml)
        lxml2 = parseString('\n\n' + xml)  # Different text, same tree

        pre1 = lxml1.getroot().getprevious().getprevious()
        pre2 = lxml1.getroot().getprevious()
        root1 = lxml1.getroot()
        sub4 = lxml1.getroot().getchildren()[0].getchildren()[0].getchildren()[0].getchildren()[0]
        sub3 = lxml1.getroot().getchildren()[0].getchildren()[0].getchildren()[0]
        notFirstChild = lxml1.getroot().getchildren()[0].getchildren()[0].getchildren()[1]
        post = lxml1.getroot().getnext()

        def assertPathEqual(node):
            refind = refindLxmlNodeCallback(lxml1, node)
            self.assertEqual(lxml1.getpath(node), lxml2.getpath(refind(lxml2)))

        assertPathEqual(root1)
        assertPathEqual(pre1)
        assertPathEqual(pre2)
        assertPathEqual(post)
        assertPathEqual(sub3)
        assertPathEqual(sub4)
        assertPathEqual(notFirstChild)

    def testAssertEqualsLxmlXpathsOkWithCompexNesting(self):
        def assertPathToTagOkInXml(xml, tagsWithPaths, namespaces=None):
            namespaces = namespaces if namespaces else {}
            lxml = parseString(xml)
            lxmlNode = lxml.getroot()
            compareXml = CompareXml(expectedNode=lxmlNode, resultNode=lxmlNode)

            for d in tagsWithPaths:
                tag, pathExc, pathIncl = d['tag'], d['excl'], d['incl']
                self.assertEqual(set(['tag', 'excl', 'incl']), set(d.keys()))
                t = lxmlNode.xpath('//%s' % tag, namespaces=namespaces)[0]
                self.assertEqual(pathExc, compareXml.xpathToHere(t, includeCurrent=False))
                self.assertEqual(pathIncl, compareXml.xpathToHere(t, includeCurrent=True))

        xml = '''\
<a>
    <b>
        <c/>
    </b>
    <b2>
        <c2>
            <d/>
        </c2>
        <c3/>
    </b2>
</a>'''
        assertPathToTagOkInXml(xml=xml, tagsWithPaths=[
            {'tag': 'a', 'excl': '', 'incl': 'a'},
            {'tag': 'b', 'excl': 'a', 'incl': 'a/b'},
            {'tag': 'c', 'excl': 'a/b', 'incl': 'a/b/c'},
            {'tag': 'b2', 'excl': 'a', 'incl': 'a/b2'},
            {'tag': 'c2', 'excl': 'a/b2', 'incl': 'a/b2/c2'},
            {'tag': 'd', 'excl': 'a/b2/c2', 'incl': 'a/b2/c2/d'},
            {'tag': 'c3', 'excl': 'a/b2', 'incl': 'a/b2/c3'}
        ])

        xml = '''\
<a>
    <b/>
    <b>
        <c>
            <c>ignored</c>
            <d/>
            <e>ignored</e>
        </c>
        <c>
            <e>ignored</e>
            <e/>
        </c>
    </b>
</a>'''
        assertPathToTagOkInXml(xml=xml, tagsWithPaths=[
            {'tag': 'b[1]', 'excl': 'a', 'incl': 'a/b[1]'},
            {'tag': 'b/c[1]', 'excl': 'a/b[2]', 'incl': 'a/b[2]/c[1]'},
            {'tag': 'd', 'excl': 'a/b[2]/c[1]', 'incl': 'a/b[2]/c[1]/d'},
            {'tag': 'b/c[2]', 'excl': 'a/b[2]', 'incl': 'a/b[2]/c[2]'},
            {'tag': 'b/c[2]/e[2]', 'excl': 'a/b[2]/c[2]', 'incl': 'a/b[2]/c[2]/e[2]'},
        ])

        xml = '''\
<a xmlns="a:a">
    <a xmlns="b:b"/>
    <a xmlns="b:b"/>
    <x:a xmlns:x="b:b">
        <x:a xmlns:x="c:c"/>
    </x:a>
</a>'''
        assertPathToTagOkInXml(xml=xml, tagsWithPaths=[
            {'tag': 'a:a', 'excl': '', 'incl': '{a:a}a'},
            {'tag': 'b:a[c:a]', 'excl': '{a:a}a', 'incl': '{a:a}a/{b:b}a[3]'},
            {'tag': 'b:a/c:a', 'excl': '{a:a}a/{b:b}a[3]', 'incl': '{a:a}a/{b:b}a[3]/{c:c}a'},
        ], namespaces={'a': 'a:a', 'b': 'b:b', 'c': 'c:c'})

    def testDepthFirst(self):
        self.checkAssertEqualsLxmlFails(
            parseString('<xml><a><b/><b/></a><a/></xml>'),
            parseString('<xml><a><c/></a><x/></xml>'),
            "Number of children not equal (expected -- result):\n    'b' -- 'c'\n    'b' -- no|tag\n\nAt location: 'xml/a[1]'")

        self.checkAssertEqualsLxmlFails(
            parseString('<xml><a><b/><b/></a><a/></xml>'),
            parseString('<xml><a><b/><c/><b/></a><a><x/></a></xml>'),
            "Number of children not equal (expected -- result):\n    'b' -- 'b'\n    'b' -- 'c'\n    no|tag -- 'b'\n\nAt location: 'xml/a[1]'")

    def testWSBetweenTagsIgnored(self):
        self.assertEqualsLxml(
            parseString('<xml><a><b></b></a></xml>'),
            parseString('<xml><a>\n   <b></b>\n</a></xml>'),
            )

    def testWSInLeafsMatter(self):
        self.checkAssertEqualsLxmlFails(
            parseString('<xml><a><b> </b></a></xml>'),
            parseString('<xml><a><b>   </b></a></xml>'),
            "Text difference: ' ' != '   '\nAt location: 'xml/a/b'")

    def testObjectsNeedToBeLxmlNodesOrTrees(self):
        expectedLxml = parseString('<ignored><root/></ignored>')
        resultLxml = parseString('<root/>')  # Tree

        expectedLxml = expectedLxml.xpath('root')[0]  # Node
        self.assertEqualsLxml(expected=expectedLxml, result=resultLxml)

        try:
            self.assertEqualsLxml('<root/>', resultLxml)
        except ValueError as e:
            self.assertEqual('Expected an Lxml Node- or Tree-like object, but got: "<root/>".', str(e))
        else:
            self.fail('Should not happen')

        try:
            o = object()
            self.assertEqualsLxml(expectedLxml, o)
        except ValueError as e:
            self.assertEqual('Expected an Lxml Node- or Tree-like object, but got: "%s".' % str(o), str(e))
        else:
            self.fail('Should not happen')

    def testAssertXmlEquals(self):
        self.assertXmlEquals('<x/>', '<x/>')
        self.assertRaises(AssertionError, lambda: self.assertXmlEquals('<x/>', '<y/>'))
        try:
            self.assertXmlEquals('<x xmlns="urn:a"/>', '<x xmlns="urn:b"/>')
        except AssertionError as e:
            self.assertTrue('-<x xmlns="urn:a"></x>\n+<x xmlns="urn:b"></x>' in str(e), str(e))
        else:
            self.fail()

    def testAssertDictEquals(self):
        self.assertDictEquals({'aap':'noot'}, dict(aap='noot'))
        try:
            self.assertDictEquals(dict(aap='noot'), dict(aap='note'))
            self.fail()
        except AssertionError as e:
            self.assertEqual("{'aap': 'noot'} != {'aap': 'note'}\n- {'aap': 'noot'}\n?            -\n\n+ {'aap': 'note'}\n?             +\n", str(e))

def parseString(s):
    return parse(StringIO(s))

COLOR_RE = re.compile(r'\033\[[^m]*m')
def stripColor(s):
    return COLOR_RE.sub('', s)
