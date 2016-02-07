'''
Created on Oct 12, 2015

@author: Dmitry
'''
from pymudclient.modules import EarlyInitialisingModule
from pymudclient.triggers import binding_trigger
import time

TEETH_CD=4
FLESHBURN_CD=4

class EnhancementFlares(EarlyInitialisingModule):
    '''
    classdocs
    '''


    def __init__(self, realm):
        self.realm = realm
        self.last_teeth = 0
        self.last_fleshburn=0
        
    
    @property
    def triggers(self):
        return [self.teeth,
                self.fleshburn]
    
    @binding_trigger("^As the weapon strikes (\w+), it burns (?:his|her) flesh painfully\.$")
    def fleshburn(self, match, realm):
        target = realm.root.get_state('target').lower()
        person = match.group(1).lower()
        if target==person:
            self.last_teeth=time.time()
    
    @binding_trigger("^The teeth along the weapon edge cut into (\w+)'s flesh\.$")
    def teeth(self, match, realm):
        target = realm.root.get_state('target').lower()
        person = match.group(1).lower()
        if target==person:
            self.last_teeth=time.time()
    
    @property
    def fleshburn_cd(self):
        if self.last_fleshburn==0:
            return 0
        return max(0, self.last_fleshburn+FLESHBURN_CD-time.time())            
    @property
    def teeth_cd(self):
        if self.last_teeth==0:
            return 0
        return max(0, self.last_teeth+TEETH_CD-time.time())