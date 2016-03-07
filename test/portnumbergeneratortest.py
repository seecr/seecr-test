## begin license ##
#
# "Seecr Test" provides test tools.
#
# Copyright (C) 2012, 2016 Seecr (Seek You Too B.V.) http://seecr.nl
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
from inspect import currentframe
from socket import socket, SO_LINGER, SO_REUSEADDR, SOL_SOCKET, SOCK_STREAM, SOCK_DGRAM, IPPROTO_TCP, IPPROTO_UDP, AF_INET

from struct import pack

from seecr.test.portnumbergenerator import PortNumberGenerator, has_dual_stack, attemptBinding


class PortNumberGeneratorTest(TestCase):
    def tearDown(self):
        PortNumberGenerator.clear()
        TestCase.tearDown(self)

    def testReasonableAmountOfUniquePortNumbers(self):
        number = PortNumberGenerator.next()

        self.assertEquals(int, type(number))

        numbers = []
        # More than 14000 gets *very* slow or fails
        # When guaranteed uniqe numbers for that many ports are needed,
        # change the approach (say reading: cat /proc/net/tcp | awk '{print $2}' | sed -e '1d')
        for i in xrange(14000):
            numbers.append(PortNumberGenerator.next())

        self.assertEquals(14000, len(numbers))
        self.assertEquals(14000, len(set(numbers)))
        self.assertEquals(True, all((0 <= n < 65536) for n in numbers))

    def testFindProblemWithLockupAfterReuseQuickly(self):
        soks = []
        try:
            for i in range(10):
                for j in xrange(950):
                    nr = PortNumberGenerator.next()
                    sok = socket()
                    sok.setsockopt(SOL_SOCKET, SO_LINGER, pack('ii', 1, 1))
                    sok.bind(('127.0.0.1', nr))
                    soks.append(sok)
                else:
                    # To prevent needing to raise ulimit's for open files
                    for s in reversed(soks):
                        s.close()
                        soks.remove(s)
        except Exception:
            for s in reversed(soks):
                s.close()
                soks.remove(s)
            raise  # "[Errno 98] Address already in use" when misimplemented

    def testClaimBlockOfPortNumbers(self):
        ports = []
        for i in xrange(20):
            p = PortNumberGenerator.next(blockSize=3)
            self.assertTrue(p in PortNumberGenerator._usedPorts)
            self.assertTrue((p + 1) in PortNumberGenerator._usedPorts)
            self.assertTrue((p + 2) in PortNumberGenerator._usedPorts)
            ports.append(p)
        self.assertEquals(20, len(ports))

    def testBlockSizeMustBePositive(self):
        self.assertRaises(ValueError, lambda: PortNumberGenerator.next(blockSize=0))
        self.assertRaises(ValueError, lambda: PortNumberGenerator.next(blockSize=-1))
        PortNumberGenerator.next(blockSize=1)

    def testBindPortNumbersGeneratedV4(self):
        p = PortNumberGenerator.next(bind=True)
        self.assertTrue(0 < p < 65536)
        for reuse in [True, False]:
            self.assertNotBound(bindV4(ip='127.0.0.1', port=p, protocol='tcp', reuse=reuse))
            self.assertNotBound(bindV4(ip='127.0.0.1', port=p, protocol='udp', reuse=reuse))
            self.assertNotBound(bindV4(ip='0.0.0.0', port=p, protocol='tcp', reuse=reuse))
            self.assertNotBound(bindV4(ip='0.0.0.0', port=p, protocol='udp', reuse=reuse))

    def testBindPortNumbersGenerated_withBlockSize_V4(self):
        blockSize = 3
        p = PortNumberGenerator.next(bind=True, blockSize=blockSize)

        for consequative_p in range(p, p + blockSize):
            for reuse in [False, True]:
                self.assertNotBound(bindV4(ip='127.0.0.1', port=consequative_p, protocol='tcp', reuse=reuse))
                self.assertNotBound(bindV4(ip='127.0.0.1', port=consequative_p, protocol='udp', reuse=reuse))
                self.assertNotBound(bindV4(ip='0.0.0.0', port=consequative_p, protocol='tcp', reuse=reuse))
                self.assertNotBound(bindV4(ip='0.0.0.0', port=consequative_p, protocol='udp', reuse=reuse))

    def testBindPortNumberGiven(self):
        port, close = attemptBinding(bindPort=0); close()
        PortNumberGenerator.bind(port=port)
        self.assertNotBound(bindV4(ip='127.0.0.1', port=port, protocol='tcp', reuse=True))
        if has_dual_stack():
            self.assertNotBound(bindV6(ip='::1', port=port, protocol='tcp', reuse=True))

        PortNumberGenerator.unbind(port=port)
        self.assertBoundAndUnbind(bindV4(ip='127.0.0.1', port=port, protocol='tcp', reuse=True))
        if has_dual_stack():
            self.assertBoundAndUnbind(bindV6(ip='::1', port=port, protocol='tcp', reuse=True))

    def testBindPortRangeNumberGiven(self):
        port = PortNumberGenerator.next(blockSize=2)
        port2 = port + 1
        PortNumberGenerator.bind(port=port, blockSize=2)
        self.assertNotBound(bindV4(ip='127.0.0.1', port=port, protocol='tcp', reuse=True))
        self.assertNotBound(bindV4(ip='127.0.0.1', port=port2, protocol='tcp', reuse=True))

        PortNumberGenerator.unbind(port=port, blockSize=2)
        self.assertBoundAndUnbind(bindV4(ip='127.0.0.1', port=port, protocol='tcp', reuse=True))
        self.assertBoundAndUnbind(bindV4(ip='127.0.0.1', port=port2, protocol='tcp', reuse=True))

    def testBindPortNumberGivenIgnoresUsedPorts(self):
        port = PortNumberGenerator.next()
        PortNumberGenerator.bind(port)
        self.assertNotBound(bindV4(ip='127.0.0.1', port=port, protocol='tcp', reuse=True))

    def testBindPortNumberGivenKeepsOldUsedPortsOnFailure(self):
        port1 = PortNumberGenerator.next()
        port2 = PortNumberGenerator.next(blockSize=2)
        port3 = port2 + 1
        PortNumberGenerator.bind(port3)

        # Overlap with already bind port: port3.
        self.assertEquals(set([port1, port2, port3]), PortNumberGenerator._usedPorts)
        self.assertEquals(set([port3]), set(PortNumberGenerator._bound.keys()))
        try:
            PortNumberGenerator.bind(port2, blockSize=2)
        except RuntimeError, e:
            self.assertEquals('Port(s) already bound', str(e))
        else: self.fail()

        self.assertEquals(set([port1, port2, port3]), PortNumberGenerator._usedPorts)
        self.assertEquals(set([port3]), set(PortNumberGenerator._bound.keys()))

        # Overlap with bound port: port3.
        PortNumberGenerator.unbind(port=port3)
        _port, close = attemptBinding(bindPort=port3)
        self.assertTrue(_port)
        self.assertEquals(set(), set(PortNumberGenerator._bound.keys()))
        try:
            PortNumberGenerator.bind(port2, blockSize=2)
        except RuntimeError, e:
            self.assertEquals('Port(s) are not free!', str(e))
        else: self.fail()

        self.assertEquals(set([port1, port2, port3]), PortNumberGenerator._usedPorts)
        self.assertEquals(set(), set(PortNumberGenerator._bound.keys()))
        close()                 # Cleanup

    def testUnbindPortNumberV4(self):
        p = PortNumberGenerator.next(bind=True)
        self.assertNotBound(bindV4(ip='127.0.0.1', port=p, protocol='tcp', reuse=True))

        PortNumberGenerator.unbind(port=p)
        self.assertBoundAndUnbind(bindV4(ip='127.0.0.1', port=p, protocol='tcp', reuse=False))
        self.assertBoundAndUnbind(bindV4(ip='127.0.0.1', port=p, protocol='tcp', reuse=False)) # Same IP-version, protocol, host, port combination: basically testing bindV4's close happened.
        self.assertBoundAndUnbind(bindV4(ip='127.0.0.1', port=p, protocol='udp', reuse=False))
        self.assertBoundAndUnbind(bindV4(ip='0.0.0.0', port=p, protocol='tcp', reuse=False))
        self.assertBoundAndUnbind(bindV4(ip='0.0.0.0', port=p, protocol='udp', reuse=False))

    def testBindPortNumbersGeneratedV6(self):
        if not has_dual_stack():
            return printDualStackSkipped()

        p = PortNumberGenerator.next(bind=True)
        self.assertTrue(0 < p < 65536)
        for protocol in ['tcp', 'udp']:
            for reuse in [True, False]:
                self.assertNotBound(bindV4(ip='127.0.0.1', port=p, protocol=protocol, reuse=reuse))
                self.assertNotBound(bindV4(ip='0.0.0.0', port=p, protocol=protocol, reuse=reuse))
                self.assertNotBound(bindV6(ip='::1', port=p, protocol=protocol, reuse=reuse))
                self.assertNotBound(bindV6(ip='::', port=p, protocol=protocol, reuse=reuse))
                self.assertNotBound(bindV6(ip='::1', port=p, protocol=protocol, reuse=reuse, ipV6Only=False))
                self.assertNotBound(bindV6(ip='::', port=p, protocol=protocol, reuse=reuse, ipV6Only=False))

    def testBindPortNumbersGenerated_withBlockSize_V6(self):
        if not has_dual_stack():
            return printDualStackSkipped()

        blockSize = 3
        p = PortNumberGenerator.next(bind=True, blockSize=blockSize)

        for consequative_p in range(p, p + blockSize):
            for protocol in ['tcp', 'udp']:
                for reuse in [False, True]:
                    self.assertNotBound(bindV4(ip='127.0.0.1', port=consequative_p, protocol=protocol, reuse=reuse))
                    self.assertNotBound(bindV4(ip='0.0.0.0', port=consequative_p, protocol=protocol, reuse=reuse))
                    self.assertNotBound(bindV6(ip='::1', port=consequative_p, protocol=protocol, reuse=reuse))
                    self.assertNotBound(bindV6(ip='::', port=consequative_p, protocol=protocol, reuse=reuse))
                    self.assertNotBound(bindV6(ip='::1', port=consequative_p, protocol=protocol, reuse=reuse, ipV6Only=False))
                    self.assertNotBound(bindV6(ip='::', port=consequative_p, protocol=protocol, reuse=reuse, ipV6Only=False))

    def testUnbindPortNumberV6(self):
        if not has_dual_stack():
            return printDualStackSkipped()

        p = PortNumberGenerator.next(bind=True)
        self.assertNotBound(bindV4(ip='::1', port=p, protocol='tcp', reuse=True))

        PortNumberGenerator.unbind(port=p)

        self.assertBoundAndUnbind(bindV6(ip='::1', port=p, protocol='tcp', reuse=False)) # Same IP-version, protocol, host, port combination: basically testing bindV6's close happened.
        for protocol in ['tcp', 'udp']:
            self.assertBoundAndUnbind(bindV4(ip='127.0.0.1', port=p, protocol=protocol, reuse=False))
            self.assertBoundAndUnbind(bindV4(ip='0.0.0.0', port=p, protocol=protocol, reuse=False))
            self.assertBoundAndUnbind(bindV6(ip='::1', port=p, protocol=protocol, reuse=False))
            self.assertBoundAndUnbind(bindV6(ip='::', port=p, protocol=protocol, reuse=False))
            self.assertBoundAndUnbind(bindV6(ip='::1', port=p, protocol=protocol, reuse=False, ipV6Only=False))
            self.assertBoundAndUnbind(bindV6(ip='::', port=p, protocol=protocol, reuse=False, ipV6Only=False))

    def testUnbindUnboundPortNumber(self):
        PortNumberGenerator.unbind(port=4321)

    def testClear(self):
        ports = []
        ports.append(PortNumberGenerator.next())
        _p = PortNumberGenerator.next(blockSize=2)
        ports.extend([_p, _p + 1])
        aBoundPort = PortNumberGenerator.next(bind=True)
        ports.append(aBoundPort)
        _p = PortNumberGenerator.next(blockSize=2, bind=True)
        ports.extend([_p, _p + 1])

        self.assertEquals(6, len(ports))
        self.assertEquals(set(ports), PortNumberGenerator._usedPorts)
        reservationKeys = PortNumberGenerator._bound.keys()
        self.assertEquals(3, len(reservationKeys))
        self.assertTrue(set(reservationKeys).issubset(set(ports)))
        self.assertNotBound(bindV4(ip='127.0.0.1', port=aBoundPort, protocol='tcp', reuse=False))

        PortNumberGenerator.clear()

        self.assertEquals(0, len(PortNumberGenerator._usedPorts))
        reservationKeys = PortNumberGenerator._bound.keys()
        self.assertEquals(0, len(reservationKeys))
        self.assertBoundAndUnbind(bindV4(ip='127.0.0.1', port=aBoundPort, protocol='tcp', reuse=False))

    ## helpers ##
    def assertNotBound(self, bindResult):
        self.assertEquals((None, None), bindResult)

    def assertBoundAndUnbind(self, bindResult):
        sok, boundPort = bindResult
        if sok is not None:
            sok.close()
        self.assertNotEquals((None, None), bindResult)


