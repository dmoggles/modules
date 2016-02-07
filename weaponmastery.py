'''
Created on Oct 6, 2015

@author: Dmitry
'''
from pymudclient.modules import EarlyInitialisingModule, BaseModule
from shield_rez import ShieldRez
from pymudclient.aliases import binding_alias
import limb_tracker
import enhancement_flares



    
class WeaponMasteryCommands(BaseModule):
    
    @property
    def aliases(self):
        return [self.cleave,
                self.sunder,
                self.impale,
                self.disembowel,
                self.arc,
                self.barge,
                self.lunge]
    
    def single_command_alias(self, match, realm, command):
        realm.send_to_mud=False
        target=realm.root.get_state('target')
        realm.send('queue eqbal %s %s'%(command, target))
    
    
    @binding_alias('^clea$')
    def cleave(self, match, realm):
        realm.send_to_mud=False
        target=realm.root.get_state('target')
        realm.send('acoff')
        realm.send('queue eqbal cleave %s'%target)
        
        
    @binding_alias('^sund$')
    def sunder(self, match, realm):
        realm.send('acoff')
        self.single_command_alias(match, realm, 'sunder')
        
    @binding_alias('^impa$')
    def impale(self, match, realm):
        self.single_command_alias(match, realm, 'impale')
        
    @binding_alias('^dise$')
    def disembowel(self, match, realm):
        self.single_command_alias(match, realm, 'disembowel')
        
    @binding_alias('^aoe$')
    def arc(self, match, realm):
        realm.send_to_mud=False
        realm.send('queue eqbal quickdraw broadsword shield|arc')
    
    @binding_alias('^bar(ne|n|nw|w|sw|s|se|e|ou|in|up|do)$')
    def barge(self, match, realm):
        realm.send_to_mud = False
        target = realm.root.get_state('target')
        direction = match.group(1)
        realm.send('queue eqbal barge %s %s'%(target, direction))
    
    @binding_alias('^lun(ne|n|nw|w|sw|s|se|e|ou|in|up|do)$')
    def lunge(self, match, realm):
        realm.send_to_mud = False
        target = realm.root.get_state('target')
        direction = match.group(1)
        realm.send('queue eqbal lunge %s %s'%(target, direction))
    
class Weaponmastery(EarlyInitialisingModule):
    


    def __init__(self, shield_track, realm, limb_damage=None):
        '''
        @type shield_track: ShieldRez
        '''
        
        self.shield_track = shield_track
        self.limb_damage = limb_damage
        self.realm = realm
     
    
        
        
    def get_toxins(self, n_toxins, target):
        pass
       
    def get_target(self):
        return "target nothing"
    
    def get_combo(self, weapon, attack1, attack2, target):
        shields=0
        if self.shield_track[target].aura:
            shields +=1
        if self.shield_track[target].shield: 
            shields +=1
        
        if shields > 0:
            attack1='raze'
        if shields > 1:
            attack2 = 'raze'
        non_shields = 2 - shields
        toxins = self.get_toxins(non_shields, target)
        target_string = self.get_target()
        combo_string = 'quickdraw %s shield|%s|combo %s %s %s %s'%(weapon, target_string, attack1, attack2, target, ' '.join(toxins))
        return combo_string

#class ScimitaryWeaponmastery(Weaponmastery):
#    def __init__(self, shield_track, realm, limb_damage, ):
#        Weaponmastery.__init__(self, shield_track, realm, limb_damage)
        
        


class LongswordWeaponmastery(Weaponmastery):
    def __init__(self, shield_track, realm, aff_tracker, weapon):
        Weaponmastery.__init__(self, shield_track, realm)
        self.aff_tracker = aff_tracker
        self.weapon = weapon
        
