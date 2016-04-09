'''
Created on Apr 1, 2016

@author: dmitrymogilevsky
'''

from pymudclient.triggers import binding_trigger
from pymudclient.library.imperian.combat_module import ImperianCombatModule

from pymudclient.tagged_ml_parser import taggedml
from pymudclient.aliases import binding_alias
import time

class Saps:
    saps_reset=30
    colors={'psy':'<purple>',
            'fir':'<red*>',
            'mag':'<blue*>',
            'col':'<blue>',
            'asp':'<yellow*>',
            'poi':'<green*>',
            'ele':'<white*>'}
    
    def __init__(self, client, name):
        self.client=client
        self.saps={}
        self.name=name
        
    def add_sap(self, realm, sap):
        sap=sap.lower()[:3]
        if sap in self.saps:
            self.saps[sap].reset(Saps.saps_reset)
        else:
            self.saps[sap] = realm.root.set_timer(Saps.saps_reset, self.reset_sap, sap)
        realm.cwrite('<purple:grey>[[SAP: <orange*:grey> %(name)s <red*:grey>: <purple*:grey> %(sap)s<red*:grey>]]'%{'name':self.name,
                                                                                                                    'sap':sap})
        
    
    def get_saps(self):
        return self.saps.keys()
    
    def has_sap(self, sap):
        sap=sap.lower()[:3]
        return sap in self.saps
    
    def reset_sap(self, realm, sap):
        sap = sap.lower()[:3]
        if sap in self.saps:
            if self.saps[sap].active():
                self.saps[sap].cancel()
            del self.saps[sap]
            realm.cwrite('<purple:grey>[[SAP REMOVED: <orange*:grey> %(name)s <red*:grey>: <purple*:grey> %(sap)s<red*:grey>]]'%{'name':self.name,
                                                                                                                    'sap':sap})
    def reset(self, realm):
        for sap in self.saps.copy():
            self.reset_sap(realm, sap)
    
    def get_color_coded_string(self):
        if len(self.saps)==0:
            return ''
        
        ccs='<white>['
        for k in self.saps.keys():
            ccs+=Saps.colors[k]+'*'
            
        ccs+='<white>]'
        return ccs
    
class Entropy:
    entropy_reset = 76
    def __init__(self, client, name):
        self.client=client
        self.entropy = 0
        self.name=name
        self.removal_timer = None
        
    def set_entropy(self, entropy):
        self.entropy = entropy
        if self.removal_timer and self.removal_timer.active():
            self.removal_timer.cancel()
        self.removal_timer = self.client.set_timer(Entropy.entropy_reset, self.reset)
        
    def reset(self, realm):
        if self.entropy>0:
            realm.cwrite('<red*:grey>[[ENTROPY: <red*:grey>%(name)s<orange*:grey>: <green*:grey> %(amount)d<red*:grey>]]'%{'name':self.name,
                                                                                                           'amount':0})
        self.entropy=0
        if self.removal_timer and self.removal_timer.active():
            self.removal_timer.cancel()
        self.removal_timer=None
        
        

class Seeds:
    seed_delay = 148
    def __init__(self, client, name):
        self.client = client
        self.seeds={}
        self.name=name
        
        
    def add_seed(self, realm, seed, how):
        seed=seed.lower()[:3]
        if seed in self.seeds:
            self.seeds[seed].reset(Seeds.seed_delay)
        else:
            self.seeds[seed] = realm.root.set_timer(Seeds.seed_delay, self.reset_seed, seed)
        realm.cwrite('<red*:grey>[[SEED %(how)s: <orange*:grey> %(name)s <red*:grey>: <green*:grey> %(seed)s<red*:grey>]]'%{'name':self.name,
                                                                                                                    'seed':seed,
                                                                                                                    'how':how.upper()})
        
    
    def get_seeds(self):
        return self.seeds.keys()
    
    def has_seed(self, seed):
        seed=seed.lower()[:3]
        return seed in self.seeds
    
    def reset_seed(self, realm, seed):
        seed = seed.lower()[:3]
        if seed in self.seeds:
            if self.seeds[seed].active():
                self.seeds[seed].cancel()
            del self.seeds[seed]
            realm.cwrite('<red*:grey>[[SEED REMOVED: <orange*:grey> %(name)s <red*:grey>: <green*:grey> %(seed)s<red*:grey>]]'%{'name':self.name,
                                                                                                                    'seed':seed})

    def reset(self, realm):
        for seed in self.seeds.copy():
            self.reset_seed(realm, seed)
            
            
