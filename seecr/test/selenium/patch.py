## begin license ##
#
# "Sharekit" is a repository service for higher education in The Netherlands.
# The service is developed by Seecr for SURFmarket.
#
# Copyright (C) 2017 SURF https://surf.nl
# Copyright (C) 2017-2018 Seecr (Seek You Too B.V.) https://seecr.nl
#
# This file is part of "Sharekit"
#
# "Sharekit" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "Sharekit" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "Sharekit"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from selenium.webdriver.remote.webelement import WebElement
# allows WebElements to be used in WebDriverWait which expects a WebDriver

def patchWebElementWithGetAttr():
    WebElement.__getattr__ = lambda self, x: getattr(self.parent, x)
