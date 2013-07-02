## begin license ##
#
# "Seecr Test" provides test tools.
#
# Copyright (C) 2005-2009 Seek You Too (CQ2) http://www.cq2.nl
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

from seecr.test import SeecrTestCase

from StringIO import StringIO

# TODO:
#   lxmltostring stuff ...
from lxml.etree import parse, tostring, Comment

# whiteboxing:
from seecr.test.seecrtestcase import CompareXml


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
        # (root) tag - prefix diff
        self.checkAssertEqualsLxmlFails(
            parseString('<a:xml xmlns:a="urn:something" />'),
            parseString('<b:xml xmlns:b="urn:something" />'),
            "Prefix difference a != b for namespace: 'urn:something'\nAt location: '{urn:something}xml'")
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
        except AssertionError, e:
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

        self.assertEquals('{n:s/#}a', c.xpathToHere(_1st_inside))
        self.assertEquals('{n:s/#}a', c.xpathToHere(_2nd_inside))
        self.assertEquals('{n:s/#}a/comment()[1]', c.xpathToHere(_1st_inside, includeCurrent=True))
        self.assertEquals('{n:s/#}a/comment()[2]', c.xpathToHere(_2nd_inside, includeCurrent=True))

        self.assertEquals('', c.xpathToHere(_1st))
        self.assertEquals('', c.xpathToHere(_pre_root))
        self.assertEquals('comment()[1]', c.xpathToHere(_1st, includeCurrent=True))
        self.assertEquals('comment()[2]', c.xpathToHere(_pre_root, includeCurrent=True))

        self.assertEquals('', c.xpathToHere(_post_root))
        self.assertEquals('', c.xpathToHere(_last))
        self.assertEquals('comment()[3]', c.xpathToHere(_post_root, includeCurrent=True))
        self.assertEquals('comment()[4]', c.xpathToHere(_last, includeCurrent=True))

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

        self.assertEquals("{n:s/#}a", c.xpathToHere(_inside_1_php))
        self.assertEquals("{n:s/#}a", c.xpathToHere(_inside_2_notphp))
        self.assertEquals("{n:s/#}a", c.xpathToHere(_inside_3_php))
        self.assertEquals("{n:s/#}a/processing-instruction('php')[1]", c.xpathToHere(_inside_1_php, includeCurrent=True))
        self.assertEquals("{n:s/#}a/processing-instruction('notphp')", c.xpathToHere(_inside_2_notphp, includeCurrent=True))
        self.assertEquals("{n:s/#}a/processing-instruction('php')[2]", c.xpathToHere(_inside_3_php, includeCurrent=True))

        self.assertEquals("", c.xpathToHere(_pro_cessing))
        self.assertEquals("", c.xpathToHere(_xml_style))
        self.assertEquals("", c.xpathToHere(_pro_newline))
        self.assertEquals("processing-instruction('pro')[1]", c.xpathToHere(_pro_cessing, includeCurrent=True))
        self.assertEquals("processing-instruction('xml-stylesheet')", c.xpathToHere(_xml_style, includeCurrent=True))
        self.assertEquals("processing-instruction('pro')[2]", c.xpathToHere(_pro_newline, includeCurrent=True))

    def testTODO(self):
        self.fail('Finish TODO`s')
    # TODO:
    # - ... You can also pass the Element, Comment, ProcessingInstruction and
    #    Entity factory functions to look only for the specific element type. ... (<element>.iter*() functions).
    # - Add a context-diff (n-lines above and below the where the differences start to occur.

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

    def testAssertEqualsLxmlXpathsOkWithCompexNesting(self):
        def assertPathToTagOkInXml(xml, tagsWithPaths, namespaces=None):
            namespaces = namespaces if namespaces else {}
            lxml = parseString(xml)
            lxmlNode = lxml.getroot()
            compareXml = CompareXml(expectedNode=lxmlNode, resultNode=lxmlNode)

            for d in tagsWithPaths:
                tag, pathExc, pathIncl = d['tag'], d['excl'], d['incl']
                self.assertEquals(set(['tag', 'excl', 'incl']), set(d.keys()))
                t = lxmlNode.xpath('//%s' % tag, namespaces=namespaces)[0]
                self.assertEquals(pathExc, compareXml.xpathToHere(t, includeCurrent=False))
                self.assertEquals(pathIncl, compareXml.xpathToHere(t, includeCurrent=True))

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
        except ValueError, e:
            self.assertEquals('Expected an Lxml Node- or Tree-like object, but got: "<root/>".', str(e))
        else:
            self.fail('Should not happen')

        try:
            o = object()
            self.assertEqualsLxml(expectedLxml, o)
        except ValueError, e:
            self.assertEquals('Expected an Lxml Node- or Tree-like object, but got: "%s".' % str(o), str(e))
        else:
            self.fail('Should not happen')

    def testAssertDictEquals(self):
        self.assertDictEquals({'aap':'noot'}, dict(aap='noot'))


def parseString(s):
    return parse(StringIO(s))