class LongswordLacerateWeaponmastery(LongswordWeaponmastery):
    def __init__(self, shield_track, realm, aff_tracker, weapon):
        LongswordWeaponmastery.__init__(self, shield_track, realm, aff_tracker, weapon)
         
    def get_attack(self, target):
        return self.get_combo(self.weapon, 'lacerate', 'lacerate', target)

    def get_toxins(self, n_toxins, target):
        toxins=[]
        tracker = self.aff_tracker.tracker(target)
        
        if not tracker['stupidity'].on:
            toxins.append('aconite')
        
        
        if not tracker['sensitivity'].on and not tracker.deaf:
            toxins.append('strychnine')
        if not tracker['sunallergy'].on:
            toxins.append('xeroderma')
        if tracker.tlocked and not tracker['cyanide'].on:
            toxins.append('cyanide')
        if not (tracker['numbness'].on or tracker['paralysis'].on):
            toxins.append('ciguatoxin')
        if not tracker['hemotoxin'].on and tracker.time_to_next_purge() < 3:
            toxins.append('hemotoxin')
        if not tracker['vomiting'].on:
            toxins.append('botulinum')
        
        if not tracker['asthma'].on:
            toxins.append('mercury')
        if not tracker['metrazol'].on:
            toxins.append('metrazol')
        if not tracker['clumsiness'].on:
            toxins.append('ether')
        if not tracker['weariness'].on:
            toxins.append('arsenic')
        if not tracker['epilepsy'].on:
            toxins.append('chloroform')
        if not tracker['butisol'].on:
            toxins.append('butisol')
       
            
            
        
        if 'strychnine' in toxins[:n_toxins] and tracker.deaf:
            return ['strychnine','strychnine']
        else:
            return toxins[:n_toxins]
         
         

class LongswordShredWeaponmastery(LongswordWeaponmastery):
    def __init__(self, shield_track, realm, aff_tracker, weapon, enhancement_cds):
        LongswordWeaponmastery.__init__(self, shield_track, realm, aff_tracker, weapon)
        self.enhancements = enhancement_cds
    
    def get_attack(self, target):
        tracker = self.aff_tracker.tracker(target)
        self.attack_status='shred'
        if tracker['haemophilia'].on:
            return LongswordWeaponmastery.get_combo(self, self.weapon, 'slash', 'lacerate', target)
        else:
            return LongswordWeaponmastery.get_combo(self, self.weapon, 'slash', 'shred', target)
        
        
    def get_target(self):
        return "target nothing"
    #def get_shred(self, target):
    #    tracker = self.aff_tracker.tracker(target)
    #    self.attack_status='shred'
    #    if tracker['haemophilia'].on:
    #        return self.get_combo(self.shred_weapon, 'slash', 'slash', target)
    #    else:
    #        return self.get_combo(self.shred_weapon, 'slash', 'shred', target)
    
    #def get_lacerate(self, target):
    #    self.attack_status='lacerate'
    #    return self.get_combo(self.lacerate_weapon, 'lacerate', 'lacerate', target)
        
    def get_toxins(self, n_toxins, target):
        toxins=[]
        tracker = self.aff_tracker.tracker(target)
        if tracker['madness'].on:
            if not tracker['anorexia'].on:
                toxins.append('bromine')
            if not tracker['recklessness'].on:
                toxins.append('atropine')
            if not tracker['stupidity'].on:
                toxins.append('aconite')
        if tracker.tlocked and not tracker['cyanide'].on:
            toxins.append('cyanide')
        if not (tracker['numbness'].on or tracker['paralysis'].on):
            toxins.append('ciguatoxin')
        
        if not tracker['hemotoxin'].on and tracker.time_to_next_purge() < 3:
            toxins.append('hemotoxin')
        if not tracker['sunallergy'].on:
            toxins.append('xeroderma')
        if not tracker['vomiting'].on:
            toxins.append('botulinum') 
        
        if not tracker['asthma'].on:
            toxins.append('mercury')
        if not tracker['clumsiness'].on:
            toxins.append('ether')
        if not tracker['weariness'].on:
            toxins.append('arsenic')
        
        if not tracker['anorexia'].on and tracker['slickness'].on and (tracker['hemotoxin'].on or tracker.time_to_next_purge() > 2) and tracker['impatience'].on:
            toxins.append('bromine')
        if not tracker['slow_balance'].on and tracker['asthma'].on and (tracker['hemotoxin'].on or tracker.time_to_next_purge() > 2):
            toxins.append('noctec')
        if not tracker['slickness'].on and tracker['asthma'].on and (tracker['hemotoxin'].on or tracker.time_to_next_purge() > 2):
            toxins.append('iodine')
        if not tracker['slow_elixirs'].on and tracker['slickness'].on and (tracker['hemotoxin'].on or tracker.time_to_next_purge() > 2):
            toxins.append('luminal')
        if not tracker['slow_herbs'].on and tracker['slickness'].on and (tracker['hemotoxin'].on or tracker.time_to_next_purge() > 2):
            toxins.append('mazanor')
        if not tracker['calotropis'].on and tracker['slickness'].on and (tracker['hemotoxin'].on or tracker.time_to_next_purge() > 2):
            toxins.append('calotropis')
        
        
        
        if not tracker['metrazol'].on:
            toxins.append('metrazol')
        
        
        
       
        if not tracker['sensitivity'].on:
            toxins.append('strychnine')
        if not tracker['epilepsy'].on:
            toxins.append('chloroform')
        if not tracker['butisol'].on:
            toxins.append('butisol')
       
            
            
        
        if 'strychnine' in toxins[:n_toxins] and tracker.deaf:
            return ['strychnine','strychnine']
        else:
            return toxins[:n_toxins]
            


