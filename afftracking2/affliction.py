'''
Created on Nov 3, 2015

@author: Dmitry
'''

import time




class Affliction:
    def __init__(self, name, cure_method, curative, priority, cure_msg, contextual_clue=False):
        self.name=name
        self.on=False
        self.cure_method=cure_method
        self.curative=curative
        self.priority=priority
        self.default_priority=priority
        self.cure_msg=cure_msg
        self.last_afflicted_time=0
        self.last_cured_time=0
        self.contextual_clue = contextual_clue
        
    def afflict(self):
        self.on=True
        self.last_afflicted_time=time.time()
        
    def cure(self):
        self.on=False
        self.last_cured_time=time.time()
        
    def reset_priority(self):
        self.priority=self.default_priority
        
        