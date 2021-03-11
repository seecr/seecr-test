## begin license ##
#
# "Seecr Test" provides test tools.
#
# Copyright (C) 2012-2015, 2018 Seecr (Seek You Too B.V.) http://seecr.nl
# Copyright (C) 2012-2014 Stichting Bibliotheek.nl (BNL) http://www.bibliotheek.nl
# Copyright (C) 2015 Koninklijke Bibliotheek (KB) http://www.kb.nl
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

from time import sleep
import sys
from simplejson import dumps

from seecr.test.mockserver import MockServer
from meresco.components.http.utils import Ok, CRLF
from urllib.parse import parse_qs


class MockAdminServer(MockServer):
    def __init__(self, port):
        MockServer.__init__(self, port)
        self.configUpdate = {}

    def buildResponse(self, **kwargs):
        if kwargs['path'] in ["/api/service/v2/update", "/api/service/v2/list"]:
            while not self.configUpdate:
                sleep(0.25)
                if self.halt:
                    sys.stderr.write('%s halting while client still on the Phone!\n' % self.__class__.__name__)
                    sys.stderr.flush()
                    break
            if self.configUpdate:
                keys = set(k for k in kwargs.get('arguments', {}).get('keys', [''])[0].split(',') if k)
                for special_key in ['services', 'config']:
                    if '-'+special_key in keys:
                        keys.remove('-'+special_key)
                    else:
                        keys.add(special_key)
                identifier = self._findIdentifier(**kwargs)
                result = {}
                for key in keys:
                    try:
                        result[key] = self.configUpdate[key]
                    except KeyError:
                        pass
                if identifier:
                    service = result.get('services', {}).get(identifier, None)
                    if service:
                        result['this_service'] = dict(service)
                        result['this_service']['state'] = {'readable':service['readable'], 'writable':service['writable']}
                return Ok + CRLF + dumps(result)
        return MockServer.buildResponse(self, **kwargs)


    def _findIdentifier(self, **kwargs):
        identifier = None
        if 'Body' in kwargs:
            identifier = parse_qs(kwargs['Body']).get('identifier', [None])[0]
        if not identifier:
            identifier = kwargs.get('arguments', {}).get('identifier', [None])[0]
        return identifier

