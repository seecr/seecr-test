# -*- coding: utf-8 -*-

from __future__ import with_statement

from os.path import isdir, join, abspath, dirname, basename
from os import system, listdir, makedirs, waitpid, kill, WNOHANG
from sys import stdout
from random import randint, choice
from time import sleep
from StringIO import StringIO
from subprocess import Popen
from signal import SIGTERM
from urllib import urlopen, urlencode
from lxml.etree import XMLSyntaxError, parse

from utils import getRequest, postRequest, postMultipartForm 

from seecrtestcase import SeecrTestCase

mydir = dirname(abspath(__file__))
projectDir = dirname(dirname(mydir))
binDir = join(projectDir, 'bin')
if not isdir(binDir):
    binDir = '/usr/bin'

class IntegrationTestCase(SeecrTestCase):
    def setUp(self):
        SeecrTestCase.setUp(self)
        self.state = state

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(name)
        return getattr(self.state, name)


class IntegrationState(object):
    def __init__(self, stateName, fastMode):
        self.stateName = stateName
        self.pids = {}
        self.integrationTempdir = '/tmp/integrationtest-%s' % stateName 
        self.testdataDir = join(dirname(mydir), 'data/integration')
        self.fastMode = fastMode
        if not fastMode:
            system('rm -rf ' + self.integrationTempdir)
            system('mkdir --parents '+ self.integrationTempdir)

    def _startServer(self, serviceName, executable, serviceReadyUrl, cwd=binDir, redirect=True, **kwargs):
        stdoutfile = join(self.integrationTempdir, "stdouterr-%s.log" % serviceName)
        stdouterrlog = open(stdoutfile, 'w')
        args = [executable]
        fileno = stdouterrlog.fileno() if redirect else None
        for k,v in kwargs.items():
            args.append("--%s" % k)
            args.append(str(v))
        serverProcess = Popen(
            executable=executable,
            args=args,
            cwd=cwd,
            stdout=fileno,
            stderr=fileno
        )
        self.pids[serviceName] = serverProcess.pid

        self._stdoutWrite("Starting service '%s', for state '%s' : v" % (serviceName, self.stateName))
        done = False
        while not done:
            try:
                self._stdoutWrite('r')
                sleep(0.1)
                serviceReadyResponse = urlopen(serviceReadyUrl).read()
                done = True
            except IOError:
                if serverProcess.poll() != None:
                    del self.pids[serviceName]
                    exit('Service "%s" died, check "%s"' % (serviceName, stdoutfile))
        self._stdoutWrite('oom!\n')

    def _stopServer(self, serviceName):
        kill(self.pids[serviceName], SIGTERM)
        waitpid(self.pids[serviceName], WNOHANG)

    def tearDown(self):
        for serviceName in self.pids.keys():
            self._stopServer(serviceName)
    
    @staticmethod
    def _stdoutWrite(aString):
        stdout.write(aString)
        stdout.flush()

