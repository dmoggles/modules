'''
Created on Mar 25, 2016

@author: Dmitry
'''
from pymudclient.modules import EarlyInitialisingModule
from pymudclient.triggers import binding_trigger
from pymudclient.library.imperian.people_services import damage_map
from pymudclient.aliases import binding_alias
from pymudclient.library.imperian.combat_module import ImperianCombatModule

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
        
        
class Diabolist(ImperianCombatModule):
    
    def __init__(self, realm, aff_tracker, shield, autoparry, communicator):
        ImperianCombatModule.__init__(self, realm, aff_tracker, shield, None, autoparry, communicator)
        self.breacher = Breacher()
        
        
        
    @property
    def modules(self):
        return[self.breacher]
    
    @property
    def triggers(self):
        tr = ImperianCombatModule.triggers(self)
        return tr+[self.evileye_affliction]
    
    @property 
    def aliases(self):
        al = ImperianCombatModule.aliases(self)
        return al+[self.pk]
        
    @property
    def macros(self):
        return {'<F1>':'delayed pk'}
    
    
    
    
    
            
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
        if self.shield[target].aura:
            affs.append('breach')
        if self.shield[target].shield:
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
    
    
    
    
  
            
    
    def combo(self, realm):
        target = realm.root.get_state('target')
            
        combo = 'order nightmare kill %(target)s'%{'target':target}
        ee = self.get_evileye_pair(target)
        hunt = self.get_hunt_aff(target, realm)
        combo+='|daegger hunt %(target)s %(toxin)s'%{'target':target,
                                                     'toxin':hunt}
        
        combo+='|deadeyes %(target)s %(ee1)s %(ee2)s'%{'target':target,
                                                        'ee1':ee[0],
                                                        'ee2':ee[1]}
        
        
        return combo
        
    @binding_alias('^pk$')
    def pk(self, match, realm):
        realm.send_to_mud = False
        combo = self.combo(realm)
       
        self.send_combo(realm, combo)
        
    
    
        