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
from pymudclient.tagged_ml_parser import taggedml
from pymudclient.library.imperian.imperian import get_char_data

profession_map={'deathknight':'demonic',
                'defiler':'demonic',
                'summoner':'demonic',
                'diabolist':'demonic',
                'assassin':'demonic',
                'wytch':'demonic',
                'runeguard':'magick',
                'bard':'magick',
                'druid':'magick',
                'hunter':'magick',
                'renegade':'magick',
                'mage':'magick',
                'templar':'antimagick',
                'monk':'antimagick',
                'priest':'antimagick',
                'berserker':'antimagick',
                'ranger':'antimagick',
                'predator':'antimagick',
                'outrider':'antimagick',
                'amazon':'antimagick'}

class LocationServices(EarlyInitialisingModule):
    '''
    classdocs
    '''


    def __init__(self, realm, mapper):
        self.who_state = None
        self.who_target = ''
        self.who_rooms={}
        self.who_location=''
        #self.f_path=os.path.join(os.path.expanduser('~'), 'muddata', 'location')
        #if not os.path.isdir(self.f_path):
        #    os.makedirs(self.f_path,)
        #self.vnum_dict={}
        #self.name_dict={}
        self.mapper = mapper
        #if os.path.exists(os.path.join(self.f_path,'vnum_dict.xml')):
        #    self.vnum_dict = json.load(open(os.path.join(self.f_path, 'vnum_dict.xml'),'r'))
        #    self.name_dict = json.load(open(os.path.join(self.f_path, 'name_dict.xml'),'r'))
        self.people_db={}
        self.circle_db={'antimagick':{}, 'magick':{}, 'demonic':{}}
        
                                       

        
    @property
    def aliases(self):
        return [self.whereis,
                self.path_go,
                self.print_circles,
                self.full_who]
        
   
    
    @property
    def triggers(self):
        return [self.who_trigger,
                self.who_end_trigger,
                self.path_search_result]
    
    #@binding_alias('^qq$')
    #def quit(self, match, realm):
    #    self.save_data()
    
    def get_color(self, circle):
        if circle=='demonic':
            return 'green*'
        elif circle == 'magick':
            return 'blue*'
        else:
            return 'red*'
    
    @binding_alias('^print circles$')
    def print_circles(self, match, realm):
        realm.send_to_mud = False
        realm.cwrite('\n'.join('<%(color)s>%(circle)s<white>: %(plist)s'%{'color':self.get_color(k),
                                                                   'circle':k,
                                                                   'plist':', '.join(sorted(self.circle_db[k].keys()))} for k in self.circle_db))
    
    @binding_alias('^fwho$')
    def full_who(self, match, realm):
        realm.send_to_mud = False
        self.who_state = 'full_who'
        realm.send('who')
        
    
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
            
        
    @binding_trigger("^(?: *)(\w+) - .* - ([\w ',\-]+)$")
    def who_trigger(self, match, realm):
        location = match.group(2)
        target = match.group(1)
        if self.who_state == 'full_who':
            data = get_char_data(target)
            self.people_db[data['name'].lower()]=data
            self.circle_db[profession_map[data['profession'].lower()]][data['name'].lower()]=data
        if self.who_state=='sent_who':
            
            if target.lower() == self.who_target:
                self.who_state = 'sent_path_search'
                self.who_location = location
                realm.send('path search %s'%location)
                realm.root.set_timer(5, self.reset_who_state)
        
        
        #line = taggedml(' <white>(<yellow*>'+'<white>,<yellow>'.join([str(i.vnum) for i in self.mapper.find_by_name(location)]) + '<white>)')
        l = [str(i.vnum) for i in self.mapper.find_by_name(location)]
        if len(l) == 1:            
            line = ' <white>(<yellow*>%s<white>)'%l[0]
        elif len(l) == 0:
            line = ' <white>(<red*>*<white>)'
        else:
            line = ' <white>(<yellow*>%s<white>,<yellow*>...<white>)'%l[0]
            
        ml = taggedml(line)
        #realm.cwrite(line)
       
        realm.alterer.insert_metaline(len(realm.metaline.line), ml)
       
        
                    
    @binding_trigger('^There are (\d+) players in this world\.$')
    def who_end_trigger(self, match, realm):
        if self.who_state == 'sent_who' or self.who_state == 'full_who':
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
            area = match.group(2)
            vnum = match.group(3)
            room = match.group(4)
            if room.startswith(self.who_location):
                self.who_rooms[number]=vnum
                realm.cwrite('<red*>%2s<white>. %10s - <yellow*>%s <red*>(%s)'%(str(number), vnum, room,area))
            
                
        
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
            