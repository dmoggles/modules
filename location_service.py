'''
Created on Oct 11, 2015

@author: Dmitry
'''
from pymudclient.modules import EarlyInitialisingModule
from pymudclient import gmcp_events
import os
import json
from pymudclient.gmcp_events import binding_gmcp_event
from pymudclient.aliases import binding_alias
from pymudclient.triggers import binding_trigger

class LocationServices(EarlyInitialisingModule):
    '''
    classdocs
    '''


    def __init__(self, realm):
        self.who_state = None
        self.who_target = ''
        self.who_rooms={}
        self.who_location=''
        self.f_path=os.path.join(os.path.expanduser('~'), 'muddata', 'location')
        if not os.path.isdir(self.f_path):
            os.makedirs(self.f_path,)
        self.vnum_dict={}
        self.name_dict={}
        if os.path.exists(os.path.join(self.f_path,'vnum_dict.xml')):
            self.vnum_dict = json.load(open(os.path.join(self.f_path, 'vnum_dict.xml'),'r'))
            self.name_dict = json.load(open(os.path.join(self.f_path, 'name_dict.xml'),'r'))
            
                                       

        
    @property
    def aliases(self):
        return [self.quit,
                self.whereis,
                self.path_go]
        
    @property
    def gmcp_events(self):
        return [self.on_room_info]
    
    @property
    def triggers(self):
        return [self.who_trigger,
                self.who_end_trigger,
                self.path_search_result]
    
    @binding_alias('^qq$')
    def quit(self, match, realm):
        self.save_data()
    
    
    def save_data(self):
        json.dump(self.vnum_dict, open(os.path.join(self.f_path, 'vnum_dict.xml'),'w'))
        json.dump(self.name_dict, open(os.path.join(self.f_path, 'name_dict.xml'),'w'))
        
    @binding_gmcp_event('Room.Info')
    def on_room_info(self, gmcp_data, realm):
        vnum = int(gmcp_data['num'])
        name= gmcp_data['name'].lower()
        area = gmcp_data['area'].lower()
    
        d={'name':name, 'vnum':vnum, 'area':area}
        self.vnum_dict[vnum]=d
    
        self.name_dict[name]=d
        
    @binding_alias('^where(?: (\w+))?$')
    def whereis(self, match, realm):
        realm.send_to_mud = False
        if match.groups()[0]==None:
            target  = realm.root.get_state('target')
        else:
            target = match.group(1)
        self.who_target = target.lower()
        self.who_state= 'sent_who'
        realm.send('who %s'%target)
            
        
    @binding_trigger("^(?: *)(\w+) - .* - ([\w ']+)$")
    def who_trigger(self, match, realm):
        if self.who_state=='sent_who':
            target = match.group(1)
            location = match.group(2)
            if target.lower() == self.who_target:
                self.who_state = 'sent_path_search'
                self.who_location = location
                realm.send('path search %s'%location)
                realm.root.set_timer(5, self.reset_who_state)
    
    @binding_trigger('^There are (\d+) players in this world\.$')
    def who_end_trigger(self, match, realm):
        if self.who_state == 'sent_who':
            self.who_state = None
            
    @binding_trigger("^(?: *)(\w+)\. ([\w ']+[a-z])(?: *)(\d+)(?: *)([\w ']+[a-z])$")
    def path_search_result(self, match, realm):
        if self.who_state == 'sent_path_search':
            realm.display_line=False
            keys = self.who_rooms.keys()
            if len(keys)==0:
                number = 1
            else:
                number = max(keys)+1
            #number = int(match.group(1))
            vnum = match.group(3)
            room = match.group(4)
            if room.startswith(self.who_location):
                self.who_rooms[number]=vnum
                realm.cwrite('<red*>%2s<white>. %10s - <yellow*>%s'%(str(number), vnum, room))
            
                
        
    @binding_alias('^pf(\w+)$')
    def path_go(self, match, realm):
        realm.send_to_mud=False
        n = int(match.group(1))
        if n in self.who_rooms:
            realm.send('path find %s|path go'%self.who_rooms[n])
        else:
            realm.cwrite('<yellow*>Room dictionary does not have element <red*>%d'%n)
    
    def reset_who_state(self, realm):
        self.who_state=None
        self.who_rooms={}
            