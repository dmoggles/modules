'''
Created on Apr 1, 2016

@author: dmitrymogilevsky
'''
from pymudclient.modules import EarlyInitialisingModule
from pymudclient.triggers import binding_trigger



class Defiler(EarlyInitialisingModule):
    def __init__(self, client, shield, tracker, limb, parry):
        self.client = client
        self.shield = shield
        self.tracker = tracker
        self.limb = limb
        self.parry = parry
        
        self.entropy={}
        self.seeds={}
        
        
    @property
    def triggers(self):
        return [self.entropy_given]
        
    @binding_trigger('^You lean torwards (\w+) with a contemptous sneer and whisper a few words\.')
    def entropy_given(self, match, realm):
        realm.root.debug('entropy')
        target = match.group(1).lower()
        self.tracker.tracker(target).add_aff('entropy')
        