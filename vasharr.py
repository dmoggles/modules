'''
Created on Feb 9, 2016

@author: Dmitry
'''
from pymudclient.library.html import HTMLLoggingModule
from pymudclient.library.accessibility import ScreenreaderProtocol
from pymudclient.modules import BaseModule
from afflictiontracking import communicator
from shield_rez import ShieldRez
from afflictiontracking.trackingmodule import TrackerModule
from imperian import autobasher
import pymudclient


name = 'Alesei'
host = 'imperian.com'
port = 23
encoding = 'ascii'
gmcp_handshakes=['Core.Hello { "client": "pymudclient", "version": "'+ pymudclient.__version__ +'" }',
                 'Core.Supports.Set [ "Core 1", "Char 1", "Char.Name 1", "Char.Skills 1", "Char.Items 1", "Comm.Channel 1", "Redirect 1", "Room 1", "IRE.Rift 1", "IRE.Composer 1" ]']
use_blocks = True


def configure(realm):
    HTMLLoggingModule(realm) #disable if you don't want HTML logging
    ScreenreaderProtocol(realm)
    
    
def gui_configure(realm):
    realm.extra_gui=None
    
    
    
class MainModule(BaseModule):

    combat_channel=3
    combat_channel_name='Military'
    
    def __init__(self, manager):
        BaseModule.__init__(self, manager)
        #mapper = MapFromXml('http://www.imperian.com/maps/map.xml') ENABLE THESE TWO LINES IF YOU WANT MY AUTO WALKER
        #self.walker = Walker(manager, mapper)
        
        self.communicator = communicator.Communicator(MainModule.combat_channel, MainModule.combat_channel_name, manager)
        self.shield_rez = ShieldRez(manager)
        self.aff_tracker = TrackerModule(manager, self.communicator, True)
        #self.basher = autobasher.AutoBasher(manager)
        
    def is_main(self, realm):
            BaseModule.is_main(self, realm)
            
            
    @property
    def modules(self):
        return [self.communicator
                ,self.shield_rez
                ,self.aff_tracker
                #,self.basher
                ]
