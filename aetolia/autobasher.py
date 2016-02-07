'''
Created on Jan 11, 2016

@author: dmitry
'''
from pymudclient.modules import EarlyInitialisingModule
from pymudclient.gmcp_events import binding_gmcp_event
from pymudclient.triggers import binding_trigger
from pymudclient.aliases import binding_alias


area_mobs={'the Salma Settlement':[('mage',False),
                    ('man',False),
                    ('guard',False),
                    ('warrior',False),
                    ('scholar',False),
                    ('artist',False),
                    ('woman',False),
                    ('child',False),
                    ('scientist',False),
                    ('dima',False),
                    ('linette',False),
                    ('miner',False),
                    ('blacksmith',False)],
           'The Teshen Caldera':[('reaver',False),
                                 ('scout',False),
                                 ('worker',False)],
           'the Three Rock Outpost':
           [('bandit',False)]}



class AutoBasher(EarlyInitialisingModule):
    '''
    classdocs
    '''


    def __init__(self, manager, attack_command, heal_command=None):
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
        
        self.scheduler=None
        
    @property
    def gmcp_events(self):
        return [self.on_char_items_add,
                self.on_char_items_remove,
                self.on_room_info]
    
    @property
    def triggers(self):
        return [self.balance_recovery,
                self.ylem_collected,
                self.ylem_emitted,
                self.health_gain,
                self.tar_error]
    @property
    def aliases(self):
        return [self.command]
    
    def schedule_process(self, realm):
        if self.scheduler:
            if self.scheduler.active():
                self.scheduler.cancel()
        self.scheduler=realm.root.set_timer(0.1, self.process)
    def process(self, realm):
        realm.cwrite('<yellow*:red>Basher:<yellow> Process - %s'%self.state)
        
        if self.state=='new_room':
            realm.cwrite('<yellow*:red>Basher:<yellow>new_room')
            self.init_scan(realm)
            if self.get_health_pct()<0.3: #recovery
                if len(self.aggro_list) + len(self.non_aggro_list) == 0:
                    self.state='recovery'
                else:
                    realm.cwrite('<yellow*:red>Basher:<yellow>Recovery, total aggro > 0 (%d)'%self.get_total_aggro())
                    self.state='run_away'
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
            realm.send('wnext')
        
        elif self.state=='need_target':
            realm.cwrite('<yellow*:red>Basher:<yellow>need_target')
            if self.get_total_aggro()>self.aggro_limit:
                realm.cwrite('<yellow*:red>Basher:<yellow>Too much aggro:leave')
                self.state='leave'
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
            
        elif self.state=='ylem':
            realm.cwrite('<yellow*:red>Basher:<yellow>Collecting ylem')
            self.get_ylem(realm)
            
        elif self.state=='recovery':
            realm.cwrite('<yellow*:red>Basher:<yellow>HP Recovery')
            if len(self.aggro_list) + len(self.non_aggro_list) == 0:
                if self.heal_command:
                    realm.send(self.heal_command)
            else:
                self.state='run_away'
                self.schedule_process(realm)
            
        elif self.state=='run_away':
            realm.cwrite('<yellow*:red>Basher:<yellow>Running Away!')
            realm.send('wnext')
    
    
    def init_scan(self, realm):  
        self.current_target=0
        self.aggro_list=[]
        self.non_aggro_list=[]
        players = realm.root.gmcp['Room.Players']
        self.players = 0
        for p in players: 
            if not p.lower() in self.player_whitelist:
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
        #realm.debug('Char.Items.Add')
        if self.state=='off':
            return
        if str(data['location']=='room'):
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
                      'You have recovered balance\.$'
                      '^You have cured stun$',
                      '^You have cured writhe_web$'])
    def balance_recovery(self, match, realm):
        if self.state == 'off':
            return
        if self.state == 'need_target' and self.get_health_pct() < 0.75:
            self.state='recovery'
        if self.state == 'ready' and self.get_health_pct() < 0.30:
            self.state='run_away'
        if self.get_total_aggro() > self.aggro_limit:
            self.state='run_away'
        self.process(realm) 
    
    @binding_trigger('^Your vision distorts briefly, light scattering subtly as ylem energy diffuses into the surrounding')
    def ylem_emitted(self, match, realm):
        if self.state == 'off':
            return
        self.state = 'ylem'
    
    @binding_trigger('^You raise your gauntlet, extending your fingers and allowing the latent ylem around you to absorb')
    def ylem_collected(self, match, realm):
        if self.state == 'off':
            return
        self.state = 'need_target'      
        
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
                self.process(realm)
                
    @binding_trigger("^You can find no such target as '(\d+)'\.")
    def tar_error(self, match, realm):
        if self.state == 'off':
            return
        self.state='need_target'
        self.process(realm)
        
    @binding_alias('^basher (\w+) (\w+)$')
    def command(self, match, realm):
        realm.send_to_mud = False
        comm = match.group(1)
        opt = match.group(2)
        if comm=='turn':
            if opt == 'on':
                realm.cwrite('<yellow*:red>Basher:<yellow>Turning on!')
                self.state = 'new_room'
                realm.send('wtraverse')
                self.process(realm)
            elif opt == 'off':
                realm.cwrite('<yellow*:red>Basher:<yellow>Turning off.')
                self.state = 'off'
            else:
                realm.cwrite('<yellow*:red>Basher:<yellow>Command "turn", unknown option "%s"'%opt)
        elif comm == 'whitelist':
            realm.cwrite('<yellow*:red>Basher:<yellow> Adding %s to whitelist'%opt)
            self.player_whitelist.append(opt.lower())