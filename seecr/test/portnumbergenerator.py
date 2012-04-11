from random import randint

class PortNumberGenerator(object):
    startNumber = randint(50000, 60000)

    @classmethod
    def next(cls):
        cls.startNumber += 1
        return cls.startNumber
