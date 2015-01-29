# -*- encoding: utf-8 -*-
## begin license ##
#
# "Seecr Test" provides test tools.
#
# Copyright (C) 2012-2015 Seecr (Seek You Too B.V.) http://seecr.nl
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

import sys
from sys import getdefaultencoding
from re import DOTALL, compile, sub
from io import StringIO
from lxml.etree import parse as parse_xml, XMLSyntaxError, HTMLParser
from socket import socket
from urllib.parse import urlencode
import sys
from sys import getdefaultencoding
from time import sleep
from glob import glob
from functools import partial
from os.path import dirname, abspath, join, isdir

_scriptTagRegex = compile("<script[\s>].*?</script>", DOTALL)
_entities = {
    '&nbsp;': ' ',
    '&ndash;': "&#8211;",
    '&mdash;': "&#8212;",
    '&lsquo;': "‘",
    '&rsquo;': "’",
    '&larr;': "&lt;-",
    '&rarr;': "-&gt;",
}

def parseHtmlAsXml(body):
    def forceXml(body):
        newBody = body
        for entity, replacement in list(_entities.items()):
            newBody = newBody.replace(entity, replacement)
        newBody = _scriptTagRegex.sub('', newBody)
        return newBody
    try:
        return parse_xml(StringIO(forceXml(body)))
    except XMLSyntaxError:
        print(body)
        raise

def getPage(port, path, arguments=None, expectedStatus="200", sessionId=None):
    additionalHeaders = {}
    if sessionId:
        additionalHeaders['Cookie'] = 'session=' + sessionId
    header, body = getRequest(
        port=port,
        path=path,
        arguments=arguments,
        parse=False,
        additionalHeaders=additionalHeaders)
    assertHttpOK(header, body, expectedStatus=expectedStatus)
    return header, body

def postToPage(port, path, data, expectedStatus="302", sessionId=None):
    additionalHeaders = {}
    if sessionId:
        additionalHeaders['Cookie'] = 'session=' + sessionId
    postBody = urlencode(data, doseq=True)
    header, body = postRequest(
        port=port,
        path=path,
        data=postBody,
        contentType='application/x-www-form-urlencoded',
        parse=False,
        additionalHeaders=additionalHeaders)
    assertHttpOK(header, body, expectedStatus=expectedStatus)
    return header, body

def assertHttpOK(header, body, expectedStatus="200"):
    try:
        assertSubstring("HTTP/1.0 %s" % expectedStatus, header)
        assertNotSubstring("Traceback", header + "\r\n\r\n" + body)
    except AssertionError as e:
        print(header, body)
        raise

def assertSubstring(value, s):
    if not value in s:
        raise AssertionError("assertSubstring fails: '%s' must occur in '%s'" % (value, s))

def assertNotSubstring(value, s):
    if value in s:
        raise AssertionError("assertNotSubstring fails: '%s' must not occur in '%s'" % (value, s))


def _socket(port, timeOutInSeconds):
    sok = socket()
    sok.connect(('localhost', port))
    sok.settimeout(5.0 if timeOutInSeconds is None else timeOutInSeconds)
    return sok

def createReturnValue(header, body, parse):
    if parse and body.strip() != '':
        body = parse_xml(StringIO(body))
    return header, body


def httpRequest(port, path, data=None, arguments=None, contentType=None, parse=True, timeOutInSeconds=None, host=None, method='GET', additionalHeaders=None):
    additionalHeaders = additionalHeaders or {}
    if type(data) is str:
        data = data.encode(getdefaultencoding())
    sok = _socket(port, timeOutInSeconds)
    try:
        contentLength = len(data) if data else 0
        requestString = path
        if arguments:
            requestString = path + '?' + urlencode(arguments, doseq=True)
        httpVersion = '1.0'
        lines = [
            '%(method)s %(requestString)s HTTP/%(httpVersion)s',
            'Content-Length: %(contentLength)s'
        ]
        if host:
            httpVersion = '1.1'
            lines.append('Host: %(host)s')
        if contentType:
            lines.append('Content-Type: %(contentType)s')
        lines += ["%s: %s" % (k, v) for k, v in list(additionalHeaders.items())]
        lines += ['', '']
        sendBuffer = ('\r\n'.join(lines) % locals()).encode() + (data or '').encode()
        totalBytesSent = 0
        bytesSent = 0
        while totalBytesSent != len(sendBuffer):
            bytesSent = sok.send(sendBuffer[totalBytesSent:])
            totalBytesSent += bytesSent
        header, body = splitHttpHeaderBody(receiveFromSocket(sok))
        return createReturnValue(header, body, parse)
    finally:
        sok.close()

