'''
Created on Jul 16, 2015

@author: Dmitry
'''
from pymudclient.modules import BaseModule
from pymudclient.aliases import binding_alias
from pymudclient.triggers import binding_trigger
from pymudclient.gmcp_events import binding_gmcp_event
import pickle
import os
from pymudclient.tagged_ml_parser import taggedml
#from twisted.internet import reactor

class BashModule(BaseModule):
    '''
    classdocs
    '''
    name="BashModule"
    def __init__(self,realm):
        BaseModule.__init__(self,realm)
        self.current_area=""
        self.current_room=-1
        self.move_index = 0
        self.recording_path=False
        self.recorded_path=[]
        self.on = False
        self.area_bash_lists = {}
        self.room_bash_list=[]
        self.pathing={}
        self.agg_mobs=[]
        self.do_next_room=False
        self.autowalking=False
        if os.path.isfile(realm.module_settings_dir+'/basher_aggro_mobs.pickle'):
            f=open(realm.module_settings_dir+'/basher_aggro_mobs.pickle','r')
            self.agg_mobs=pickle.load(f)
        self._autobash = False
        if os.path.isfile(realm.module_settings_dir+'/basher_area_bash_lists.pickle'):
            input_file = open(realm.module_settings_dir+'/basher_area_bash_lists.pickle','r')
            self.area_bash_lists=pickle.load(input_file)
        if os.path.isfile(realm.module_settings_dir+'/basher_pathing.pickle'):
            f=open(realm.module_settings_dir+'/basher_pathing.pickle','r')
            self.pathing=pickle.load(f)
        self.pb_balance=True
        self.unknown_affs=0
        
    @property
    def aliases(self):
        return [self.bash,self.target,self.autobash, self.scan_room,
                self.add_target_to_area, self.save_state, self.kill_next,
                self.basher_on, self.record_path, self.stop_record_path, self.move_next,
                self.basher_off, self.basher_pause]
    
    @property
    def triggers(self):
        return [self.on_balance, self.health_gain, self.stop_autowalking, self.unknown_affliction,
                self.pb_back, self.pb_do_pb, self.pb_no_affs,self.pb_not_back]
    
    @property
    def gmcp_events(self):
        return [self.on_room_info, self.on_affliction_remove, self.on_item_remove]
    
    @binding_alias('^bon$')
    def basher_on(self,match,realm):
        realm.send_to_mud=False
        self.on=True
        self.move_index=0
        self.scanRoomForBashing(realm.root)
    
    @binding_alias('^bres$')
    def basher_pause(self,match,realm):
        realm.send_to_mud=False
        self.on=True
        self.scanRoomForBashing(realm)
        
    @binding_alias('^boff$')
    def basher_off(self,match,realm):
        realm.send_to_mud=False
        self.on=False
    
    @binding_trigger(r'^You have reached your destination/.$')
    def stop_autowalking(self, match, realm):
        self.autowalking=False
        
    @binding_alias(r"^tar (\w+)$")
    def target(self, match, realm):
        self.tar=match.groups(1)
        realm.write('Target is %s'%match.groups(1))
        realm.send_to_mud=False
        
    @binding_alias("^bash$")
    def bash(self,match,realm):
        realm.send_to_mud=False
        realm.send("queue eqbal kill %s"%self.tar)
        
    @binding_alias("^autobash$")
    def autobash(self,match,realm):
        self._autobash=True
        self.bash(match,realm)
        
        
    def on_balance_op(self,realm):
        if self._autobash==1:
            realm.send("queue eqbal kill %s"%self.tar)
        else:
            if len(self.room_bash_list)>0:
                realm.send("queue eqbal kill %s"%self.room_bash_list[0])
            else:
                self.MoveToNextRoom(realm)
     
         
    @binding_trigger(r'^You have recovered balance.$')    
    def on_balance(self, match,realm):
        print('actual on balance')
        if self.on:
            self.on_balance_op(realm)
    
    @binding_trigger('^Health gain:')
    def health_gain(self, match, realm):
        if self.on:
            realm.display_line = False            
    
    @binding_gmcp_event('Room.Info')
    def on_room_info(self,gmcp_data,realm):
        room_num = gmcp_data['num']
        self.current_area=gmcp_data['area']
        self.exits=gmcp_data['exits']
        if room_num != self.current_room: #We've entered a new room.
            print('New room: %d'%room_num)
            self.current_room=room_num
        
            if self.do_next_room:
                self.move_index+=1
            if self.recording_path==True:
                self.recorded_path.append(room_num)
                realm.write('+%s'%room_num)
            if not self.autowalking:
                self.scanRoomForBashing(realm)
            
            
        
    
    @binding_alias('^record_path$')
    def record_path(self,match,realm):
        realm.send_to_mud=False
        realm.write('Starting to record path')
        self.recorded_path=[self.current_room]
        self.recording_path=True
        self.recording_area=self.current_area
    
    @binding_alias('^stop_record$')
    def stop_record_path(self,match,realm):
        realm.send_to_mud=False
        realm.write('Path recording done')
        self.pathing[self.recording_area]=self.recorded_path
        self.recording_path=False
        f=open(realm.root.module_settings_dir+'/basher_pathing.pickle','w+')
        pickle.dump(self.pathing, f)
        
    @binding_gmcp_event('Char.Afflictions.Remove')
    def on_affliction_remove(self, gmcp_data, realm):
        if "prone" in gmcp_data:
            print('on balance op affliction remove')
            self.on_balance_op(realm)
     
    @binding_gmcp_event('Char.Items.Remove')
    def on_item_remove(self, gmcp_data, realm): 
          
        if len(self.room_bash_list)>0 and gmcp_data['item']['id']==self.room_bash_list[0]:
            self.room_bash_list.pop(0)
            
    @binding_alias('^scan_room$')
    def scan_room(self, matches, realm):
        realm.send_to_mud=False
        self.scanRoomForBashing(realm.root)
        realm.write(self.room_bash_list)
    
    @binding_alias('^kill_next$')
    def kill_next(self, matches, realm):
        realm.send_to_mud=False
        self.scanRoomForBashing(realm.root)
        self.on_balance(matches, realm)
    
    
    @binding_alias('^add_target_to_area (\w+)$')
    def add_target_to_area(self, matches, realm):
        if self.current_area != "":
            if not self.area_bash_lists.has_key(self.current_area):
                self.area_bash_lists[self.current_area]=[]
            self.area_bash_lists[self.current_area].append(matches.group(1))
        realm.write(self.area_bash_lists)
        realm.send_to_mud=False
    
    @binding_alias('^save_state$')
    def save_state(self,matches,realm):
        output_file=open(realm.root.module_settings_dir+'/basher_area_bash_lists.pickle','w+')
        pickle.dump(self.area_bash_lists, output_file)
        realm.send_to_mud=False
    
    def scanRoomForBashing(self, realm):
        if not self.area_bash_lists.has_key(self.current_area) or not realm.gmcp.has_key('Char.Items.List') or not self.on:
           
            return
        if len(realm.gmcp['Room.Players']) > 0:
            self.moveToNextRoom(realm)
            
        area_kill_list = self.area_bash_lists[self.current_area]
        obj_list = realm.gmcp['Char.Items.List']['items']
        self.room_bash_list=[]
        aggs=0
        for t1 in area_kill_list:
            for t2 in obj_list:
                if t1 in t2['name']:
                    self.room_bash_list.append(t2['id'])
                    if t2['id'] in self.agg_mobs:
                        aggs+=1
        if aggs>2:
            self.MoveToNextRoom(realm)
        else:
            print('on_balance scanRoomForBashing')                        
            self.on_balance_op(realm)
        
    def MoveToNextRoom(self, realm):
        realm.send('queue eqbal put gold in pack')
        if self.current_area in self.pathing:
            if len(self.pathing[self.current_area]) > self.move_index+1:
                next_room = self.pathing[self.current_area][self.move_index+1]
                print('>>>>>> %d'%self.current_room)
                print('next room: %d'%next_room)
                print('room exits: %s'%str(self.exits))
                print('index: %d'%self.move_index)
                print('path: %s'%str(self.pathing[self.current_area][max(0,self.move_index-2):self.move_index+2]))
                print('<<<<<<')
                for k in self.exits:
                    if self.exits[k]==next_room:
                        self.delayed_caller=realm.root.factory.reactor.callLater(0.5, realm.root.send, k)
                        self.do_next_room=True
                        return
                realm.send('path find %s|path go'%next_room)
            else:
                self.autowalking=True
                realm.send('path find %s|path go'%self.pathing[self.current_area][0])
                
                    
    @binding_alias('^move_next$')
    def move_next(self,match,realm):
        self.send_to_mud=False
        self.MoveToNextRoom(realm)
        
    @binding_trigger('^You are confused as to the effects of the toxin')
    def unknown_affliction(self, match, realm):
        if self.on:
            print("unknown_affliction")
            self.unknown_affs+=1
            if self.pb_balance:
                realm.send('pb')
            realm.write(taggedml('<red>Unknown afflictions: <red*>%d'%self.unknown_affs))
    @binding_trigger('^You have regained the ability to purge your body')
    def pb_back(self, match, realm):
        if self.on:
            print("pb_back")
            self.pb_balance=True
            if self.unknown_affs>0:
                realm.send('pb')
                realm.write(taggedml('<red>Unknown afflictions: <red*>%d'%self.unknown_affs))
            
    @binding_trigger('^You concentrate on purging your body of foreign toxins')
    def pb_do_pb(self, match, realm):
        if self.on:
            print("pb_do_pb")
            self.pb_balance=False
            if self.unknown_affs>0:
                self.unknown_affs-=1
                realm.write(taggedml('<red>Unknown afflictions: <red*>%d'%self.unknown_affs))        
    @binding_trigger('^You find your body already clear of harmful substance/.$')
    def pb_no_affs(self, match, realm):
        if self.on:
            print("pb_no_affs")
            self.unknown_affs=0
        
    @binding_trigger('^You have not regained the ability to purge your body of toxins/.$')
    def pb_not_back(self, match, realm):
        if self.on:
            print("pb_not_back")
            self.pb_balance=False
        
class MainModule(BashModule):
    pass

    