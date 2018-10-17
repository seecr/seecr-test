## begin license ##
#
# "Seecr Test" provides test tools.
#
# Copyright (C) 2018 Seecr (Seek You Too B.V.) http://seecr.nl
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

from simplejson import JSONDecodeError
from lxml.etree import XML
from meresco.components.http.utils import parseResponse, CRLF
from meresco.components.json import JsonDict, JsonList
from .utils import postRequest as _postRequest, getRequest as _getRequest, postMultipartForm as _postMultipartForm

def parseHeaderAndBody(h, b=None, parseBody=True):
    if b is None:
        h, b = h
    header, body = parseResponse(h + CRLF * 2 + b)
    if body and parseBody and 'Content-Type' in header['Headers']:
        contentType = header['Headers']['Content-Type']
        if 'xml' in contentType:
            return header, XML(body)
        if 'json' in contentType:
            try:
                return header, JsonDict.loads(body) if body[0] == '{' else JsonList.loads(body)
            except JSONDecodeError:
                return header, 'JSONDecodeError in: ' + body
    return header, body

def enhance_request(request_method):
    def f(port, path, *args, **kwargs):
        parseBody = kwargs.get('parse', True)
        kwargs['parse'] = False
        kwargs.setdefault('additionalHeaders', {})
        cookie = kwargs.pop('cookie', None)
        if cookie and not 'Cookie' in kwargs["additionalHeaders"]:
            kwargs['additionalHeaders']['Cookie'] = cookie
        return parseHeaderAndBody(request_method(port, path, *args, **kwargs), parseBody=parseBody)
    return f
postRequest = enhance_request(_postRequest)
postMultipartForm = enhance_request(_postMultipartForm)
getRequest = enhance_request(_getRequest)
