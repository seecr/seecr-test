from unittest import TestCase

from traceback import print_exc

from seecr.test.io import stdout_replaced, stderr_replaced


class IOTest(TestCase):

    def testStdOutReplaced(self):
        with stdout_replaced() as s:
            print 'output'
            self.assertEquals('output\n', s.getvalue())

    def testStdErrReplaced(self):
        with stderr_replaced() as s:
            try:
                raise Exception('xcptn')
            except Exception:
                print_exc()
            result = s.getvalue()
            self.assertTrue('Traceback' in result, result)
            self.assertTrue('Exception: xcptn' in result, result)

