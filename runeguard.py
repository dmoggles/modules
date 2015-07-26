'''
Created on Jul 23, 2015

@author: dmitry
'''
from pymudclient.modules import BaseModule
from shield_rez import ShieldRez
from pymudclient.aliases import binding_alias
import os
import pickle
from pymudclient.tagged_ml_parser import taggedml
from pymudclient.triggers import binding_trigger
from pymudclient.gmcp_events import binding_gmcp_event
from twisted.conch.test.test_userauth import Realm

class FlareTracker:
    KENA='kena'
    FEHU='fehu'
    PITHAKHAN='pithakhan'
    INGUZ='inguz'
    WUNJO='wunjo'
    SOWULU='sowulu'
    HUGALAZ='hugalaz'
    NAUTHIZ='nauthiz'
    MANNAZ='mannaz'
    SLEIZAK='sleizak'
    NAIRAT='nairat'
    EIHWAZ='eihwaz'
    LOSHRE='loshre'
    RUNES=[KENA,FEHU,PITHAKHAN,INGUZ,WUNJO,SOWULU,HUGALAZ,NAUTHIZ,MANNAZ,SLEIZAK,NAIRAT,EIHWAZ,LOSHRE]
    def __init__(self):
        self.runes={r:1 for r in FlareTracker.RUNES}
        self.priority_list=[]
    def __getitem__(self,key):
        return self.runes[key]
    def __setitem__(self,key,value):
        self.runes[key]=value
    
    def getNextRune(self):
        for r in self.priority_list:
            if self.runes[r]==1:
                return r
        return ''
        
