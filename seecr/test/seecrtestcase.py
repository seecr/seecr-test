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

from unittest import TestCase
from string import whitespace
from tempfile import mkdtemp, mkstemp
from shutil import rmtree
from timing import T
from sys import path as systemPath
from os import getenv, close as osClose, remove, getpid
from os.path import join, isfile, realpath, abspath
from itertools import izip_longest


XPATH_IS_ONE_BASED = 1


class SeecrTestCase(TestCase):

    def setUp(self):
        TestCase.setUp(self)
        self.tempdir = mkdtemp()
        fd, self.tempfile = mkstemp()
        osClose(fd)
        self.vmsize = self._getVmSize()

    def tearDown(self):
        rmtree(self.tempdir)
        remove(self.tempfile)
        TestCase.tearDown(self)

    def assertTiming(self, t0, t, t1):
        self.assertTrue(t0*T < t < t1*T, t/T)

    def select(self, aString, index):
        while index < len(aString):
            char = aString[index]
            index = index + 1
            if not char in whitespace:
                return char, index
        return '', index

    def cursor(self, aString, index):
        return aString[:index - 1] + "---->" + aString[index - 1:]

    def assertEqualsWS(self, s1, s2):
        index1 = 0
        index2 = 0
        while True:
            char1, index1 = self.select(s1, index1)
            char2, index2 = self.select(s2, index2)
            if char1 != char2:
                self.fail('%s != %s' % (self.cursor(s1, index1), self.cursor(s2, index2)))
            if not char1 or not char2:
                break

    def assertEqualsLxml(self, expected, result):
        expectedNode = getattr(expected, 'getroot', lambda: expected)()
        resultNode = getattr(result, 'getroot', lambda: result)()

        if not getattr(expectedNode, 'getroottree', False):
            raise ValueError('Expected an Lxml Node- or Tree-like object, but got: "%s".' % str(expectedNode))
        if not getattr(resultNode, 'getroottree', False):
            raise ValueError('Expected an Lxml Node- or Tree-like object, but got: "%s".' % str(resultNode))

        toVerify = [(expectedNode, resultNode)]
        compare = CompareXml(
            expectedNode=expectedNode,
            resultNode=resultNode,
            remainingContainer=toVerify
        )

        while toVerify:
            expectedNode, resultNode = toVerify.pop()
            compare.compareNode(expectedNode, resultNode)

    def _getVmSize(self):
        status = open('/proc/%d/status' % getpid()).read()
        i = status.find('VmSize:') + len('VmSize:')
        j = status.find('kB', i)
        vmsize = int(status[i:j].strip())
        return vmsize

    def assertNoMemoryLeaks(self, bandwidth=0.8):
        vmsize = self._getVmSize()
        self.assertTrue(self.vmsize*bandwidth < vmsize < self.vmsize/bandwidth,
                "memory leaking: before: %d, after: %d" % (self.vmsize, vmsize))


    @staticmethod
    def binPath(executable):
        allPath = [join(p, 'bin') for p in systemPath]
        if getenv('SEECRTEST_USR_BIN'):
            allPath.append(getenv('SEECRTEST_USR_BIN'))
        allPath.append('/usr/bin')
        for path in allPath:
            executablePath = join(path, executable)
            if isfile(executablePath):
                return realpath(abspath(executablePath))
        raise ValueError("No executable found for '%s'" % executable)


class CompareXml(object):
    def __init__(self, expectedNode, resultNode, remainingContainer):
        self._expectedNode = expectedNode
        self._resultNode = resultNode
        self._remainingContainer = remainingContainer

    def compareNode(self, expectedNode, resultNode):
        if expectedNode.tag != resultNode.tag:
            raise AssertionError("Tags do not match '%s' != '%s' at location: '%s'" % (expectedNode.tag, resultNode.tag, self.xpathToHere(expectedNode)))

        if expectedNode.text != resultNode.text:
            raise AssertionError("Text difference: %s != %s\nAt location: '%s'" % (
                '>no|text<' if expectedNode.text is None else "'" + expectedNode.text + "'",
                '>no|text<' if resultNode.text is None else "'" + resultNode.text + "'",
                self.xpathToHere(expectedNode, includeCurrent=True)
            ))

        if expectedNode.tail != resultNode.tail:
            raise AssertionError("Tail difference (text after closing of tag): %s != %s\nAt location: '%s'" % (
                '>no|tail<' if expectedNode.tail is None else "'" + expectedNode.tail + "'",
                '>no|tail<' if resultNode.tail is None else "'" + resultNode.tail + "'",
                self.xpathToHere(expectedNode, includeCurrent=True)
            ))

        expectedAttrs = expectedNode.attrib
        expectedAttrsSet = set(expectedAttrs.keys())
        resultAttrs = resultNode.attrib
        resultAttrsSet = set(resultAttrs.keys())

        diff = expectedAttrsSet.difference(resultAttrsSet)
        if diff:
            raise AssertionError("Missing attributes %s at location: '%s'" % (
                    ', '.join(
                        (("'%s'" % a) for a in diff)), 
                        self.xpathToHere(expectedNode, includeCurrent=True)
                ))
        diff = resultAttrsSet.difference(expectedAttrsSet)
        if diff:
            raise AssertionError("Unexpected attributes %s at location: '%s'" % (
                    ', '.join(
                        (("'%s'" % a) for a in diff)), 
                        self.xpathToHere(expectedNode, includeCurrent=True)
                ))

        for attrName, expectedAttrValue in expectedAttrs.items():
            resultAttrValue = resultAttrs[attrName]
            if expectedAttrValue != resultAttrValue:
                raise AssertionError("Attribute '%s' has a different value ('%s' != '%s') at location: '%s'" % (attrName, expectedAttrValue, resultAttrValue, self.xpathToHere(expectedNode, includeCurrent=True)))

        expectedChildren = expectedNode.getchildren()
        resultChildren = resultNode.getchildren()
        if len(expectedChildren) != len(resultChildren):
            tagsLandR = [
                (getattr(x, 'tag', None), getattr(r, 'tag', None))
                for x, r in izip_longest(expectedChildren, resultChildren)
            ]
            tagsLandR = [
                (x and "'%s'" % x or 'no|tag',
                 r and "'%s'" % r or 'no|tag')
                for x,r in tagsLandR
            ]
            tagsLandR = '\n'.join([
                '    %s -- %s' % (x, r)
                 for x, r in tagsLandR
            ])
            raise AssertionError("Number of children not equal (expected -- result):\n%s\n\nAt location: '%s'" % (tagsLandR, self.xpathToHere(expectedNode, includeCurrent=True)))

        self._remainingContainer.extend(zip(expectedChildren, resultChildren))

    def xpathToHere(self, node, includeCurrent=False):
        path = []
        startNode = node
        while node != self._expectedNode:
            node = node.getparent()
            path.insert(0, self._currentPointInTreeElementXpath(node))

        if includeCurrent:
            path.append(self._currentPointInTreeElementXpath(startNode))

        return '/'.join(path)

    def _currentPointInTreeElementXpath(self, node):
        nodeTag = node.tag
        if node == self._expectedNode:
            return nodeTag

        othersWithsameTagCount = 0
        for i, n in enumerate(node.getparent().iterfind(nodeTag)):
            if n == node:
                nodeIndex = i + XPATH_IS_ONE_BASED
            else:
                othersWithsameTagCount += 1

        return '%s[%s]' % (nodeTag, nodeIndex) if othersWithsameTagCount else nodeTag

