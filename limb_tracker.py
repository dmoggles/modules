'''
Created on Oct 8, 2015

@author: dmitry
'''
from pymudclient.triggers import binding_trigger
from operator import __getitem__
from pymudclient.modules import EarlyInitialisingModule

class Limb:
    def __init__(self, name):
        self.hits=0
        self.observed_damage=0
        self.implied_damage_per_hit=0
        self.damage=0
        self.name=name
        
    def clear(self):
        self.hits=0
        self.observed_damage=0
        self.implied_damage_per_hit=0
        self.damage=0
    
    def hit(self,mult=1):
        self.hits+=1*mult
        self.damage += self.implied_damage_per_hit*mult
    
    @property
    def hits_left(self):
        if self.implied_damage_per_hit:
            return 1.0 /self.implied_damage_per_hit - self.hits
        return 0  
    
    def set_confirmed_33(self):
        self.observed_damage = .33
        self.implied_damage_per_hit = .33/float(self.hits)
        self.damage = self.hits * self.implied_damage_per_hit
        
    def set_confirmed_66(self):
        self.observed_damage = .66
        self.implied_damage_per_hit = .66/float(self.hits)
        self.damage = self.hits * self.implied_damage_per_hit
        
class Limbs(object):


    def __init__(self, name):
        '''
        Constructor
        '''
        self.name = name
        limbs = [Limb('head'),Limb('torso'),Limb('right arm'), Limb('left arm'), Limb('right leg'), Limb('left leg')]
        self.limbs = {l.name:l for l in limbs}
    
    
    def __getitem__(self, key):
        if key in self.limbs:
            return self.limbs[key]
        else:
            return None

class LimbTracker(EarlyInitialisingModule):
    def __init__(self, realm):
        self.realm=realm
        self.trackers={}
        self.target_body_part = ''
        self.hack_mult=1
    
    def __getitem__(self, key):
        key=key.lower()
        if key in self.trackers:
            return self.trackers[key]
        else:
            self.trackers[key]=Limbs(key)
            return self.trackers[key]
        
    @property
    def triggers(self):
        return [self.limb_hit,
                self.limb_33,
                self.limb_66,
                self.prompt,
                self.set_target, 
                self.tendoncut,
                self.limb_hit_hack]
    
    
    @binding_trigger('You swing a .* at (\w+), calmly severing the tendons in his ([\w ]+)\.$')
    def tendoncut(self, match, realm):
        target = match.group(1).lower()
        bodypart = match.group(2)
        self.__getitem__(target)[bodypart].clear()
    
    @binding_trigger(['^You are aiming your attacks to the ([\w ]+)\.$',
                      '^You will now target the ([\w ]+) of your opponent\.$'])
    def set_target(self, match, realm):
        self.target_body_part=match.group(1)
        
        
    @binding_trigger(["^You slash into (\w+)'s ([\w ]+) with a .*\.$",
                      "^Lightning-quick, you jab (\w+)'s ([\w ]+) with a .*\.$",
                      "^You swing a .* at (\w+)'s ([\w ]+) with all your might\.$"])
    def limb_hit(self, match, realm):
        tracker = self.__getitem__(match.group(1).lower())
        if (tracker[match.group(2).lower()]):
            tracker[match.group(2).lower()].hit()
            
    @binding_trigger("You hack at (\w+)'s ([\w ]+) with a .*\.$")
    def limb_hit_hack(self, match, realm):
        tracker = self.__getitem__(match.group(1).lower())
        if (tracker[match.group(2).lower()]):
            tracker[match.group(2).lower()].hit(mult=self.hack_mult)
    
    @binding_trigger("^(\w+)'s (.+) trembles slightly under the blow\.")
    def limb_33(self, match, realm):
        tracker = self.__getitem__(match.group(1).lower())
        if tracker[match.group(2).lower()]:
            tracker[match.group(2).lower()].set_confirmed_33()
            
    @binding_trigger("^You notice several bruises forming on (\w+)'s (.+)\.$")
    def limb_66(self, match, realm):
        tracker = self.__getitem__(match.group(1).lower())
        if tracker[match.group(2).lower()]:
            tracker[match.group(2).lower()].set_confirmed_66()
            
    @binding_trigger('^H:(\d+) M:(\d+)')
    def prompt(self, match, realm):
        target=realm.root.get_state('target')
        if not target=='':
            tracker = self.__getitem__(target)
            for l in tracker.limbs:
                realm.root.gui.enemy.limb_panel[l].update(tracker.limbs[l].damage,
                                                          tracker.limbs[l].hits_left,
                                                          tracker.limbs[l].observed_damage,
                                                          tracker.limbs[l].hits)