'''
Created on May 9, 2016

@author: Dmitry
'''
from pymudclient.modules import BaseModule
from pymudclient.aliases import binding_alias
from pymudclient.triggers import binding_trigger

elixirs = ['health','mana','immunity','frost','speed','levitation']
salves = ['caloric','mass','restoration','epidermal','mending']
toxins = ['atropine',
          'mercury',
          'digitalis',
          'xeroderma',
          'luminal',
          'ciguatoxin',
          'benzene',
          'vitriol',
          'strychnine',
          'botulinum',
          'chloroform',
          'mazanor',
          'arsenic',
          'benzedrine',
          'lindane',
          'butisol',
          'bromine',
          'cyanide',
          'opium',
          'avidya',
          'calotropis',
          'aconite',
          'metrazol',
          'noctec',
          'hemotoxin',
          'mebaral'
          ]

class ElixRefiller(BaseModule):
    
    def __init__(self, client):
        BaseModule.__init__(self, client)
        self.missing_toxins=[]
        self.missing_elixirs = []
        self.missing_salves=[]
        self.empties = []
        self.status = False
        self.mode = ''
        
    @property
    def aliases(self):
        return [self.refill]

    @property
    def triggers(self):
        return [self.more_trigger,
                self.done_trigger,
                self.toxin_trigger,
                self.empty_trigger,
                self.no_vialbelt_trigger,
                self.toxin_refill_trigger,
                self.elixir_trigger,
                self.elixir_refill_trigger,
                self.salve_trigger,
                self.salve_refill_trigger]

    @binding_alias('^refiller refill (all|toxins|elixirs|salves)$')
    def refill(self, match, realm):
        realm.send_to_mud = False
        self.mode = match.group(1)
        self.status = True
        self.empties = []
        if self.mode == 'all' or self.mode == 'toxins':
            self.missing_toxins = toxins[:]
        if self.mode == 'all' or self.mode == 'elixirs':
            self.missing_elixirs= elixirs[:]
        if self.mode == 'all' or self.mode == 'salves':
            self.missing_salves = salves[:]
        realm.send('elixlist')
        
            
    @binding_trigger('^Type MORE to continue reading\. \(.*\)$')
    def more_trigger(self, match, realm):
        if self.status:
            realm.send('more')
        
    @binding_trigger('^You have \d+ containers in your inventory\.$')
    def done_trigger(self, match, realm):
        if not self.status:
            return
        if self.mode == 'all' or self.mode == 'toxins':
            realm.cwrite('Missing toxins: \n{0}'.format('\n'.join(sorted(self.missing_toxins))))
        if self.mode == 'all' or self.mode == 'elixirs':
            realm.cwrite('Missing elixirs: \n{0}'.format('\n'.join(sorted(self.missing_elixirs))))
        if self.mode == 'all' or self.mode == 'salves':
            realm.cwrite('Missing salves: \n{0}'.format('\n'.join(sorted(self.missing_salves))))
        self.refill_one(realm)
            
        
    
    def refill_one(self, realm):
        if len(self.empties)==0:
                realm.cwrite('Refiller out of empty vials!')
                return
        if self.mode == 'all' or self.mode == 'toxins':
            if len(self.missing_toxins) > 0:
                realm.send('vialbelt tap {empty} {toxin}'.format(empty=self.empties[0], toxin=self.missing_toxins[0]))
                return
        if self.mode == 'all' or self.mode == 'elixirs':
            if len(self.missing_elixirs) > 0:
                realm.send('vialbelt tap {empty} {elixir}'.format(empty=self.empties[0], elixir=self.missing_elixirs[0]))
                return
        if self.mode == 'all' or self.mode == 'salves':
            if len(self.missing_salves) > 0:
                realm.send('vialbelt tap {empty} {salve}'.format(empty=self.empties[0], salve=self.missing_salves[0]))
                return
        self.status = False
        
    
    
    @binding_trigger('^vial\d* *the toxin (\w+) *(?:\d+) *(\d+)$')
    def toxin_trigger(self, match, realm):
        if not self.status:
            return
        toxin = match.group(1).lower()
        months = int(match.group(2))
        if months >= 10 and toxin in self.missing_toxins:
            self.missing_toxins.remove(toxin)
            
    @binding_trigger('^vial\d* *an elixir of (\w+) *(?:\d+) *(\d+)$')
    def elixir_trigger(self, match, realm):
        if not self.status:
            return
        elixir = match.group(1).lower()
        months = int(match.group(2))
        if months >= 10 and elixir in self.missing_elixirs:
            self.missing_elixirs.remove(elixir)
      
    @binding_trigger('^vial\d* *(?:a|an) (?:salve of )*(\w+)(?: salve)* *(?:\d+) *(\d+)$')
    def salve_trigger(self, match, realm):
        if not self.status:
            return
        salve = match.group(1).lower()
        months = int(match.group(2))
        if months >= 10 and salve in self.missing_salves:
            self.missing_salves.remove(salve)
                  
    @binding_trigger('^vial(\d+) *empty *(?:\d+) *(\d+)$')
    def empty_trigger(self, match, realm):
        if not self.status:
            return
        iid = match.group(1)
        months = int(match.group(2))
        if months >= 30:
            self.empties.append(iid)   
    
    @binding_trigger('^You find no vialbelt slots able to refill your vial\.$')
    def no_vialbelt_trigger(self, match, realm):
        if not self.status:
            return
        if (self.mode=='all' or self.mode=='toxins') and len(self.missing_toxins) > 0:
            self.missing_toxins.pop(0)
            self.refill_one(realm)
        elif(self.mode=='all' or self.mode=='elixirs') and len(self.missing_elixirs) > 0:
            self.missing_elixirs.pop(0)
            self.refill_one(realm)
            
    @binding_trigger('^Finding a .* empty of the toxin (\w+), you quickly roll the mouth of the vial across one')
    def toxin_refill_trigger(self, match, realm):
        if not self.status:
            return
        toxin = match.group(1).lower()
        self.empties.pop(0)
        self.missing_toxins.remove(toxin)
        self.refill_one(realm)
        
    @binding_trigger('^Finding a .* empty of an elixir of (\w+), you quickly roll the mouth of the vial across one')
    def elixir_refill_trigger(self, match, realm):
        if not self.status:
            return
        elixir = match.group(1).lower()
        self.empties.pop(0)
        self.missing_elixirs.remove(elixir)
        self.refill_one(realm)
        
    @binding_trigger('^Finding a .* empty of (?:an|a) (?:salve of )*(\w+)(?: salve)*, you quickly roll the mouth of the vial across one')
    def salve_refill_trigger(self, match, realm):
        if not self.status:
            return
        salve = match.group(1).lower()
        self.empties.pop(0)
        self.missing_salves.remove(salve)
        self.refill_one(realm)