class SaberWeaponmastery(LongswordShredWeaponmastery):
    def __init__(self, shield_track, realm, aff_tracker, weapon, enhancements):
        LongswordShredWeaponmastery.__init__(self, shield_track, realm, aff_tracker, weapon,enhancements)
     
    def get_attack(self, target):
        return self.get_combo(self.weapon, 'slash', 'slash', target)
     
    def get_target(self):
        return "target nothing"   
#     def get_toxins(self, n_toxins, target):
#         toxins=[]
#         tracker = self.aff_tracker.tracker(target)
#         if tracker['madness'].on:
#             if not tracker['anorexia'].on:
#                 toxins.append('bromine')
#             if not tracker['recklessness'].on:
#                 toxins.append('atropine')
#             if not tracker['stupidity'].on:
#                 toxins.append('aconite')
#         if tracker.tlocked and not tracker['cyanide'].on:
#             toxins.append('cyanide')
#         if not tracker['anorexia'].on and tracker['slickness'].on and (tracker['hemotoxin'].on or tracker.time_to_next_purge() > 2) and tracker['impatience'].on:
#             toxins.append('bromine')
#         if not tracker['slow_balance'].on and tracker['asthma'].on and (tracker['hemotoxin'].on or tracker.time_to_next_purge() > 2):
#             toxins.append('noctec')
#         if not tracker['slickness'].on and tracker['asthma'].on and (tracker['hemotoxin'].on or tracker.time_to_next_purge() > 2):
#             toxins.append('iodine')
#         if not tracker['slow_elixirs'].on and tracker['slickness'].on and (tracker['hemotoxin'].on or tracker.time_to_next_purge() > 2):
#             toxins.append('luminal')
#         if not tracker['slow_herbs'].on and tracker['slickness'].on and (tracker['hemotoxin'].on or tracker.time_to_next_purge() > 2):
#             toxins.append('mazanor')
#         if not tracker['calotropis'].on and tracker['slickness'].on and (tracker['hemotoxin'].on or tracker.time_to_next_purge() > 2):
#             toxins.append('calotropis')
#         if not tracker['clumsiness'].on:
#             toxins.append('ether')
#         if not tracker['sunallergy'].on:
#             toxins.append('xeroderma')
#         if not tracker['metrazol'].on:
#             toxins.append('metrazol')
#         if not tracker['weariness'].on:
#             toxins.append('arsenic')
#         if not tracker['asthma'].on:
#             toxins.append('mercury')
#         if not (tracker['numbness'].on or tracker['paralysis'].on):
#             toxins.append('ciguatoxin')
#         
#         if not tracker['hemotoxin'].on and tracker.time_to_next_purge() < 3:
#             toxins.append('hemotoxin')
#         
#         
#         
#         if not tracker['vomiting'].on:
#             toxins.append('botulinum') 
#         
#         if not tracker['sensitivity'].on:
#             toxins.append('strychnine')
#         if not tracker['epilepsy'].on:
#             toxins.append('chloroform')
#         if not tracker['butisol'].on:
#             toxins.append('butisol')
#        
#             
#             
#         
#         if 'strychnine' in toxins[:n_toxins] and tracker.deaf:
#             return ['strychnine','strychnine']
#         else:
#             return toxins[:n_toxins]