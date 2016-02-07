from pymudclient.library.html import HTMLLoggingModule
from pymudclient.library.imperian.imperian_gui import ImperianGui
from pymudclient.modules import BaseModule
import pymudclient
from pymudclient.library.accessibility import ScreenreaderProtocol
from movement.map import MapFromXml
from movement.walker import Walker
from pymudclient.library.imperian.imperian import ImperianModule
from pymudclient.library.imperian.channel_handler import ChannelHandler
from pymudclient.library.imperian.imperian_prompt import ImperianPrompt
from autocuring_control import AutocuringControl
from necromancy import Necromancy
from deathknight import Deathknight
from afflictiontracking import communicator
name = 'Alesei'
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



shred_agony = '174566'
shred_draining = '193509'
lacerate = '226085'
sabre = 'sabre'


class MainModule(BaseModule):

    combat_channel=3
    combat_channel_name='Military'
    
    def __init__(self, manager):
        BaseModule.__init__(self, manager)
        mapper = MapFromXml('http://www.imperian.com/maps/map.xml')
        self.walker = Walker(manager, mapper)
        self.necromancy=Necromancy(manager)
        self.communicator = communicator.Communicator(MainModule.combat_channel, MainModule.combat_channel_name, manager)
            
        self.deathknight = Deathknight(manager, self.communicator, shred_draining, shred_agony, lacerate, sabre)
            
    def is_main(self, realm):
            BaseModule.is_main(self, realm)
        
    
    @property
    def modules(self):
        return[ImperianModule, ChannelHandler, 
                    self.walker,
                    ImperianPrompt,
                    AutocuringControl,
                    self.necromancy,
                    self.deathknight,
                    self.communicator
                    ]