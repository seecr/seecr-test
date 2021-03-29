# -*- coding: utf-8 -*-
## begin license ##
#
# "Seecr Test" provides test tools.
#
# Copyright (C) 2012-2015, 2019-2021 Seecr (Seek You Too B.V.) https://seecr.nl
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

from seecr.test import SeecrTestCase, CallTrace

from seecr.test.io import stdout_replaced
from seecr.test.timing import T
from seecr.test.utils import ignoreLineNumbers, sleepWheel, parseHtmlAsXml, findTag, includeParentAndDeps, _parseData, mkdir, loadTestsFromPath, createReturnValue, assertHttpOK, postRequest
from lxml.etree import XMLSyntaxError

from time import time
from os import makedirs
from os.path import join, isdir


class UtilsTest(SeecrTestCase):
    def testIgnoreLineNumber(self):
        theTraceback = """Traceback (most recent call last):
  File "../some/file.py", line 104, in aFunction
    for _var  in vars:
  File "some/other/file.py", line 249, in anotherFuntion
    raise Exception('xcptn')
Exception: xcptn\n"""

        expected = """Traceback (most recent call last):
  File [file.py], line [#], in aFunction
    for _var  in vars:
  File [file.py], line [#], in anotherFuntion
    raise Exception('xcptn')
Exception: xcptn\n"""

        self.assertEqual(expected, ignoreLineNumbers(theTraceback))

    def testSleepWheelNoCallback(self):
        t0 = time()
        with stdout_replaced():
            retval = sleepWheel(0.01, interval=0.001)
        t1 = time()
        delta = t1 - t0
        self.assertTrue(0.01 < delta < max(0.02, (0.02 * T_ADJUSTMENT * T)), delta)
        self.assertEqual(False, retval)

    def testSleepWheelCallbackFalsy(self):
        calls = []
        def callback():
            calls.append(True)
        t0 = time()
        with stdout_replaced() as out:
            retval = sleepWheel(0.01, interval=0.001, callback=callback)
            t1 = time()
            self.assertEqual('\\\x08|\x08/\x08-\x08\\\x08|\x08/\x08-\x08\\\x08|\x08', out.getvalue())
        delta = t1 - t0
        self.assertTrue(0.01 < delta < max(0.02, (0.02 * T_ADJUSTMENT * T)), delta)
        self.assertEqual(10, len(calls))
        self.assertEqual(False, retval)

    def testSleepWheelCallbackTruthy(self):
        calls = []
        def callback():
            calls.append(True)
            return True
        t0 = time()
        with stdout_replaced() as out:
            retval = sleepWheel(0.01, interval=0.001, callback=callback)
            t1 = time()
            self.assertEqual('\\\x08', out.getvalue())
        delta = t1 - t0
        self.assertTrue(0.001 < delta < max(0.002, (0.002 * T_ADJUSTMENT * T)), delta)
        self.assertEqual(1, len(calls))
        self.assertEqual(True, retval)

    def testParseHtmlAsXml(self):
        with stdout_replaced():
            self.assertRaises(XMLSyntaxError, parseHtmlAsXml, b'<not xml>')
        result = parseHtmlAsXml(b'<html><body>&lsquo;to the left &larr;&rsquo;</body></html>')
        self.assertEqual(['‘to the left <-’'], result.xpath('/html/body/text()'))

    def testFindTag(self):
        self.assertEqual(1, len(list(findTag("input", b"<input></input>"))))
        self.assertEqual(1, len(list(findTag("input", b"<input />"))))
        self.assertEqual(1, len(list(findTag("input", b"<input/>"))))
        self.assertEqual(2, len(list(findTag("input", b"<form><input/><input></input></form>"))))
        self.assertEqual(2, len(list(findTag("input", b"<form><input attr='value'/><input></input></form>"))))
        self.assertEqual(2, len(list(findTag("input", b"<form><input></input><input/></form>"))))
        self.assertEqual(1, len(list(findTag("a", b"<a><img/></a>"))))
        self.assertEqual(1, len(list(findTag("a", b"<a>&euro;</a>"))))
        self.assertEqual(1, len(list(findTag("a", b"<html><a/><a class='test'>text</a></html>", **{"class": "test"}))))
        self.assertEqual(1, len(list(findTag("a", b"<html><a a='1' b='2'/><a a='1'/></html>", **dict(a=1, b=2)))))

    def testParseData(self):
        data = b"HTTP/1.1 200 Ok\r\nContent-Type: whatever\r\nother-header: value\r\n\r\ndata"
        statusAndHeaders, body = _parseData(data)
        self.assertEqual('200', statusAndHeaders["StatusCode"])
        self.assertEqual({'Content-Type': 'whatever', 'Other-Header': 'value'}, statusAndHeaders["Headers"])
        self.assertEqual(b'data', body)

    def testParseDataEmptyBody(self):
        data = b'HTTP/1.0 503 Service Temporarily Unavailable\r\n\r\n'
        statusAndHeaders, body = _parseData(data)
        self.assertEqual('503', statusAndHeaders["StatusCode"])
        self.assertEqual({}, statusAndHeaders["Headers"])
        self.assertEqual(b'', body)

    def testCreateReturnValue(self):
        data = b"HTTP/1.1 200 Ok\r\nContent-Type: whatever\r\nother-header: value\r\n\r\ndata"
        statusAndHeaders, body = createReturnValue(data, parse=True)
        self.assertEqual('200', statusAndHeaders["StatusCode"])
        self.assertEqual({'Content-Type': 'whatever', 'Other-Header': 'value'}, statusAndHeaders["Headers"])
        self.assertEqual(b'data', body)

        data = b"HTTP/1.1 200 Ok\r\nContent-Type: application/json\r\nother-header: value\r\n\r\n{\"key\": 42}"
        statusAndHeaders, body = createReturnValue(data, parse=True)
        self.assertEqual(dict(key=42), body)

        data = b"HTTP/1.1 200 Ok\r\nother-header: value\r\n\r\n<aap>noot</aap>"
        statusAndHeaders, body = createReturnValue(data, parse=True)
        self.assertEqual(['noot'], body.xpath('/aap/text()'))
        statusAndHeaders, body = createReturnValue(data, parse=False)
        self.assertEqual(b'<aap>noot</aap>', body)

        # Make a list if header appears more than once
        data = b"HTTP/1.1 200 Ok\r\nother-header: whatever\r\nother-header: value\r\n\r\ndata"
        statusAndHeaders, body = createReturnValue(data, parse=True)
        self.assertEqual({'Other-Header': ['whatever', 'value']}, statusAndHeaders["Headers"])

        # Set-Cookie is always a list
        data = b"HTTP/1.1 200 Ok\r\nSet-Cookie: whatever\r\n\r\ndata"
        statusAndHeaders, body = createReturnValue(data, parse=True)
        self.assertEqual({'Set-Cookie': ['whatever']}, statusAndHeaders["Headers"])


    def testMkdir(self):
        self.assertFalse(isdir(join(self.tempdir, "mkdir")))
        self.assertEqual(join(self.tempdir, "mkdir"), mkdir(self.tempdir, "mkdir"))
        self.assertTrue(isdir(join(self.tempdir, "mkdir")))

        self.assertFalse(isdir(join(self.tempdir, "1", "2", "3", "4")))
        mkdir(self.tempdir, "1", "2", "3", "4")
        self.assertTrue(isdir(join(self.tempdir, "1", "2", "3", "4")))

    def testLoadTestFromPath(self):
        g = {}
        loadTestsFromPath(self.tempdir, _globals=g)
        self.assertEqual({}, g)
        with open(join(self.tempdir, "sometest.py"), "w") as fp:
            fp.write(TEST_TEMPLATE)
        loadTestsFromPath(self.tempdir, _globals=g)
        self.assertTrue('SomeTest' in g, g)

    def testLoadTestFromPathSubDirs(self):
        with open(join(self.tempdir, "sometest.py"), "w") as fp:
            fp.write(TEST_TEMPLATE)

        with open(join(mkdir(self.tempdir, "sub"), "sometest.py"), "w") as fp:
            fp.write(TEST_TEMPLATE)

        g = {}
        loadTestsFromPath(self.tempdir, _globals=g)
        self.assertEqual(2, len(g))
        self.assertEqual({'sub.SomeTest', 'SomeTest'}, set(g.keys()))

    def testAssertHttpOK(self):
        headers = {'StatusCode': '302', 'Headers': {'Location': '/form'}}
        assertHttpOK(headers, '', expectedStatus=302)
        headers = {'StatusCode': '302', 'Headers': {'Location': '/form'}}
        assertHttpOK(headers, '', expectedStatus="302")
        try:
            headers = {'StatusCode': '200', 'Headers': {'Location': '/form'}}
            assertHttpOK(headers, '', expectedStatus=302)
        except AssertionError as e:
            self.assertEqual('HTTP Status code; expected 302, got 200', str(e))

        try:
            body = 'blah blah Traceback blah blah'
            assertHttpOK({'StatusCode': '302'}, body, expectedStatus=302)
        except AssertionError as e:
            self.assertEqual('Traceback found in body:\n{}'.format(body), str(e))

        try:
            body = b'blah blah Traceback blah blah'
            assertHttpOK({'StatusCode': '302'}, body, expectedStatus=302)
        except AssertionError as e:
            self.assertEqual('Traceback found in body', str(e))

    def testPostRequestWithCookie(self):
        mockSocket = self.createMockSocket([b'HTTP/1.1 200 Ok\r\nMy-Header: this\r\n\r\ndata'])
        headers, result = postRequest(12345,
                '/some/path',
                data=b'lekker, lekker',
                cookie='gevulde-koek',
                timeOutInSeconds=200,
                _createSocket=mockSocket.createSocket,
                parse=False)
        self.assertEqual(b'data', result)
        self.assertEqual({"StatusCode":'200', 'Headers':{"My-Header": 'this'}}, headers)
        self.assertEqual(['createSocket', 'send', 'recv', 'recv', 'close'], mockSocket.calledMethodNames())
        create, send = mockSocket.calledMethods[:2]
        self.assertEqual((12345, 200), create.args)
        self.assertEqual('''POST /some/path HTTP/1.0
Content-Length: 14
Content-Type: text/xml; charset="utf-8"
Cookie: gevulde-koek

lekker, lekker''', send.args[0].decode().replace('\r\n','\n'))


    def createMockSocket(self, responses):
        def recv(*args):
            return responses.pop() if len(responses) else None
        mockSocket = CallTrace(returnValues={'close':None}, methods=dict(send=lambda data: len(data), recv=recv))
        mockSocket.returnValues['createSocket'] = mockSocket
        mockSocket.methods['send'] = lambda data: len(data)
        return mockSocket



TEST_TEMPLATE = """from seecr.test import SeecrTestCase
class SomeTest(SeecrTestCase):
    def testOne(self):
        pass"""

T_ADJUSTMENT = 1.5
