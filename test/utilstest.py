from unittest import TestCase

from seecr.test.utils import ignoreLineNumbers


class UtilsTest(TestCase):
    def testIgnoreLineNumber(self):
        theTraceback = """Traceback (most recent call last):
  File "../some/file.py", line 104, in aFunction
    for _var  in vars:
  File "some/other/file.py", line 249, in anotherFuntion
    raise Exception('xcptn')
Exception: xcptn\n"""

        expected = """Traceback (most recent call last):
  File "../some/file.py", line [#], in aFunction
    for _var  in vars:
  File "some/other/file.py", line [#], in anotherFuntion
    raise Exception('xcptn')
Exception: xcptn\n"""

        self.assertEquals(expected, ignoreLineNumbers(theTraceback))

