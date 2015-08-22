from pymudclient.modules import  EarlyInitialisingModule
from pymudclient.aliases import binding_alias
from pymudclient.triggers import binding_trigger

class EvileyeCombo:
    def get_combo(self):
        pass
    
    
class EvileyePriorityList(EvileyeCombo, EarlyInitialisingModule):
    def __init__(self, realm, affliction_tracker):
        self.tracker=affliction_tracker
        self.realm=realm
        
        
        
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
    def __init__(self, manager):
        self.warded = False
        
    @property
    def triggers(self):
        return [self.hit_curseward, self.strip_curseward]
    
    
    @binding_trigger(['^You try to give (\w+) the evileye, but he is warded\.$',
                      '^A shimmering curseward appears around (\w+)\.$'])
    def hit_curseward(self, match, realm):
        realm.display_line=False
        
        target = realm.root.state['target']
        if match.group(1) == target:
            self.warded = True
            realm.cwrite('<red*:yellow>Curseward is UP on %s!'%target)
            
    @binding_trigger('^His curseward has failed!$')
    def strip_curseward(self, match, realm):
        realm.display_line=False
        self.warded=False
        target = realm.root.state['target']
        realm.cwrite('<green*:yello>Curseward is DOWN on %s!'%target)
        
        