def bindV4(ip, port, protocol, reuse=False):
    """
    Binds to a ip, port, protocol combination given - where protocol is the string 'tcp' or 'udp'.
    Returns boundSok, boundPort

    boundPort only useful when binding to port 0.
    """
    if protocol == 'tcp':
        sok = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)
    elif protocol == 'udp':
        sok = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
    else:
        raise AssertionError('Bad protocol for tests: either "tcp" or "udp".')

    sok.setsockopt(SOL_SOCKET, SO_LINGER, pack('ii', 0, 0))
    sok.setsockopt(SOL_SOCKET, SO_REUSEADDR, (1 if reuse else 0))
    try:
        sok.bind((ip, port))
    except IOError:
        return None, None
    else:
        _host, boundPort = sok.getsockname()
        return sok, boundPort

def printDualStackSkipped():
    test_f = currentframe().f_back
    testClassName = test_f.f_locals['self'].__class__.__name__
    testFuncName = test_f.f_code.co_name
    sys.stderr.write('Skipped (no Dual-Stack support): %s.%s\n' % (testClassName, testFuncName))

if has_dual_stack():
    from socket import AF_INET6, IPPROTO_IPV6, IPV6_V6ONLY

    def bindV6(ip, port, protocol, reuse=False, ipV6Only=True):
        """
        Binds to a ip, port, protocol combination given - where protocol is the string 'tcp' or 'udp'.
        When ipV6Only is False, binds on both IPv4 and IPv6 versions of the address.
        Returns boundSok, boundPort

        boundPort only useful when binding to port 0.
        """
        if protocol == 'tcp':
            sok = socket(AF_INET6, SOCK_STREAM, IPPROTO_TCP)
        elif protocol == 'udp':
            sok = socket(AF_INET6, SOCK_DGRAM, IPPROTO_UDP)
        else:
            raise AssertionError('Bad protocol for tests: either "tcp" or "udp".')

        sok.setsockopt(IPPROTO_IPV6, IPV6_V6ONLY, (1 if ipV6Only else 0))
        sok.setsockopt(SOL_SOCKET, SO_LINGER, pack('ii', 0, 0))
        sok.setsockopt(SOL_SOCKET, SO_REUSEADDR, (1 if reuse else 0))
        try:
            sok.bind((ip, port, 0, 0))
        except IOError:
            return None, None
        else:
            _host, boundPort, _flowInfo, _scopeId = sok.getsockname()
            return sok, boundPort
