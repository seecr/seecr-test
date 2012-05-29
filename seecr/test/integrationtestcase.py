# -*- coding: utf-8 -*-
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

from seecrtestcase import SeecrTestCase

class IntegrationTestCase(SeecrTestCase):
    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(name)
        return getattr(self.state, name)

    def run(self, result=None, state=None):
        self.state = state
        SeecrTestCase.run(self, result=result)

class IntegrationState(object):
    def __init__(self, stateName, tests=None, fastMode=False):
        self.stateName = stateName
        self.__tests = tests
        self.fastMode = fastMode
        self.pids = {}
        self.integrationTempdir = '/tmp/integrationtest-%s' % stateName 
        if not self.fastMode:
            system('rm -rf ' + self.integrationTempdir)
            system('mkdir --parents '+ self.integrationTempdir)

    def addToTestRunner(self, testRunner):
        testRunner.addGroup(
            self.stateName, 
            self.__tests,
            state=self)
    
    def binDir(self):
        raise ValueError("Needs implementation")


    def _startServer(self, serviceName, executable, serviceReadyUrl, cwd=None, redirect=True, flagOptions=None, **kwargs):
        stdoutfile = join(self.integrationTempdir, "stdouterr-%s.log" % serviceName)
        stdouterrlog = open(stdoutfile, 'w')
        args = [executable]
        fileno = stdouterrlog.fileno() if redirect else None
        flagOptions = flagOptions if flagOptions else []
        for flag in flagOptions:
            args.append("--%s" % flag)
        for k,v in kwargs.items():
            args.append("--%s=%s" % (k, str(v))
        serverProcess = Popen(
            executable=executable,
            args=args,
            cwd=cwd if cwd else self.binDir(),
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

