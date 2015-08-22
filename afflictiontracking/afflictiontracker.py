'''
Created on Aug 17, 2015

@author: Dmitry
'''
import csv
import os
import re
import time


TREEABLE = 1<<0
PURGEABLE = 1<<1
FOCUSABLE = 1<<2




HERB = 1<<3
PIPE = 1<<4
SALVE = 1<<5

PASSIVE= 1<<6

TREE_BALANCE=15
PURGE_BALANCE=15
FOCUS_BALANCE=4

skill_to_aff={}
toxin_to_aff={}
aff_to_toxin={}
aff_to_skill={}

class AfflictionDictionaries:
    class __AfflictionDictionaries:
        def __init__(self):
            self.affliction_dictionaries_populated=False
            self.skill_to_aff={}
            self.toxin_to_aff={}
            self.aff_to_toxin={}
            self.aff_to_skill={}
    
        def s2a(self,skill_name):
            skill_name=skill_name.lower()
            if skill_name in self.skill_to_aff:
                return self.skill_to_aff[skill_name]
            else:
                return skill_name
        
        def t2a(self,toxin_name):
            toxin_name=toxin_name.lower()
            if toxin_name in self.toxin_to_aff:
                return self.toxin_to_aff[toxin_name]
            else:
                return toxin_name
            
        def a2t(self,aff_name):
            aff_name=aff_name.lower()
            if aff_name in self.aff_to_toxin:
                return self.aff_to_toxin[aff_name]
            else:
                return aff_name
            
        def a2s(self,aff_name):
            aff_name=aff_name.lower()
            if aff_name in self.aff_to_skill:
                return self.aff_to_skill[aff_name]
            else:
                return aff_name
            
    instance = None
    def __init__(self):
        if not AfflictionDictionaries.instance:
            AfflictionDictionaries.instance = AfflictionDictionaries.__AfflictionDictionaries()
        
    def __getattr__(self,name):
        return getattr(self.instance, name)
            

def normalize_aff(aff):
    return aff.replace(' ','_')

def get_cure(cure):
    for c in ['wormwood','mandrake','kelp','orphine','nightshade','galingale','maidenhair', 'ginger']:
        if c in cure:
            return c
    if cure == 'thick, musty smoke':
        return 'laurel'
    if cure == 'light, bluish mist':
        return 'lovage'
    if cure == 'thick, white haze':
        return 'linseed'
    return ''

class Affliction:
    def __init__(self, name, afftype, cures, priority, confidence_threshold, third_party_cure, extra_cures=0,):
        '''
        @param name: affliction name
        @param afftype: affliction type (herb, pipe or salve)
        @param cure: the name of the curative (orphine, etc)
        @param priority: assumed curing priority (lower for stuff you want to stay on)
        @param confidence_threshold: below which confidence % assume it's no longer on
        @param cures: Additional cures flag (TREE, PURGE, FOCUS)
        '''
        self.name=name
        self.afftype=afftype
        self.cures=cures
        self.priority=priority
        self.extra_cures=extra_cures
        self.confidence=0
        self.gained_at=0
        self.default_priority=priority
        self.confidence_threshold=confidence_threshold
        self.third_party_cure=third_party_cure
        self.mark=False
        
    def is_it(self, what):
        return (self.extra_cures & what)
    
    def cured_by(self, what):
        return (self.afftype & what)
    
    @property
    def on(self):
        return self.confidence >= self.confidence_threshold
    
    @on.setter
    def on(self, value):
        if value == False:
            self.confidence = 0
        else:
            self.confidence = 1
    
    @property
    def ready(self):
        return self.on and self.mark
    
    def __str__(self):
        return '%s: cure:(%s, %s) extra_cures:(%s)'%(self.name, self.afftype, self.cure, self.cures)
    
    
