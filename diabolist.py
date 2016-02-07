'''
Created on Aug 18, 2015

@author: Dmitry
'''
from pymudclient.aliases import binding_alias
from evileye import  EvileyePriorityList, EvileyeHealth
from pymudclient.modules import EarlyInitialisingModule
from malignosis import Daegger, Ouroboros, Demons
from afflictiontracking.trackingmodule import TrackerModule
from shield_rez import ShieldRez
from afflictiontracking import communicator
from pymudclient.gui.keychords import from_string

def do_nothing(self, shield_status):
        pass
    
class Diabolist(EarlyInitialisingModule):
    '''
    classdocs
    '''
    

    def __init__(self, realm, communicator):
        '''
        Constructor
        '''
        self.realm=realm
        #self.evileye = RepeatingEvileyeCombo(realm)
        self.eq_attack=None
        #self.breacher = Breacher(realm)
        self.tracker = TrackerModule(realm, communicator, True)
        #self.evileye = EvileyePriorityList(realm, self.tracker)
        self.shield_rez = ShieldRez(realm, do_nothing, do_nothing)
        self.daegger=Daegger(realm, self.tracker)
        self.demons=Demons(realm)
        self.evileye = EvileyeHealth(realm, self.tracker, self.shield_rez, self.daegger)
        
    @property
    def modules(self):
        return [self.evileye, self.daegger, self.tracker, Ouroboros,
                self.shield_rez, self.demons]
    
    @property
    def aliases(self):
        return [self.combo, self.set_eq_attack, self.no_daegger_combo]
    
    @property 
    def macros(self):
        return {from_string('<F1>'):self.combo_macro}
    
    
    def attack_combo(self,with_toxin=True):
        target = self.realm.state['target']
        combo='contemplate %s'%target
        print('demon: %s'%self.demons.active_demon)
        if self.demons.active_demon!=None:
            combo+='|order %s attack %s'%(self.demons.active_demon,target)
        if self.daegger.ready and with_toxin:# and self.shield_rez[target].all_stripped:
            toxin = self.daegger.next_toxin_physical()
            
            daegger_combo = '|daegger hunt %s %s'%(target,toxin)
            combo+=daegger_combo
            
        ee_combo = self.evileye.get_combo(target)
        
        if ee_combo == '':
            self.realm.cwrite('<red*> Evileye combo not set!!')
            return
        combo+="|%s"%ee_combo
        if not self.eq_attack == None:
            combo+='|%s %s'%(self.eq_attack, target)
           
        
        return 'queue eqbal %s'%combo
    
    
    def combo_macro(self, realm):
        realm.send('cc')
        
    
    @binding_alias('^cc$')
    def combo(self, match, realm):
        realm.send_to_mud=False
        realm.send(self.attack_combo())
    
    @binding_alias('^ccd$')
    def no_daegger_combo(self,match,realm):
        realm.send_to_mud=False
        realm.send(self.attack_combo(False))
        
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