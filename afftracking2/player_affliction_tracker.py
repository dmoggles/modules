
import time

HERB_CURE=1<<0
PIPE_CURE=1<<1
SALVE_CURE=1<<2
TREE_CURE=1<<3
PURGE_CURE=1<<4
FOCUS_CURE=1<<5
ELIXIR = -100
TOADSTOOL = -200

cure_types=[HERB_CURE,PIPE_CURE,SALVE_CURE,TREE_CURE,PURGE_CURE,FOCUS_CURE,ELIXIR,TOADSTOOL]

TREE_BALANCE=15
PURGE_BALANCE=15
FOCUS_BALANCE=4

HERB_BALANCE=2
SALVE_BALANCE=3
PIPE_BALANCE=3

cure_cooldowns={HERB_CURE:     HERB_BALANCE,
               SALVE_CURE:    SALVE_BALANCE,
               PIPE_CURE:     PIPE_BALANCE,
               TREE_CURE:     TREE_BALANCE,
               PURGE_CURE:    PURGE_BALANCE,
               FOCUS_CURE:    FOCUS_BALANCE,
               TOADSTOOL:     6,
               ELIXIR:        5}

class PlayerAfflictionTracking:
    
    #class UncertainCures:
        
    def __init__(self, who, realm):
        self.who=who
        self.affs=create_aff_dict()
        self.realm = realm
        self.times={ct:0 for ct in cure_types}
        self.deaf=True
        self.uncertain_cures=[]
    
    def __getitem__(self, affliction):
        if not affliction in self.affs:
            return None
        return self.affs[affliction]
    
    def add(self, affliction):
        if affliction in self.affs:
            aff=self.affs[affliction]
            
            if aff in self.uncertain_cures:
                self.uncertain_cures.remove(aff)
                
            aff.afflict()
            self.realm.fireEvent('addAfflictionEvent', self.who, aff)
            return True
        return False
    
    def remove(self, affliction, cure_type=None, cure=None):
        if affliction in self.affs:
            aff=self.affs[affliction]
            aff.cure()
            if self.output_handler:
                self.output_handler.remove_affliction(aff, cure_type, cure)
            return True
        return False
    
    
    def cd(self, cure_type):
        if self.times[cure_type]==0:
            return 0
        else:
            return max(0, self.times[cure_type]+cure_cooldowns[cure_type]-time.time())
                
        
        
        
        