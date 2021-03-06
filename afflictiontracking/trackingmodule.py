from pymudclient.modules import EarlyInitialisingModule
from pymudclient.triggers import binding_trigger
from pymudclient.aliases import binding_alias

from afflictiontracker import Tracker,TREEABLE,FOCUSABLE,PURGEABLE,HERB,PIPE,SALVE,PASSIVE
from pymudclient.tagged_ml_parser import taggedml


class TrackerModule(EarlyInitialisingModule):
    def __init__(self, realm,communicator, remove_ambiguous=False):
        self.trackers={}
        self.realm = realm
        self.stored_priorities=[]
        self.communicator=communicator
        self.remove_ambiguous= remove_ambiguous
        self.communicator.aff_tracker=self
        
    def tracker(self, name):
        name=name.lower()
        if name not in self.trackers:
            self.trackers[name]=Tracker(name, self.manager, self.communicator, self.remove_ambiguous)
            self.trackers[name].apply_priorities(self.stored_priorities)
            
        return self.trackers[name]
    
    def apply_priorities(self, priorities):
        self.stored_priorities=priorities
        for t in self.trackers.values():
            t.apply_priorities(priorities)
    
    @property
    def triggers(self):
        return[self.drinks_elixir,
               self.eats_plant,
               self.smokes_pipe,
               self.applies_salve,
               self.uses_focus,
               self.purges_blood,
               self.touches_tree,
               self.third_party_message,
               self.passive_cure,
               self.on_prompt,
               self.peace_off,
               self.asthma_off,
               self.toxin_hit,
               self.haemophilia,
               self.numbness_to_paralysis,
               self.justice,
               self.madness,
               self.epilepsy,
               self.deadening,
               self.sunallergy,
               self.masochism,
               self.hallucinations,
               self.addiction,
               self.clumsiness]
        
    @property
    def aliases(self):
        return [self.reset,
                self.print_priorities]
    
    @binding_alias('^aff priorities$')
    def print_priorities(self,match,realm):
        realm.send_to_mud=False
        self.tracker('me').print_priorities()
    
    @binding_trigger("^(\w+) lurches forward, but misses you with .+\.$")
    def clumsiness(self, match, realm):
        person=match.group(1).lower()
        self.tracker(person).add_aff('addiction')
    
    @binding_trigger("^At \w+'s command, .+treant.+ shreds (\w+)'s skin with its branches, thorns cutting painfully into (?:his|her) flesh\.$")
    def addiction(self, match, realm):
        person=match.group(1).lower()
        self.tracker(person).add_aff('addiction')
    
    
    @binding_trigger(["^(\w+) leaps up in what is apparently an attempt at a graceful swan dive\.$",
                      "^(\w+) squints strangely at you\.$"])
    def hallucinations(self, match, realm):
        person=match.group(1).lower()
        self.tracker(person).add_aff('hallucinations')
    
    @binding_trigger(["^(\w+) smiles as (?:he|she) rams (?:his|her) fist into (?:his|her) jaw\.$",
                      "^(\w+) uses (?:his|her) (?:right|left) foot to stomp on (?:his|her) (?:right|left) as hard as possible\.$",
                      "^With the heel of (?:his|her) palm, (\w+) smacks (?:himself|herself) upside the head\.$"])
    def masochism(self, match, realm):
        person=match.group(1).lower()
        self.tracker(person).add_aff('masochism')
    
    @binding_trigger("^(\w+) screams in agony, skin steaming in the sunlight\.$")
    def sunallergy(self, match, realm):
        person=match.group(1).lower()
        self.tracker(person).add_aff('sunallergy')
    
    @binding_trigger("^(\w+) makes an oddly stuttered sound\.$")
    def deadening(self, match, realm):
        person=match.group(1).lower()
        self.tracker(person).add_aff('deadening')
    
    @binding_trigger("^Justice is dealt out and (\w+)'s attack rebounds onto \w+\.$")
    def justice(self, match, realm):
        person=match.group(1).lower()
        self.tracker(person).add_aff('justice')
    
    @binding_trigger("^(\w+) trembles and (?:his|her) eyes widen in terror\.$")
    def madness(self, match, realm):
        person=match.group(1).lower()
        self.tracker(person).add_aff('madness')
        
    @binding_trigger("^(\w+) twitches imperceptibly\.$")
    def epilepsy(self, match, realm):
        person=match.group(1).lower()
        self.tracker(person).add_aff('madness')
    
      
    @binding_trigger(["^(\w+)'s blood starts flowing more freely\.",
                      "^You shred (\w+)'s skin viciously with a shining longsword, causing a nasty infection\.$"])
    def haemophilia(self, match, realm):
        person=match.group(1).lower()
        self.tracker(person).add_aff('haemophilia')
    
    @binding_trigger(['^Your (\w+) toxin has affected (\w+)\.$'])
    def toxin_hit(self, match, realm):
        toxin = match.group(1)
        person = match.group(2).lower()
        self.tracker(person).add_aff(toxin)
        
    @binding_trigger(['^(\w+) empties out .* into (?:his|her) mouth\.$',
                      '^(\w+) takes a drink from .*\.$'])
    def drinks_elixir(self, match, realm):
        name=match.group(1)
        self.tracker(name).drink_elixir()
        
    @binding_trigger('^(\w+) quickly eats (?:a|an|some) (.*)\.$')
    def eats_plant(self, match, realm):
        name=match.group(1)
        plant=match.group(2)
        self.tracker(name).add_tentative_cure(HERB, plant)
        
    @binding_trigger('^(\w+) takes a long drag off (?:his|her)* pipe, exhaling a (.+)\.$')
    def smokes_pipe(self,match,realm):
        name=match.group(1)
        pipe=match.group(2)
        self.tracker(name).add_tentative_cure(PIPE,pipe)
        
    @binding_trigger('^(\w+) rubs some salve on (?:his|her) ([\w\s]+)\.$')
    def applies_salve(self,match,realm):
        name=match.group(1)
        self.tracker(name).add_tentative_cure(SALVE, None)
        
    @binding_trigger('^(\w+) touches a tree of life tattoo\.$')
    def touches_tree(self, match, realm):
        name=match.group(1)
        self.tracker(name).add_tentative_cure(TREEABLE,None)
        
    @binding_trigger('^(\w+) concentrates on purging toxins from (?:his|her) body\.$')
    def purges_blood(self, match, realm):
        name=match.group(1)
        self.tracker(name).add_tentative_cure(PURGEABLE, None)
        
    @binding_trigger('^A look of extreme focus crosses the face of (\w+)$')
    def uses_focus(self, match, realm):
        name=match.group(1)
        self.tracker(name).add_tentative_cure(FOCUSABLE, None)
    
    @binding_trigger("^(\w+)'s muscles lock up in paralysis\.$")
    def numbness_to_paralysis(self, match, realm):
        name = match.group(1)
        self.tracker(name).cure_specific_aff('numbness')
        self.tracker(name).add_aff('paralysis')
        
    @binding_trigger("^(\w+)'s looks much less fit after the attack\.$")
    def asthma_off(self, match, realm):
        name=match.group(1)
        self.tracker(name).cure_specific_aff('asthma')
        
    @binding_trigger(['^(\w+) glares angrily, driving off the pacifying attempt\.$',
                      "^(\w+)'s eyes flash with rage\.$"])
    def peace_off(self,match,realm):
        #print('removing peace')
        name=match.group(1)
        self.tracker(name).cure_specific_aff('peace')
    
    @binding_trigger(["^(\w+)'s colour returns to \w+ face\.$",
                      "^(\w+)'s skin color returns to normal and \w+ sweating subsides\.$",
                      "^(\w+) looks relieved as \w+ skin loses its reddish hue\.$",
                      "^(\w+)'s expression no longer looks so vacant\.$",
                      "^(\w+) breathes in relief as \w+ withered throat is restored\.$",
                      "^The raging fire about (\w+)'s skin is put out\.$",
                      "^(\w+) appears less dizzy\.$"])
    def third_party_message(self,match,realm):
        msg=match.group(0)
        name=match.group(1)
        self.tracker(name).add_tentative_cure_message(msg)
        
    @binding_trigger(["^The musical healing energy of the Song of Therapeutics draws an affliction from (\w+)'s body\.$",
                      "^(\w+) looks healthier and cleansed\.$",
                      "^Shadows whirl around (\w+), curing (?:his|her) maladies\.$",
                      "^(\w+)'s Ouroboros envelops (?:him|her) in a red glow\.$",
                      "^(\w+) calls upon the purifying waters to ease up (?:his|her) maladies\.$",
                      "^A soothing light envelops (\w+) momentarily\.$",
                      "^(\w+) focuses on (?:his|her) link with Cadmus, the cursed shaman\.$",
                      "^The spiritual power of a seraph touches (\w+) momentarily\.$"])
    def passive_cure(self,match,realm):
        name=match.group(1)
        self.tracker(name).add_tentative_cure(PASSIVE,None)
    
    
    
    @binding_alias('^aff reset$')
    def reset(self, match,realm):
        realm.send_to_mud=False
        target=realm.root.state['target']
        realm.cwrite('<black:white>Resetting afflictions on %s'%target)
        self.tracker(target).reset()
    
    @binding_trigger('^H:(\d+) M:(\d+)', sequence=100)
    def on_prompt(self, match, realm):
        target=realm.root.get_state('target')
        
        for t in self.trackers.values():
            t.process()
        
        if target != "":
            tracker = self.tracker(target)
            mentals = [a.name for a in tracker.affs.values() if a.is_it(FOCUSABLE) and a.on==True]
            physicals = [a.name for a in tracker.affs.values() if not a.is_it(FOCUSABLE) and a.on==True ]
            if len(mentals)>0 or len(physicals)>0:
                line = '[M: <blue>%(mentals)s <white>P:<red*> %(physicals)s<white>]'%{'mentals':'<white>,<blue>'.join(mentals),
                                                                          'physicals':'<white>,<red*>'.join(physicals)}
                
                realm.alterer.insert_metaline(len(realm.metaline.line), taggedml(line))
            #t.output()
        #if target!=None and target !='':
            #if realm.root.gui:
            #    realm.root.gui.update_cooldowns()
            #else:
            #    realm.cwrite('<orange>%s'%self.tracker(target).output())    
        