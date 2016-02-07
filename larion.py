'''
Created on Dec 7, 2015

@author: Dmitry
'''
from pymudclient.library.html import HTMLLoggingModule

from pymudclient.library.imperian.channel_handler import ChannelHandler
from pymudclient.library.aetolia.aetolia import AetoliaModule
from aetolia.Carnifex import Carnifex
from aetolia.warhounds import WarhoundPicker, WarhoundParser
from aetolia.soul_consumption import SoulConsumption
from pymudclient.aliases import binding_alias
from pymudclient.modules import BaseModule
import pymudclient
from pymudclient.library.aetolia.aetolia_gui import AetoliaGui
from movement.map import MapFromXml
from movement.walker import Walker
from aetolia.verminer import Verminer
from aetolia.autobasher import AutoBasher

name = 'Larion'
host = 'aetolia.com'
port = 23
encoding = 'ascii'
gmcp_handshakes=['Core.Hello { "client": "pymudclient", "version": "'+ pymudclient.__version__ +'" }',
                 'Core.Supports.Set [ "Core 1", "Char 1", "Char.Name 1", "Char.Skills 1", "Char.Items 1", "Comm.Channel 1", "Redirect 1", "Room 1", "IRE.Rift 1", "IRE.Composer 1" ]']
use_blocks = True

def configure(realm):
    HTMLLoggingModule(realm)
    
    
def gui_configure(realm):
    realm.extra_gui=AetoliaGui(realm)

class MainModule(BaseModule):

    def __init__(self, manager):
        BaseModule.__init__(self, manager)
        self.warhound_parser = WarhoundParser()
        mapper = MapFromXml('http://www.aetolia.com/maps/map.xml')
        self.walker = Walker(manager, mapper)
        
    
    def is_main(self, realm):
            BaseModule.is_main(self, realm)
        
    @property
    def aliases(self):
        return [self.test_alias]
    @property
    def modules(self):
        return[AetoliaModule, ChannelHandler, 
                    self.warhound_parser, WarhoundPicker,
                    SoulConsumption,
                    self.walker,
                    Verminer(self.manager, self.walker, 'queue eqbal hammer doublebash %s'),
                    AutoBasher(self.manager, 'stand|hammer doublebash %(target)s','soul consume for health')]
        
    @property
    def macros(self):
        return {'<F1>':'test_alias diaf'}
    
    @binding_alias('^test_alias (\w+)$')
    def test_alias(self, match, realm):
        realm.send_to_mud = False
        
        realm.cwrite('test non existing variable %s'%match.group(1))
        