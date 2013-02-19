## begin license ##
# 
# "NBC+" also known as "ZP (ZoekPlatform)" is
#  initiated by Stichting Bibliotheek.nl to provide a new search service
#  for all public libraries in the Netherlands. 
# 
# Copyright (C) 2012 Seecr (Seek You Too B.V.) http://seecr.nl
# Copyright (C) 2012 Stichting Bibliotheek.nl (BNL) http://www.bibliotheek.nl
# 
# This file is part of "NBC+ (Zoekplatform BNL)"
# 
# "NBC+ (Zoekplatform BNL)" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# "NBC+ (Zoekplatform BNL)" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with "NBC+ (Zoekplatform BNL)"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# 
## end license ##

from sys import stdout
from lxml.etree import _ElementTree as ElementTreeType
from meresco.components import lxmltostring
from weightless.core import NoneOfTheObserversRespond, DeclineMessage
from meresco.core import Observable


class LogComponent(Observable):
    def _log(self, method, *args, **kwargs):
        printKwargs = dict(kwargs)
        for key, value in kwargs.items():
            if type(value) == ElementTreeType:
                printKwargs[key] = "%s(%s)" % (value.__class__.__name__, lxmltostring(value))
        print "[%s] %s(*%s, **%s)" % (self.observable_name(), method, args, printKwargs)
        stdout.flush()
    
    def all_unknown(self, message, *args, **kwargs):
        self._log(message, *args, **kwargs)
        yield self.all.unknown(message, *args, **kwargs)

    def any_unknown(self, message, *args, **kwargs):
        self._log(message, *args, **kwargs)
        try:
            response = yield self.any.unknown(message, *args, **kwargs)
        except NoneOfTheObserversRespond:
            raise DeclineMessage
        raise StopIteration(response)

    def do_unknown(self, message, *args, **kwargs):
        self._log(message, *args, **kwargs)
        self.do.unknown(message, *args, **kwargs)

    def call_unknown(self, message, *args, **kwargs):
        self._log(message, *args, **kwargs)
        try:
            return self.call.unknown(message, *args, **kwargs)
        except NoneOfTheObserversRespond:
            raise DeclineMessage