class Tracker:
    def __init__(self, who, realm):
        self.name=who
        self.affs = new_aff_dict()
        self.realm=realm
        self.last_eat=0
        self.last_smoke=0
        self.last_salve=0
        self.last_elixir=0
        self.last_focus=0
        self.last_purge=0
        self.last_tree=0
        self.last_toadstool=0
        
        self.tentative_cures=[]
        self.tentative_cure_messages=[]
        
    def __getitem__(self, value):
        adict = AfflictionDictionaries()
        value = adict.t2a(value)
        value = adict.s2a(value)
        if not value in self.affs:
            return None
        return self.affs[value]
        
    def output(self):
        s ='<aff %s>: %s'
        afflictions=[k for k,v in self.affs.items() if v.on]
        return s%(self.name,','.join(afflictions))

    def add_aff(self, aff):
        aff=normalize_aff(aff)
        if not aff in self.affs:
            self.realm.write(self.name + " received unknown aff " + aff + ". Needs adding to new_aff_dict()")
            return
        old_conf = self.affs[aff].on
        self.affs[aff].on=True
        if old_conf!=True:
            print(self.output()) 
        

    def _remove_aff(self, cure, cure_type, cure_msg):
        if not cure_msg == '':
            temp_affs = [v for v in self.affs.values() if v.third_party_cure != '']
            for a in temp_affs:
                if re.match(a.third_party_cure, cure_msg):
                    a.on=False
        
        else:
            if cure:
                temp_affs = [v for v in self.affs.values() if v.third_party_cure == '' and 
                             v.cured_by(cure_type) and 
                             cure in v.cures and
                             v.on]
            else:
                temp_affs=[v for v in self.affs.values() if v.third_party_cure == '' and 
                           v.cured_by(cure_type) and
                           v.on]
            temp_affs = sorted(temp_affs, key=lambda aff:aff.priority)
            if len(temp_affs)>0:
                aff_to_remove=temp_affs[0]
                old_confidence = aff_to_remove.on
                aff_to_remove.on = False
                if (old_confidence==True):
                    print(self.output())
                    
    def _remove_aff_extra_cure(self, cure_type, cure_msg):
        if not cure_msg == '':
            temp_affs = [v for v in self.affs.values() if v.third_party_cure != '']
            for a in temp_affs:
                if re.match(a.third_party_cure, cure_msg):
                    a.on=False
        
        else:
            temp_affs = [v for v in self.affs.values() if v.third_party_cure == '' and 
                v.is_it(cure_type) and 
                v.on]
            temp_affs = sorted(temp_affs, key=lambda aff:aff.priority)
            if len(temp_affs)>0:
                aff_to_remove=temp_affs[0]
                old_confidence = aff_to_remove.on
                aff_to_remove.on = False
                if (old_confidence==True):
                    print(self.output())

    def eat_cure(self, cure, cure_msg):
        cure=get_cure(cure)
        self.affs['anorexia'].on=False
        self.last_eat = time.time()
        self._remove_aff(cure, HERB, cure_msg)
            
    
    def pipe_cure(self, cure, cure_msg):
        cure=get_cure(cure)
        self.affs['asthma'].on=False
        self.last_smoke=time.time()
        self._remove_aff(cure, PIPE, cure_msg)
    
    def salve_cure(self,  cure_msg):
        self.affs['slickness'].on=False
        self.last_salve = time.time()  
        self._remove_aff(None, SALVE, cure_msg)
        
    def tree_cure(self, cure_msg):
        self.affs['numbness'].on=False
        self.affs['paralysis'].on=False
        self.last_tree=time.time()
        self._remove_aff_extra_cure(TREEABLE, cure_msg)
          
    def purge_cure(self, cure_msg):
        self.affs['hemotoxin'].on=False
        self.last_purge=time.time()
        self._remove_aff_extra_cure(PURGEABLE, cure_msg)
        
    def focus_cure(self, cure_msg):
        self.affs['impatience'].on=False
        self.last_focus=time.time()
        self._remove_aff_extra_cure(FOCUSABLE, cure_msg)
    
    def drink_elixir(self):
        self.affs['anorexia'].on=False
        self.last_elixir=time.time()
        
    def passive_cure(self, cure_msg):
        if not cure_msg == '':
            temp_affs = [v for v in self.affs.values() if v.third_party_cure != '']
            for a in temp_affs:
                if re.match(a.third_party_cure, cure_msg):
                    a.on = False
        
        else:
            temp_affs = [v for v in self.affs.values() if v.third_party_cure == '' and 
                v.on]
            temp_affs = sorted(temp_affs, key=lambda aff:aff.priority)
            if len(temp_affs)>0:
                aff_to_remove=temp_affs[0]
                old_confidence = aff_to_remove.on
                aff_to_remove.on = False
                if (old_confidence==True):
                    print(self.output())
         
    @property
    def next_focus(self):
        return time.time()-FOCUS_BALANCE
    
    @property
    def next_tree(self):
        return time.time() - TREE_BALANCE
    
    @property
    def next_purge(self):
        return time.time() - PURGE_BALANCE
    
    def add_tentative_cure(self, cure_type, cure):
        self.tentative_cures.append((cure_type, cure))
        self.tentative_cure_messages.append('')
    
    def add_tentative_cure_message(self, cure_message):
        self.tentative_cure_messages[len(self.tentative_cure_messages)-1]=cure_message
    
    def process(self):
        for indx, cure in enumerate(self.tentative_cures):
            msg=self.tentative_cure_messages[indx]
            if cure[0]==FOCUSABLE:
                self.focus_cure(msg)
            elif cure[0]==TREEABLE:
                self.tree_cure(msg)
            elif cure[0]==PURGEABLE:
                self.purge_cure(msg)
            elif cure[0]==HERB:
                self.eat_cure(cure[1], msg)
            elif cure[0]==PIPE:
                self.pipe_cure(cure[1], msg)
            elif cure[0]==SALVE:
                self.salve_cure(msg)
            elif cure[0]==PASSIVE:
                self.passive_cure(msg)
                
        self.tentative_cure_messages=[]
        self.tentative_cures=[]
        for a in self.affs.values():
            a.mark=False
            
