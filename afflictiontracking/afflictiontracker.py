'''
Created on Aug 17, 2015

@author: Dmitry
'''
import csv
import os
import re
import time
import random


TREEABLE = 1<<0
PURGEABLE = 1<<1
FOCUSABLE = 1<<2
HERB = 1<<3
PIPE = 1<<4
SALVE = 1<<5
PASSIVE= 1<<6
ELIXIR=-10






TREE_BALANCE=15
PURGE_BALANCE=15
FOCUS_BALANCE=4

HERB_BALANCE=2
SALVE_BALANCE=3
PIPE_BALANCE=3

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
    for c in ['wormwood','mandrake','kelp','orphine','nightshade','galingale','maidenhair', 'ginger', 'juniper']:
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
    def __init__(self, name, afftype, cures, priority, confidence_threshold, third_party_cure, cooldown=0,extra_cures=0):
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
        self.cooldown=cooldown
        self.last_given=0
        self.last_cured=0
        self.mark=False
        
    
    def cure_it(self):
        self.on=False
        self.last_cured=time.time()
        
    def give_it(self):
        self.on=True
        self.last_given = time.time()
        

    def is_it(self, what):
        return (self.extra_cures & what)
    
    def cured_by(self, what):
        return (self.afftype & what)
    
    @property 
    def on_for(self):
        return time.time() - self.last_given if self.last_given > 0 else 0
    @property
    def on(self):

        return self.confidence >= self.confidence_threshold

    @property
    def usable(self):
        return (not self.on) and (self.last_given+self.cooldown < time.time())
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
    def __init__(self, who, realm, communicator=None, remove_ambiguous=False):
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
        self.last_peace=0
        self.presumed_afflictions=0
        self.remove_ambiguous = remove_ambiguous
        self.tentative_cures=[]
        self.tentative_cure_messages=[]
        self.communicator=communicator
        self.deaf = True
    
    @property 
    def tlock(self):
        return self.affs['anorexia'].on and self.affs['slickness'].on and self.affs['asthma'].on and self.affs['impatience'].on and self.affs['hemotoxin'].on and (self.affs['numbness'].on or self.affs['paralysis'].on)
    
    
    def reset(self):
        for a in self.affs.values():
            a.cure_it()
            self.realm.fireEvent('afflictionLostEvent',self.name, [a.name for a in self.affs.values()])
        self.presumed_afflictions=0
            
    def __getitem__(self, value):
        adict = AfflictionDictionaries()
        value = adict.t2a(value)
        value = adict.s2a(value)
        if not value in self.affs:
            return None
        return self.affs[value]
    
    def apply_priorities(self, priorities):
        adict = AfflictionDictionaries()
        for p in priorities:
            a=adict.t2a(p[0])
            a=adict.s2a(a)
            self.affs[a].priority=p[1]
            
    def print_priorities(self):
        affs=sorted(self.affs.values(), key=lambda aff:aff.priority)
        for a in affs:
            self.realm.cwrite('<black:yellow>%s: <red*:black>%d'%(a.name,a.priority))
               
    def output(self):
        pass
        #if not self.realm.gui:
        #    return self.text_output()
        #else:
        #    self.realm.gui.update_cooldowns()
        #    for v in self.affs.values():
        #        self.realm.gui.set_aff(v.name, v.on)
                
    def text_output(self):
        s ='<aff %s(PA: %d)(E: %d, S: %d, P:%d, F: %d, B: %d, T: %d)>: %s'
        afflictions=[k for k,v in self.affs.items() if v.on]
        now=time.time()
        since_eat=round(now-self.last_eat) if self.last_eat != 0 else 0
        since_salve=round(now-self.last_salve)  if self.last_salve != 0 else 0
        since_pipe=round(now-self.last_smoke)  if self.last_smoke != 0 else 0
        since_focus=round(now-self.last_focus) if self.last_focus != 0 else 0
        since_purge=round(now-self.last_purge) if self.last_purge != 0 else 0
        since_tree=round(now-self.last_tree) if self.last_tree != 0 else 0
        return s%(self.name,
                  self.presumed_afflictions,
                  since_eat,
                  since_salve,
                  since_pipe,
                  since_focus,
                  since_purge,
                  since_tree,
                  str(','.join(afflictions)))

    def add_aff(self, aff, announce=True):
        aff=normalize_aff(aff)
        
        adict = AfflictionDictionaries()
        aff = adict.t2a(aff)
        aff = adict.s2a(aff)
        if not aff in self.affs:
            self.realm.write(self.name + " received unknown aff " + aff + ". Needs adding to new_aff_dict()")
            return
        if aff == 'sensitivity' and self.deaf:
            self.deaf=False
            return
        
        old_conf = self.affs[aff].on
        self.affs[aff].give_it()
        self.presumed_afflictions+=1
        self.realm.fireEvent('afflictionGainedEvent',self.name, [aff])
        self.realm.cwrite('<white*:purple>%(name)s - Added <green*:red>%(aff)s'%{'name':self.name,
                                                                               'aff':aff})
        if old_conf!=True:
            if self.communicator and announce:
                self.communicator.send_aff(aff,self.name)
            

    def _remove_aff(self, cure, cure_type, cure_msg):
        if not cure_msg == '':
            temp_affs = [v for v in self.affs.values() if v.third_party_cure != '']
            for a in temp_affs:
                if re.match(a.third_party_cure, cure_msg):
                    a.cure_it()
                    self.realm.fireEvent('afflictionLostEvent',self.name, [a.name])
                    self.realm.cwrite('[[<purple*:green>%s]: <purple*:orange>%s]'%(self.name,a.name))
        
                    self.presumed_afflictions-=1
        
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
            if len(temp_affs)==0:
                temp_affs=[v for v in self.affs.values() if v.third_party_cure =='' and
                           v.cured_by(cure_type) and 
                           v.on]
            #if len(temp_affs)==0:
            #    temp_affs=[v for v in self.affs.values() if v.third_party_cure=='' and
            #               v.on]
            
            
            #if len(temp_affs)>1 and not self.remove_ambiguous:
            #    self.presumed_afflictions-=1
            #    self.realm.cwrite('[[<purple*:green>%s]: <purple*:orange>AMBIGUOUS]'%self.name)
        
            #    return
            
            temp_affs = sorted(temp_affs, key=lambda aff:aff.priority)
            if len(temp_affs)>0:
                prio = temp_affs[0].priority
                #old_tmp_affs = [t for t in temp_affs]
                if cure:
                    temp_affs = [v for v in self.affs.values() if v.third_party_cure == '' and 
                                 v.cured_by(cure_type) and 
                                 cure in v.cures and
                                 v.on and 
                                 v.priority == prio]
                else:
                    temp_affs=[v for v in self.affs.values() if v.third_party_cure == '' and 
                               v.cured_by(cure_type) and
                               v.on and
                               v.priority == prio]
                if len(temp_affs)==0:
                    temp_affs=[v for v in self.affs.values() if v.third_party_cure =='' and
                               v.cured_by(cure_type) and 
                               v.on and
                               v.priority == prio]
                #if len(temp_affs) == 0:
                #    self.realm.debug('old: %s'%','.join(['%s:%d'%(a.name,a.priority) for a in old_tmp_affs]))
                #    self.realm.debug('new: %s'%','.join(['%s:%d'%(a.name,a.priority) for a in temp_affs]))
                #    self.realm.debug('prio: %d'%prio)
                if len(temp_affs) == 1:
                    i = 0
                else:
                    self.realm.debug(len(temp_affs))
                    i = random.randint(0, len(temp_affs)-1)
                aff_to_remove=temp_affs[i]
                old_confidence = aff_to_remove.on
                aff_to_remove.cure_it()
                self.realm.cwrite('[[<purple*:green>%s]: <purple*:orange>%s]'%(self.name,aff_to_remove.name))
                self.realm.fireEvent('afflictionLostEvent',self.name, [aff_to_remove.name])
                #if self.realm.gui:
                #    self.realm.gui.set_aff(aff_to_remove.name, False)
                    
                self.presumed_afflictions-=1
                #if (old_confidence==True):
                #    print(self.output())
                    
    def _remove_aff_extra_cure(self, cure_type, cure_msg):
        if not cure_msg == '':
            temp_affs = [v for v in self.affs.values() if v.third_party_cure != '']
            for a in temp_affs:
                if re.match(a.third_party_cure, cure_msg):
                    a.cure_it()
                    self.realm.fireEvent('afflictionLostEvent',self.name, [a.name])
                    self.realm.cwrite('[[<purple*:green>%s]: <purple*:orange>%s]'%(self.name,a.name))
        
                    self.presumed_afflictions-=1
        
        else:
            temp_affs = [v for v in self.affs.values() if v.third_party_cure == '' and 
                v.is_it(cure_type) and 
                v.on]
            #if len(temp_affs)==0:
            #    temp_affs=[v for v in self.affs.values() if v.third_party_cure=='' and
            #               v.on]
            temp_affs = sorted(temp_affs, key=lambda aff:aff.priority)
            if len(temp_affs)>1 and not self.remove_ambiguous:
                self.presumed_afflictions-=1
                self.realm.cwrite('[[<purple*:green>%s]: <purple*:orange>AMBIGUOUS]'%self.name)
        
                return
            if len(temp_affs)>0:
                aff_to_remove=temp_affs[0]
                old_confidence = aff_to_remove.on
                aff_to_remove.cure_it()
                self.realm.cwrite('[[<purple*:green>%s]: <purple*:orange>%s]'%(self.name,aff_to_remove.name))
        
                self.realm.fireEvent('afflictionLostEvent',self.name, [aff_to_remove.name])
                    
                self.presumed_afflictions-=1
                #if (old_confidence==True):
                #    print(self.output())

                    
    def cure_specific_aff(self, affliction):
        #print 'removing specific affliction: %s'%affliction
        if affliction in self.affs:
            self.presumed_afflictions-=1
            self.affs[affliction].cure_it()
            self.realm.fireEvent('afflictionLostEvent',self.name, [affliction])

    def eat_cure(self, cure, cure_msg):
        cure=get_cure(cure)
        self.affs['anorexia'].cure_it()
        self.realm.fireEvent('afflictionLostEvent',self.name, ['anorexia'])
        self.last_eat = time.time()
        if cure == 'juniper':
            self.deaf = True
        else:
            if not cure == '':
                self._remove_aff(cure, HERB, cure_msg)
                
    
    def pipe_cure(self, cure, cure_msg):
        cure=get_cure(cure)
        self.affs['asthma'].cure_it()
        self.realm.fireEvent('afflictionLostEvent',self.name, ['asthma'])
        
        self.last_smoke=time.time()
        self._remove_aff(cure, PIPE, cure_msg)
    
    def salve_cure(self,  cure_msg):
        self.affs['slickness'].cure_it()
        self.realm.fireEvent('afflictionLostEvent',self.name, ['slickness'])
        
        self.last_salve = time.time()  
        self._remove_aff(None, SALVE, cure_msg)
        
    def tree_cure(self, cure_msg):
        self.affs['numbness'].cure_it()
        self.affs['paralysis'].cure_it()
        self.realm.fireEvent('afflictionLostEvent',self.name, ['numbness','paralysis'])
        
        self.last_tree=time.time()
        self._remove_aff_extra_cure(TREEABLE, cure_msg)
          
    def purge_cure(self, cure_msg):
        self.affs['hemotoxin'].cure_it()
        self.realm.fireEvent('afflictionLostEvent',self.name, ['hemotoxin'])
        
        self.last_purge=time.time()
        self._remove_aff_extra_cure(PURGEABLE, cure_msg)
        
    def focus_cure(self, cure_msg):
        self.affs['impatience'].cure_it()
        self.realm.fireEvent('afflictionLostEvent',self.name, ['impatience'])
        
        self.last_focus=time.time()
        self._remove_aff_extra_cure(FOCUSABLE, cure_msg)
    
    def drink_elixir(self):
        self.affs['anorexia'].cure_it()
        self.realm.fireEvent('afflictionLostEvent',self.name, ['anorexia'])
        
        self.last_elixir=time.time()
        
    def passive_cure(self, cure_msg):
        if not cure_msg == '':
            temp_affs = [v for v in self.affs.values() if v.third_party_cure != '']
            for a in temp_affs:
                if re.match(a.third_party_cure, cure_msg):
                    a.cure_it()
                    self.realm.fireEvent('afflictionLostEvent',self.name, [a.name])
        
                    self.realm.cwrite('[[<purple*:green>%s]: <purple*:orange>%s]'%(self.name,a.name))
        
        else:
            temp_affs = [v for v in self.affs.values() if v.third_party_cure == '' and 
                v.on]
            if len(temp_affs)>1 and not self.remove_ambiguous:
                self.realm.cwrite('[[<purple*:green>%s]: <purple*:orange>AMBIGUOUS]'%self.name)
                return
            temp_affs = sorted(temp_affs, key=lambda aff:aff.priority)
            if len(temp_affs)>0:
                aff_to_remove=temp_affs[0]
                old_confidence = aff_to_remove.on
                aff_to_remove.cure_it()
                self.realm.fireEvent('afflictionLostEvent',self.name, [aff_to_remove.name])
        
                self.realm.cwrite('[[<purple*:green>%s]: <purple*:orange>%s]'%(self.name,aff_to_remove.name))
        
                self.presumed_afflictions-=1
                #if (old_confidence==True):
                #    print(self.output())
    
    def time_to_next_purge(self):
        return max(0,self.last_purge+PURGE_BALANCE-time.time())
    
    def time_to_next_tree(self):
        return max(0,self.last_tree + TREE_BALANCE - time.time())
    
    @property
    def tlocked(self):
        return self.affs['anorexia'].on and self.affs['asthma'].on and self.affs['slickness'].on and self.affs['impatience'].on and (self.affs['hemotoxin'].on or self.time_to_next_purge() > 10) and (self.affs['numbness'].on or self.affs['paralysis'].on or self.time_to_next_tree() > 10)
    
    @property
    def pboc(self):
        return self.time_to_next_purge()>0
    
    @property
    def peacecd(self):
        return self.last_peace + 5 - time.time()
    
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
        target = self.realm.get_state('target')
        #if self.realm.gui and self.name==target:
        #    if cure_type==FOCUSABLE:
        #        self.realm.gui.reset_cooldown('focus')
        #    if cure_type==TREEABLE:
        #        self.realm.gui.reset_cooldown('tree')
        #    if cure_type==PURGEABLE:
        #        self.realm.gui.reset_cooldown('purge')
        #    if cure_type==HERB:
        #        self.realm.gui.reset_cooldown('herb')
        #    if cure_type==PIPE:
        #        self.realm.gui.reset_cooldown('pipe')
        #    if cure_type==SALVE:
        #        self.realm.gui.reset_cooldown('salve')
        
    
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
        if self.presumed_afflictions==0:
            for a in self.affs.values():
                a.cure_it()
        
        t = time.time()
        if self.affs['numbness'].on and (t - self.affs['numbness'].last_given)>6:
            self.affs['numbness'].cure_it()
        if self.last_purge != 0 and t - (self.last_purge + PURGE_BALANCE) > 3 and not (self.affs['hemotoxin'].on or (t - self.affs['hemotoxin'].last_cured) < 2):
            for a in [aff.name for aff in self.affs.values() if aff.is_it(PURGEABLE)]:
                self.cure_specific_aff(a)

        if self.last_tree != 0 and t - (self.last_tree + TREE_BALANCE) > 3 and not (self.affs['paralysis'].on or self.affs['numbness'].on or (t - self.affs['numbness'].last_cured) < 2 or (t - self.affs['paralysis'].last_cured) < 2):
            for a in [aff.name for aff in self.affs.values() if aff.is_it(TREEABLE)]:
                self.cure_specific_aff(a)
        
        if self.last_focus != 0 and t - (self.last_focus + FOCUS_BALANCE) > 3 and not (self.affs['impatience'].on or (t - self.affs['impatience'].last_cured) < 2):
            for a in [aff.name for aff in self.affs.values() if aff.is_it(FOCUSABLE)]:
                self.cure_specific_aff(a)
        
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
            if row['cooldown']:
                cooldown=float(row['cooldown'])
            else:
                cooldown =0
            affs[row['affliction']]=Affliction(row['affliction'],cure_types, cures, int(row['priority']),
                                         1.0,row['cure_msg'],cooldown, extra_cures)
            
            
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
    t.add_tentative_cure(HERB, 'toadstool root')
    t.add_tentative_cure(FOCUSABLE,None)
    t.add_tentative_cure_message("test's expression no longer looks so vacant.")
    t.add_tentative_cure(PIPE, 'light, bluish mist')
    t.add_aff('clumsiness')
    print('stupidity: %s'%t['stupidity'].on)
    print('xeroderma: %s'%t['xeroderma'].on)
    print('clumsiness: %s'%t['clumsy'].on)
    t.process()
    