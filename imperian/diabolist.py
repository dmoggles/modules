'''
Created on Mar 25, 2016

@author: Dmitry
'''
from pymudclient.modules import EarlyInitialisingModule
from pymudclient.triggers import binding_trigger
from pymudclient.library.imperian.people_services import damage_map
from pymudclient.aliases import binding_alias
import time

evileye_queue = ['impatience',
                 'numbness',
                 'peace',
                 'clumsy',
                 'asthma',
                 'reckless',
                 'addiction',
                 'sensitivity',
                 'vomiting',
                 'masochism',
                 'reckless',
                 'stupid',
                 'dizzy',
                 'dementia',
                 'vertigo',
                 'claustrophobia',
                 'agoraphobia',
                 'anorexia']

hunt_queue = ['metrazol',
              'hemotoxin',
              'ether',
              'xeroderma',
              'butisol',
              'arsenic'
              'avidya',
              'mazanor']



class Breacher(EarlyInitialisingModule):
    def __init__(self):
        self.warded = {}
        
    def get_warded(self,target):
        if not target.lower() in self.warded:
            self.warded[target.lower()]=True
            
        return self.warded[target.lower()]
            
    def set_warded(self,target, state):
        if not target.lower() in self.warded:
            self.warded[target.lower()]=True
            
        self.warded[target.lower()]=state
        
    @property
    def triggers(self):
        return [self.hit_curseward, self.strip_curseward]
    
    
    @binding_trigger(['^You try to give (\w+) the evileye, but (?:he|she) is warded\.$',
                      '^A shimmering curseward appears around (\w+)(?:\.)?$'])
    def hit_curseward(self, match, realm):
        realm.display_line=False
        
        target = realm.root.get_state('target')
        self.set_warded(match.group(1), True)
        realm.root.fireEvent('cursewardEvent',match.group(1).lower(),1)
        
        if match.group(1).lower() == target.lower():
            realm.cwrite('<red*:yellow>Curseward is UP on %s!'%target)
            
            
    @binding_trigger(['^(?:His|Her) curseward has failed!$',
                      '^There is nothing left to breach\.$'])
    def strip_curseward(self, match, realm):
        target = realm.root.get_state('target')
        realm.display_line=False
        self.set_warded(target, False)
        #if realm.root.gui:
        #        realm.root.gui.set_shield('curseward',False)
        realm.root.fireEvent('cursewardEvent',target,0)
        realm.cwrite('<green*:yellow>Curseward is DOWN on %s!'%target)
        
    
    @binding_trigger('You stare at yourself, giving you the evil eye of breach.')
    def strip_curseward_self(self, match, realm):
        target='me'
        self.set_warded(target, False)
        
        
