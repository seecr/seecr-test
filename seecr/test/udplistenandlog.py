## begin license ##
#
# "Seecr Test" provides test tools.
#
# Copyright (C) 2014 Seecr (Seek You Too B.V.) http://seecr.nl
#
# This file is part of "Seecr Test"
#
# "NBC+ (Zoekplatform BNL)" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "NBC+ (Zoekplatform BNL)" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "NBC+ (Zoekplatform BNL)"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR, SO_LINGER
from struct import pack
from threading import Thread

class UdpListenAndLog(object):
    def __init__(self, port):
        self._sok = createSocket(port)
        self._stop = False
        self._log = []
        thread = Thread(None, self._listenAndLog)
        thread.daemon = True
        thread.start()

    def _listenAndLog(self):
        while not self._stop:
            data, remote = self._sok.recvfrom(2048)
            self._log.append(data)

    def log(self):
        return self._log[:]

    def stop(self):
        self._stop = True

def createSocket(port):
    sok = socket(AF_INET, SOCK_DGRAM)
    sok.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sok.setsockopt(SOL_SOCKET, SO_LINGER, pack('ii', 0, 0))
    sok.bind(('0.0.0.0', port))
    return sok

