'''
Created on Jul 15, 2015

@author: Dmitry
'''
from pymudclient.modules import BaseModule, load_file
from pymudclient.aliases import binding_alias
from pymudclient.triggers import binding_trigger
from pymudclient.net.gmcp import ImperianGmcpHandler

from BashModule import BashModule
from sys import modules
from pymudclient.metaline import Metaline, RunLengthList
from pymudclient.colours import fg_code, bg_code, BLACK, RED, CYAN
from pymudclient.tagged_ml_parser import taggedml
from pymudclient.library.html import HTMLLoggingModule
from runeguard import Runeguard
from pymudclient.gmcp_events import binding_gmcp_event
from pymudclient.library.imperian.imperian import ImperianModule
from pymudclient.library.imperian.channel_handler import ChannelHandler



class MainModule(HTMLLoggingModule):
        name = 'Ailish'
        host = 'imperian.com'
        port = 23
        
        def __init__(self, realm):
            BaseModule.__init__(self,realm)
            self.map_mode=False
            
            
        
            
        def is_main(self, realm):
            HTMLLoggingModule.is_main(self, realm)
         
        @property
        def modules(self):
            return[ImperianModule, ChannelHandler]
            
        @property
        def gmcp_handler(self):
            return ImperianGmcpHandler
       
    
        