'''
Created on Nov 17, 2015

@author: Dmitry
'''
from pymudclient.modules import BaseModule
from pymudclient.aliases import binding_alias

class AutocuringControl(BaseModule):
    '''
    classdocs
    '''


    def __init__(self, manager):
        BaseModule.__init__(self,manager)
        self.autocuring=True
        self.manager.set_state('autocuring','on')
        
    @property
    def aliases(self):
        return [self.acon, self.acoff]
        
    @binding_alias('^acon$')
    def acon(self, match, realm):
        realm.send_to_mud=False
        self.manager.set_state('autocuring','on')
        self.autocuring=True
        realm.send('autocuring on')
        self.manager.safe_to_send = True
        realm.cwrite('<white> Autocuring is <green*>ON')
        realm.fireEvent('autocuringStateChangeEvent','on')
        
    @binding_alias('^acoff$')
    def acoff(self, match, realm):
        realm.send_to_mud=False
        self.manager.set_state('autocuring','off')
        self.autocuring=False
        self.manager.safe_to_send = False
        realm.send('autocuring off')
        realm.cwrite('<white> Autocuring is <red*>OFF')
        realm.fireEvent('autocuringStateChangeEvent','off')
        
    