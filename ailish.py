'''
Created on Nov 9, 2015

@author: Dmitry
'''
from pymudclient.modules import BaseModule
from movement.map import MapFromXml
from movement.walker import Walker
from pymudclient.library.imperian.imperian import ImperianModule
from pymudclient.library.imperian.channel_handler import ChannelHandler
from pymudclient.library.imperian.imperian_prompt import ImperianPrompt
import pymudclient
from pymudclient.library.html import HTMLLoggingModule
from pymudclient.library.imperian.imperian_gui import ImperianGui

from imperian.autobasher import AutoBasher
from pymudclient.library.imperian.berserker.rage import RageTracker
from shield_rez import ShieldRez

name = 'Ailish'
host = 'imperian.com'
port = 23
encoding = 'ascii'
gmcp_handshakes=['Core.Hello { "client": "pymudclient", "version": "'+ pymudclient.__version__ +'" }',
                 'Core.Supports.Set [ "Core 1", "Char 1", "Char.Name 1", "Char.Skills 1", "Char.Items 1", "Comm.Channel 1", "Redirect 1", "Room 1", "IRE.Rift 1", "IRE.Composer 1" ]']
use_blocks = True

def configure(realm):
    HTMLLoggingModule(realm)
    #ScreenreaderProtocol(realm)
    
    
def gui_configure(realm):
    realm.extra_gui=ImperianGui(realm)
    
class MainModule(BaseModule):
        
        def __init__(self, realm):
            BaseModule.__init__(self,realm)
            self.map_mode=False
            self.rage = RageTracker()
            self.mapper= MapFromXml()
            self.walker = Walker(realm, self.mapper)
            self.bash_module = AutoBasher(realm, 
                                          attack_command='touch amnesia|stand|shield slam %(target)s|warchant thunder shout %(target)s|warchant shout %(target)s',
                                          heal_command='warchant restore')
            self.shield_track = ShieldRez(realm)
            
        
            
        def is_main(self, realm):
            BaseModule.is_main(self, realm)
         
        @property
        def modules(self):
            return[ImperianModule, 
                   ChannelHandler, 
                   self.walker, 
                   ImperianPrompt, 
                   self.bash_module,
                   self.rage,
                   self.shield_track]
            
        