'''
Created on Mar 24, 2016

@author: Dmitry
'''
from pymudclient.modules import BaseModule
from pymudclient.library.imperian.people_services import PeopleServices
from pymudclient.library.imperian.player_tracker import PlayerTracker

from pymudclient.aliases import binding_alias
from necromancy import Necromancy
from pymudclient.library.imperian.defenses import Defenses
from pymudclient.library.imperian.imperian import ImperianModule
from pymudclient.library.imperian.channel_handler import ChannelHandler
from self_afflictions import SelfAfflictions
from pymudclient.library.imperian.imperian_prompt import ImperianPrompt
from autocuring_control import AutocuringControl
from pymudclient.library.imperian.alerts import Alerts
from afflictiontracking import communicator
from afflictiontracking.trackingmodule import TrackerModule
from shield_rez import ShieldRez
from pymudclient.library.imperian.limb_tracker import LimbTrack
from pymudclient.library.imperian.autoparry import Autoparry
from movement.map import MapFromXml
from location_service import LocationServices
from security import CitySecurity
from movement.walker import Walker
from imperian import autobasher
from imperian.diabolist import Diabolist



dlist = {'demon armour':['demon armor',1],
         'carved pentagram':['carve pentagram on body',2],
                'deathsight':['deathsight',100],
                'selfishness':['selfishness',100],
                'curseward':['curseward',0],
                'nightsight':['nightsight',5],
                'third eye':['thirdeye',50],
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
        #self.people_service = PeopleServices(realm)
        #self.player_tracker = PlayerTracker(realm, self.people_service)
        self.necromancy=Necromancy(realm)
        self.communicator = communicator.Communicator(MainModule.combat_channel, MainModule.combat_channel_name, realm, "demonic", None)#self.people_service)
        self.tracker = TrackerModule(realm, self.communicator, True)
        self.tracker.apply_priorities([('impatience',0)])
        self.shield_track = ShieldRez(realm)
        self.limb_tracker = LimbTrack(realm)
        self.autoparry = Autoparry(realm, self.limb_tracker)
        
        self.mapper= MapFromXml()
        self.location_services=LocationServices(realm, self.mapper)
        self.guards=CitySecurity('squad2')
        #self.limb_tracker = LimbTracker(realm)
        
        self.walker = Walker(realm, self.mapper)
        self.defenses = Defenses(realm, dlist)
        self.basher = autobasher.AutoBasher(manager=realm, heal_command='vigour')
        self.diabolist = Diabolist(realm, self.tracker, self.shield_track, self.autoparry, self.communicator)
            
    @property
    def modules(self):
        return [ImperianModule,ChannelHandler, self.necromancy, self.defenses,
                   SelfAfflictions, self.communicator,
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
                   Alerts, 
                   #self.people_service,
                   #self.player_tracker,
                   self.diabolist]
        
    @property
    def aliases(self):
        return [self.test_alias]
            
    @binding_alias('test_me')
    def test_alias(self, match, realm):
        realm.cwrite('success!')
            