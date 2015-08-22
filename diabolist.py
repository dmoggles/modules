'''
Created on Aug 18, 2015

@author: Dmitry
'''
from pymudclient.modules import EarlyInitialisingModule
from pymudclient.aliases import binding_alias
from evileye import RepeatingEvileyeCombo, Breacher
from pymudclient.modules import BaseModule
from malignosis import Daegger

class Diabolist(BaseModule):
    '''
    classdocs
    '''


    def __init__(self, realm):
        '''
        Constructor
        '''
        BaseModule.__init__(self, realm)
        self.realm=realm
        self.evileye = RepeatingEvileyeCombo(realm)
        self.eq_attack=None
        self.breacher = Breacher(realm)
    
    @property
    def modules(self):
        return [self.evileye, self.breacher, Daegger]
    
    @property
    def aliases(self):
        return [self.combo, self.set_eq_attack]
    
    def attack_combo(self):
        ee_combo = self.evileye.get_combo()
        target = self.realm.state['target']
        if ee_combo == None:
            self.realm.cwrite('<red*> Evileye combo not set!!')
            return
        
        combo = 'deadeyes %s %s %s'%(target,ee_combo[0],ee_combo[1])
        if not self.eq_attack == None:
            combo+='|%s %s'%(self.eq_attack, target)
            
        return 'queue eqbal %s'%combo
    
    @binding_alias('^cc$')
    def combo(self, match, realm):
        realm.send(self.attack_combo())
    
    @binding_alias('^ee seteq (\w+)$')
    def set_eq_attack(self, match, realm):
        realm.send_to_mud=False
        attack = match.group(1)
        if attack=='sap':
            attack='demon sap'
        self.eq_attack=attack
        realm.cwrite('<red*>EQ Attack set to: %s'%self.eq_attack)
        
class MainModule(Diabolist):
    pass