'''
Created on Jan 11, 2016

@author: dmitry
'''
from pymudclient.modules import EarlyInitialisingModule
from pymudclient.gmcp_events import binding_gmcp_event
from pymudclient.triggers import binding_trigger
from pymudclient.aliases import binding_alias


area_mobs={"Demon's Pass":[('moroi',True),
                    ('bat',True),
                    ('direwolf',True),
                    ('ghoul',True),
                    ('zombie',True)],
           'the Bloodstone Quarry':[('shapeshifter',True),
                                 ('drone',True),
                                 ('worker',False)],
           'the Necropolis':
           [('wight',True),
            ('skeleton',True),
            ('ghost',True),
            ('wraith',True),
            ('banshee',True),
            ('ghoul',True),
            ('hound',True),
            ('zombie',True),
            ('archer',True)],
           'the Sewage Tunnels of Antioch':
           [('worm',True)],
           'the Iaat Valley':
           [('avian',True),
            ('beast',True),
            ('mutant',True),
            ('direbear',True),
            ('equine',True)]}

room_blacklist = {"Demon's Pass":[28335],
                  'the Necropolis':[9328]}

class AutoBasher(EarlyInitialisingModule):
    '''
    classdocs
    '''


    def __init__(self, manager, attack_command='stand|kill %(target)s', heal_command=None):
        self.manager = manager
        self.state='off'
        self.player_whitelist=[]
        self.players=0
        self.aggro_list=[]
        self.non_aggro_list=[]
        self.aggro_limit=2
        self.current_target=0
        self.attack_command = attack_command
        self.heal_command=heal_command
        self.current_room=0
        self.auto_move = False
        
        self.scheduler=None
        
    @property
    def gmcp_events(self):
        return [self.on_char_items_add,
                self.on_char_items_remove,
                self.on_room_info]
    
    @property
    def triggers(self):
        return [self.balance_recovery,
                self.health_gain,
                self.tar_error, 
                self.exp_notify,
                self.follower_not_ready]
    @property
    def aliases(self):
        return [self.command]
    
    def schedule_process(self, realm, timer=0.1):
        if self.scheduler:
            if self.scheduler.active():
                self.scheduler.cancel()
        self.scheduler=realm.root.set_timer(timer, self.process)
    def process(self, realm):
        realm.cwrite('<yellow*:red>Basher:<yellow> Process - %s'%self.state)
        
        if self.state=='new_room':
            realm.cwrite('<yellow*:red>Basher:<yellow>new_room, init scan')
            self.init_scan(realm)
            if self.get_health_pct()<0.5: #recovery
                if len(self.aggro_list) + len(self.non_aggro_list) == 0:
                    self.state='recovery'
                else:
                    realm.cwrite('<yellow*:red>Basher:<yellow>Recovery, total aggro > 0 (%d)'%self.get_total_aggro())
                    self.state='leave'
            else:
                if self.players>0:
                    realm.cwrite('<yellow*:red>Basher:<yellow>players > 0, state:leave')
                    self.state='leave'
                else:
                    realm.cwrite('<yellow*:red>Basher:<yellow>need_target')
                    self.state='need_target'
            self.schedule_process(realm)
        
        elif self.state=='leave':
            realm.cwrite('<yellow*:red>Basher:<yellow>leave')
            self.move_next(realm)
        
        elif self.state=='need_target':
            realm.cwrite('<yellow*:red>Basher:<yellow>need_target')
            if self.get_total_aggro()>self.aggro_limit:
                realm.cwrite('<yellow*:red>Basher:<yellow>Too much aggro:leave')
                self.state='leave'
                self.schedule_process(realm)
            elif len(self.non_aggro_list)+len(self.aggro_list)==0:
                realm.cwrite('<yellow*:red>Basher:<yellow>No targets:leave')
                self.state='leave'
                self.schedule_process(realm)
            else:
                if len(self.aggro_list)>0:
                    self.current_target=self.aggro_list.pop(0)
                else:
                    self.current_target=self.non_aggro_list.pop(0)
                realm.cwrite('<yellow*:red>Basher:<yellow>new_target:%d'%self.current_target)
                self.state = 'ready'
                self.schedule_process(realm)
                
        elif self.state=='ready':
            realm.cwrite('<yellow*:red>Basher:<yellow>Ready, performing attack')
            self.attack(realm)
            
            
        elif self.state=='recovery':
            realm.cwrite('<yellow*:red>Basher:<yellow>HP Recovery')
            if len(self.aggro_list) + len(self.non_aggro_list) == 0:
                if self.heal_command:
                    realm.send(self.heal_command)
            else:
                self.state='leave'
                self.schedule_process(realm)
            
        elif self.state=='leave':
            realm.cwrite('<yellow*:red>Basher:<yellow>Running Away!')
            self.move_next(realm)
    
    
    def move_next(self, realm):
        if self.auto_move:
            realm.send('wnext')
        else:
            realm.cwrite('<yellow*:red>Basher:<yellow>Room is all done!')
        #realm.root.debug('MOVE NEXT!')
        
    
    def init_scan(self, realm):  
        self.current_target=0
        self.aggro_list=[]
        self.non_aggro_list=[]
        players = []
        if 'Room.Players' in realm.root.gmcp:
            players = realm.root.gmcp['Room.Players']
        self.players = 0
        for p in players: 
            if not p['name'].lower() in self.player_whitelist:
                self.players+=1
                
        area = str(realm.root.gmcp['Room.Info']['area'])
        if not area in area_mobs:
            return
        mobs = area_mobs[area]
        items = realm.root.gmcp['Char.Items.List']['items']
        for item in items:
            for name,aggro in mobs:
                if name in item['name'].lower():
                    if aggro:
                        self.aggro_list.append(int(item['id']))
                    else:
                        self.non_aggro_list.append(int(item['id']))
                
                
    def get_ylem(self, realm):
        realm.send('absorb ylem')
        
    def attack(self, realm):
        realm.send(self.attack_command%{'target':self.current_target})
    
    def get_total_aggro(self):
        tot_aggro = 0
        if not self.current_target == 0 and self.state == "ready":
            tot_aggro+=1
        tot_aggro+=len(self.aggro_list)
        return tot_aggro
    
    def get_health_pct(self):
        hp = float(self.manager.gmcp['Char.Vitals']['hp'])
        hp_max = float(self.manager.gmcp['Char.Vitals']['maxhp'])
        return hp/hp_max
          
    @binding_gmcp_event('Char.Items.Add')
    def on_char_items_add(self, data, realm):
        if self.state=='off':
            return
        if str(data['location'])=='room':
            area = str(realm.root.gmcp['Room.Info']['area'])
            if area not in area_mobs:
                return 
            mobs = area_mobs[area]
            for name, aggro in mobs:
                if name in data['item']['name'].lower():
                    if aggro:
                        self.aggro_list.append(int(data['item']['id']))
                        realm.cwrite('<yellow*:red>Basher:<yellow>Aggro mob: %s'%str(data['item']['name']))
                    else:
                        realm.cwrite('<yellow*:red>Basher:<yellow>Non aggro mob: %s'%str(data['item']['name']))
                        self.non_aggro_list.append(int(data['item']['id']))
        elif str(data['location'])=='inv':
            id = int(data['item']['id'])
            realm.cwrite('<yellow*:red>Basher:<yellow>%d in inventory, removing from lists'%id)
            if self.current_target == id:
                self.current_target = 0
            if id in self.aggro_list:
                self.aggro_list.remove(id)
            if id in self.non_aggro_list:
                self.non_aggro_list.remove(id)
                        
    @binding_gmcp_event('Char.Items.Remove')
    def on_char_items_remove(self, data, realm):
        if self.state=='off':
            return
        if str(data['location'])=='room':            
            item_id = int(data['item']['id'])
            realm.cwrite('<yellow*:red>Basher:<yellow>Char.Items.Remove - %d'%item_id)
            if item_id == self.current_target:
                self.current_target = 0
                self.state = 'need_target'
                
            else:
                if item_id in self.aggro_list:
                    self.aggro_list.remove(item_id)
                if item_id in self.non_aggro_list:
                    self.non_aggro_list.remove(item_id)
                    
                
                
    
    @binding_trigger(['^You have recovered balance on all limbs\.$',
                      '^You have recovered equilibrium\.$',
                      '^You have recovered balance\.$',
                      '^You have cured stun$',
                      '^You have cured writhe_web$',
                      '^You have cured paralysis\.$'])
    def balance_recovery(self, match, realm):
        if self.state == 'off':
            return
        if self.state == 'need_target' and self.get_health_pct() < 0.75:
            self.state='recovery'
        if self.state == 'ready' and self.get_health_pct() < 0.50:
            self.state='leave'
        if self.get_total_aggro() > self.aggro_limit:
            self.state='leave'
        self.schedule_process(realm) 
    
    
    
         
        
    @binding_gmcp_event('Room.Info')
    def on_room_info(self, gmcp_data, realm):
        if self.state == 'off':
            return 
        vnum = int(gmcp_data['num'])
        
        if not vnum == self.current_room:
            self.current_room=vnum
            realm.cwrite('<yellow*:red>Basher:<yellow>New room: %d'%vnum)
            if self.state == 'run_away':
                self.state = 'leave'
            else:
                self.state = 'new_room'
            self.schedule_process(realm)
            
    @binding_trigger('^Health Gain: (\d+)$')
    def health_gain(self, match, realm):
        if self.state=='off':
            return
        if self.state == 'recovery':
            if self.get_health_pct()>0.75:
                self.state='need_target'
                self.schedule_process(realm)
                
    @binding_trigger(["^You can find no such target as '(\d+)'\.",
                      '^Ahh, I am truly sorry, but I do not see anyone by that name here\.$',
                      '^Nothing can be seen here by that name\.$',
                      '^I do not recognize anything called that here\.$'])
    def tar_error(self, match, realm):
        if self.state == 'off':
            return
        self.state='need_target'
        self.schedule_process(realm)
        
    @binding_alias('^basher (\w+) ([a-zA-Z0-9 ]+)$')
    def command(self, match, realm):
        realm.send_to_mud = False
        comm = match.group(1)
        opt = match.group(2)
        if comm=='turn':
            if opt == 'on':
                realm.cwrite('<yellow*:red>Basher:<yellow>Turning on!')
                self.state = 'new_room'
                area = str(realm.root.gmcp['Room.Info']['area'])
                if area in room_blacklist:
                    realm.send('wblacklist %s'%','.join(str(i) for i in room_blacklist[area]))
                realm.send('wtraverse')
                self.schedule_process(realm)
            elif opt == 'off':
                realm.cwrite('<yellow*:red>Basher:<yellow>Turning off.')
                self.state = 'off'
                realm.root.fireEvent('promptDataEvent','exp','')
            else:
                realm.cwrite('<yellow*:red>Basher:<yellow>Command "turn", unknown option "%s"'%opt)
        elif comm == 'whitelist':
            realm.cwrite('<yellow*:red>Basher:<yellow> Adding %s to whitelist'%opt)
            self.player_whitelist.append(opt.lower())
        elif comm == 'reset':
            if opt == 'all':
                self.non_aggro_list = []
                self.aggro_list = []
                self.current_target = 0
        elif comm == 'move':
            self.auto_move = (opt=='on')
        elif comm == 'aggrolimit':
            self.aggro_limit = int(opt)
            
    @binding_trigger('Your movement is held up by (\w+)\.')
    def follower_not_ready(self, match, realm):
        self.schedule_process(realm, 1)
    @binding_trigger('You gain .* \(bash\) experience. You need (.*) more for level (\d+)\.$')
    def exp_notify(self, match, realm):
        if not self.state=='off':
            realm.root.fireEvent('promptDataEvent','exp','<green*>exp: <red*> %s'%match.group(1))