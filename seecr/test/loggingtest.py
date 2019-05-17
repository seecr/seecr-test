## begin license ##
#
# "Seecr Test" provides test tools.
#
# Copyright (C) 2012-2014, 2016, 2019 Seecr (Seek You Too B.V.) http://seecr.nl
# Copyright (C) 2012-2014 Stichting Bibliotheek.nl (BNL) http://www.bibliotheek.nl
# Copyright (C) 2016 Koninklijke Bibliotheek (KB) http://www.kb.nl
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

from os import stat
from os.path import isfile, join
from re import compile
from stat import ST_MTIME
from StringIO import StringIO
from sys import stderr
from time import strftime, localtime
from unittest import TextTestRunner, TextTestResult, TestProgram


class LoggingTestProgram(TestProgram):
    def runTests(self):
        self.testRunner.verbosity = self.verbosity
        result = self.testRunner.run(self.test)
        exit(not result.wasSuccessful())


class TestLogger(object):
    def __init__(self, logstream):
        self._stream = logstream

    def startTest(self, test):
        self._stream.write(str(test)) #self.getDescription(..) also returns docstring. Not wanted for now.
        self._stream.write(" ... ")
        self._stream.flush()

    def addSuccess(self, test):
        self._stream.write("ok\n")
        self._stream.flush()

    def addError(self, test, err):
        self._stream.write("ERROR\n")
        self._stream.flush()

    def addFailure(self, test, err):
        self._stream.write("FAIL\n")
        self._stream.flush()

    def addSkip(self, test, reason):
        self._stream.write("skipped\n")
        self._stream.flush()

class NoneLogger(object):
    def nothing(self, *args, **kwargs):
        pass
    startTest = nothing
    addSuccess = nothing
    addFailure = nothing
    addError = nothing
    addSkip = nothing

def wrapTestResult(result, logger):
    for m in ['startTest', 'addSuccess', 'addSkip', 'addFailure', 'addError']:
        def _m(orig, *args, **kwargs):
            getattr(logger, m)(*args, **kwargs)
            return orig(*args, **kwarg)
        setattr(result, m, _m(getattr(result, m)))

class _LoggingTextTestResult(TextTestResult):
    def __init__(self, *args, **kwargs):
        self._testLogger = kwargs.pop('testLogger', NoneLogger())
        TextTestResult.__init__(self, *args, **kwargs)

    def startTest(self, test):
        TextTestResult.startTest(self, test)
        self._testLogger.startTest(test)

    def addSuccess(self, test):
        TextTestResult.addSuccess(self, test)
        self._testLogger.addSuccess(test)

    def addError(self, test, err):
        TextTestResult.addError(self, test, err)
        self._testLogger.addError(test, err)

    def addFailure(self, test, err):
        TextTestResult.addFailure(self, test, err)
        self._testLogger.addFailure(test, err)

    def addSkip(self, test, reason):
        TextTestResult.addSkip(self, test, reason)
        self._testLogger.addSkip(test, reason)

    def printResult(self, timeTaken):
        pass



testNameRe = compile("([A-Z]+[a-z0-9]*)")
def formatTestname(testname):
    return ' '.join([part.lower() for part in testNameRe.split(testname) if part and part != 'test']).capitalize()

def readTestFile(*pathparts):
    fullFilename = join(*pathparts)
    if not isfile(fullFilename):
        return {}
    def l(testname, classname, _, status):
        return dict(testname=testname, classname=classname.replace('(', '').replace(')', ''), status=status)
    return {'timestamp':strftime("%Y-%m-%d %H:%M:%S", localtime(stat(fullFilename)[ST_MTIME])), 'tests': [
        l(*line.strip().split()) for line in open(fullFilename) if line.strip()]}

def runUnitTests(loggingFilepath=None):
    logStream = StringIO() if loggingFilepath is None else open(loggingFilepath, 'w')
    try:
        LoggingTestProgram(testRunner=LoggingTestRunner(stream=testStream))
    finally:
        logStream.close()

