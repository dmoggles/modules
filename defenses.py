'''
Created on Aug 14, 2015

@author: Dmitry
'''
from pymudclient.modules import BaseModule
from pymudclient.gmcp_events import binding_gmcp_event
from pymudclient.aliases import binding_alias
import csv
import os

class Defense:
    def __init__(self, name, command, restore):
        self.name=name
        self.command=command
        self.restore=restore

class Defenses(BaseModule):
    '''
    classdocs
    '''


    def __init__(self, manager):
        '''
        Constructor
        '''
        BaseModule.__init__(self,manager)
        self.defense_list={}
        self.load_defense_list(manager)
        self.active_defenses=[]
        self.state='maintain'
        self.always_on=False
        
        
    def load_defense_list(self,realm):
        self.defense_list={}
        
        item_setting_file=realm.module_settings_dir+'/'+realm.factory.name.lower()+'_defenses.csv'
        if os.path.exists(item_setting_file):
            with open(item_setting_file) as csvfile:
                reader=csv.DictReader(csvfile)
                for row in reader:
                    self.defense_list[row['defense']]=Defense(row['defense'],row['command'],row['restore']=='TRUE')
        realm.write('loaded total %d defenses'%len(self.defense_list))
        
        
    @property
    def gmcp_events(self):
        return [self.on_def_add, self.on_def_remove]
    
    @property
    def aliases(self):
        return [self.def_up]
    
    
    
    @binding_gmcp_event('Char.Defences.Add')
    def on_def_add(self, gmcp_data, realm):
        realm.write('Added defense: %s'%str(gmcp_data['name']))
        self.active_defenses.append(gmcp_data['name'])
        self.put_up_next_defense(realm)
        
    
    def put_up_next_defense(self,realm):
        if self.state=='defup' or self.always_on:
            missing_defenses = [d for k,d in self.defense_list.iteritems() if not k in self.active_defenses]
            if len(missing_defenses) == 0:
                self.state='maintain'
                return
        else:
            missing_defenses = [d for k,d in self.defense_list.iteritems() if not k in self.active_defenses and d.restore == True]
            if len(missing_defenses)==0:
                return
            
        realm.send('queue eqbal %s'%missing_defenses[0].command)
        
    @binding_gmcp_event('Char.Defences.Remove')
    def on_def_remove(self, gmcp_data, realm):
        realm.write('Removed defense: %s'%str(gmcp_data))
        for d in gmcp_data:
            self.active_defenses.remove(d)
        self.put_up_next_defense(realm)
        
    @binding_alias('^def (\w+)(?: (\w+))?$')
    def def_up(self, match, realm):
        command = match.group(1)
        option = match.group(2)
        
        realm.send_to_mud = False
        if command=='up':
            self.state='defup'
            self.put_up_next_defense(realm)
        if command=='always':
            if option == 'on':
                self.always_on=True
                realm.cwrite('Restore all defenses: <green*> ON')
            else:
                self.always_on=False
                realm.cwrite('Restore all defenses: <red*> OFF')
        if command=='reset':
            data = realm.root.gmcp['Char.Defences.List']
            self.active_defenses=[d['name'] for d in data]
            realm.cwrite('<red*>Defenses reset!')
        if command=='reload':
            self.load_defense_list(realm)
            
            
        
        
        
class MainModule(Defenses):
    pass