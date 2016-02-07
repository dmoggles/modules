'''
Created on Jul 15, 2015

@author: Dmitry
'''
from pymudclient.modules import BaseModule

from pymudclient.net.gmcp import ImperianGmcpHandler


from pymudclient.library.html import HTMLLoggingModule
from pymudclient.library.imperian.imperian import ImperianModule
from pymudclient.library.imperian.imperian_prompt import ImperianPrompt
from pymudclient.library.imperian.channel_handler import ChannelHandler
from necromancy import Necromancy
from defenses import Defenses
from self_afflictions import SelfAfflictions
from afflictiontracking import communicator
from deathknight import Deathknight
from location_service import LocationServices
from security import CitySecurity
from limb_tracker import LimbTracker
from movement.map import MapFromXml
from movement.walker import Walker
from autocuring_control import AutocuringControl

shred_agony = '174566'
shred_draining = '193509'
lacerate = '226085'
sabre = 'sabre'



class MainModule(HTMLLoggingModule):
        name = 'Alesei_deathknight'
        host = 'imperian.com'
        port = 23
        
        combat_channel=3
        combat_channel_name='Military'
        
        def __init__(self, realm):
            BaseModule.__init__(self,realm)
            self.map_mode=False
            self.necromancy=Necromancy(realm)
            self.communicator = communicator.Communicator(MainModule.combat_channel, MainModule.combat_channel_name, realm)
            self.deathknight = Deathknight(realm, self.communicator, shred_draining, shred_agony, lacerate, sabre)
            self.location_services=LocationServices(realm)
            self.guards=CitySecurity('squad2')
            self.limb_tracker = LimbTracker(realm)
            self.mapper= MapFromXml()
            self.walker = Walker(realm, self.mapper)
            
        def is_main(self, realm):
            HTMLLoggingModule.is_main(self, realm)
         
        @property
        def modules(self):
            return[ImperianModule,ChannelHandler, self.necromancy, Defenses,
                   SelfAfflictions, self.communicator,
                   self.deathknight,
                   self.location_services,
                   self.guards,
                   self.limb_tracker,
                   ImperianPrompt,
                   self.walker,
                   AutocuringControl]
            
        @property
        def gmcp_handler(self):
            return ImperianGmcpHandler
       
    
        