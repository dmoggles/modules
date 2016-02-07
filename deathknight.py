'''
Created on Oct 6, 2015

@author: Dmitry
'''
from pymudclient.modules import   EarlyInitialisingModule
from afflictiontracking.trackingmodule import TrackerModule
from afflictiontracking import communicator
from weaponmastery import LongswordShredWeaponmastery,\
    LongswordLacerateWeaponmastery, WeaponMasteryCommands, SaberWeaponmastery
from pymudclient.gui.keychords import from_string
from pymudclient.aliases import binding_alias
from shield_rez import ShieldRez
from pymudclient.triggers import binding_trigger
from pymudclient.gmcp_events import binding_gmcp_event
from enhancement_flares import EnhancementFlares
import time

def shield_handler(realm, shield_status):
    realm.cwrite('SHIELD HANDLER, SHIELD HANDLER:')
    if realm.get_state('attack_queued'):
        
        realm.send('fc')

class Deathknight(EarlyInitialisingModule):
    '''
    classdocs
    '''


    def __init__(self, realm, communicator, draining_shred_weapon, agony_shred_weapon, lacerate_weapon, saber_weapon):
        self.aff_tracker = TrackerModule(realm, communicator, True)
        self.communicator =communicator
        self.aff_tracker.apply_priorities([('haemophilia',1)])
        #self.shield_track = ShieldRez(realm, shield_handler, shield_handler)
        self.shield_track = ShieldRez(realm)
        self.prev_target=''
        self.next_balance=0
        self.next_equilibrium=0
        self.enhancement_tracker = EnhancementFlares(realm)
        self.haemophilia_combo_counter = 0
        self.skip_counter = 0
        self.realm = realm
        self.display_data={}
        self.display_attack_counter=-1
        self.gags=True
        self.post_combo = False
        self.combo_fired = False
        self.draining_shred_weaponmastery = LongswordShredWeaponmastery(self.shield_track, 
                                                   realm,
                                                   self.aff_tracker,
                                                   draining_shred_weapon,
                                                   self.enhancement_tracker)
        self.agony_shred_weaponmastery = LongswordShredWeaponmastery(self.shield_track, 
                                                                      realm,
                                                                      self.aff_tracker,
                                                                      agony_shred_weapon,
                                                                      self.enhancement_tracker)
        self.lacerate_weaponmastery = LongswordLacerateWeaponmastery(self.shield_track, 
                                                   realm,
                                                   self.aff_tracker,
                                                   lacerate_weapon)
        self.saber_weaponmastery = SaberWeaponmastery(self.shield_track,
                                                              realm,
                                                              self.aff_tracker,
                                                              saber_weapon,
                                                              self.enhancement_tracker)
        
    
        self.realm.registerEventHandler('setTargetEvent', self.on_target_set)
    
    @property
    def modules(self):
        return [WeaponMasteryCommands, self.aff_tracker, self.shield_track,
                self.enhancement_tracker]
    
    @property
    def aliases(self):
        return [self.combo_shred, self.combo_lacerate,
                self.bulwark, self.automated_combo, self.automated_combo_2,
                self.automated_combo_3]
    
    @property
    def triggers(self):
        return [self.trueassess_trigger,
                self.clot, self.on_balance,
                self.on_equilibrium,
                self.bloodscent_enter,
                self.bloodscent_leave,
                self.just_gag,
                self.quickdraw_weapons,
                self.target_nothing,
                self.slash_attack,
                self.lacerate_attack,
                self.shred_attack,
                self.toxin_hit,
                self.on_prompt,
                self.engage,
                self.raze_attack,
                self.teeth,
                self.fleshburn]
    @property
    def macros(self):
        return {'<F1>':'cc1',
                '<F2>':'cc2',
                '<F3>':'fc3',
                '<F12>':'sh',
                '<F11>':'queue eqbal bwind'} 
        
    @property
    def gmcp_events(self):
        return[self.on_char_afflictions_add]
        
    @binding_gmcp_event('Char.Afflictions.Add')
    def on_char_afflictions_add(self, gmcp_data, realm):
        if gmcp_data['name']=='peace':
            realm.send('rage') 
    
    
    @binding_trigger('^You sense through your hound that (\w+) has entered the area.$')
    def bloodscent_enter(self, match, realm):
        player = match.group(1)
        area = realm.root.gmcp['Room.Info']['area']
        self.communicator.player_entered(player, area)    
    
    @binding_trigger('^You sense through your hound that (\w+) has left the area.$')
    def bloodscent_leave(self, match, realm):
        player = match.group(1)
        area = realm.root.gmcp['Room.Info']['area']
        self.communicator.player_left(player, area)
    
    def bwind_macro(self, realm):
        realm.send('queue eqbal bwind')
    
    @binding_trigger('^Autocuring: clot$')
    def clot(self, match,realm):
        realm.safe_send('clot|clot|clot|clot|clot')
    
    def bulwark_macro(self, realm):
        realm.send('sh')
    
    def make_full_combo(self, generator, target, use_soulstorm):
        if not use_soulstorm:
            combo = 'queue eqbal curseward|order hound kill %s|%s|engage %s|trueassess %s|'%(target, generator.get_attack(target), target, target)
        else:
            combo = 'queue eqbal curseward|order hound kill %s|%s|soulstorm %s|trueassess %s|'%(target, generator.get_attack(target), target, target)
        
        return combo
    
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
        self.haemophilia_combo_counter = 0
        self.skip_counter = 0
        
    @binding_alias('^fc3$')
    def automated_combo_3(self, match, realm):
        
        realm.send_to_mud=False
        self.combo_fired = True
        target = realm.root.get_state('target')
        if target=='':
            return
        mp=realm.root.get_state('mp')
        mpmax=realm.root.get_state('maxmp')
        mppct=float(mp)/float(mpmax)
        tracker = self.aff_tracker.tracker(target)
        
        if tracker['haemophilia'].on:
            if self.haemophilia_combo_counter >= 3 and self.enhancement_tracker.fleshburn_cd == 0 and self.shield_track[target].aura == False:
                realm.send(self.make_full_combo(self.lacerate_weaponmastery, target, True))
            else:
                if mppct>0.6 or self.haemophilia_combo_counter == 2:
                    realm.send(self.make_full_combo(self.agony_shred_weaponmastery, target, False))
                else:
                    realm.send(self.make_full_combo(self.draining_shred_weaponmastery, target, False))
        else:
            if   (tracker.time_to_next_tree == 0 and not (tracker['numbness'].on or tracker['paralysis'].on)) or \
                 (tracker.time_to_next_tree == 0 and not tracker['hemotoxin'].on) and\
                 self.skip < 3:
                realm.send(self.make_full_combo(self.saber_weaponmastery, target, False))
                self.skip += 1
            if self.shield_track[target].aura or self.shield_track[target].shield:
                realm.send(self.make_full_combo(self.saber_weaponmastery, target, False))
            elif self.enhancement_tracker.teeth_cd==0:
                if mppct>0.6:
                    realm.send(self.make_full_combo(self.agony_shred_weaponmastery, target, False))
                else:
                    realm.send(self.make_full_combo(self.draining_shred_weaponmastery, target, False))
            else:
                realm.send(self.make_full_combo(self.saber_weaponmastery, target, False))
            
    @binding_alias('^fc2$')
    def automated_combo_2(self, match, realm):
        realm.send_to_mud=False
        target = realm.root.get_state('target')
        realm.root.set_state('attack_queued',True)
        mp=realm.root.get_state('mp')
        mpmax=realm.root.get_state('maxmp')
        mppct=float(mp)/float(mpmax)
        tracker = self.aff_tracker.tracker(target)
        if tracker['haemophilia'].on:
            if tracker['haemophilia'].on_for > 7.5 and self.enhancement_tracker.fleshburn_c==0:
                realm.cwrite('----burst down')
                realm.send(self.make_full_combo(self.lacerate_weaponmastery, target, True))
            else:
                realm.cwrite('----off_shred')
                if mppct>0.6:
                    realm.send(self.make_full_combo(self.agony_shred_weaponmastery, target, False))
                else:
                    realm.send(self.make_full_combo(self.draining_shred_weaponmastery, target, False))
        else:
            if self.shield_track[target].aura or self.shield_track[target].shield:
                realm.cwrite('----Manual rebounding')
                realm.cwrite('-------aura = %s'%self.shield_track[target].aura)
                realm.cwrite('-------shield = %s'%self.shield_track[target].shield)
                realm.send(self.make_full_combo(self.saber_weaponmastery, target, False))
            if mppct>0.6:
                realm.send(self.make_full_combo(self.agony_shred_weaponmastery, target, False))
            else:
                realm.send(self.make_full_combo(self.draining_shred_weaponmastery, target, False))
        
    @binding_alias('^fc$')
    def automated_combo(self, match, realm):
        realm.send_to_mud=False
        target = realm.root.get_state('target')
        realm.root.set_state('attack_queued',True)
        mp=realm.root.get_state('mp')
        mpmax=realm.root.get_state('maxmp')
        mppct=float(mp)/float(mpmax)
        if not target == self.prev_target:
            self.prev_target=target
            self.haemophilia_combo_counter=0
            
        tracker = self.aff_tracker.tracker(target)
        if tracker['haemophilia'].on:
            realm.cwrite('----haemo on')
            self.haemophilia_combo_counter+=1
            if tracker['haemophilia'].on_for > 7.5 and self.enhancement_tracker.fleshburn_c==0:
                realm.cwrite('----burst down')
                realm.send(self.make_full_combo(self.lacerate_weaponmastery, target, True))
            else:
                realm.cwrite('----off_shred')
                if mppct>0.6:
                    realm.send(self.make_full_combo(self.agony_shred_weaponmastery, target, False))
                else:
                    realm.send(self.make_full_combo(self.draining_shred_weaponmastery, target, False))
        else:
            if self.shield_track[target].aura or self.shield_track[target].shield:
                realm.cwrite('----Manual rebounding')
                realm.cwrite('-------aura = %s'%self.shield_track[target].aura)
                realm.cwrite('-------shield = %s'%self.shield_track[target].shield)
                realm.send(self.make_full_combo(self.saber_weaponmastery, target, False))
            #elif (self.aff_tracker.tracker(target).time_to_next_purge() < 2 and not self.aff_tracker.tracker(target)['hemotoxin'].on) or (self.aff_tracker.tracker(target).time_to_next_tree() < 2 and not (self.aff_tracker.tracker(target)['numbness'].on or self.aff_tracker.tracker(target)['paralysis'].on)):
            #    realm.send(self.make_full_combo(self.saber_weaponmastery, target, False))
            elif self.enhancement_tracker.teeth_cd<100:
                realm.cwrite('----teeth cooldown off')
                if mppct>0.6:
                    realm.send(self.make_full_combo(self.agony_shred_weaponmastery, target, False))
                else:
                    realm.send(self.make_full_combo(self.draining_shred_weaponmastery, target, False))
            else:
                if self.haemophilia_combo_counter >= 2:
                    realm.cwrite('----teeth on cooldown, but hit counter threshold')
                    if mppct>0.6:
                        realm.send(self.make_full_combo(self.agony_shred_weaponmastery, target, False))
                    else:
                        realm.send(self.make_full_combo(self.draining_shred_weaponmastery, target, False))
                else:
                    realm.cwrite('----sabre')
                    realm.send(self.make_full_combo(self.saber_weaponmastery, target, False))
            self.haemophilia_combo_counter=0
                
    
    @binding_alias('^sh$')
    def bulwark(self, match,realm):
        realm.send_to_mud = False
        realm.send('queue eqbal curseward|bulwark')
    
    @binding_alias('^cc1$')
    def combo_shred(self, match, realm):
        realm.send_to_mud=False
        target = realm.root.get_state('target')
        realm.send('queue eqbal curseward|order hound kill %s|%s|engage %s|trueassess %s'%(target, self.shred_weaponmastery.get_attack(target),target,target))
        
    @binding_alias('^cc2$')
    def combo_lacerate(self, match, realm):
        realm.send_to_mud=False
        target = realm.root.get_state('target')
        realm.send('queue eqbal curseward|order hound kill %s|%s|soulstorm %s|trueassess %s'%(target, self.lacerate_weaponmastery.get_attack(target), target, target))
    
    @binding_trigger("^(\w+)'s condition stands at (\d+)/(\d+) health and (\d+)/(\d+) mana\.$")
    def trueassess_trigger(self, match, realm):
        if self.gags and self.combo_fired:
            realm.display_line=False
        person = match.group(1).lower()
        hp=int(match.group(2))
        max_hp=int(match.group(3))
        mana=int(match.group(4))
        max_mana=int(match.group(5))
        target = realm.root.get_state('target').lower()
        #realm.send('rt %s: %d/%d HP, %d/%d (%0.0f%%) Mana'%
        #          (person.upper(), hp, max_hp, mana, max_mana, 100*float(mana)/float(max_mana)))
        self.communicator.send_health_mana(person, hp, max_hp, mana, max_mana)
        if target==person and realm.root.gui:
            realm.root.gui.enemy.hp_mana.set_curr_hp(hp)
            realm.root.gui.enemy.hp_mana.set_max_hp(max_hp)
            realm.root.gui.enemy.hp_mana.set_curr_mana(mana)
            realm.root.gui.enemy.hp_mana.set_max_mana(max_mana)
            
        
    
  
            
    
    def shred_macro(self, realm):
        realm.send('cc1')
    
    def lacerate_macro(self, realm):
        realm.send('cc2')
        
    def auto_macro_do(self, realm):
        realm.send('fc3')
        
    def auto_macro(self, realm):
        delay = self.to_eqbal
        if delay > 0.1:
            realm.cwrite('Scheduling AUTO MACRO in <red*>%0.2f<white> seconds'%float(delay))
            realm.root.set_timer(delay-0.1, self.auto_macro_do, realm)
        else:
            self.auto_macro_do(realm)
            
            
            
    #Gags and replacements
    @binding_trigger(['^You already have curseward up\.$',
                      "^Removed defense: \[u'anti-weapon field'\]$",
                      'Added defense: engage',
                      'Your aura of weapons rebounding disappears\.$',
                      '^You have lost the anti-weapon field defence\.$',
                      '^You have gained the engage defence\.$',
                      '^Mana Lost:',
                      '^You order a ravenous hound to attack (\w+)$',
                      '^Your aura of weapons rebounding disappears\.$'
                      '^A ravenous hound obeys your command\.$'
                      '^Your aura of weapons rebounding disappears\.$',
                      '^You rub some (\w+) on (?:a|an) (.*)\.$',
                      '^You are already engaging (\w+)\.$',
                      '^\w+ appears terrified as (?:her|his) muscles seem to become difficult to control\.$'])
    def just_gag(self, match, realm):
        if self.gags and self.combo_fired:
            realm.display_line=False
        
    @binding_trigger('^You secure your previously wielded items and instantly draw (?:a|an) (.*) into your (\w+) hand, with (?:a|an) (.*) flowing into your right hand\.$')
    def quickdraw_weapons(self, match, realm):
        if self.gags and self.combo_fired:
            realm.display_line=False
        item1=match.group(1)
        hand1=match.group(2)
        item2=match.group(3)
        self.display_data['left_hand']=item1 if hand1=='left' else item2
        self.display_data['right_hand']=item1 if hand1=='right' else item2
        
    @binding_trigger('^You will now aim your attacks wherever you see openings\.$')
    def target_nothing(self, match, realm):
        if self.gags and self.combo_fired:
            realm.display_line = False
        self.display_data['limb']='None'
        
    @binding_trigger(['^With a lightning-quick motion, you slash (\w+) with (?:a|an) (.*)\.$',
                      '^You slash viciously into (\w+) with (?:a|an) .*\.$',
                      '^You swing (?:a|an) .* at (\w+) with a powerful strike\.$'])
    def slash_attack(self, match, realm):
        self.single_attack(match.group(1), 'Slash', realm)
    
    @binding_trigger("^You lacerate (\w+)'s skin calmly with the sharp edge of (?:a|an) (.*), amplifying (?:his|her) bleeding wounds\.$")
    def lacerate_attack(self, match, realm):
        self.single_attack(match.group(1), 'Lacerate', realm)
        
    @binding_trigger("You shred (\w+)'s skin viciously with (?:a|an) .*, causing a nasty infection.")
    def shred_attack(self, match, realm):
        self.single_attack(match.group(1), "Shred", realm)
        
    def single_attack(self, target, attack, realm):
        if not self.post_combo:
            if self.aff_tracker.tracker(target)['haemophilia'].on:
                self.haemophilia_combo_counter+=1
            else:
                self.haemophilia_combo_counter=0
        if self.gags and self.combo_fired:
            realm.display_line=False
        self.post_combo=True
        self.display_attack_counter+=1
        self.display_data['target']=target
        if not 'attacks' in self.display_data:
            self.display_data['attacks'] =[]
        if len(self.display_data['attacks']) <= self.display_attack_counter:
            self.display_data['attacks'].append({})
        self.display_data['attacks'][self.display_attack_counter]['attack']=attack
        
        
    @binding_trigger('^Your (\w+) toxin has affected (\w+)\.$')
    def toxin_hit(self, match, realm):
        if self.gags and self.combo_fired:
            realm.display_line = False
        self.display_data['attacks'][self.display_attack_counter]['toxin']=match.group(1)
    
    @binding_trigger('^You move in to engage (\w+)')
    def engage(self, match, realm):
        if self.gags and self.combo_fired:
            realm.display_line=False
        self.display_data['engage']=match.group(1)
    
    @binding_trigger('^H:(\d+) M:(\d+)')
    def on_prompt(self, match, realm):
        
        if self.post_combo:
            self.combo_fired=False
            realm.cwrite(self.build_output())
            self.display_data={}
            self.display_attack_counter=-1
     
            self.post_combo = False
        
    @binding_trigger(['^You raze (\w+)\'s aura of rebounding with .+\.$',
                      '^You whip .+ through the air in front of (\w+), to no effect\.$',
                      '^You raze (\w+)\'s translucent shield with (.*)\.$'])
    def raze_attack(self, match, realm):
        self.single_attack(match.group(1), 'Raze', realm)
  
    @binding_trigger("^As the weapon strikes (\w+), it burns (?:his|her) flesh painfully\.$")
    def fleshburn(self, match, realm):
        if self.gags and self.combo_fired:
            realm.display_line = False
        if 'flares' not in self.display_data['attacks'][self.display_attack_counter]:
            self.display_data['attacks'][self.display_attack_counter]['flares']=[]
        self.display_data['attacks'][self.display_attack_counter]['flares'].append('Fleshburn')
    
    @binding_trigger("^The teeth along the weapon edge cut into (\w+)'s flesh\.$")
    def teeth(self, match, realm):
        if self.gags and self.combo_fired:
            realm.display_line = False
        if 'flares' not in self.display_data['attacks'][self.display_attack_counter]:
            self.display_data['attacks'][self.display_attack_counter]['flares']=[]
        self.display_data['attacks'][self.display_attack_counter]['flares'].append('Teeth')
    
    def build_output(self):
        output=''
        if not 'attacks' in self.display_data:
            return ''
        for data in self.display_data['attacks']:
            output+='\n<white>     [T: <red*> %15s <white>Attack: <'%self.display_data['target']
            if data['attack']=='Slash':
                output+='yellow*>'
            elif data['attack']=='Lacerate':
                output+='purple*>'
            elif data['attack']=='Shred':
                output+='cyan*>'
            elif data['attack']=='Raze':
                output+='white*>'
            output+='%10s<white>'%data['attack']
            if 'toxin' in data:
                output+=' Toxin: <green*> %15s'%data['toxin']
            if 'flares' in data:
                output+=' <white>Enh: '
                flare_texts=[]
                for flare in data['flares']:
                    
                    if flare=='Teeth':
                        flare_texts.append('<black*:white>%10s'%'Teeth')
                    if flare=='Fleshburn':
                        flare_texts.append('<red*:white>%10s'%'Fleshburn')
                output+='<white>,'.join(flare_texts)
            output+='<white>]'
        if 'engage' in self.display_data:
            extras=[]
            output+='\n<white>     ['
            if 'engage' in self.display_data:
                extras.append('<white*:blue>++Engaged++')
                
            output+=','.join(extras)
            output+='<white>]'    
            
        return output
        