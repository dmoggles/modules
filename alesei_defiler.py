'''
Created on Mar 31, 2016

@author: Dmitry
'''
from pymudclient.modules import BaseModule
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
from pymudclient.library.imperian.imperian import ImperianModule
from pymudclient.library.imperian.channel_handler import ChannelHandler
from self_afflictions import SelfAfflictions
from pymudclient.library.imperian.imperian_prompt import ImperianPrompt
from autocuring_control import AutocuringControl
from pymudclient.library.imperian.alerts import Alerts
from pymudclient.library.imperian.defenses import Defenses

defenses = {'deathsight':['deathsight',100],
            'selfishness':['selfishness',100],
            'curseward':['curseward',0],
            'nightsight':['nightsight',5],
            'third eye':['thirdeye',50],
            'gripping':['grip',1],
            'blooddrinker':['blooddrinker on',10],
            'waterwalking':['shadowbind me with waterwalking',20],
            'shroud':['shadowbind me with shroud',20],
            'confutation':['shadowbind me with confutation',15],
            'regrowth':['shadowbind me with regrowth',15],
            'recuperation':['shadowbind me with recuperation',15]}

class MainModule(BaseModule):
    '''
    classdocs
    '''

    combat_channel=3
    combat_channel_name='Military'


    def __init__(self, client):
        BaseModule.__init__(self, client)
        self.communicator = communicator.Communicator(MainModule.combat_channel, MainModule.combat_channel_name, client, "demonic", None)#self.people_service)
        self.tracker = TrackerModule(client, self.communicator, True)
        self.shield_track = ShieldRez(client)
        self.limb_tracker = LimbTrack(client)
        self.autoparry = Autoparry(client, self.limb_tracker)
        self.mapper= MapFromXml()
        self.location_services=LocationServices(client, self.mapper)
        self.guards=CitySecurity('squad2')
        self.walker = Walker(client, self.mapper)
        self.defenses = Defenses(client, defenses)
        self.basher = autobasher.AutoBasher(manager=client, heal_command='vigour')
                
    @property
    def modules(self):
        return [ImperianModule,ChannelHandler, self.defenses,
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
                   Alerts]