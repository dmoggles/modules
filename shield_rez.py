'''
Created on Jul 21, 2015

@author: dmitry
'''
from pymudclient.modules import EarlyInitialisingModule, BaseModule
from pymudclient.triggers import binding_trigger
from pymudclient.metaline import simpleml, Metaline, RunLengthList
from pymudclient.colours import fg_code, bg_code, RED,YELLOW, GREEN
from pymudclient.aliases import binding_alias


def basic_shields_up(realm, shield_status):
    if not 'last_command_type' in realm.root.state or realm.root.state['last_command_type']!='raze':
        realm.send('queue reset eqbal')
        realm.root.state['last_command_type']='none'
            
def basic_shields_down(realm, shield_status):
    if 'last_command_type' in realm.root.state and realm.root.state['last_command_type']=='raze':
        realm.send('queue reset eqbal')
        realm.root.state['last_command_type']='none'
  
  
class ShieldStatus:
    def __init__(self, shield=False, aura=False, barrier=False):
        self.shield=shield
        self.aura=aura
        self.barrier=barrier
        
    @property  
    def all_stripped(self):
        return not (self.shield or self.aura or self.barrier)
     
    @property
    def metaLine(self):
        line="Shield|Aura|Barrier"
        fg=RunLengthList([(0, fg_code(YELLOW,True))])
        bg=RunLengthList([(0, bg_code(GREEN))])
        if self.shield:
            bg.add_change(0, bg_code(RED))
        else:
            bg.add_change(0, bg_code(GREEN))
        first_separator=line.find('|')
        if self.aura:
            bg.add_change(first_separator+1, RED)
        else:
            bg.add_change(first_separator+1, GREEN)
        second_separator=line.find('|',first_separator+1)
        if self.barrier:
            bg.add_change(second_separator+1, RED)
        else:
            bg.add_change(second_separator+1, GREEN)
        ml=Metaline(line, fg, bg)
        return ml
        
