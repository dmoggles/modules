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
from FlareTracker import FlareTracker, FlareObject
from RingAnnouncer import RingAnnouncer
from ToxinTracker import FlareKeyedToxinTracker

class Runeguard(BaseModule):
    '''
    classdocs
    '''


    def __init__(self, realm):
        '''
        Constructor
        '''
        BaseModule.__init__(self,realm)
        self.communicator=RingAnnouncer(realm)
        self.shield_razer=ShieldRez(realm)
        self.flaretracker = FlareTracker(realm, self.communicator)
        self.toxin_tracker = FlareKeyedToxinTracker()
        self.items={}
        self.item_setting_file=realm.module_settings_dir+'/'+realm.factory.name+'_runeguard_items.pickle'
        if os.path.exists(self.item_setting_file):
            f=open(self.item_setting_file,'r')
            self.items=pickle.load(f)
        self.lw='0'
        self.rw='0'
        self.weapon_match_status=''
        self.active_weapon='battleaxe'
        
    @property
    def modules(self):
        return[self.shield_razer, self.flaretracker, self.communicator]
    @property
    def aliases(self):
        return [self.kestrel_summon, self.bulwark, self.set_weapon,self.ii,self.pain_totem,
                self.transfix_totem,self.dsl,self.reave, self.raze, self.reave_or_raze, self.impale, self.disembowel,
                self.cleave, self.sunder]
    @property
    def triggers(self):
        return[self.match_item, self.end_of_matching]
    @property
    def gmcp_events(self):
        return[self.on_char_vitals]
    
    @binding_alias('^imp$')
    def impale(self, match, realm):
        realm.send_to_mud=False
        target=realm.root.state['target']
        if not self.rw == 'broadsword':
            realm.send('queue eqbal quickdraw broadsword|impale %s'%target)
        else:  
            realm.send('queue eqbal impale %s'%target)
        realm.root.state['last_command_type']='attack'
    @binding_alias('^cle$')
    def cleave(self, match, realm):
        realm.send_to_mud=False
        target=realm.root.state['target']
        realm.send('queue eqbal cleave %s'%target)
        realm.root.state['last_command_type']='attack'
    @binding_alias('^sund$') 
    def sunder(self, match, realm):
        realm.send_to_mud=False
        target=realm.root.state['target']
        realm.send('queue eqbal sunder %s'%target)
        realm.root.state['last_command_type']='attack'
        
    @binding_alias('^dis$')
    def disembowel(self, match, realm):
        realm.send_to_mud=False
        target=realm.root.state['target']
        realm.send('queue eqbal disembowel %s'%target)
        realm.root.state['last_command_type']='attack'
        
    @binding_alias('^xx')
    def reave_or_raze(self, match,realm):
        realm.send_to_mud=False
        target=realm.root.state['target']
        if target in self.shield_razer.raze_data and not self.shield_razer.raze_data[target].all_stripped:
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
        flare=self.flaretracker.getNextRune(target)
        toxin1,toxin2=self.toxin_tracker.getNextToxinSet(flare)
        command=''
        if flare==FlareObject.SOWULU or flare==FlareObject.PITHAKHAN or flare==FlareObject.NAUTHIZ:
            if self.lw != 'tablet':
                command=command+'quickdraw %s left|'%self.items['tablet']
        else:
            if self.lw != 'shield':
                command=command+'quickdraw %s left|'%self.items['shield']
                
        if self.rw != weapon:
            command=command+'quickdraw %s right|'%self.items[weapon]
        command=command+'grip|order kestrel attack %s|'%target
        if attack=='reave':
            command=command+'tgs|lns|'
        command=command+'wm %s %s %s %s %s|'%(attack, attack, target, toxin1, toxin2)
        command=command+'engage %s|flare %s at %s'%(target, flare, target)
        return command
    
    @binding_alias('^spt$')
    def pain_totem(self, match, realm):
        target=realm.root.state['target']
        realm.send('queue eqbal quickdraw %s|stand totem for %s'%(self.items['paintotem'],target))
        realm.root.state['last_command_type']='totem'
        realm.send_to_mud=False
        
    @binding_alias('^stt$')
    def transfix_totem(self, match, realm):
        target=realm.root.state['target']
        realm.send('queue eqbal quickdraw %s|stand totem for %s'%(self.items['transfixtotem'],target))
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
            command='quickdraw %s|grip|'%self.items['shield']
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
        if 'leftwield' in gmcp:
            lw=gmcp['leftwield']
            self.lw=''
            for k in self.items:
                if self.items[k]==lw:
                    self.lw=k
        if 'rightwield' in gmcp:
            rw=gmcp['rightwield']
            self.rw=''
            for k in self.items:
                if self.items[k]==rw:
                    self.rw=k
        
class MainModule(Runeguard):
    pass