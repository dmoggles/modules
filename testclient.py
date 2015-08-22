#!C:\Python27\Python
from mudpyl.modules import BaseModule
from mudpyl.realms import RootRealm
from twisted.internet.stdio import StandardIO


class MainModule(RootRealm):
    pass

StandardIO(MainModule())
from twisted.internet import reactor
reactor.run()