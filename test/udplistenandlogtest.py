## begin license ##
#
# "Seecr Test" provides test tools.
#
# Copyright (C) 2014, 2019-2021 Seecr (Seek You Too B.V.) https://seecr.nl
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
from socket import socket, AF_INET, SOCK_DGRAM
from time import sleep

from seecr.test.portnumbergenerator import PortNumberGenerator
from seecr.test.udplistenandlog import UdpListenAndLog

class UdpListenAndLogTest(TestCase):

    def testListenAndLog(self):
        port = PortNumberGenerator.next()
        ulal = UdpListenAndLog(port)

        with socket(AF_INET, SOCK_DGRAM) as s:
            s.sendto(b"THIS IS THE PAYLOAD", ('127.0.0.1', port))
            sleep(.5)

        self.assertEqual([b'THIS IS THE PAYLOAD'], ulal.log())
        ulal.stop()

    def testResetLog(self):
        port = PortNumberGenerator.next()
        ulal = UdpListenAndLog(port)

        with socket(AF_INET, SOCK_DGRAM) as s:
            s.sendto(b"THIS IS THE PAYLOAD", ('127.0.0.1', port))
            sleep(.5)

        self.assertEqual(1, len(ulal.log()))
        ulal.reset()
        self.assertEqual(0, len(ulal.log()))
        with socket(AF_INET, SOCK_DGRAM) as s:
            s.sendto(b"THIS IS THE PAYLOAD", ('127.0.0.1', port))
            sleep(.5)
        self.assertEqual(1, len(ulal.log()))

        ulal.stop()