class Defiler(ImperianCombatModule):
    transmission_str = 'shadowbind %(target)s with transmission'
    seek_str = 'shadowbind seek %(target)s'
    projection_str = 'SHADOWBIND ME WITH PROJECTION %(direction)s'
    mistbind_str = 'SHADOWBIND HERE WITH MISTBIND'
    obscurity_str = 'SHADOWBIND HERE WITH OBSCURITY'
    apparition_str = 'SHADOWBIND HERE WITH APPARITION'
    manadrain_str = 'SHADOWBIND %(target)s WITH MANADRAIN'
    healthdrain_str = 'SHADOWBIND %(target)s WITH HEALTHDRAIN'
    sap_strs={'f':'SHADOWBIND %(target)s WITH FIRESAP',
              'fir':'SHADOWBIND %(target)s WITH FIRESAP',
              'c':'SHADOWBIND %(target)s WITH COLDSAP',
              'col':'SHADOWBIND %(target)s WITH COLDSAP',
              'p':'SHADOWBIND %(target)s WITH POISONSAP',
              'poi':'SHADOWBIND %(target)s WITH POISONSAP',
              'y':'SHADOWBIND %(target)s WITH PSYSAP',
              'psy':'SHADOWBIND %(target)s WITH PSYSAP',
              'b':'SHADOWBIND %(target)s WITH BREATHSAP',
              'asp':'SHADOWBIND %(target)s WITH BREATHSAP',
              's':'SHADOWBIND %(target)s WITH SPARKSAP',
              'ele':'SHADOWBIND %(target)s WITH SPARKSAP'}
    hound_str = 'TORMENT %(target)s WITH HOUND'
    ravage_str= 'RAVAGE %(target)s %(toxin)s'
    devastate_str= 'DEVASTATE %(target)s %(toxin)s'
    
    evolve_str = 'TREANT EVOLVE %(target)s %(seed_evolve)s'
    entropy_str = 'TORMENT %(target)s WITH ENTROPY'
    whirl_str = 'WHIRL BRANCH AT %(target)s %(seed_whirl)s'
    germinate_str = 'TREANT GERMINATE %(target)s %(seed)s'
    bileshroud_str = 'BILESHROUD EXPLODE'
    bellow_str = 'TREANT BELLOW %(target)s'
    shadow_str = 'TORMENT %(target)s WITH SHADOW'
    def __init__(self, client, shield, tracker, limb, parry, communicator):
        ImperianCombatModule.__init__(self, client, tracker, shield, limb, parry, communicator)
        
        
        self.entropies={}
        self.seeds={}
        self.saps={}
        self.can_whirl = True
        #self.shadow=True
        #self.last_shadow=0
        
     
     
        
    def entropy(self, person):
        person = person.lower()
        if not person in self.entropies:
            self.entropies[person]=Entropy(self.realm, person)
        return self.entropies[person]
        
    def seed(self, person):
        person = person.lower()
        if not person in self.seeds:
            self.seeds[person]=Seeds(self.realm, person)
        return self.seeds[person]
    

    def sap(self, person):
        person=person.lower()
        if not person in self.saps:
            self.saps[person]=Saps(self.realm, person)
        return self.saps[person]
        
    @property
    def macros(self):
        return {'<F1>':'delayed pk',
                '<F2>':'delayed fin'}
    
    @property
    def triggers(self):
        return super(Defiler, self).triggers+[self.entropy_given,
                                                           self.entropy_effect,
                                                           self.whirl,
                                                           self.whirl_back,
                                                           self.reset_entropy,
                                                           self.seed_faded,
                                                           self.evolve,
                                                           self.shadowsap_apply,
                                                           self.shadowsap_remove,
                                                           self.germinate,
                                                           self.get_shadow,
                                                           self.kill_shadow]
        
    @property
    def aliases(self):
        return super(Defiler,self).aliases+[self.transmission,
                                            self.seek,
                                            self.sap_alias,
                                            self.mistbind,
                                            self.obscurity,
                                            self.apparition,
                                            self.manadrain,
                                            self.healthdrain,
                                            self.hound,
                                            self.hound_track,
                                            self.get_combo,
                                            self.finisher,
                                            self.reset_all,
                                            self.shadow]
    
    @binding_trigger('^You lean towards (\w+) with a contemptuous sneer and whisper a few words\.')
    def entropy_given(self, match, realm):
        realm.root.debug('entropy')
        target = match.group(1).lower()
        self.tracker.tracker(target).add_aff('entropy')
        
    @binding_trigger("^You sense that (\w+)'s entropy is now at (\d+)%\.$")
    def entropy_effect(self, match, realm):
        realm.display_line=False
                                                                                                           
        person=match.group(1)
        entropy_amt = int(match.group(2))
        realm.cwrite('<red*:grey>[[ENTROPY: <red*:grey>%(name)s<orange*:grey>: <green*:grey> %(amount)d<red*:grey>]]'%{'name':person,
                                                                                                           'amount':entropy_amt})
        
        self.entropy(person).set_entropy(entropy_amt)
        
    @binding_trigger("^The effects of entropy have faded from (\w+)'s body\.$")
    def reset_entropy(self, match, realm):
        person = match.group(1)
        self.entropy(person).reset(realm)
        realm.display_line=False
        
    @binding_trigger("^Following your gesture, a .* whirls a branch mightily towards (\w+), releasing a spore of the (\w+) tree that swiftly burrows into (?:his|her) skin\.$")
    def whirl(self, match, realm):
        realm.display_line=False
        person = match.group(1)
        seed_type = match.group(2)
        self.seed(person).add_seed(realm, seed_type, 'whirl')
        self.can_whirl = False
        
    @binding_trigger("^Your treant is again able to whirl a branch\.$")
    def whirl_back(self, match, realm):
        realm.display_line=False
        self.can_whirl=True
        
    @binding_trigger("^The splintered (\w+) seed in (\w+)'s body has withered away\.$")
    def seed_faded(self, match, realm):
        seed=match.group(1)
        person=match.group(2)
        realm.display_line=False
        self.seed(person).reset_seed(realm, seed)
        
    @binding_trigger("^At your command, .* swings a branch rapidly at (\w+). Upon impact, the branch splinters, releasing a small (\w+) seed that burrows into (?:her|his) skin and drains a portion of the accumulated entropy\.$")
    def evolve(self, match, realm):
        realm.display_line=False
        person = match.group(1)
        seed_type = match.group(2)
        self.seed(person).add_seed(realm, seed_type, 'evolve')
    
    @binding_trigger("^You rub one of your shadowgems and shadows swirl around (\w+), increasing (?:her|his) vulnerability to (\w+) damage\.$")
    def shadowsap_apply(self, match, realm):
        person=match.group(1)
        sap = match.group(2)
        self.sap(person).add_sap(realm, sap)
        realm.display_line=False
        
    @binding_trigger("^The shadows around (\w+) retreat, no longer increasing (?:her|his) vulnerability to (\w+) damage\.$")
    def shadowsap_remove(self, match, realm):
        person=match.group(1)
        sap = match.group(2)
        self.sap(person).reset_sap(realm, sap)
        realm.display_line=False
        
    @binding_trigger("^Following your command, .* releases a strangely smelling substance that seems into (\w+)'s pores. The (\w+) seed inside (?:her|him) suddenly erupts into life before withering away\.$")
    def germinate(self, match, realm):
        person=match.group(1)
        seed = match.group(2)
        self.seed(person).reset_seed(realm, seed)
        realm.display_line=False
        realm.cwrite('<red*>GERMINATE ON: <green*>%(target)s <red*> WITH <blue*> %(seed)s'%{'target':person,
                                                                                            'seed':seed})
    @binding_trigger("^Chanting quietly, you quickly sketch a pentagram on the ground. Flames leap high as an incorporeal shadow appears in its center, moving aggressively towards (\w+)$")
    def get_shadow(self, match, realm):
        self.shadow=True
    
    @binding_trigger("^An incorporeal shadow, your loyal companion, has been slain by (\w+)\.$")
    def kill_shadow(self, match, realm):
        self.shadow=False
        self.last_shadow=time.time()
            
    def execute_on_prompt(self, match, realm):
        target = realm.root.get_state('target')
        if target=='':
            return
        
        ent = self.entropy(target)
        if self.can_whirl:
            line_whirl = taggedml('[<orange*>B<white>]')
            realm.alterer.insert_metaline(len(realm.metaline.line), line_whirl)
        if ent.entropy>0:
            line_end=taggedml('[<red*>Ent: <green*>%d<white>]'%ent.entropy)
            realm.alterer.insert_metaline(len(realm.metaline.line), line_end)
        seeds = self.seed(target)
        if len(seeds.get_seeds())>0:
            line_seeds = taggedml('[<red*>Seeds: <blue>%s<white>]'%'<white>,<blue>'.join(seeds.get_seeds()))
            realm.alterer.insert_metaline(len(realm.metaline.line), line_seeds)
        saps = self.sap(target).get_color_coded_string()
        if saps!='':
            realm.alterer.insert_metaline(len(realm.metaline.line), taggedml(saps))
        
        
        
        
    @binding_alias('^trn$')
    def transmission(self, match, realm):
        realm.send_to_mud=False
        target = realm.root.get_state('target')
        realm.send('queue eq '+ Defiler.transmission_str%{'target':target})
        
    @binding_alias('^sk$')
    def seek(self, match, realm):
        realm.send_to_mud=False
        target = realm.root.get_state('target')
        realm.send('queue eq '+ Defiler.seek_str%{'target':target})
    
    @binding_alias('^(\w+)sp$')
    def sap_alias(self, match, realm):
        sap_type = match.group(1)
        realm.send_to_mud=False
        target = realm.root.get_state('target')
        if sap_type in Defiler.sap_strs:
            realm.send('queue eq '+ Defiler.sap_strs[sap_type]%{'target':target})
            
    @binding_alias('^msb$')
    def mistbind(self, match, realm):
        realm.send_to_mud=False
        realm.send('queue eq '+Defiler.mistbind_str)
        
    @binding_alias('^obs$')
    def obscurity(self, match, realm):
        realm.send_to_mud=False
        realm.send('queue eq '+Defiler.obscurity_str)
      
    @binding_alias('^apr')
    def apparition(self, match, realm):
        realm.send_to_mud=False
        realm.send('queue eq '+Defiler.apparition_str)  
        
    @binding_alias('^mdr$')
    def manadrain(self, match, realm):
        realm.send_to_mud=False
        target = realm.root.get_state('target')
        realm.send('queue eq '+ Defiler.manadrain_str%{'target':target})
        
    @binding_alias('^hdr$')
    def healthdrain(self, match, realm):
        realm.send_to_mud=False
        target = realm.root.get_state('target')
        realm.send('queue eq '+ Defiler.healthdrain_str%{'target':target})
        
    @binding_alias('^shd')
    def shadow(self, match, realm):
        realm.send_to_mud=False
        target = realm.root.get_state('target')
        realm.send('queue eq '+ Defiler.shadow_str%{'target':target})
        
    @binding_alias('^hnd')
    def hound(self, match, realm):
        realm.send_to_mud=False
        target = realm.root.get_state('target')
        realm.send('queue eq '+ Defiler.hound_str%{'target':target})
        
    @binding_alias('^hnt$')
    def hound_track(self, match, realm):
        realm.send_to_mud=False
        realm.send('queue eq hound track')
    
    @binding_alias('^dres$')
    def reset_all(self, match, realm):
        realm.send_to_mud=False
        target = realm.root.get_state('target')
        self.sap(target).reset(realm)
        self.entropy(target).reset(realm)
        self.seed(target).reset(realm)
    
    
    @binding_alias('^fin$')
    def finisher(self, match, realm):
        realm.send_to_mud=False
        target = realm.root.get_state('target')
        combo_parts=[]
        combo_parts.append(Defiler.germinate_str%{'target':target,
                                                  'seed':'hawthorn'})
        combo_parts.append(Defiler.whirl_str%{'target':target,
                                              'seed_whirl':'hawthorn'})
        combo_parts.append(Defiler.germinate_str%{'target':target,
                                                  'seed':'hawthorn'})
        combo_parts.append(Defiler.germinate_str%{'target':target,
                                                  'seed':'elder'})
        combo_parts.append(Defiler.germinate_str%{'target':target,
                                                  'seed':'blackthorn'})
        combo_parts.append(Defiler.bileshroud_str)
        
        combo_parts.append(Defiler.bellow_str%{'target':target})
        combo = '|'.join(combo_parts)
        self.send_combo(realm, combo)
        
    @binding_alias('^pk$')
    def get_combo(self, match, realm):
        realm.send_to_mud=False
        seeds_needed=['hawthorn','elder','blackthorn']
        saps_needed=['psy','poi']
        target = realm.root.get_state('target')
        toxin=self.get_toxin(target)
        combo_parts=[]
        seeds = self.seed(target)
        entropy = self.entropy(target).entropy
        saps = self.sap(target)
        evolve=False
        evolve_seed=''
        whirl_seed=''
        sap=''
        if entropy > 50 and len(saps.get_saps()) < 2:
            sap = next(s for s in saps_needed if not saps.has_sap(s))
            combo_parts.append(Defiler.sap_strs[sap])
        #elif entropy < 50 and entropy > 5 and not self.shadow and time.time() - self.last_shadow > 30:
        #    combo_parts.append(Defiler.shadow_str)
        else:
            if self.shield[target].shield or self.shield[target].aura:
                combo_parts.append(Defiler.devastate_str)
            else:
                combo_parts.append(Defiler.ravage_str)
              
            if (entropy > 50 and len(seeds.get_seeds())<3) or (entropy > 20 and len(seeds.get_seeds())<2):
                combo_parts.append(Defiler.evolve_str)
                evolve_seed=next(s for s in seeds_needed if not seeds.has_seed(s)) 
                evolve=True                            
            elif entropy > 50 and len(saps.get_saps()) < 2:
                sap = next(s for s in saps_needed if not saps.has_sap(s))
                combo_parts.append(Defiler.sap_strs[sap])
            else:
                combo_parts.append(Defiler.entropy_str)
            
            if self.can_whirl and ((len(seeds.get_seeds())<3 and not evolve) or len(seeds.get_seeds())<2):
                combo_parts.append(Defiler.whirl_str)  
                whirl_seed = next(s for s in seeds_needed if not(seeds.has_seed(s) or s == evolve_seed))
            
        combo='|'.join(combo_parts)%{'target':target,
                                     'toxin':toxin,
                                     'seed_whirl':whirl_seed,
                                     'seed_evolve':evolve_seed}
            
        self.send_combo(realm, combo)
        
    def get_toxin(self, target):
        toxins=['xeroderma','ether','arsenic']
        
        useful_toxins=[]
        tracker = self.tracker.tracker(target)
        for t in toxins:
            if not tracker[t].on:
                useful_toxins.append(t)
        
        useful_toxins.append('strychnine')
        return useful_toxins[0]
            