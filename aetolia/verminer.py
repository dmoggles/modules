'''
Created on Jan 8, 2016

@author: dmitry
'''
from pymudclient.modules import BaseModule, EarlyInitialisingModule
from pymudclient.gmcp_events import binding_gmcp_event
from pymudclient.aliases import binding_alias
from movement.map import MapFromXml
from movement.walker import Walker
from pymudclient.triggers import binding_trigger


vermins = ['pincher','beetle']
monsters = ['cricket']

class Verminer(EarlyInitialisingModule):
    def __init__(self, manager, walker, kill_command):
        self.walker = walker
        self.kill_command = kill_command
        self.status = 'off'
        self.vermin_limit = 3
        self.room_vermin_count = 0
        self.vermin_ids = []
        self.current_room = 0
        self.check_delegate = None
        self.ylem = False
        self.post_ylem_need_to_kill = False
        self.post_ylem_need_to_move = False
        self.rooms_done = {}
        self.max_wait_time = 10.0
        #manager.registerEventHandler()
    
    @property
    def gmcp_events(self):
        return [self.on_char_item_add, self.on_room_info]
    
    @property
    def aliases(self):
        return [self.turn_on]
    
    
    @property
    def triggers(self):
        return [self.handle_ylem, self.ylem_handled, self.tar_error]
    
    @binding_trigger("^You can find no such target as '(\d+)'\.")
    def tar_error(self, match, realm):
        if len(self.vermin_ids) > 0 and self.vermin_ids[0] == match.group(1):
            self.vermin_ids.pop(0)
    
    @binding_trigger('^Your vision distorts briefly, light scattering subtly as ylem energy diffuses into the surrounding')
    def handle_ylem(self, match, realm):
        if self.status == 'on':
            realm.cwrite("<black*:white> I'll handle this ylem for you!")
            self.ylem=True
            realm.send('queue eqbal absorb ylem')
    
    @binding_trigger('^You raise your gauntlet, extending your fingers and allowing the latent ylem around you to absorb')
    def ylem_handled(self, match, realm):
        self.ylem=False
        if self.post_ylem_need_to_kill:
            self.kill_next_mob(realm)
        elif self.post_ylem_need_to_move:
            self.move_next(realm)
            
    @binding_alias('^verm reset$')
    def reset(self, match, realm):
        realm.send_to_mud=False
        realm.cwrite('<yellow>Resetting vermin counters!')
        self.rooms_done={}        
            
    @binding_alias('^verm turn (on|off)$')
    def turn_on(self, match, realm):
        realm.send_to_mud = False
        self.status = match.group(1)
        realm.cwrite('<yellow>Verminer is %s'%('<green>On!' if match.group(1) == 'on' else '<red>Off!'))
        if match.group(1) == 'on':
            if realm.root.gmcp['Room.Info']['environment']==str('Sewer'):
                self.vermin_limit=5
            else:
                self.vermin_limit=3
            self.current_room=int(realm.root.gmcp['Room.Info']['num'])
            self.room_vermin_count = 0
            realm.send('wtraverse')
            self.check_delegate = realm.root.set_timer(self.max_wait_time, self.move_next)
        else:
            if self.check_delegate:
                self.check_delegate.cancel()
                self.check_delegate=None
            
            
    def kill_next_mob(self, realm):
        if self.ylem == False:
            self.post_ylem_need_to_kill = False
            realm.send(self.kill_command%str(self.vermin_ids[0]))
        else:
            self.post_ylem_need_to_kill = True
        
    @binding_gmcp_event('Room.Info')
    def on_room_info(self, data, realm):
        if self.current_room != int(data['num']) and self.status == 'on':
            if int(data['num']) in self.rooms_done:
                self.room_vermin_count = self.rooms_done[int(data['num'])]
                wait_time = self.max_wait_time-self.room_vermin_count*(self.max_wait_time/self.vermin_limit) if self.room_vermin_count > 0 else 5
            else:
                self.room_vermin_count = 0
                wait_time = self.max_wait_time
            self.check_delegate = realm.root.set_timer(wait_time, self.move_next)
            self.current_room = int(data['num'])
            
    @binding_gmcp_event('Char.Items.Add')
    def on_char_item_add(self, data, realm):
        if self.status == 'on':
            if str(data['location'])=='room':
                for v in vermins:
                    if v in data['item']['name']:
                        self.vermin_ids.append(int(data['item']['id']))
                        if self.check_delegate:
                            self.check_delegate.cancel()
                            self.check_delegate=None
                        self.kill_next_mob(realm)
            elif str(data['location'])=='inv':
                if int(data['item']['id'])==self.vermin_ids[0]:
                    self.vermin_ids.pop(0)
                    self.room_vermin_count+=1
                    realm.cwrite('<blue*:yellow> Killed <white*:yellow>%d/%d <blue*:yellow>vermins in this room!'%(self.room_vermin_count, self.vermin_limit))
                    if len(self.vermin_ids)>0:
                        self.kill_next_mob(realm)
                    else:
                        if self.room_vermin_count == self.vermin_limit:
                            self.move_next(realm)
                        else:
                            self.check_delegate=realm.root.set_timer(self.max_wait_time-(self.room_vermin_count * (self.max_wait_time/self.vermin_limit)), self.move_next)
                
  
    def move_next(self, realm):
        if self.ylem == False:
            self.rooms_done[self.current_room]=self.room_vermin_count
            realm.cwrite('<red*:yellow> Moving to the next room.  %d rooms left!'%(len(self.walker.path)-1))
            self.post_ylem_need_to_move=False
            realm.send('wnext')
            
        else:
             self.post_ylem_need_to_move = True
  
class MainModule(Verminer):
    def __init__(self, manager):
        Verminer.__init__(self, manager, Walker(manager, MapFromXml('http://www.aetolia.com/maps/map.xml')), 'queue eqbal hammer doublebash %s')
        
       
              