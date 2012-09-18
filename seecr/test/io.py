import sys

from StringIO import StringIO

from contextlib import contextmanager


@contextmanager
def stderr_replaced():
    oldstderr = sys.stderr
    mockStderr = StringIO()
    sys.stderr = mockStderr
    try:
        yield mockStderr
    finally:
        sys.stderr = oldstderr

@contextmanager
def stdout_replaced():
    oldstdout = sys.stdout
    mockStdout = StringIO()
    sys.stdout = mockStdout
    try:
        yield mockStdout
    finally:
        sys.stdout = oldstdout

