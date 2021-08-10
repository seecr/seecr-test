## begin license ##
#
# "Seecr Test" provides test tools.
#
# Copyright (C) 2012-2013, 2017, 2019-2021 Seecr (Seek You Too B.V.) https://seecr.nl
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
from contextlib import contextmanager
from functools import wraps
import tempfile
import os
import io


class IOCatcher(object):
    def __init__(self):
        self._file = tempfile.TemporaryFile(mode="w+t", buffering=1)

    def __getattr__(self, name):
        return getattr(self._file, name)

    def getvalue(self):
        self.flush()
        self.seek(0)
        return self.read()

    def __del__(self):
        self.close()


def _set_replaced_stream(name, replacement=None):

    org_stream = getattr(sys, name)
    org_fd = org_stream.fileno()
    org_fd_backup = os.dup(org_fd)

    if replacement is None:
        replacement = IOCatcher()
        os.dup2(replacement.fileno(), org_fd)

    def andBackAgain():
        os.dup2(org_fd_backup, org_fd)
        setattr(sys, name, org_stream)

    setattr(sys, name, replacement)
    return replacement, andBackAgain


class _ContextMngrOrDecorated(object):
    def __init__(self, streamName, replacement=None):
        self._streamName = streamName
        self._replacement = replacement

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)
        return wrapper

    def __enter__(self):
        mockStream, self._back = _set_replaced_stream(self._streamName, self._replacement)
        return mockStream

    def __exit__(self, exc_type, exc_value, traceback):
        self._back()
        return False


def stderr_replaced(*func_arg):
    if func_arg:
        return _ContextMngrOrDecorated(streamName='stderr')(*func_arg)
    return _ContextMngrOrDecorated(streamName='stderr')

def stdout_replaced(*func_arg):
    if func_arg:
        return _ContextMngrOrDecorated(streamName='stdout')(*func_arg)
    return _ContextMngrOrDecorated(streamName='stdout')

def stdin_replaced(inStream=None):
    return _ContextMngrOrDecorated(streamName='stdin', replacement=inStream)
