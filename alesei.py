'''
Created on Jul 15, 2015

@author: Dmitry
'''
from pymudclient.modules import BaseModule

from pymudclient.net.gmcp import ImperianGmcpHandler


from pymudclient.library.html import HTMLLoggingModule
from pymudclient.library.imperian.imperian import ImperianModule
from pymudclient.library.imperian.channel_handler import ChannelHandler
from necromancy import Necromancy
from defenses import Defenses
from self_afflictions import SelfAfflictions
from diabolist import Diabolist



class MainModule(HTMLLoggingModule):
        name = 'Alesei'
        host = 'imperian.com'
        port = 23
        
        def __init__(self, realm):
            BaseModule.__init__(self,realm)
            self.map_mode=False
            self.necromancy=Necromancy(realm)
            
            
        
            
        def is_main(self, realm):
            HTMLLoggingModule.is_main(self, realm)
         
        @property
        def modules(self):
            return[ImperianModule,ChannelHandler, self.necromancy, Defenses,
                   SelfAfflictions, Diabolist]
            
        @property
        def gmcp_handler(self):
            return ImperianGmcpHandler
       
    
        