'''
Created on Aug 6, 2015

@author: dmitry
'''
from pymudclient.modules import BaseModule
from pymudclient.gmcp_events import binding_gmcp_event
from pymudclient.triggers import binding_trigger
from pymudclient.aliases import binding_alias
import os
import pickle

class CityDefenseChecker(BaseModule):
    '''
    classdocs
    '''


    def __init__(self, realm):
        '''
        Constructor
        '''
        BaseModule.__init__(self,realm)
        self.current_path=[]
        self.room_index=0
        self.paths={}
        if os.path.isfile(realm.module_settings_dir+'/CityDefPaths.pickle'):
            f=open(realm.module_settings_dir+'/CityDefPaths.pickle','r')
            self.paths=pickle.load(f)
        
        self.current_room=0
        self.state=''
        self.on=False
        self.cur_mono=0
        self.all_monos=[]
        self.rooms_checked=[]
        self.item_checked = 'a hazeward stone'
        
    @property
    def gmcp_events(self):
        return[self.on_room_info]
        
    @property
    def triggers(self):
        return[self.usefulness, self.date, self.prompt]
        
    @property
    def aliases(self):
        return [self.command]
    
    @binding_alias('citydef (\w+)(?: (\w+))?')
    def command(self, match,realm):
        realm.send_to_mud=False
        com=match.group(1)
        arg=match.group(2)
        if com=='start':
            self.on=True
            print(self.paths)
            if arg in self.paths:
                self.current_path=self.paths[arg]
                self.room_index=0
                self.rooms_checked=[]
                self.current_room = realm.root.gmcp['Room.Info']['num']
                self.current_exits=realm.root.gmcp['Room.Info']['exits']
                while not self.current_path[self.room_index]==self.current_room and self.room_index < len(self.current_path):
                    self.room_index+=1
                print('Def Checker start.  Room Index %d'%self.room_index)
                self.state='new_room_scan'
                self.run()
        elif com=='stop':
            self.on=False
        elif com=='map':
            realm.cwrite('<red:blue>Starting to map!')
            self.state='map'
            self.current_path=[]
            realm.send('ql')
        elif com=='mapdone':
            realm.cwrite('<blue:red>Mapping Done!')
            self.state=''
            self.paths[arg]=self.current_path
            f=open(realm.root.module_settings_dir+'/CityDefPaths.pickle','w+')
            pickle.dump(self.paths, f)
        elif com=='process':
            if self.state=='path_done':
                self.process_data()
                self.state='processing_done'
        elif com=='write_mono':
            if self.state=='processing_done':
                self.write_mono_report() 
        elif com=='set_item':
            self.item_checked=arg
    
    @binding_gmcp_event('Room.Info')
    def on_room_info(self, gmcp_data, realm):
        if gmcp_data['num']!=self.current_room:
            self.do_new_room(gmcp_data)
            
    @binding_trigger('^Today is the (\d+)(?:(?:th)|(?:nd)|(?:st)|(?:th)) day of (\w+) .*, in the year (\d+)')
    def date(self, match,realm):
        if self.state=='get_date':
            day=match.group(1)
            month=match.group(2)
            year=match.group(3)
            self.the_date={'day':day, 'month':month, 'year':year}
            self.state='path_done'
            
    @binding_trigger('It has (\d+) months? of usefulness left\.')
    def usefulness(self, match, realm):
        num_months=int(match.group(1))
        if self.state=='scan_mono':
            if not self.current_room in self.rooms_checked:
                self.all_monos.append({'months':num_months, 'vnum':self.cur_mono,'room':self.current_room})
            self.state='do_monolith'
            self.run()
    @binding_trigger('^H:(\d+)')
    def prompt(self,match,realm):
        if self.state=='room_done' or self.state=='do_monolith':
            self.run()
            
    def do_new_room(self,gmcp_data):
        self.current_room=gmcp_data['num']
        self.current_exits=gmcp_data['exits']
        if self.state=='map':
            self.current_path.append(gmcp_data['num'])
            self.manager.cwrite('Adding room %s to path'%self.current_room)
            print('path length %d'%len(self.current_path))
        elif self.on:
            if self.state=='move_to_next_room':
                self.room_index+=1
            self.state='new_room_scan'
            
        
            self.run()
        
        
    def run(self):
        if self.state=='new_room_scan':
            if self.current_room in self.rooms_checked:
                self.state='room_done'
            else:    
                items=self.manager.gmcp['Char.Items.List']['items']
                self.room_monoliths=[]
                self.state='room_done'
                for item in items:
                    print('comparing %s to %s'%(item['name'],self.item_checked))
                    if item['name']==self.item_checked:
                        self.room_monoliths.append(item['id'])
                        self.state='do_monolith'
            self.manager.send('ql')
        elif self.state=='do_monolith':
            if len(self.room_monoliths) == 0:
                self.state='room_done'
                self.manager.send('ql')
            else:
                mono=self.room_monoliths.pop(0)
                self.state='scan_mono'
                self.cur_mono=mono
                self.manager.send('probe %s'%mono)
        elif self.state=='room_done':
            if self.current_room not in self.rooms_checked:
                self.rooms_checked.append(self.current_room)
            if self.current_path[self.room_index]!= self.current_room:
                print(self.current_path)
                print(self.room_index)
                print(self.current_room)
                self.manager.cwrite("Room desyncronized")
                self.room_index=0
                while self.current_path[self.room_index]!=self.current_room:
                    self.room_index+=1
            
            if self.room_index+1<len(self.current_path):
                self.manager.cwrite('<red:blue>Path progress: %d/%d'%(self.room_index,len(self.current_path)))
                next_room=self.current_path[self.room_index+1]
                next_dir = ''
                for nd in self.current_exits:
                    if self.current_exits[nd]==next_room:
                        next_dir=nd
                        
                print('--start--')
                print('path: %s'%str(self.current_path))
                print('current room %s'%self.current_room)
                print('next_dir %s'%next_dir)
                print('next room %s'%next_room)
                print(self.current_exits)
                print('room_index %s'%self.room_index)
                print('--end--')
                self.manager.cwrite('<red:blue>Next exit is %s'%next_dir)
                self.state='move_to_next_room'
                self.delayed_caller=self.manager.factory.reactor.callLater(0.2, self.manager.send, next_dir)
                
            else:
                self.manager.cwrite('<red:blue>Path done!')
                self.state='get_date'
                self.on=False
                self.manager.send('date')
                print(self.all_monos)                
                
    def process_data(self):
        self.mono_sorted_by_left = sorted(self.all_monos, key=lambda mono: mono['months'])
        self.manager.cwrite('<red*>~~~Soonest to decay~~~')
        for i in self.mono_sorted_by_left[:10]:
            self.manager.cwrite('<red*> vnum: %s, room: %s, months left: %s'%(i['vnum'],i['room'],i['months']))
        self.mono_less_than_20 = [i for i in self.all_monos if int(i['months'])<20]
        self.manager.cwrite('<red*>~~~Less than 20 months~~~~')
        for i in self.mono_less_than_20:
            self.manager.cwrite('<red*> vnum: %s, room: %s, months left: %s'%(i['vnum'],i['room'],i['months']))
        self.room_mono_dict={}
        for i in self.all_monos:
            room=i['room']
            if not room in self.room_mono_dict:
                self.room_mono_dict[room]=[]
            self.room_mono_dict[room].append(i)
        self.rooms_with_no_monos=[r for r in self.rooms_checked if r not in self.room_mono_dict]
        if len(self.rooms_with_no_monos)>0:
            self.manager.cwrite('<red*>~~Rooms with no mono~~')
            for i in self.rooms_with_no_monos:
                self.manager.cwrite('<red*>%s'%i)
        self.rooms_with_one_mono=[r for r in self.room_mono_dict if len(self.room_mono_dict[r]) == 1]
        if len(self.rooms_with_one_mono)>0:
            self.manager.cwrite('<red*>~~Rooms with 1 mono~~')
            for i in self.rooms_with_one_mono:
                self.manager.cwrite('<red*>%s'%i)
        
    def write_mono_report(self):
        self.manager.send('~~~~~Monolith Inspection Report~~~~')
        self.manager.send('Performed by Alesei Lynne')
        self.manager.send('Date: %s'%self.get_date())
        self.manager.send('Rooms Checked: %s'%len(self.rooms_checked))
        self.manager.send(' ')    
        self.manager.send('~~Rooms with no Monolith~~')
        if len(self.rooms_with_no_monos)==0:
            self.manager.send('None')
        else:
            for i in self.rooms_with_no_monos:
                self.manager.send(str(i))
        self.manager.send(' ')
        self.manager.send('~~Rooms with one Monolith~~')
        if len(self.rooms_with_one_mono)==0:
            self.manager.send('None')
        else:
            for i in self.rooms_with_one_mono:
                self.manager.send(str(i))
        self.manager.send(' ')
        self.manager.send('~~Monoliths with less than 20 months left~~')
        if len(self.mono_less_than_20)==0:
            self.manager.send('None')
        else:
            for i in self.mono_less_than_20:
                self.manager.send('Room: %s. vnum: %s.  Months Left: %s'%(i['room'],i['vnum'],i['months']))
            
        self.manager.send(' ')
        self.manager.send('~~20 Monoliths that expire the soonest~~')
        for i in self.mono_sorted_by_left[:20]:
                self.manager.send('Room: %s. vnum: %s.  Months Left: %s'%(i['room'],i['vnum'],i['months']))
        
    def get_date(self):
        return '%s - %s - %s'%(self.the_date['day'],self.the_date['month'], self.the_date['year'])
            
class MainModule(CityDefenseChecker):
    pass    