'''
Created on Jan 12, 2016

@author: dmitry
'''
from pymudclient.modules import BaseModule
from pymudclient.aliases import binding_alias
from pymudclient.triggers import binding_trigger

class SoulConsumption(BaseModule):
    '''
    classdocs
    '''


    def __init__(self, manager):
        BaseModule.__init__(self, manager)
        self.status = 'off'
        
    @property
    def aliases(self):
        return [self.soul_consumption]
        
    @property
    def triggers(self):
        return [self.on_equilibrium, self.on_soul_gaze]
    
    @binding_alias('^soul consumption$')
    def soul_consumption(self, match, realm):
        self.status = 'on'
        realm.send_to_mud=False
        realm.send('soul consumption|soul cull')
        
    @binding_trigger(['^You have recovered equilibrium\.$',
                      '^You have recovered balance on all limbs\.$'])
    def on_equilibrium(self, match, realm):
        if self.status == 'on':
            realm.send('soul strike wraith|soul cull|soul gaze')
        
    @binding_trigger('^Your soulstone pulses with the life force of (\d+) souls\.$')
    def on_soul_gaze(self, match, realm):
        souls = int(match.group(1))
        if souls == 12000:
            self.status = 'off'
            realm.send('soul summon')
        