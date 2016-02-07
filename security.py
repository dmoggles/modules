'''
Created on Oct 20, 2015

@author: Dmitry
'''
from pymudclient.modules import EarlyInitialisingModule
from pymudclient.aliases import binding_alias

class CitySecurity(EarlyInitialisingModule):
    '''
    classdocs
    '''


    def __init__(self, squad_name):
        '''
        Constructor
        '''
        self.squad_name=squad_name
        
    
    
    @property
    def aliases(self):
        return[self.move_guards]
        
    
    @binding_alias('^mg(\w+)$')
    def move_guards(self, match, realm):
        realm.send_to_mud=False
        direction = match.group(1)
        if not direction in ['n','nw','w','sw','s','se','e','ne','in','out','u','d']:
            realm.cwrite('<red*>Unknown guard move direction, %s'%direction)
            return
        room_name = realm.root.gmcp['Room.Info']['name']
        realm.send('order squad %s move %s|%s'%(self.squad_name, direction, direction))
        realm.send('rt Moving %s from %s to %s'%(self.squad_name, room_name, direction))
        
        