postRequest = partial(httpRequest, method='POST', contentType='text/xml; charset="utf-8"')
putRequest = partial(httpRequest, method='PUT')
deleteRequest = partial(httpRequest, method='DELETE')

def getRequest(port, path, arguments=None, **kwargs):
    return httpRequest(port=port, path=path, arguments=arguments, method='GET', **kwargs)

def postMultipartForm(port, path, formValues, parse=True, timeOutInSeconds=None, **kwargs):
    boundary = '-=-=-=-=-=-=-=-=TestBoundary1234567890'
    body = createPostMultipartForm(boundary, formValues)
    return postRequest(
        port,
        path,
        body,
        contentType='multipart/form-data; boundary=' + boundary,
        parse=parse,
        timeOutInSeconds=timeOutInSeconds,
        **kwargs)

def createPostMultipartForm(boundary, formValues):
    strm = StringIO()
    for valueDict in formValues:
        fieldType = valueDict['type']
        headers = {}
        headers['Content-Disposition'] = 'form-data; name="%(name)s"' % valueDict
        if fieldType == 'file':
            headers['Content-Disposition'] = headers['Content-Disposition'] + '; filename="%(filename)s"' % valueDict
            headers['Content-Type'] = valueDict['mimetype']

        strm.write('--' + boundary + '\r\n')
        for item in list(headers.items()):
            strm.write('%s: %s\r\n' % item)
        strm.write('\r\n')
        strm.write(valueDict['value'])
        strm.write('\r\n')
    strm.write('--' + boundary + '--\r\n')
    return strm.getvalue()

def receiveFromSocket(sok):
    response = b''
    part = sok.recv(1024)
    response += part
    while part != None:
        part = sok.recv(1024)
        if not part:
            break
        response += part
    return response.decode()

def splitHttpHeaderBody(response):
    try:
        header, body = response.split('\r\n\r\n', 1)
    except ValueError as e:
        raise ValueError("%s can not be split into a header and body" % repr(response))
    else:
        return header, body

def headerToDict(header):
   return dict(
       tuple(s.strip() for s in line.split(':', 1))
       for line in header.split('\r\n')
       if ':' in line
   )

def sleepWheel(seconds, callback=None, interval=0.2):
    parts = ['\\', '|', '/', '-']
    for i in range(int(seconds/interval)):
        sys.stdout.write(parts[i%len(parts)])
        sys.stdout.flush()
        sleep(interval)
        sys.stdout.write("\b")
        sys.stdout.flush()
        if not callback is None:
            if callback():
                return True
    return False

def ignoreLineNumbers(s):
    return sub("line \d+,", "line [#],", s)

def openConsole():
    from code import InteractiveConsole
    from inspect import currentframe

    frame = currentframe().f_back

    d={'_frame':frame}         # Allow access to frame object.
    d.update(frame.f_globals)  # Unless shadowed by global
    d.update(frame.f_locals)

    message = "Break in %s:%s" % (frame.f_code.co_filename, frame.f_lineno)

    i = InteractiveConsole(d)
    i.interact(message)

def findTag(tag, body, **attrs):
    try:
        xmlNode = parse_xml(StringIO(body), parser=HTMLParser()).getroot()
    except XMLSyntaxError:
        print(body)
        raise

    xpathExpr = "//%s" % tag
    if attrs:
        xpathExpr += "[%s]" % ' and '.join('@%s="%s"' % item for item in attrs.items())

    for tag in xmlNode.xpath(xpathExpr):
        yield tag


def includeParentAndDeps(filename, systemPath=None, cleanup=True, additionalPaths=None):
    raise NotImplementedError("includeParentAndDeps moved to seecr.deps package. Change import to: 'from seecr.deps import includeParentAndDeps'")
