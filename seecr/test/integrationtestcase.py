# -*- coding: utf-8 -*-
## begin license ##
#
# "Seecr Test" provides test tools.
#
# Copyright (C) 2012, 2014-2016, 2018-2021 Seecr (Seek You Too B.V.) https://seecr.nl
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



from errno import ECHILD
from os.path import join, basename
from os import system, waitpid, kill, WNOHANG, getenv
from sys import stdout
from random import choice
from time import sleep
from subprocess import Popen, TimeoutExpired
from signal import SIGTERM
from urllib.request import urlopen
from string import ascii_letters
from time import time

from urllib.error import HTTPError

from .seecrtestcase import SeecrTestCase

randomString = lambda n=4: ''.join(choice(ascii_letters) for i in range(n))

class IntegrationTestCase(SeecrTestCase):
    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(name)
        return getattr(self.state, name)

    def run(self, result=None, state=None):
        self.state = state
        SeecrTestCase.run(self, result=result)

INTEGRATION_TEMPDIR_BASE = getenv('INTEGRATION_TEMPDIR_BASE', '/tmp/integrationtest')
REMOTE_USERNAME = getenv('REMOTE_USERNAME', '')

class IntegrationState(object):
    def __init__(self, stateName, tests=None, fastMode=False):
        self.stateName = stateName
        self.__tests = tests
        self.fastMode = fastMode
        self.processes = {}
        self.openFiles = {}
        self.integrationTempdir = '%s-%s' % (INTEGRATION_TEMPDIR_BASE, stateName)
        if REMOTE_USERNAME:
            self.integrationTempdir += '-%s' % REMOTE_USERNAME
        if not self.fastMode:
            system('rm -rf ' + self.integrationTempdir)
            system('mkdir --parents '+ self.integrationTempdir)
        self._servicesReadyMethods = []

    def addToTestRunner(self, testRunner):
        testRunner.addGroup(
            self.stateName,
            self.__tests,
            state=self)

    def binDir(self):
        raise NotImplementedError()

    def binPath(self, executable, binDirs=None):
        return SeecrTestCase.binPath(executable, binDirs=[self.binDir()] + (binDirs or []))

    def _startServer(self, serviceName, executable, serviceReadyUrl, cwd=None, redirect=True, flagOptions=None, env=None, waitForStart=True, args=None, debugInfo=False, **kwargs):
        stdoutfile = join(self.integrationTempdir, "stdouterr-%s.log" % serviceName)
        stdouterrlog = open(stdoutfile, 'a')
        self.openFiles.setdefault(serviceName, []).append(stdouterrlog)
        args = executable if isinstance(executable, list) else [executable] + (args if not args is None else [])
        executable = args[0]
        fileno = stdouterrlog.fileno() if redirect else None
        flagOptions = flagOptions if flagOptions else []
        for flag in flagOptions:
            args.append("--%s" % flag)
        for k,v in list(kwargs.items()):
            if not hasattr(v, 'append'):
                v = [v]
            for x in v:
                if '-' in k:
                    args.append(k)
                    args.append(str(x))
                else:
                    args.append("--%s=%s" % (k, str(x)))
        self._stdoutWrite("Starting service '%s', for state '%s'\n" % (serviceName, self.stateName))
        if debugInfo:
            print("-----StartServer-----")
            print(args)
            print("-"*21)
            print()
        serverProcess = Popen(
            executable=executable,
            args=args,
            cwd=cwd if cwd else getenv('SEECRTEST_USR_BIN', self.binDir()),
            stdout=fileno,
            stderr=fileno,
            env=env,
        )
        self.processes[serviceName] = serverProcess

        def serviceReady():
            try:
                sleep(0.1)
                self._stdoutWrite('r')
                try:
                    u = urlopen(serviceReadyUrl)
                except HTTPError as e:
                    if e.code != 404:
                        raise
                self._stdoutWrite("\nStarted '%s'\n" % serviceName)
                return True
            except IOError:
                if serverProcess.poll() != None:
                    del self.processes[serviceName]
                    self._clearServicesReadyMethods()
                    exit('Service "%s" died, check "%s"' % (serviceName, stdoutfile))
            return False
        self._servicesReadyMethods.append(serviceReady)
        if waitForStart:
            self.waitForServicesStarted()

    def _stopServer(self, serviceName, waitInSeconds=20.0):
        serviceProc = self.processes[serviceName]
        try:
            serviceProc.terminate()
        except OSError:
            self._stdoutWrite("Server with servicename '%s' and pid '%s' was already stopped.\n" % (serviceName, serviceProc.pid))

        try:
            serviceProc.wait(waitInSeconds)
        except TimeoutExpired:
            self._stdoutWrite("\033[1;31mServer with servicename '%s' and pid '%s' did not stop within %s seconds - giving up.\033[0m\n" % (serviceName, serviceProc.pid, waitInSeconds))

        del self.processes[serviceName]
        for f in self.openFiles.get(serviceName, []):
            f.close()

    def _runExecutable(self, executable, processName=None, cwd=None, redirect=True, flagOptions=None, timeoutInSeconds=15, expectedReturnCode=0, env=None, **kwargs):
        processName = randomString() if processName is None else processName
        args = executable if isinstance(executable, list) else [executable]
        executable = args[0]
        stdoutfile = join(self.integrationTempdir, "stdouterr-%s-%s.log" % (basename(executable), processName))
        with open(stdoutfile, 'w') as stdouterrlog:
            fileno = stdouterrlog.fileno() if redirect else None
            flagOptions = flagOptions if flagOptions else []
            for flag in flagOptions:
                args.append("--%s" % flag)
            for k,v in list(kwargs.items()):
                args.append("--%s=%s" % (k, str(v)))
            process = Popen(
                executable=executable,
                args=args,
                cwd=cwd if cwd else getenv('SEECRTEST_USR_BIN', self.binDir()),
                stdout=fileno,
                stderr=fileno,
                env=env,
            )

            self._stdoutWrite("Running '%s', for state '%s' : v" % (basename(executable), self.stateName))
            result = 0
            t0 = time()
            keepRunning = True
            while keepRunning:
                self._stdoutWrite('r')
                sleep(0.1)
                result = process.poll()
                keepRunning = result is None
                if time() - t0 > timeoutInSeconds:
                    process.terminate()
                    exit('Executable "%s" took more than %s seconds, check "%s"' % (basename(executable), timeoutInSeconds, stdoutfile))

            if expectedReturnCode is not None and result != expectedReturnCode:
                exit('Executable "%s" exited with returncode %s, check "%s"' % (basename(executable), result, stdoutfile))
            self._stdoutWrite('oom!\n')
            process.wait()
        if redirect:
            with open(stdoutfile) as fp:
                return fp.read()

    def tearDown(self):
        for serviceName in list(self.processes.keys()):
            self._stdoutWrite("Stopping service '%s' for state '%s'\n" % (serviceName, self.stateName))
            self._stopServer(serviceName)

    def waitForServicesStarted(self):
        for r in self._servicesReadyMethods:
            while not r():
                pass
        self._clearServicesReadyMethods()

    def _clearServicesReadyMethods(self):
        del self._servicesReadyMethods[:]


    @staticmethod
    def _stdoutWrite(aString):
        stdout.write(aString)
        stdout.flush()

