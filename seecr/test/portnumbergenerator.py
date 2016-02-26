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

from copy import copy
from socket import socket, SO_LINGER, SOL_SOCKET, SO_REUSEADDR
from struct import pack


class PortNumberGenerator(object):
    _ephemeralPortLow, _ephemeralPortHigh = [int(p) for p in open('/proc/sys/net/ipv4/ip_local_port_range', 'r').read().strip().split('\t', 1)]  # low\thigh
    # TODO: read & exclude ip_local_reserved_ports; see: http://www.mjmwired.net/kernel/Documentation/networking/ip-sysctl.txt#774
    # TODO: detect non-dual stack impl and either FIX or FAIL; FAIL easier in the short term...
    _maxTries = (_ephemeralPortHigh - _ephemeralPortLow) / 2
    _usedPorts = set([])
    _reservations = {}

    @classmethod
    def next(cls, blockSize=1, reserve=False):
        blockSize = int(blockSize)
        if blockSize < 1:
            raise ValueError('blockSize smaller than 1')  # FIXME: Testme!

        for i in xrange(cls._maxTries):
            port, reservations = attemptEphemeralBindings(
                blockSize=blockSize,
                reserve=reserve,
                blacklistedPorts=cls._usedPorts)
            if port:
                cls._usedPorts.update(set(range(port, port + blockSize)))
                return port

            continue

        raise RuntimeError('Not been able to get an new uniqe free port within a reasonable amount (%s) of tries.' % cls._maxTries)


def attemptEphemeralBindings(blockSize, reserve, blacklistedPorts=None):
    """
    Returns port and reservations if succesful; otherwise all None's.

    port:
        First port (of consequative ports iff blockSize > 1).
    reservations:
        Dictionary of port-numbers to bond socket objects (.close() to release the "reservation") - if reserve is False, empty.
    """
    blacklistedPorts = set() if blacklistedPorts is None else blacklistedPorts

    port = None
    portNumberToBind = 0
    togo = blockSize
    reservations = {}
    # togo > 0; but called quite often, so a quicker check.
    while togo is not 0:
        # portNumberToBind > 0; but called quite often, so a quicker check.
        if portNumberToBind is not 0 and portNumberToBind in blacklistedPorts:
            return None, None

        aPort, sok = attemptBinding(port=portNumberToBind)

        if aPort is None:
            return None, None
        elif aPort in blacklistedPorts:
            sok.close()
            return None, None

        if reserve is True:
            reservations[aPort] = sok

        if port is None:
            portNumberToBind = port = aPort
        portNumberToBind += 1
        togo -= 1

    return port, []  # TODO: reservations!


def attemptBinding(port):
     sok = socket()
     sok.setsockopt(SOL_SOCKET, SO_LINGER, pack('ii', 0, 0))
     sok.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
     try:
         sok.bind(('127.0.0.1', port))
     except IOError, e:
         if port is 0:
             raise
         return None, None

     # Not needed when port != 0; but still *quicker* than testing port and returning it in Python.
     ignoredHost, aPort = sok.getsockname()

     return aPort, sok