class Diabolist(EarlyInitialisingModule):
    
    def __init__(self, realm, aff_tracker, shield_tracker, autoparry, communicator):
        self.realm = realm
        self.tracker = aff_tracker
        self.shield_tracker = shield_tracker
        self.breacher = Breacher()
        self.next_balance=0
        self.next_equilibrium=0
        self.realm.registerEventHandler('setTargetEvent', self.on_target_set)
        self.autoparry = autoparry
        self.communicator = communicator
        
        
        
    @property
    def modules(self):
        return[self.breacher]
    
    @property
    def triggers(self):
        return [self.evileye_affliction,
                self.clot,
                self.on_balance,
                self.on_equilibrium,
                self.trueassess_trigger
                ]
    
    @property 
    def aliases(self):
        return [self.pk,
                self.auto_macro]
        
    @property
    def macros(self):
        return {'<F1>':'delayed pk'}
    
    @binding_trigger('^Autocuring: clot$')
    def clot(self, match,realm):
        realm.safe_send('clot|clot|clot|clot|clot')
    
    
    
    
    
    @binding_trigger('^Balance Taken: (\d+\.\d+)s$')
    def on_balance(self, match, realm):
        #realm.root.set_state('attack_queued',False)
        self.next_balance=time.time()+float(match.group(1))
       
    @binding_trigger('^Equilibrium Taken: (\d+\.\d+)s$')
    def on_equilibrium(self, match,realm):
        self.next_equilibrium=time.time()+float(match.group(1))
    
    @property
    def to_balance(self):
        return max(0, self.next_balance-time.time())
    
    @property
    def to_equilibrium(self):
        return max(0, self.next_equilibrium-time.time())
    
    @property
    def to_eqbal(self):
        return max(self.to_balance, self.to_equilibrium)    
        
        
    def on_target_set(self, target):
        self.tracker.tracker(target).reset()
    
    def auto_macro_do(self, realm, command):
        realm.send(command)
        
        
    
        
    @binding_alias('^delayed (\w+)$')
    def auto_macro(self, matches, realm):
        command = matches.group(1)
        realm.send_to_mud = False
        delay = self.to_eqbal
        if delay > 0.1:
            realm.cwrite('Scheduling AUTO MACRO in <red*>%0.2f<white> seconds'%float(delay))
            realm.root.set_timer(delay-0.1, self.auto_macro_do, command)
        else:
            self.auto_macro_do(realm, command) 
            
            
    @binding_trigger('^You stare at (\w+), giving (?:him|her) the evil eye of (\w+)\.$')
    def evileye_affliction(self, match, realm):
        target = match.group(1)
        aff = match.group(2)
        
        t=self.tracker.tracker(target)
        t.add_aff(aff)    
    
    def get_evileye_pair(self, target):
        tracker = self.tracker.tracker(target)
        target_class = self.realm.get_state('target_prof')
        affs=[]
        if self.breacher.get_warded(target):
            affs.append('breach')
        if self.shield_tracker[target].aura:
            affs.append('breach')
        if self.shield_tracker[target].shield:
            affs.append('breach')
        for a in evileye_queue:
            if a == 'peace' and target_class.lower() in ['ranger','amazon','berserker','deathknight','runeguard','templar']:
                continue
            if a == 'numbness' and tracker['paralysis'].on:
                continue
            if not tracker[a].on and tracker[a].usable:
                affs.append(a)
        affs.append('sensitivity')
        affs.append('recklessness')
        return affs[:2]
    
    
    def get_hunt_aff(self, target, realm):
        tracker = self.tracker.tracker(target)
        profession = realm.root.get_state('target_prof')
        if profession == '' or profession in damage_map['physical']:
            dmg_type = 'p'
        else:
            dmg_type = 'm'
        for a in hunt_queue:
            if not tracker[a].on:
                if a=='ether' and dmg_type == 'm':
                    return 'avidya'
                else:
                    return a
        
        return 'strychnine'
    
    
    @binding_trigger("^(\w+)'s condition stands at (\d+)/(\d+) health and (\d+)/(\d+) mana\.$")
    def trueassess_trigger(self, match, realm):
        #if self.gags and self.combo_fired:
        #    realm.display_line=False
        person = match.group(1).lower()
        hp=int(match.group(2))
        max_hp=int(match.group(3))
        mana=int(match.group(4))
        max_mana=int(match.group(5))
        target = realm.root.get_state('target').lower()
        #realm.send('rt %s: %d/%d HP, %d/%d (%0.0f%%) Mana'%
        #          (person.upper(), hp, max_hp, mana, max_mana, 100*float(mana)/float(max_mana)))
        self.communicator.send_health_mana(person, hp, max_hp, mana, max_mana)
        if target==person:
            realm.root.fireEvent('targetStatUpdateEvent','hp',hp)
            realm.root.fireEvent('targetStatUpdateEvent','mana',mana)
            realm.root.fireEvent('targetStatUpdateEvent','hp_max',max_hp)
            realm.root.fireEvent('targetStatUpdateEvent','mana_max',max_mana)
            
        
    
  
            
    
    def combo(self, realm):
        target = realm.root.get_state('target')
        parry = self.autoparry.evaluate_parry()
        combo = ''
        if parry!='':
            combo = 'parry %s'%parry
            
        combo += 'light pipes|enemy %(target)s|stand|order nightmare kill %(target)s'%{'target':target}
        ee = self.get_evileye_pair(target)
        hunt = self.get_hunt_aff(target, realm)
        combo+='|daegger hunt %(target)s %(toxin)s'%{'target':target,
                                                     'toxin':hunt}
        
        combo+='|deadeyes %(target)s %(ee1)s %(ee2)s'%{'target':target,
                                                        'ee1':ee[0],
                                                        'ee2':ee[1]}
        combo+='|trueassess %s'%target
        
        
        return combo
        
    @binding_alias('^pk$')
    def pk(self, match, realm):
        realm.send_to_mud = False
        combo = self.combo(realm)
       
        realm.send('queue eqbal %s'%combo)
        
    
    
        