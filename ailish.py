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
from afflictiontracking import communicator
from afflictiontracking.trackingmodule import TrackerModule
from pymudclient.library.imperian.berserker.warchants import Warchants
from pymudclient.library.imperian.berserker.shield import ShieldMaiming
from pymudclient.library.imperian.berserker.berserk import BerskerComboMaker
from pymudclient.library.imperian.berserker.rampage import Dances
from pymudclient.library.imperian.defenses import Defenses
from pymudclient.triggers import binding_trigger
from autocuring_control import AutocuringControl
from self_afflictions import SelfAfflictions
from location_service import LocationServices

name = 'Ailish'
host = 'imperian.com'
port = 23
encoding = 'ascii'
gmcp_handshakes=['Core.Hello { "client": "pymudclient", "version": "'+ pymudclient.__version__ +'" }',
                 'Core.Supports.Set [ "Core 1", "Char 1", "Char.Name 1", "Char.Skills 1", "Char.Items 1", "Comm.Channel 1", "Redirect 1", "Room 1", "IRE.Rift 1", "IRE.Composer 1" ]']
use_blocks = True


clan_number = 5
clan_name = 'Legion'

toxin_list = ['hemotoxin',
              'xeroderma',
              'ciguatoxin',
              'mercury',
              'iodine',
              'bromine',
              'strychnine']

defense_list = {'shield absorb':['shield absorb',1],
                'gripping':['grip',0],
                'deathsight':['deathsight',100],
                'selfishness':['selfishness',100],
                'curseward':['curseward',0],
                'celerity':['celerity',100],
                'nightsight':['nightsight',5],
                'third eye':['thirdeye',50],
                'reprise':['blade reprise',10],
                'slippery':['flexibility',4],
                'berserker rage':['warchant rage',3]}

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
            self.communicator = communicator.Communicator(clan_number, clan_name, realm)
            self.tracker = TrackerModule(realm, self.communicator, True)
            
            self.warchants = Warchants(realm, self.tracker)
            self.shields = ShieldMaiming(realm, self.tracker)
            self.dances = Dances(realm)
            self.location_services = LocationServices(realm, self.mapper)
            self.berserk = BerskerComboMaker(realm,
                                             self.shields, 
                                             self.rage, 
                                             self.shield_track, 
                                             self.dances,
                                             self.tracker,
                                             toxin_list,
                                             self.warchants)
            self.defenses = Defenses(realm, defense_list)
            
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
                   self.shield_track,
                   self.communicator,
                   self.warchants, 
                   self.tracker,
                   self.shields,
                   self.berserk,
                   self.dances,
                   self.defenses,
                   AutocuringControl,
                   SelfAfflictions,
                   self.location_services]
            
        
        
       