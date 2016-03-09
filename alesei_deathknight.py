'''
Created on Jul 15, 2015

@author: Dmitry
'''
from pymudclient.modules import BaseModule




from pymudclient.library.html import HTMLLoggingModule
from pymudclient.library.imperian.imperian import ImperianModule
from pymudclient.library.imperian.imperian_prompt import ImperianPrompt
from pymudclient.library.imperian.channel_handler import ChannelHandler
from necromancy import Necromancy

from self_afflictions import SelfAfflictions
from afflictiontracking import communicator

from location_service import LocationServices
from security import CitySecurity
from limb_tracker import LimbTracker
from movement.map import MapFromXml
from movement.walker import Walker
from autocuring_control import AutocuringControl
from pymudclient.library.imperian.imperian_gui import ImperianGui
from pymudclient.library.imperian.defenses import Defenses
import pymudclient
from pymudclient.library.imperian.deathknight.deathknight import Deathknight
from afflictiontracking.trackingmodule import TrackerModule
from shield_rez import ShieldRez
from imperian import autobasher
from pymudclient.library.imperian.limb_tracker import LimbTrack
from pymudclient.library.imperian.autoparry import Autoparry
from pymudclient.library.imperian.alerts import Alerts


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



shred_infused = '123747'
shred_draining = '24163'
lacerate = '305569'
light = '263757'
sabre = 'sabre'

dlist = {'weathering':['weathering',1],
                'gripping':['grip',0],
                'deathsight':['deathsight',100],
                'selfishness':['selfishness',100],
                'curseward':['curseward',0],
                'nightsight':['nightsight',5],
                'third eye':['thirdeye',50],
                'fitness':['fitness',3],
                'resistance':['resistance',2],
                'shroud':['shroud',10],
                'lifevision':['lifevision',15],
                'soulmask':['soulmask',16],
                'putrefaction':['putrefaction',5],
                'deathaura':['deathaura',20]}


class MainModule(BaseModule):
        
        
        combat_channel=3
        combat_channel_name='Military'
        
        def __init__(self, realm):
            BaseModule.__init__(self,realm)
            self.map_mode=False
            self.necromancy=Necromancy(realm)
            self.communicator = communicator.Communicator(MainModule.combat_channel, MainModule.combat_channel_name, realm)
            self.tracker = TrackerModule(realm, self.communicator, True)
            self.shield_track = ShieldRez(realm)
            self.limb_tracker = LimbTrack(realm)
            self.autoparry = Autoparry(realm, self.limb_tracker)
            self.deathknight = Deathknight(realm,self.communicator,
                                           self.tracker,
                                           self.shield_track,
                                           light,shred_infused,
                                           shred_draining,lacerate,
                                           self.autoparry)
            self.mapper= MapFromXml()
            self.location_services=LocationServices(realm, self.mapper)
            self.guards=CitySecurity('squad2')
            #self.limb_tracker = LimbTracker(realm)
            
            self.walker = Walker(realm, self.mapper)
            self.defenses = Defenses(realm, dlist)
            self.basher = autobasher.AutoBasher(manager=realm, heal_command='vigour')
            
        def is_main(self, realm):
            BaseModule.is_main(self, realm)
         
        @property
        def modules(self):
            return[ImperianModule,ChannelHandler, self.necromancy, self.defenses,
                   SelfAfflictions, self.communicator,
                   self.deathknight,
                   self.location_services,
                   self.guards,
                   #self.limb_tracker,
                   ImperianPrompt,
                   self.walker,
                   AutocuringControl,
                   self.tracker,
                   self.shield_track,
                   self.basher,
                   self.limb_tracker,
                   self.autoparry,
                   Alerts]
            

       
    
        