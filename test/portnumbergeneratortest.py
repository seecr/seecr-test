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

from unittest import TestCase

from seecr.test.portnumbergenerator import PortNumberGenerator

from socket import socket, SO_LINGER, SOL_SOCKET, SHUT_RDWR
from struct import pack

class PortNumberGeneratorTest(TestCase):
    def testReasonableAmountOfUniquePortNumbers(self):
        number = PortNumberGenerator.next()

        self.assertEquals(int, type(number))

        numbers = []
        # More than 14000 gets *very* slow or fails
        # When guaranteed uniqe numbers for that many ports are needed,
        # change the approach (say reading: cat /proc/net/tcp | awk '{print $2}' | sed -e '1d')
        for i in xrange(140):
            numbers.append(PortNumberGenerator.next())

        self.assertEquals(140, len(numbers))
        self.assertEquals(140, len(set(numbers)))
        self.assertEquals(True, all((0 <= n < 65536) for n in numbers))

    def testFindProblemWithLockupAfterReuseQuickly(self):
        nr = PortNumberGenerator.next()
        portsInUse = PortNumberGenerator._inUsePortForLocalAddresses()

        self.assertFalse(nr in portsInUse, portsInUse)

        sok = socket()
        sok.setsockopt(SOL_SOCKET, SO_LINGER, pack('ii', 1, 1))
        sok.bind(('127.0.0.1', nr))
        try:
            portsInUse = PortNumberGenerator._inUsePortForLocalAddresses()
            self.assertTrue(nr in portsInUse, '%s not in %s' % (nr, repr(portsInUse)))
        finally:
            sok.close()

