'''
Created on Nov 11, 2015

@author: Dmitry
'''
from pymudclient.modules import EarlyInitialisingModule
from pymudclient.aliases import binding_alias
from pymudclient.gmcp_events import binding_gmcp_event
from pymudclient.triggers import binding_trigger
from time import time
class Walker(EarlyInitialisingModule):
    '''
    classdocs
    '''


    def __init__(self, manager, mapper):
        self.manager = manager
        self.map=mapper
        self.status="ready"
        self.path=[]
        self.celerity = 2
        self.moves=[]
        self.delayed_move=None
        self.blacklist = []
        
        
        
    def set_path(self, path):
        self.status='onpath'
        self.path=path
        
    @property
    def triggers(self):
        return [self.water]
    
    @property
    def aliases(self):
        return [self.next,
                self.traverse,
                self.set_blacklist]
    
    @property
    def gmcp_events(self):
        return [self.on_room_info]
    
    @binding_gmcp_event('Room.Info')
    def on_room_info(self, gmcp_data, realm):
        if self.status=='onpath':
            if int(gmcp_data['num'])== self.path[0]:
                self.makes_a_move=False
                p=self.path.pop(0)
                realm.root.fireEvent('newRoomWalkerEvent',p)
                self.moves.append(time())
                
               
               
    @binding_alias('^wblacklist (.*)$')
    def set_blacklist(self, match, realm):
        self.blacklist = [int(s) for s in match.group(1).split(',')]
        realm.send_to_mud = False
        realm.cwrite('<green*>WALKER INFO: <white> set blacklist to %s'%match.group(1))
        
        
    
    @binding_alias('^wtraverse$')
    def traverse(self, match, realm):
        realm.send_to_mud=False
        room=int(self.manager.gmcp['Room.Info']['num'])
        p = self.map.traverse(room, self.blacklist)
        realm.cwrite('<green*>WALKER INFO:<white> Set traversal path.  Length: %d'%len(p))
        self.set_path(p[1:])
    
    @binding_trigger("^There's water ahead of you\. You'll have to swim to make it through\.$")
    def water(self, match, realm):
        if self.makes_a_move:
            realm.send('swim %s'%self.move)
        
    def eqbal_move(self, realm):
        realm.send('queue eqbal %s'%self.move)
    
    def noeqbal_move(self, realm):
        realm.send('%s'%self.move)
        
    @binding_alias('^wnext$')
    def next(self,match, realm):
        self.do_next(match, realm, self.noeqbal_move)

    @binding_alias('^wnexteqbal')
    def nexteqbal(self, match, realm):
        self.do_next(match, realm, self.eqbal_move)
    
    def do_next(self, match, realm,move_f):
        realm.send_to_mud=False
        if not self.status == 'onpath':
            realm.cwrite('<red*>WALKER ERROR:<white> Walker not on path')
        else:
            if self.delayed_move and self.delayed_move.active():
                self.delayed_move.cancel()
                self.delayed_move=None
                
            cur_room = int(self.manager.gmcp['Room.Info']['num'])
            next_room = self.path[0]
            if not next_room in self.map[cur_room].exits:
                realm.cwrite('<red*>WALKER ERROR:<white> Next room not found.  Off Path.')
                self.status='offpath'
            else:
                self.makes_a_move=True
                while len(self.moves)>0 and (time() - self.moves[0])>1:
                        self.moves.pop(0)
                self.move = self.map[cur_room].exits[next_room]
                if len(self.moves)<self.celerity:
                    self.eqbal_move(realm)
                    
                else:
                    
                    self.delayed_move=realm.root.set_timer(1-(time()-self.moves[0]),move_f)
                    
    
    
        