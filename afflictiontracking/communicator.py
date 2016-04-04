'''
Created on Sep 9, 2015

@author: Dmitry
'''
from pymudclient.modules import EarlyInitialisingModule
from pymudclient.triggers import binding_trigger
from pymudclient.aliases import binding_alias
import json
import os

class Communicator(EarlyInitialisingModule):
    '''
    classdocs
    '''


    def __init__(self, clan_number, clan_name, realm, my_circle, people_services):
        
        '''
        Constructor
        '''
        self.clan_number=clan_number
        self.clan_name=clan_name.capitalize()
        self.realm = realm
        self.aff_tracker=None
        self.my_circle=my_circle,
        self.people_services = people_services
        self.on=False
        self.whitelist=[]
        d_name = os.path.join(os.path.expanduser('~'),'muddata','whitelist', 'alesei_deathknight')
        if not os.path.isdir(d_name):
            os.makedirs(d_name)
        if os.path.exists(d_name+'/'+'whitelist.xml'):
            f=open(d_name+'/whitelist.xml','r')
            self.whitelist = json.load(f)
            
        
        
        
    @property
    def triggers(self):
        return [self.received_channel_affliction,
                self.cath_command,
                self.trace_msg,
                self.where_request,
                self.starburst,
                self.slain]
    
    @property
    def aliases(self):
        return [self.switch,
                self.add_whitelist]
    
    @binding_alias('^comm (\w+)$')
    def switch(self, match, realm):
        realm.send_to_mud=False
        command = match.group(1)
        if command=='on':
            self.on=True
            realm.cwrite('<white:blue>Communicator ON')
        elif command=='off':
            self.on=False
            realm.cwrite('<white:blue>Communicator OFF')
            
        
    def say(self, message):
        if self.on:
            self.realm.send('clt%d %s'%(self.clan_number,message))
    @binding_alias('^whitelist (\w+)$')
    def add_whitelist(self, match, realm):
        realm.send_to_mud = False
        self.whitelist.append(match.group(1).lower())
        d_name = os.path.join(os.path.expanduser('~'),'muddata','whitelist', realm.root.name.lower())
        f=open(d_name+'/whitelist.xml','w')
        json.dump(self.whitelist, f)
        realm.cwrite('<white*> Added %s to whitelist'%match.group(1))
        
    @binding_trigger('^\(Ring\): (?:\w+) says, "Cath (\w+) NOW!"')
    def cath_command(self, match, realm):
        if self.on:
            target = match.group(1)
            realm.send('queue eqbal demon catharsis %s'%target)
            realm.cwrite('<red*>CATH CALL!!!')
            realm.cwrite('<green*>CATH CALL!!!!')
            realm.cwrite('<red*>CATH CALL!!!')
            realm.cwrite('<green*>CATH CALL!!!!')
            realm.cwrite('<red*>CATH CALL!!!')
            realm.cwrite('<green*>CATH CALL!!!!')
    
    @binding_trigger('^\(Ring\): .* says, "(?:(?:Locate)|(?:Where)|(?:Discover)|(?:Pinpoint)|(?:Scry)|(?:Find)) (?:.* )?(?:A|a)(?:L|l)(?:E|e)(?:S|s)(?:E|e)(?:I|i)\."$')
    def where_request(self, match, realm):
        room_name=realm.root.gmcp['Room.Info']['name']
        room_num = realm.root.gmcp['Room.Info']['num']
        room_players = [i['name'] for i in realm.root.gmcp['Room.Players']]
        
        realm.send("rt I'm at %s (%s) with: %s"%(room_name, room_num, ", ".join(room_players)))
    
    @binding_trigger('^Your Ouroboros reports that (\w+) has moved to (.*)\.$')
    def trace_msg(self, match, realm):
        if self.on:
            person=match.group(1)
            where = match.group(2)
            realm.send('rt %s is at %s'%(person, where))
    
    @binding_trigger('\((\w+)\): (?:\w+) says, "Afflicted (\w+) (.*)\.')
    def received_channel_affliction(self, match, realm):
        if self.aff_tracker!=None:
            channel=match.group(1)
            target=match.group(2)
            affliction=match.group(3)
            if affliction == 'sun allergy':
                affliction = 'sunallergy'
            affliction = affliction.replace(' ','_')
            if channel==self.clan_name:
                self.aff_tracker.tracker(target).add_aff(affliction, False)
    
    def announce_target(self, target):
        if self.on:
            self.realm.send('rt Target: %s'%target.capitalize())
    
    def send_health_mana(self, target, hp, maxhp, mana, maxmana):
        if self.on:
            self.realm.send('rt %s: %d/%d HP, %d/%d (%0.0f%%) Mana'%
                   (target.upper(), hp, maxhp, mana, maxmana, 100*float(mana)/float(maxmana)))
    
    def send_aff(self, aff, target):
        self.say('afflicted %s %s'%(target, aff))
        
    def player_entered(self, player, area):
        circle = self.people_services.check_circle(player)
        
        if self.on and circle!=self.my_circle:
            self.realm.send('rt [Bloodscent]: %s ENTERED %s'%(player, area))
    
    def player_left(self, player, area):
        circle = self.people_services.check_circle(player)
        if self.on and circle!=self.my_circle:
            self.realm.send('rt [Bloodscent]: %s LEFT %s'%(player, area))
              
    @binding_trigger('^A starburst tattoo flares and bathes (\w+) in a nimbus of white light.$')
    def starburst(self, match, realm):
        realm.send('rt %s STARBURSTED!!'%match.group(1))
        
    @binding_trigger('^You have slain (\w+)$')
    def slain(self, match, realm):
        realm.send('rt Target %s is DOWN!'%match.group(1))