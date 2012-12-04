from unittest import TestCase

from seecr.test.mockserver import MockServer
from seecr.test.portnumbergenerator import PortNumberGenerator

from time import time
from urllib2 import urlopen, HTTPError, URLError

class MockServerTest(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.ms = MockServer(port=PortNumberGenerator.next())

    def testResponse(self):
        self.ms.response = 'HTTP/1.0 200 OK\r\n\r\nRe-Sponsed.'
        self.ms.start()

        self.assertEquals([], self.ms.requests)
        self.assertEquals('Re-Sponsed.', urlopen(self.ms.myUrl).read())
        self.assertEquals('Re-Sponsed.', urlopen(self.ms.myUrl).read())
        self.assertEquals(2, len(self.ms.requests))
        self.assertTrue('User-Agent: Python-urllib' in self.ms.requests[0], self.ms.requests[0])
        self.assertTrue('GET / HTTP/1.1\r\n' in self.ms.requests[0], self.ms.requests[0])

    def testResponses(self):
        self.ms.responses = ['HTTP/1.0 200 OK\r\n\r\nRe-Sponsed.', 'HTTP/1.0 200 OK\r\n\r\nAnother-Sponsed.']
        self.ms.start()

        self.assertEquals('Re-Sponsed.', urlopen(self.ms.myUrl).read())
        self.assertEquals('Another-Sponsed.', urlopen(self.ms.myUrl).read())
        self.assertRaises(HTTPError, lambda: urlopen(self.ms.myUrl).read())
        self.assertEquals(3, len(self.ms.requests))

    def testHangupConnectionTimeout(self):
        self.ms = MockServer(port=PortNumberGenerator.next(), hangupConnectionTimeout=0.1)
        self.ms.start()

        t0 = time()
        self.assertRaises(URLError, lambda: urlopen(self.ms.myUrl).read())
        t1 = time()
        delta = t1 - t0
        self.assertTrue(0.09 < delta < 0.12)
        self.assertEquals(0, len(self.ms.requests))

    def tearDown(self):
        self.ms.halt = True
        TestCase.tearDown(self)