class ShieldRez(EarlyInitialisingModule):
    def __init__(self,realm, on_shields_up=basic_shields_up, on_shields_down=basic_shields_down):
        #self.raze_commands = raze_commands
        self.raze_data = {}
        self.on_shields_up = on_shields_up
        self.on_shields_down = on_shields_down
    
    def __getitem__(self, item):
        '''
        @rtype: ShieldStatus
        '''
        if not item in self.raze_data:
            self.raze_data[item]=ShieldStatus(aura=True)
        return self.raze_data[item]
    
    @binding_trigger([r'^You suddenly perceive the vague outline of an aura of rebounding around (\w+)\.$',
                      r'^You suddenly perceive the vague outline of an aura of rebounding around (\w+)$',
                      r'^The attack rebounds off (\w+)\'s rebounding aura\!$',
                      '^A demonic daegger hurls itself at (\w+), striking his aura of rebounding\.'])
    def rebounding_on(self, match, realm):
        print(match.group(0))
        realm.display_line=False
        my_target = match.group(1).lower()
        if not my_target in self.raze_data: 
            self.raze_data[my_target]=ShieldStatus(aura=True)
        else:
            self.raze_data[my_target].aura=True
        realm.root.fireEvent('reboundingEvent',my_target,1)
        if realm.root.state['target'].lower()==my_target:
            new_line = 'REBOUNDING ON, REBOUNDING ON'
            realm.write(simpleml(new_line, fg_code(YELLOW,True),bg_code(RED)))
            if self.on_shields_up!=None:
                self.on_shields_up(realm,self.raze_data[my_target])
            
            
    @binding_trigger(r'^(?:His|Her) aura of rebounding is breached\.$')
    def no_target_rebound_off(self, match,realm):
        realm.display_line=False
        my_target=realm.root.state['target'].lower()
        if not my_target in self.raze_data:
            self.raze_data[my_target]=ShieldStatus(aura=False)
        else:
            self.raze_data[my_target].aura=False
        realm.write(simpleml('REBOUNDING OFF, REBOUNDING OFF',fg_code(YELLOW,True),bg_code(RED)))
        if realm.root.gui:
                realm.root.gui.set_shield('rebound',False)
        realm.root.fireEvent('reboundingEvent',my_target,0)
            
            
    @binding_trigger(r'^The attack rebounds back onto you!$')
    def no_target_rebound_on(self, match, realm):
        realm.display_line=False
        my_target=realm.root.state['target'].lower()
        if not my_target in self.raze_data:
            self.raze_data[my_target]=ShieldStatus(aura=True)
        else:
            self.raze_data[my_target].aura=True
        realm.write(simpleml('REBOUNDING ON, REBOUNDING ON',fg_code(YELLOW,True),bg_code(RED)))
        realm.root.fireEvent('reboundingEvent',my_target,1)
        if self.on_shields_up!=None:
            self.on_shields_up(realm, self.raze_data[my_target])
    
    @binding_trigger(['^\w+ razes (\w+)\'s aura of rebounding with .+\.$',
                      '^You raze (\w+)\'s aura of rebounding with .+\.$',
                      '^You whip .+ through the air in front of (\w+), to no effect\.$',
                      '^\w+ drives .+ through (\w+)\'s aura of rebounding, destroying it\.$',
                      '^(\w+)\'s aura of weapons rebounding disappears\.$',
                      '^You jab .+ towards (\w+) but tumble forward slightly as it meets no resistance\.$',
                      '^You jab .+ towards (\w+), piercing through and shattering \w+ aura of rebounding\.$'])
    def rebound_off(self, match,realm):
        realm.display_line=False
        my_target=match.group(1).lower()
        if not my_target in self.raze_data:
            self.raze_data[my_target]=ShieldStatus()
        else:
            self.raze_data[my_target].aura=False
        realm.root.fireEvent('reboundingEvent',my_target,0)
            
        if realm.root.state['target'].lower()==my_target:
            realm.cwrite('--- REBOUNDING IS ---- %s'%self.raze_data[my_target].aura)
            realm.write(simpleml('REBOUNDING DOWN, REBOUNDING DOWN',fg_code(YELLOW,True),bg_code(GREEN)))
            if self.raze_data[my_target].all_stripped:
                realm.write(simpleml('ALL SHIELDS DOWN, ALL SHIELDS DOWN',fg_code(YELLOW,True),bg_code(GREEN)))
                if self.on_shields_down!=None:
                    self.on_shields_down(realm, self.raze_data[my_target])
                    
    @binding_trigger(['^A numbing energy runs up your limbs as your attack rebounds off of (\w+)\'s shield\.$',
                      '^A shimmering translucent shield forms around (\w+)\.$',
                      '^(\w+) wraps (?:his|her) bone wings about (?:his|her) body, forming a translucent shield\.$',
                      '^(\w+) grasps (?:his|her) shield solidly in front of (?:him|her) as (?:he|she) mumbles a quick prayer\.',
                      '^(\w+) wraps (?:his|her) wings about (?:his|her) body, forming a translucent shield\.',
                      '^(\w+) grips (?:his|her) shield tightly as a murky haze slowly rises from it, forming a protective translucent barrier around (?:him|her)\.',
                      '^(\w+) whips his shield swiftly in the air around him, tracing a',
                      '^(\w+) bangs against h(?:is|er) shield with a clenched fist, then spins it around until a translucent barrier forms around h(?:im|er)\.$'
                      ])
    def shield_on(self,match,realm):
        realm.display_line=False
        my_target = match.group(1).lower()
        if not my_target in self.raze_data: 
            self.raze_data[my_target]=ShieldStatus(shield=True)
        else:
            self.raze_data[my_target].shield=True
        realm.root.fireEvent('shieldEvent',my_target,1)
        if realm.root.state['target'].lower()==my_target:
            new_line = 'SHIELD ON, SHIELD ON'
            realm.write(simpleml(new_line, fg_code(YELLOW,True),bg_code(RED)))
            if self.on_shields_up!=None:
                self.on_shields_up(realm, self.raze_data[my_target])
        
    @binding_trigger(['^The shimmering translucent shield around (\w+) fades away\.$',
                      '^A massive, ethereal hammer rises out of \w+\'s tattoo and smashes (\w+)\'s translucent shield\.$',
                      '^(\w+)\'s protective shield melts away\.$',
                      '^You touch your tattoo and a massive, ethereal hammer rises up and shatters the translucent shield surrounding (\w+)\.',
                      '^You raze (\w+)\'s translucent shield with (.*)\.$',
                      '^With an enraged fury, \w+ smashes (?:his|her) mace against a translucent shield surrounding (\w+), shattering it\.',
                      '^You whip .* through the air in front of (\w+), to no effect\.',
                      '^You jab .+ towards (\w+) but tumble forward slightly as it meets no resistance\.',
                      '^The flame explodes into a searing furnace that strips (\w+)\'s translucent shield before vanishing entirely\.$'])
    def shield_off(self,match,realm):
        realm.display_line=False
        my_target=match.group(1).lower()
        if not my_target in self.raze_data:
            self.raze_data[my_target]=ShieldStatus()
        else:
            self.raze_data[my_target].shield=False
        realm.root.fireEvent('shieldEvent',my_target,0)
            
        if realm.root.state['target'].lower()==my_target:
           
            realm.write(simpleml('SHIELD DOWN, SHIELD DOWN',fg_code(YELLOW,True),bg_code(GREEN)))
            if self.raze_data[my_target].all_stripped:
                realm.write(simpleml('ALL SHIELDS DOWN, ALL SHIELDS DOWN',fg_code(YELLOW,True),bg_code(GREEN)))
                if self.on_shields_down!=None:
                    self.on_shields_down(realm, self.raze_data[my_target])
                    
    @binding_trigger(['^(\w+) spins .+ into a quick blur, catching the light and settling it around \w+ in a protective barrier\.$',
                      '^(\w+) slowly draws a circle around (?:her|him)self, and a shimmering prismatic barrier slowly forms, creating a sturdy barrier around (?:her|him)\.$',
                      '^(\w+) strums a few notes on .+, and a prismatic barrier forms around (?:him|her)\.$',
                      '^Your attack is repelled by the prismatic barrier surrounding (\w+)\.$'])
    def barrier_on(self, match,realm):
        realm.display_line=False
        my_target = match.group(1).lower()
        if not my_target in self.raze_data: 
            self.raze_data[my_target]=ShieldStatus(barrier=True)
        else:
            self.raze_data[my_target].barrier=True
        realm.root.fireEvent('barrierEvent',my_target,1)
        if realm.root.state['target'].lower()==my_target:
            if realm.root.gui:
                realm.root.gui.set_shield('prism',True)
            new_line = 'BARRIER ON, BARRIER ON'
            realm.write(simpleml(new_line, fg_code(YELLOW,True),bg_code(RED)))
            if self.on_shields_up!=None:
                self.on_shields_up(realm,self.raze_data[my_target])
    
    @binding_trigger('^(\w+)\'s prismatic barrier dissolves into nothing\.$')
    def barrier_off(self,match,realm):
        realm.display_line=False
        my_target=match.group(1).lower()
        if not my_target in self.raze_data:
            self.raze_data[my_target]=ShieldStatus()
        else:
            self.raze_data[my_target].barrier=False
        realm.root.fireEvent('barrierEvent',my_target,0)
        
        if realm.root.state['target'].lower()==my_target:
            if realm.root.gui:
                realm.root.gui.set_shield('prism',False)
            realm.write(simpleml('BARRIER DOWN, BARRIER DOWN',fg_code(YELLOW,True),bg_code(GREEN)))
            if self.raze_data[my_target].all_stripped:
                realm.write(simpleml('ALL SHIELDS DOWN, ALL SHIELDS DOWN',fg_code(YELLOW,True),bg_code(GREEN)))
                if self.on_shields_down!=None:
                    self.on_shields_down(realm, self.raze_data[my_target])
                    
    @binding_trigger('(\w+) takes a long drag off his pipe, exhaling a thick, white haze')
    def rebounding_soon(self, match, realm):
        realm.display_line = False
        my_target=match.group(1).lower()
        if my_target==realm.root.state['target'].lower():
            realm.write(simpleml('REBOUNDING SOON, REBOUNDING SOON!', fg_code(YELLOW,True),bg_code(RED)))
            def delayed_aura(realm):
                realm.write("DONE!")
                if not my_target in self.raze_data:
                    self.raze_data[my_target]=ShieldStatus(aura=True)
                else:
                    self.raze_data[my_target].aura=True
                if self.on_shields_up!=None:
                    self.on_shields_up(realm, self.raze_data[my_target])
            self.aura_timer=realm.root.set_timer(7, delayed_aura, realm.root)
    @property    
    def triggers(self):
        return [self.rebounding_on, self.no_target_rebound_on, self.rebound_off, 
                self.shield_on, self.shield_off, self.barrier_on, self.barrier_off,
                self.no_target_rebound_off]
     
    @binding_alias('^rzst$')
    def raze_status(self, match, realm):
        realm.send_to_mud=False
        target=realm.root.state['target']
        if target in self.raze_data:
            realm.write(self.raze_data[target].metaLine)    
    @property
    def aliases(self):
        return[self.raze_status]          
class MainModule(ShieldRez):
    pass