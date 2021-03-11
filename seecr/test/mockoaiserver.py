#!/usr/bin/env python
## begin license ##
#
# "Seecr Test" provides test tools.
#
# Copyright (C) 2012-2016 Seecr (Seek You Too B.V.) http://seecr.nl
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

from sys import stdout
from os.path import join

from tempfile import mkdtemp
from shutil import rmtree
from time import sleep

from escaping import escapeFilename

from weightless.core import compose, be
from weightless.io import Reactor

from meresco.components.json import JsonList
from meresco.core import Observable
from meresco.core.processtools import setSignalHandlers, registerShutdownHandler

from meresco.components.log import LogCollector, ApacheLogWriter, HandleRequestLog
from meresco.components.http import ObservableHttpServer, PathFilter, StringServer
from meresco.components.http.utils import ContentTypePlainText
from meresco.oai import OaiJazz, OaiPmh, SuspendRegister
from meresco.oai.oaijazz import DEFAULT_BATCH_SIZE


def iterOaiData(dataDir):
    for line in open(join(dataDir, 'oai.ids')):
        action, filename, setSpecsRaw = line.strip().split(' ', 2)
        yield action, filename, [setSpec for setSpec in setSpecsRaw.split('|') if setSpec.strip()]

def allSets(dataDir):
    return set(setSpec for _,_,setSpecs in iterOaiData(dataDir) for setSpec in setSpecs)

def dna(reactor, portNumber, config, tempDir, batchSize):
    print('Config', config)
    root = HandleRequestLog()

    storage = DataStorage()
    for data in config:
        oaiName = ''.join(data['path'].split('/'))
        oaiSuspendRegister = SuspendRegister()
        try:
            oaiJazz = OaiJazz(join(tempDir, oaiName), preciseDatestamp=True)  # needed for backwards compatibility with meresco-oai versions preceding 5.16
        except TypeError:
            oaiJazz = OaiJazz(join(tempDir, oaiName))
        oaiJazz = be(
            (oaiJazz,
                (oaiSuspendRegister,)
            )
        )
        oaiJazzOperations = {
            'ADD': oaiJazz.addOaiRecord,
            'DEL': oaiJazz.deleteOaiRecord
        }

        for directory in data['dirs']:
            for action, filename, setSpecs in iterOaiData(directory):
                identifier, metadataPrefix = filename.rsplit('.', 1)
                oaiJazzOperations[action](
                    identifier=identifier,
                    setSpecs=setSpecs,
                    metadataPrefixes=[metadataPrefix],
                )
                storage.addFile(filename, join(directory, escapeFilename(filename)))
                sleep(0.000001)
        oaiJazz.commit()

        try:
            oaiPmh = OaiPmh(repositoryName='Mock', adminEmail='no@example.org', supportXWait=True, batchSize=batchSize, preciseDatestamp=True)
        except TypeError:
            oaiPmh = OaiPmh(repositoryName='Mock', adminEmail='no@example.org', supportXWait=True, batchSize=batchSize)  # needed for backwards compatibility with meresco-oai versions preceding 5.16
        tree = be(
            (PathFilter(data['path'], excluding=['/ready']),
                (IllegalFromFix(),
                    (oaiPmh,
                        (oaiJazz,),
                        (oaiSuspendRegister,),
                        (storage,),
                    )
                )
            )
        )
        root.addObserver(tree)

    return \
        (Observable(),
            (ObservableHttpServer(reactor, portNumber),
                (LogCollector(),
                    (ApacheLogWriter(stdout),),
                    (root,
                        (PathFilter("/ready"),
                            (StringServer('yes', ContentTypePlainText),)
                        )
                    )
                )
            )
        )


class IllegalFromFix(Observable):
    def handleRequest(self, arguments, **kwargs):
        if 'from' in arguments:
            f = arguments['from']
            arguments['from'] = ['1970-01-01'] if f == ['0000'] else f
        yield self.all.handleRequest(arguments=arguments, **kwargs)


class DataStorage(object):
    def __init__(self):
        self.filepathFor = {}

    def addFile(self, filename, filepath):
        self.filepathFor[filename] = filepath

    def getData(self, identifier, name):
        return open(self.filepathFor.get('%s.%s' % (identifier, name))).read()

    def retrieveData(self, identifier, name):
        raise StopIteration(self.getData(identifier=identifier, name=name))
        yield


def startServer(port, dataDir=None, jsonConfig=None, batchSize=None):
    batchSize = batchSize or DEFAULT_BATCH_SIZE
    setSignalHandlers()
    tempDir = mkdtemp(prefix='mockoai-')

    config = JsonList.loads(jsonConfig or '[]')
    if dataDir:
        config.append({'dirs': dataDir, 'path': '/'})
    try:
        reactor = Reactor()
        server = be(dna(reactor, port, config=config, tempDir=tempDir, batchSize=batchSize))
        print('Ready to rumble the mock plein server at', port)
        list(compose(server.once.observer_init()))
        registerShutdownHandler(statePath=tempDir, server=server, reactor=reactor)
        stdout.flush()
        reactor.loop()
    finally:
        rmtree(tempDir)
