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

from socket import socket, SO_LINGER, SOL_SOCKET, SO_REUSEADDR
from struct import pack
from time import sleep

from itertools import cycle
from random import choice


class PortNumberGenerator(object):
    _ephemeralPortLow, _ephemeralPortHigh = [int(p) for p in open('/proc/sys/net/ipv4/ip_local_port_range', 'r').read().strip().split('\t', 1)]  # low\thigh
    _usedPorts = set([])
    _ephemeralPorts = set(range(_ephemeralPortLow, _ephemeralPortHigh + 1))

    @classmethod
    def next(cls):
        portsInUse = cls._inUsePortForLocalAddresses()
        forbiddenPorts = cls._usedPorts.union(portsInUse)
        usablePorts = cls._ephemeralPorts.difference(forbiddenPorts)

        chosenPort = choice(list(usablePorts))
        cls._usedPorts.add(chosenPort)
        return chosenPort
    #raise RuntimeError('Not been able to get an new uniqe free port within a reasonable amount (%s) of tries.' % cls._maxTries)

    @classmethod
    def _inUsePortForLocalAddresses(cls):
        ipv4TcpLocalPorts = portsForProcNetTcpFile("/proc/net/tcp")
        ipv6TcpLocalPorts = portsForProcNetTcpFile("/proc/net/tcp6")
        ipv4UdpLocalPorts = portsForProcNetTcpFile("/proc/net/udp")
        ipv6UdpLocalPorts = portsForProcNetTcpFile("/proc/net/udp6")
        return ipv4TcpLocalPorts.union(ipv6TcpLocalPorts).union(ipv4UdpLocalPorts).union(ipv6UdpLocalPorts)

def portsForProcNetTcpFile(filePath):
    ports = set([])
    for i, line in enumerate(open(filePath)):
        # Line structure, space(s) separated:
        # sl  local_address rem_address   st tx_queue rx_queue tr tm->when retrnsmt   uid  timeout inode
        # 0: 00000000:006F 00000000:0000 0A 00000000:00000000 00:00000000 00000000     0        0 3441 1 ffff88007d7b8000 300 0 0 2 -1
        if i == 0:
            continue
        _localIP, localPortHex = line.strip().split()[1].split(':')
        localPort = int(localPortHex, 16)
        ports.add(localPort)
    return ports

