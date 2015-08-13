'''
Created on Aug 3, 2015

@author: dmitry
'''
from pymudclient.modules import EarlyInitialisingModule
from pymudclient.aliases import binding_alias

class RingAnnouncer(EarlyInitialisingModule):
    '''
    classdocs
    '''

    def __init__(self, realm):
        '''
        Constructor
        '''
        self.manager=realm
        self.on=False
    
    @property
    def aliases(self):
        return [self.announce_on, self.announce_off]
    
    @binding_alias('announce_on')
    def announce_on(self, match, realm):
        self.on=True
        realm.send_to_mud=False
        realm.cwrite('<red>~~~~~~RT Announcing ON!~~~~~~')
    
    @binding_alias('announce_off')
    def announce_off(self, match, realm):
        self.on=False
        realm.send_to_mud=False
        realm.cwrite('<red>~~~~~~RT Announcing OFF!~~~~~~')
        
    def announce(self, msg):
        if self.on:
            self.manager.send('rt %s'%msg)
        