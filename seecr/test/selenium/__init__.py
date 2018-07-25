from os import environ

from patch import patchWebElementWithGetAttr
patchWebElementWithGetAttr()

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

UI_TEST_PORT = int(environ.get('UI_TEST_PORT', 9515))

def remoteChrome(remoteHost='127.0.0.1', remotePort=UI_TEST_PORT):
    return WebDriver(
        command_executor='http://{}:{}'.format(remoteHost, remotePort),
        desired_capabilities=DesiredCapabilities.CHROME
    )
