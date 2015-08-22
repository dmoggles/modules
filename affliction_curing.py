'''
Created on Aug 11, 2015

@author: Dmitry
'''

import random
import logging

class Affliction:
    def __init__(self, name, short, priority, herb, salve, pipe, purgable, focusable, use_purge, use_focus, use_tree):
        self.name=name
        self.short=short
        self.priority
        self.herb=herb
        self.salve=salve
        self.pipe=pipe
        self.purgable = True if purgable=="1" else False
        self.focusable = True if focusable=="1" else False
        self.use_purge = True if use_purge=="1" else False
        self.use_focus = True if use_focus=="1" else False
        self.use_tree = True if use_tree=="1" else False
        
        
        
class Priority:
    def __init__(self,random=True):
        self.queue={i:[] for i in xrange(11)}
        self.set={}
        self.random=random
    
    def add(self, item):
        if item.name in self.set:
            self.remove(item)
        priority = item.priority
        if not priority in self.queue:
            self.queue[priority]=[]
        self.queue[priority].append(item.name)
    
    def has_item(self, item):
        return item.name in self.set
    
    def remove(self,key):
        if key in self.set:
            priority=self.set[key]
            self.queue[priority].remove(key)
            if len(self.queue[priority])==0:
                self.queue.remove(priority)
            self.set.remove(key)
    
    def pop(self):
        if len(self.set)==0:
            return None
        priority=min(self.queue.keys())
        if self.random:
            el=random.randint(0, len(self.queue[priority]))
        else:
            el=0
        key=self.queue[priority][el]
        item=self.set[key]
        self.remove(key)
        return item
    
    def peek(self):
        
        priority=min(self.queue.keys())
        if self.random:
            el=random.randint(0, len(self.queue[priority]))
        else:
            el=0
        key=self.queue[priority][el]
        item=self.set[key]
        return item
            
        
class AfflictionCuring:
    def __init__(self):
        self.affliction_data={}
        self.smoke_queue = Priority()
        self.herb_queue = Priority()
        self.salve_queue = Priority()
        self.afflictions = {}
        self.formaldehyde=0
        self.herbb=True
        self.salveb=True
        self.pipeb=True
        
        self.next_herb_to_eat=None
        self.next_pipe_to_smoke=None
        self.next_salve_to_apply=None
    
    def add_affliction(self, affliction_name):
        if not affliction_name in self.affliction_data:
            logging.error("Unknown affliction %s"%affliction_name)
            return
        affliction = self.affliction_data[affliction_name]
        self.afflictions[affliction_name]=affliction
        
        
    def handle_herb(self):
        self.next_herb_to_eat=None
        if not self.herbb:
            logging.debug("Don't have herb balance")
            return
        if 'anorexia' in self.afflictions:
            logging.debug("Can't eat herb - have anorexia")
            return
        self.next_herb_to_eat=self.pick_herb()
        
    def pick_herb(self):
        affliction=self.herb_queue.peek()
        return affliction.herb
    
    def handle_salve(self):
        self.next_salve_to_apply=None
        if not self.salveb:
            logging.debug("Don't have salve balance")