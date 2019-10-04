## begin license ##
#
# "Seecr Test" provides test tools.
#
# Copyright (C) 2005-2009 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2012, 2014 Seecr (Seek You Too B.V.) http://seecr.nl
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

from unittest import TestCase
from types import GeneratorType
from seecr.test import CallTrace
from seecr.test.calltrace import TracedCall


class CallTraceTest(TestCase):
    def testSimpleCall(self):
        callTrace = CallTrace()
        callTrace.simpleCall()
        self.assertEqual(1, len(callTrace.calledMethods))
        tracedCall = callTrace.calledMethods[0]
        self.assertEqual('simpleCall', tracedCall.name)
        self.assertEqual(0, len(tracedCall.args))

    def testCallWithArguments(self):
        callTrace = CallTrace()
        callTrace.simpleCall('argument one', 2)
        self.assertEqual(1, len(callTrace.calledMethods))

        tracedCall = callTrace.calledMethods[0]
        self.assertEqual('simpleCall', tracedCall.name)
        self.assertEqual(2, len(tracedCall.args))
        self.assertEqual('argument one', tracedCall.args[0])
        self.assertEqual(2, tracedCall.args[1])

        callTrace.simpleCall('argument two', 4)
        self.assertEqual(2, len(callTrace.calledMethods))
        tracedCall = callTrace.calledMethods[1]
        self.assertEqual('simpleCall', tracedCall.name)
        self.assertEqual(2, len(tracedCall.args))
        self.assertEqual('argument two', tracedCall.args[0])
        self.assertEqual(4, tracedCall.args[1])

    def testCallWithReturnValue(self):
        callTrace = CallTrace()
        callTrace.returnValues['simpleCall'] = 'OK'
        result = callTrace.simpleCall('argument one', 2)
        self.assertEqual('OK', result)

        callTrace = CallTrace()
        callTrace.methods['simpleCall'] = lambda x: x+3
        result = callTrace.simpleCall(1)
        self.assertEqual(4, result)

    def testCallWithException(self):
        class TestException(Exception):
            pass
        callTrace = CallTrace()
        callTrace.exceptions['simpleCall'] = TestException('test')
        try:
            result = callTrace.simpleCall()
            self.fail()
        except TestException as e:
            self.assertEqual('test', str(e))


    def testTracedCallDictRepresentationOneArgument(self):
        callTrace = CallTrace()
        callTrace.simpleCall('argument one')
        self.assertEqual({'name': "simpleCall", 'args': ('argument one', ), 'kwargs': {}}, callTrace.calledMethods[0].asDict())

    def testTracedCallDictRepresentationTwoArguments(self):
        callTrace = CallTrace()
        callTrace.simpleCall('argument one', 2)
        self.assertEqual({'name': "simpleCall", 'args': ('argument one', 2), 'kwargs': {}}, callTrace.calledMethods[0].asDict())

    def testTracedCallDictRepresentationWithKwargs(self):
        callTrace = CallTrace()
        callTrace.simpleCall(argument='one', second=2)
        self.assertEqual({'name': "simpleCall", 'args': (), 'kwargs': {'argument': "one", 'second': 2}}, callTrace.calledMethods[0].asDict())

    def testTracedCallRepresentationOneArgument(self):
        callTrace = CallTrace()
        callTrace.simpleCall('argument one')
        self.assertEqual("simpleCall('argument one')", str(callTrace.calledMethods[0]))

    def testTracedCallRepresentationTwoArguments(self):
        callTrace = CallTrace()
        callTrace.simpleCall('argument one', 2)
        self.assertEqual("simpleCall('argument one', 2)", str(callTrace.calledMethods[0]))

    def testTracedCallRepresentationObjectArgument(self):
        class SomeClass:
            pass
        callTrace = CallTrace()
        callTrace.simpleCall(SomeClass())
        self.assertEqual("simpleCall(<SomeClass>)", str(callTrace.calledMethods[0]))

    def testTracedCallRepresentationClassArgument(self):
        class SomeClass:
            pass
        callTrace = CallTrace()
        callTrace.simpleCall(SomeClass)
        self.assertEqual("simpleCall(<class SomeClass>)", str(callTrace.calledMethods[0]))

    def testGetList(self):
        callTrace = CallTrace()
        callTrace.simpleCall('argument one', 2)
        self.assertEqual(["""simpleCall('argument one', 2)"""], callTrace.__calltrace__())

    def testNonZero(self):
        callTrace = CallTrace()
        self.assertTrue(callTrace)

    def testNotEqualToNone(self):
        callTrace = CallTrace(verbose=True)
        self.assertTrue(callTrace != None)

    def testCallTraceDunderMethodsNotSupported(self):
        trace = CallTrace()
        trace.returnValues['__call__'] = 'output'
        try:
            self.assertEqual('output', trace())
            self.fail()
        except TypeError as e:
            self.assertEqual("'CallTrace' object is not callable", str(e))

    def testRewriteReprWithMemAddresses(self):
        trace = CallTrace()
        class A(object):
            pass
        trace.blah(A())
        self.assertEqual('blah(<A>)', str(trace.calledMethods[0]))

    def testIgnoreAttributes(self):
        trace = CallTrace(ignoredAttributes=["aMessage"])
        self.assertTrue(hasattr(trace, 'someAttribute'))
        self.assertFalse(hasattr(trace, 'aMessage'))

    def testRepresentRE(self):
        self._verbose = False
        c = TracedCall('someMethod', self)
        class IsObject:
            pass
        self.assertEqual('<IsObject>', c.represent(IsObject()))
        self.assertEqual('<class IsObject>', c.represent(IsObject))

        self.assertEqual("'aap'", c.represent('aap'))
        self.assertEqual('1', c.represent(1))
        self.assertEqual('1.1', c.represent(1.1))
        self.assertEqual('None', c.represent(None))

        self._verbose = True
        self.assertEqual('<CallTraceTest.testRepresentRE.<locals>.IsObject>', c.represent(IsObject()))
        self.assertEqual('<class CallTraceTest.testRepresentRE.<locals>.IsObject>', c.represent(IsObject))

        del self._verbose

    def testOnlySpecifiedMethods(self):
        trace = CallTrace(onlySpecifiedMethods=True)
        self.assertRaises(AttributeError, lambda: trace.someMethod())
        trace = CallTrace(returnValues={"someMethod": 'result'}, onlySpecifiedMethods=True)
        self.assertEqual('result', trace.someMethod())
        trace = CallTrace(methods={"someMethod": lambda : "result"}, onlySpecifiedMethods=True)
        self.assertEqual("result", trace.someMethod())
        trace = CallTrace(emptyGeneratorMethods=["someMethod"], onlySpecifiedMethods=True)
        self.assertEqual(GeneratorType, type(trace.someMethod()))

    def testReset(self):
        callTrace = CallTrace()
        callTrace.simpleCall()
        self.assertEqual(1, len(callTrace.calledMethods))
        callTrace.simpleCall()
        self.assertEqual(2, len(callTrace.calledMethods))
        callTrace.calledMethods.reset()
        self.assertEqual(0, len(callTrace.calledMethods))
        callTrace.simpleCall()
        self.assertEqual(1, len(callTrace.calledMethods))

    def testTracedMethodStr(self):
        myObject = CallTrace('myObject')
        myMethod = myObject.myMethod
        self.assertEqual("<bound method myMethod of <CallTrace: myObject>>", str(myMethod))

    def testEmptyGeneratorMethods(self):
        calltrace = CallTrace(emptyGeneratorMethods=['emptyGen'])
        result = calltrace.emptyGen()
        self.assertEqual(GeneratorType, type(result))
        self.assertEqual([], list(result))
        self.assertEqual(1, len(calltrace.calledMethods))

    def testCalledMethodNames(self):
        calltrace = CallTrace('name')
        calltrace.methodOne('aap')
        calltrace.methodTwo('aap')
        self.assertEqual(['methodOne', 'methodTwo'], calltrace.calledMethodNames())
