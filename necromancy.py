'''
Created on Aug 13, 2015

@author: Dmitry
'''
from pymudclient.modules import EarlyInitialisingModule
from pymudclient.triggers import binding_trigger

class Necromancy(EarlyInitialisingModule):
    '''
    classdocs
    '''


    def __init__(self, realm):
        '''
        Constructor
        '''
        self.realm=realm
        
    
    @property
    def triggers(self):
        return [self.gags]
    
    @binding_trigger(['Your essence slowly drains as you maintain your putrefaction\.',
                      'You gag a bit as you inhale your own stink\.',
                      'Your essence slowly drains away as you strain to maintain your aura of death\.'])
    def gags(self, match, realm):
        realm.display_group = False
        
    