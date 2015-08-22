from pymudclient.modules import BaseModule
from pymudclient.triggers import binding_trigger
from afflictiontracker import Tracker,TREEABLE,FOCUSABLE,PURGEABLE,HERB,PIPE,SALVE,PASSIVE


class TrackerModule(BaseModule):
    def __init__(self, realm):
        BaseModule.__init__(self,realm)
        
        self.trackers={}
        
    def tracker(self, name):
        name=name.lower()
        if name not in self.trackers:
            self.trackers[name]=Tracker(name, self.manager)
            
        return self.trackers[name]
    
    @property
    def triggers(self):
        return[self.drinks_elixir,
               self.eats_plant,
               self.smokes_pipe,
               self.applies_salve,
               self.uses_focus,
               self.purges_blood,
               self.touches_tree,
               self.third_parth_message,
               self.passive_cure]
        
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
        
    @binding_trigger('^A look of extreme focus crosses the face of (\w+)\.$')
    def uses_focus(self, match, realm):
        name=match.group(1)
        self.tracker(name).add_tentative_cure(FOCUSABLE, None)
        
    
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
    
    
    def on_prompt(self, realm):
        target=realm.root.state['target']
        
        for t in self.trackers:
            t.process()
        if target!=None and target !='':
            realm.cwrite('<orange>%s'%self.tracker(target).output())    
        