class Runeguard(BaseModule):
    '''
    classdocs
    '''


    def __init__(self, realm):
        '''
        Constructor
        '''
        BaseModule.__init__(self,realm)
        self.shield_razer=ShieldRez(realm)
        
        self.items={}
        self.item_setting_file=realm.module_settings_dir+'/'+realm.factory.name+'_runeguard_items.pickle'
        if os.path.exists(self.item_setting_file):
            f=open(self.item_setting_file,'r')
            self.items=pickle.load(f)
        self.flaretracker=FlareTracker()
        self.flaretracker.priority_list=[FlareTracker.SOWULU,FlareTracker.PITHAKHAN]
        self.lw='0'
        self.rw='0'
        self.weapon_match_status=''
        
        
    @property
    def modules(self):
        return[self.shield_razer]
    @property
    def aliases(self):
        return [self.kestrel_summon, self.bulwark, self.set_weapon,self.ii,self.pain_totem,
                self.transfix_totem,self.dsl,self.reave, self.raze, self.reave_or_raze]
    @property
    def triggers(self):
        return[self.match_item, self.end_of_matching, self.rune_back]
    @property
    def gmcp_events(self):
        return[self.on_char_vitals]
    
    
    @binding_alias('^rrv$')
    def reave_or_raze(self, match,realm):
        target=realm.root.state['target']
        if target in self.shield_razer.raze_data and not self.shield_razer.raze_data[target].all_stripped():
            self.raze(match,realm)
        else:
            self.reave(match, realm)
            
    
    @binding_alias('^raze$')
    def raze(self, match, realm):
        target=realm.root.state['target']
        realm.send('queue eqbal wm raze raze %s'%target)
        realm.root.state['last_command_type']='raze'
        realm.send_to_mud=False
        
        
    @binding_alias('^dsl$')
    def dsl(self, match, realm):
        command=self.make_combo('slash','broadsword',realm)
        
        realm.send('queue eqbal '+command)
        realm.root.state['last_command_type']='attack'
        realm.send_to_mud=False
    
    @binding_alias('^rv$')
    def reave(self, match, realm):
        command=self.make_combo('reave', 'battleaxe', realm)
        realm.send('queue eqbal '+command)
        realm.root.state['last_command_type']='attack'
        realm.send_to_mud=False
    
    def make_combo(self, attack, weapon, realm):    
        target=realm.root.state['target']
        flare=self.flaretracker.getNextRune()
        toxin1,toxin2=('strychnine','strychnine')
        command=''
        if flare==FlareTracker.SOWULU or flare==FlareTracker.PITHAKHAN:
            if self.lw != 'tablet':
                command=command+'unwield left|wield %s left|'%self.items['tablet']
        else:
            if self.lw != 'shield':
                command=command+'unwield left|wield %s left|'%self.items['shield']
                
        if self.rw != weapon:
            command=command+'unwield right|wield %s right|'%self.items[weapon]
        command=command+'grip|order kestrel attack %s|'%target
        if attack=='reave':
            command=command+'tgs|lns|'
        command=command+'wm %s %s %s %s %s|'%(attack, attack, target, toxin1, toxin2)
        command=command+'engage %s|flare %s at %s'%(target, flare, target)
        return command
    
    @binding_alias('^spt$')
    def pain_totem(self, match, realm):
        target=realm.root.state['target']
        realm.send('queue eqbal unwield left|unwield right|wield %s|stand totem for %s'%(self.items['paintotem'],target))
        realm.root.state['last_command_type']='totem'
        realm.send_to_mud=False
        
    @binding_alias('^stt$')
    def transfix_totem(self, match, realm):
        target=realm.root.state['target']
        realm.send('queue eqbal unwield left|unwield right|wield %s|stand totem for %s'%(self.items['transfixtotem'],target))
        realm.root.state['last_command_type']='totem'
        realm.send_to_mud=False
                
    @binding_alias('^ksum$')
    def kestrel_summon(self, match, realm):
        realm.send_to_mud=False
        realm.send('kestrel recall')
        
    @binding_alias('^bw$')
    def bulwark(self, match, realm):
        realm.send_to_mud=False
        command=''
        if not self.lw=='shield':
            command='unwield left|wield %s|grip|'%self.items['shield']
        realm.send('queue eqbal %sbulwark'%command)
        realm.root.state['last_command_type']='defense'
    @binding_alias('^set_weapon (\w+) ([0-9]+)$')
    def set_weapon(self,match,realm):
        weapon_name=match.group(1)
        weapon_number=match.group(2)
        realm.send_to_mud=False
        realm.write(taggedml('Weapon <red*>%s<white> set to <red*>%s'%(weapon_name,weapon_number)))
        self.items[weapon_name]=weapon_number
        f=open(self.item_setting_file,'w+')
        pickle.dump(self.items, f)
        
    @binding_alias('^iii (\w+)')
    def ii(self, match, realm):
        realm.send_to_mud=False
        self.ii_matching_item=match.group(1)
        self.weapon_match_status='matching'
        realm.send('ii %s'%self.ii_matching_item)
        
    
    
    #triggers
    
    @binding_trigger('^The residual effects of the (\w+) rune around (\w+) fade\.$')
    def rune_back(self, match, realm):
        rune=match.group(1)
        my_target=match.group(2)
        target=realm.root.state['target']
        realm.display_line=False
        if my_target==target:
            self.flaretracker[rune.lower()]=0
            realm.write(taggedml('<green*>RUNE UP:  <blue*:green>%s',rune))
            realm.write(taggedml('<green*>RUNE UP:  <blue*:green>%s',rune))
            
    @binding_trigger('^Number of matching objects:')
    def end_of_matching(self,match,realm):
        self.weapon_match_status='off'
        f=open(self.item_setting_file,'w+')
        pickle.dump(self.items, f)
    @binding_trigger(['^\"([a-z\s]+)([0-9]+)\"',
                      '^\s*([a-z\s]+)([0-9]+)'])
    def match_item(self,match,realm):
        if self.weapon_match_status=='matching':
            name=match.group(1)
            number=match.group(2)   
            realm.write(taggedml('Weapon <red*>%s<white> set to <red*>%s'%(self.ii_matching_item,number)))
            self.items[self.ii_matching_item]=number
            self.weapon_match_status='off'
    
    
    @binding_gmcp_event('Char.Vitals')
    def on_char_vitals(self, gmcp, realm):
        lw=gmcp['leftwield']
        rw=gmcp['rightwield']
        
        self.lw=''
        self.rw=''
        
        for k in self.items:
            if self.items[k]==lw:
                self.lw=k
            if self.items[k]==rw:
                self.rw=k
        
class MainModule(Runeguard):
    pass