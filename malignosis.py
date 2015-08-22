'''
Created on Aug 12, 2015

@author: Dmitry
'''
from pymudclient.modules import BaseModule
from pymudclient.aliases import binding_alias
from pymudclient.triggers import binding_trigger

class Daegger(BaseModule):
    
    def __init__(self, realm):
        BaseModule.__init__(self,realm)
        self.ready=True
        
    @property
    def triggers(self):
        return [self.daegger_hunt, self.daegger_ready]
    @property
    def aliases(self):
        return [self.summon_daegger, self.hunt]


    @binding_alias('^daeg$')
    def summon_daegger(self,match,realm):
        realm.send_to_mud=False
        realm.send('queue eqbal summon daegger|attach wriststrap to daegger')
    
    @binding_alias('^dh$')
    def hunt(self, match,realm):
        realm.send_to_mud=False
        target=realm.root.state['target']
        realm.send('daegger hunt %s'%target)
        
    @binding_trigger('^"Hunt!" you order your daegger\.$')
    def daegger_hunt(self,match,realm):
        realm.display_line=False
        realm.cwrite('<black:cyan>---- DAEGGER HUNT ----')
        self.ready=False
        self.timed_ready=realm.root.set_timer(12, self._daegger_ready, realm)
        
    @binding_trigger('^The daegger is again ready to hunt its prey\.$')
    def daegger_ready(self,match,realm):
        realm.display_group=False
        realm.cwrite('<white*:cyan>++++ DAEGGER READY ++++')
        self._daegger_ready(realm.root)
        
    def _daegger_ready(self, realm):
        if not self.ready:
            self.ready=True
            realm.cwrite('<white*:cyan>+++++ DAEGGER READY +++++')
        