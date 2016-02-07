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
        self.killed_list=[]
        self.agg_mobs=[]
        self.next_room=-1
        self.health_pct=1.0
        self.skip=2
        self.safe_list=['larion']
        self.state='bashing'
        self.do_next_room=False
        self.autowalking=False
        settings_dir = os.path.join(os.path.expanduser('~'), 'muddata',)
        if os.path.isfile(os.path.join(settings_dir,'basher_aggro_mobs.pickle')):
            f=open(os.path.join(settings_dir,'basher_aggro_mobs.pickle'),'r')
            self.agg_mobs=pickle.load(f)
            
        self._autobash = False
        if os.path.isfile(os.path.join(settings_dir,'/basher_area_bash_lists.pickle')):
            input_file = open(os.path.join(settings_dir,'/basher_area_bash_lists.pickle','r'))
            realm.cwrite('Found file!')
            
            self.area_bash_lists=pickle.load(input_file)
        else:
            realm.cwrite('Didnt find file %s'%os.path.join(settings_dir,'basher_area_bash_lists.pickle'))
        if os.path.isfile(os.path.join(settings_dir,'/basher_pathing.pickle')):
            f=open(os.path.join(settings_dir,'/basher_pathing.pickle'))
            self.pathing=pickle.load(f)
        self.pb_balance=True
        self.unknown_affs=0
        
    @property
    def aliases(self):
        return [self.bash,self.target,self.autobash, self.scan_room,
                self.add_target_to_area, self.save_state, self.kill_next,
                self.basher_on, self.record_path, self.stop_record_path, self.move_next,
                self.basher_off, self.basher_pause, self.reset_area,
                self.set_skip]
    
    @property
    def triggers(self):
        return [self.on_balance, self.health_gain, self.stop_autowalking, self.unknown_affliction,
                self.pb_back, self.pb_do_pb, self.pb_no_affs,self.pb_not_back]
    
    @property
    def gmcp_events(self):
        return [self.on_room_info, self.on_affliction_remove, 
                self.on_item_remove, self.on_char_vitals]
    
    @binding_alias('^set_skip (\d+)$')
    def set_skip(self,match,realm):
        self.skip=int(match.group(1))
        realm.write("set skip number to %d"%self.skip)
        realm.send_to_mud=False
        
    @binding_alias('^bon$')
    def basher_on(self,match,realm):
        realm.send_to_mud=False
        self.on=True
        self.move_index=0
        self.next_room=-1
        self.autowalking=False
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
        
    @binding_gmcp_event('Char.Vitals')
    def on_char_vitals(self, data, realm):
        if not self.on:
            return
        hp = float(data['hp'])
        maxhp=float(data['maxhp'])
        self.health_pct=hp/maxhp
        if self.state=='bashing' and self.health_pct<.25:
            realm.cwrite('<red*:white>Health is low! Entering recovery state!')
            self.state='recovery'
        if self.state=='recovery' and self.health_pct>.75:
            realm.cwrite('<green*:white>Recovered enough health.  Resuming bashing!')
            self.state='bashing'
            self.on_balance_op(realm)
        
    @binding_trigger('^H:(\d+) M:(\d+)')
    def prompt(self, match, realm):
       #realm.alterer.insert(-1, ' <hahah<')
       #realm.cwrite('[hahah]')
       pass
        
        
    def on_balance_op(self,realm):
        if not self.on:
            return
        if self._autobash==1:
            realm.send("touch amnesia|stand|queue eqbal kill %s"%self.tar)
        else:
            if len(self.room_bash_list)>0:
                if self.state=='recovery':
                    realm.cwrite('Room not safe for recovery - moving on!')
                    self.MoveToNextRoom(realm)
                else:
                    realm.send("touch amnesia|stand|queue eqbal kill %s"%self.room_bash_list[0])
            else:
                if self.state=='recovery':
                    realm.cwrite('Safe room for recovery.  Resting here for a while!')
                elif self.health_pct<0.75:
                    realm.cwrite('Recovering health post-battle...')
                    self.state='recovery'
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
        if not self.on:
            return
        room_num = gmcp_data['num']
        self.current_area=gmcp_data['area']
        self.exits=gmcp_data['exits']
        if room_num != self.current_room : #We've entered a new room.
            print('New room: %d'%room_num)
            self.current_room=room_num
            self.killed_list =[]
            if self.do_next_room and (room_num == self.next_room or self.next_room == -1):
                self.move_index+=1
            if self.recording_path==True:
                self.recorded_path.append(room_num)
                realm.write('+%s'%room_num)
            if not self.autowalking:
                self.scanRoomForBashing(realm)
            
    @binding_alias('^reset_area')
    def reset_area(self,match,realm):
        realm.send_to_mud=False
        realm.write('resetting all targets in the area')
        self.area_bash_lists[self.current_area]=[]        
        realm.write(self.area_bash_lists)
    
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
        if not self.on:
            return
        if "prone" in gmcp_data and self.on:
            print('on balance op affliction remove')
            self.on_balance_op(realm)
     
    @binding_gmcp_event('Char.Items.Remove')
    def on_item_remove(self, gmcp_data, realm): 
        if not self.on:
            return
        if len(self.room_bash_list)>0 and gmcp_data['item']['id']==self.room_bash_list[0]:
            #self.room_bash_list.pop(0)
            self.killed_list.append(gmcp_data['item']['id'])
            self.scanRoomForBashing(realm,self.killed_list)
            
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
    
    def scanRoomForBashing(self, realm, exclude=[]):
        realm.write('Scanning room for mobs to kill')
        if not self.area_bash_lists.has_key(self.current_area) or not realm.gmcp.has_key('Char.Items.List') or not self.on:
            if not self.area_bash_lists.has_key(self.current_area):
                realm.write('test1')
                realm.write(self.area_bash_lists)
            if not realm.gmcp.has_key('Char.Items.List'):
                realm.write('test2')
            if not self.on:
                realm.write('test3')
            return
        realm.write('Players: %d'% len(realm.gmcp['Room.Players']))
        if len(realm.gmcp['Room.Players']) > 0:
            others = False
            for p in realm.gmcp['Room.Players']:
                if not p['name'].lower() in self.safe_list:
                    self.moveToNextRoom(realm)
                    realm.write('Unrecognized players, %s'%p['name'].lower())
                    return
            
        area_kill_list = self.area_bash_lists[self.current_area]
        obj_list = realm.gmcp['Char.Items.List']['items']
        realm.write(obj_list)
        self.room_bash_list=[]
        aggs=0
        for t1 in area_kill_list:
            for t2 in obj_list:
                if t1 in t2['name'] and (exclude==[] or not t2['id'] in exclude):
                    self.room_bash_list.append(t2['id'])
                    if t2['id'] in self.agg_mobs or (self.current_area.lower() == 'the vorrak mines' and 'ogre' in t2['name']) or self.current_area.lower() == "demon's pass" or self.current_area.lower() == 'the necropolis' or 'underworld' in self.current_area.lower():
                        aggs+=1
        if (aggs>self.skip) or (self.state=='recovery' and aggs>0):
            realm.cwrite('<red*:green>Too many mobs! <green*:red>(There are %d mobs)'%aggs)
            realm.send('ih')
            self.MoveToNextRoom(realm)
        else:
            print('on_balance scanRoomForBashing')                        
            self.on_balance_op(realm)
        
    def MoveToNextRoom(self, realm):
        realm.send('queue eqbal put gold in pack')
        if self.current_area in self.pathing:
            if len(self.pathing[self.current_area]) > self.move_index+1:
                self.next_room = self.pathing[self.current_area][self.move_index+1]
                print('>>>>>> %d'%self.current_room)
                print('next room: %d'%self.next_room)
                print('room exits: %s'%str(self.exits))
                print('index: %d'%self.move_index)
                print('path: %s'%str(self.pathing[self.current_area][max(0,self.move_index-2):self.move_index+2]))
                print('<<<<<<')
                for k in self.exits:
                    if self.exits[k]==self.next_room:
                        
                        #self.delayed_caller=realm.root.factory.reactor.callLater(0.5, realm.root.send, k)
                        self.delayed_caller=realm.root.set_timer(0.5, realm.root.send, k)
                        self.do_next_room=True
                        return
                realm.send('path find %s|path go'%self.next_room)
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
        

    