def new_aff_dict():
    afffile = os.path.join(os.path.expanduser('~'), 'muddata',
                            'afflictions.csv')
    affs={}
    with open(afffile) as csvfile:
        reader=csv.DictReader(csvfile)
        
        for row in reader:
            cures=[]
            cure_types=0
            herb=row['herb']
            pipe=row['pipe']
            salve=row['salve']
            if not herb=='':
                cures.extend(herb.split(','))
                cure_types=cure_types|HERB
            if not pipe=='':
                cures.extend(pipe.split(','))
                cure_types=cure_types|PIPE
            if not salve=='':
                cures.extend(salve.split(','))
                cure_types=cure_types|SALVE
            extra_cures=0
            if row['focus']:
                extra_cures=extra_cures|FOCUSABLE
            if row['purge']:
                extra_cures=extra_cures|PURGEABLE
            if row['tree']:
                extra_cures=extra_cures|TREEABLE
                
            affs[row['affliction']]=Affliction(row['affliction'],cure_types, cures, int(row['priority']),
                                         1.0,row['cure_msg'],extra_cures)
            
            
            adict = AfflictionDictionaries()
            if not adict.affliction_dictionaries_populated:
                if row['toxin']!= '':
                    adict.toxin_to_aff[row['toxin']]=row['affliction']
                    adict.aff_to_toxin[row['affliction']]=row['toxin']
                    
                if row['skill']!= '':
                    adict.skill_to_aff[row['skill']]=row['affliction']
                    adict.aff_to_skill[row['affliction']]=row['skill']
    adict.affliction_dictionaries_populated=True
    
    return affs




if __name__=='__main__':
    t=Tracker('test',None)
    t.add_aff('stupidity')
    t.add_aff('numbness')
    t.add_aff('slickness')
    print(t)
    adict = AfflictionDictionaries()
    print(adict.t2a('xeroderma'))
    t.add_aff('asthma')
    t.add_tentative_cure(HERB, 'maidenhair root')
    t.add_tentative_cure(FOCUSABLE,None)
    t.add_tentative_cure_message("test's expression no longer looks so vacant.")
    t.add_tentative_cure(PIPE, 'light, bluish mist')
    t.add_aff('clumsiness')
    print('stupidity: %s'%t['stupidity'].on)
    print('xeroderma: %s'%t['xeroderma'].on)
    print('clumsiness: %s'%t['clumsy'].on)
    t.process()
    