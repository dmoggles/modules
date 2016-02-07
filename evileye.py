from pymudclient.modules import  EarlyInitialisingModule
from pymudclient.aliases import binding_alias
from pymudclient.triggers import binding_trigger
from afflictiontracking.afflictionpriority import AfflictionPriority

class EvileyeCombo(EarlyInitialisingModule):
    def __init__(self, realm, affliction_tracker):
        self.realm=realm
        self.tracker=affliction_tracker
        self.breacher = Breacher()
        
    def get_combo(self):
        pass
    
    @property
    def aliases(self):
        return [self.decay]
    
    @property
    def modules(self):
        return [self.breacher]
    
    @property 
    def triggers(self):
        return [self.evileye_affliction]
    @binding_alias('^dec$')
    def decay(self,match,realm):
        realm.send_to_mud=False
        target=realm.root.get_state('target')
        realm.send('stare %s decay'%target)
        
    @binding_trigger('^You stare at (\w+), giving (?:him|her) the evil eye of (\w+)\.$')
    def evileye_affliction(self, match, realm):
        target = match.group(1)
        aff = match.group(2)
        
        t=self.tracker.tracker(target)
        t.add_aff(aff)    
        
class EvileyeMana(EvileyeCombo):
    def __init__(self, realm, affliction_tracker, shield_tracker, daegger):
        EvileyeCombo.__init__(self, realm, affliction_tracker)
        self.shield = shield_tracker
        self.daegger = daegger
    
    @property
    def bloodworms(self):
        bw=[k for k in self.realm.gmcp['Char.Items.List']['items'] if k['name']=='a frenzied bloodworm']
        return len(bw)
    
    def get_combo(self, target):
        tracker = self.tracker.tracker(target)
        
        queue=[]
        if self.breacher.get_warded(target):
            queue.append('breach')
        if self.daegger.ready and (self.shield[target].shield or self.shield[target].aura):
            queue.append('breach')
        if not tracker['anorexia'].on and (tracker['slickness'].on and tracker['impatience'].on and (tracker['hemotoxin'].on or tracker.pboc)):
            queue.append('anorexia')
        if not tracker['cyanide'].on and (tracker['anorexia'].on and (tracker['hemotoxin'].on or tracker.pboc) and (tracker['numbness'].on or tracker['paralysis'].on)):
            queue.append('plague')
        if not tracker['epilepsy'].on and (tracker['asthma'].on and (tracker['hemotoxin'].on or tracker.pboc) and (tracker['impatience'].on)):
            queue.append('epilepsy') 
        
        if not tracker['impatience'].on:
            queue.append('impatience')
        if not tracker['numbness'].on and not tracker['paralysis'].on:
            queue.append('numbness')
        if not tracker['addiction'].on:
            queue.append('addiction')
        if not tracker['recklessness'].on:
            queue.append('reckless')
        if not tracker['asthma'].on:
            queue.append('asthma')
        if not tracker['clumsiness'].on:
            queue.append('clumsy')
       
        if not tracker['peace'].on and not tracker.peacecd>0:
            queue.append('peace')
        if not tracker['stupidity'].on:
            queue.append('stupid')
        if not tracker['ignorance'].on:
            queue.append('ignorance')
        
        if not tracker['nausea'].on:
            queue.append('vomiting')
        if not tracker['dizziness'].on:
            queue.append('dizzy')
        if not tracker['sensitivity'].on:
            queue.append('sensitivity')
        if not tracker['vertigo'].on:
            queue.append('vertigo')
        if not tracker['paranoia'].on:
            queue.append('paranoia')
        if not tracker['dementia'].on:
            queue.append('dementia')
        if not tracker['claustrophobia'].on:
            queue.append('claustrophobia')
        if not tracker['agoraphobia'].on:
            queue.append('agoraphobia')
        queue.append('amnesia')
        return 'deadeyes %s %s %s'%(target, queue[0], queue[1])
            
        
class EvileyeHealth(EvileyeCombo):
    def __init__(self, realm, affliction_tracker, shield_tracker, daegger):
        EvileyeCombo.__init__(self, realm, affliction_tracker)
        self.shield = shield_tracker
        self.daegger = daegger
    
    @property
    def bloodworms(self):
        bw=[k for k in self.realm.gmcp['Char.Items.List']['items'] if k['name']=='a frenzied bloodworm']
        return len(bw)
    
    def get_combo(self, target):
        tracker = self.tracker.tracker(target)
        
        queue=[]
        if self.breacher.get_warded(target):
            queue.append('breach')
        if self.daegger.ready and (self.shield[target].shield or self.shield[target].aura):
            queue.append('breach')
        if not tracker['anorexia'].on and (tracker['slickness'].on and tracker['impatience'].on and (tracker['hemotoxin'].on or tracker.pboc)):
            queue.append('anorexia')
        if not tracker['cyanide'].on and (tracker['anorexia'].on and (tracker['hemotoxin'].on or tracker.pboc) and (tracker['numbness'].on or tracker['paralysis'].on)):
            queue.append('plague')
        if not tracker['epilepsy'].on and (tracker['asthma'].on and (tracker['hemotoxin'].on or tracker.pboc) and (tracker['impatience'].on)):
            queue.append('epilepsy') 
        
        if not tracker['numbness'].on and not tracker['paralysis'].on:
            queue.append('numbness')
        if not tracker['asthma'].on:
            queue.append('asthma')
        if not tracker['nausea'].on:
            queue.append('vomiting')
        
        if not tracker['clumsiness'].on:
            queue.append('clumsy')
       
        if not tracker['impatience'].on:
            queue.append('impatience')
        
        if not tracker['addiction'].on:
            queue.append('addiction')
            
        if not tracker['masochism'].on:
            queue.append('masochism')
       
        if not tracker['peace'].on and not tracker.peacecd>0:
            queue.append('peace')
        if not tracker['stupidity'].on:
            queue.append('stupid')
        if not tracker['ignorance'].on:
            queue.append('ignorance')
        
        if not tracker['recklessness'].on:
            queue.append('reckless')
        
        
        if not tracker['dizziness'].on:
            queue.append('dizzy')
        if not tracker['sensitivity'].on:
            queue.append('sensitivity')
        if not tracker['vertigo'].on:
            queue.append('vertigo')
        if not tracker['paranoia'].on:
            queue.append('paranoia')
        if not tracker['dementia'].on:
            queue.append('dementia')
        if not tracker['claustrophobia'].on:
            queue.append('claustrophobia')
        if not tracker['agoraphobia'].on:
            queue.append('agoraphobia')
        queue.append('amnesia')
        return 'deadeyes %s %s %s'%(target, queue[0], queue[1])
            
        
        
        
    
    
class EvileyePriorityList(EvileyeCombo):
    def __init__(self, realm, affliction_tracker):
        EvileyeCombo.__init__(self,realm, affliction_tracker)
        self.priority_manager = AfflictionPriority('evileye',realm.factory.name, realm)
        self.priority_manager.load_priorities('default')
        self.tracker.apply_priorities(self.priority_manager.get_priorities())
        
        
     
    
    
    @property
    def aliases(self):
        #return [self.load_priorities]
        return [self.load_priorities]+EvileyeCombo.aliases.fget(self)
    @binding_alias('^ee priority (\w+)$')
    def load_priorities(self,match,realm):
        group=match.group(1)
        realm.cwrite('Loading evileye priority group %s'%group)
        realm.send_to_mud=False
        self.priority_manager.load_priorities(group)
        self.tracker.apply_priorities(self.priority_manager.get_priorities())   
        
    def get_combo(self, target):
        if self.breacher.get_warded(target):
            affs=self.priority_manager.get_afflictions(self.tracker.tracker(target), 1)
            return 'deadeyes %s breach %s'%(target, affs[0])
        else:
            affs=self.priority_manager.get_afflictions(self.tracker.tracker(target), 2)
            if len(affs)==2:
                return 'deadeyes %s %s %s'%(target, affs[0],affs[1])
            elif len(affs)==1:
                return 'stare %s %s'%(target, affs[0])
            else:
                return ''
        
class RepeatingEvileyeCombo(EvileyeCombo, EarlyInitialisingModule):
    def __init__(self, manager):
        self.combo=None
        
        
    @property
    def aliases(self):
        return[self.set_combo]
        
    @binding_alias('^ee set (\w+) (\w+)$')
    def set_combo(self, match, realm):
        realm.send_to_mud=False
        aff1=match.group(1)
        aff2=match.group(2)
        self.combo=(aff1,aff2)
        realm.cwrite('<white*:green> Set evileyes combo to %s, %s'%(aff1,aff2))
    
    def get_combo(self):
        return self.combo

    def print_status(self):
        return '<evileye> [%s,%s]'%self.combo
    
    


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
        
        target = realm.root.state['target']
        self.set_warded(match.group(1), True)
        if match.group(1).lower() == target.lower():
            realm.cwrite('<red*:yellow>Curseward is UP on %s!'%target)
            if realm.root.gui:
                realm.root.gui.set_shield('curseward',True)
            
    @binding_trigger(['^(?:His|Her) curseward has failed!$',
                      '^There is nothing left to breach\.$'])
    def strip_curseward(self, match, realm):
        target = realm.root.state['target']
        realm.display_line=False
        self.set_warded(target, False)
        if realm.root.gui:
                realm.root.gui.set_shield('curseward',False)
        realm.cwrite('<green*:yellow>Curseward is DOWN on %s!'%target)
        
    
    @binding_trigger('You stare at yourself, giving you the evil eye of breach.')
    def strip_curseward_self(self, match, realm):
        target='me'
        self.set_warded(target, False)
        if realm.root.gui:
                realm.root.gui.set_shield('curseward',False)