'''
Created on Jul 30, 2015

@author: dmitry
'''
from pymudclient.modules import EarlyInitialisingModule
from pymudclient.triggers import binding_trigger
from pymudclient.aliases import binding_alias

class FlareObject:
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
        self.runes={r:True for r in FlareObject.RUNES}
        
    def getNextRune(self, priority_list):
        for r in priority_list:
            if self.runes[r]:
                return r
    def __getitem__(self,key):
        return self.runes[key]
    def __setitem__(self,key,value):
        self.runes[key]=value
        
class FlareTracker(EarlyInitialisingModule):
    '''
    Tracks which flares are active and returns the next available
    flare based on priority list
    '''
    def __init__(self,realm, communicator):
        self.communicator=communicator
        self.targets={}
        self.priority_list=[FlareObject.PITHAKHAN,FlareObject.SOWULU,
                            FlareObject.NAUTHIZ, FlareObject.WUNJO]
    
    def announce(self, msg):
        if not self.communicator==None:
            self.communicator.announce(msg)
            
    def getNextRune(self, target):
        if not target in self.targets:
            self.targets[target]=FlareObject()
        return self.targets[target].getNextRune(self.priority_list)
        
    def getString(self, target):
        if not target in self.targets:
            self.targets[target]=FlareObject()
        s = ''
        for r in self.targets[target].runes:
            if self.targets[target][r]:
                s += '<white*>%s |'%r
            else:
                s += '<white>%s |'%r
        s=s[:-2]
        return s
    @binding_alias('^tar (\w+)$')
    def set_target(self, match,realm):
        realm.send_to_mud=False
        self.outputToGui(realm.root)
        
    @binding_alias('^shoot_fl$')
    def shoot_flare(self, match, realm):
        realm.send_to_mud=False
        target=realm.root.state['target']
        flare = self.getNextRune(target)
        realm.send('flare %s at %s'%(flare, target))
        
    @binding_trigger("^You concentrate on the (\w+) rune on (?:an|a) .*, and its searing image suddenly flares on (\w+)'s skin\.$")
    def self_flare(self, match, realm):
        target = match.group(2)
        rune = match.group(1).lower()
        if not target in self.targets:
            self.targets[target]=FlareObject()
        self.targets[target][rune]=False
        self.outputToGui(realm.root)
        
    @binding_trigger('^The residual effects of the (\w+) rune around (\w+) fade\.$')
    def rune_back(self, match, realm):
        rune=match.group(1)
        my_target=match.group(2)
        target=realm.root.state['target']
        realm.display_line=False
        if not my_target in self.targets:
            self.targets[my_target]=FlareObject()
            
        self.targets[my_target][rune.lower()]=True
        if target==my_target:
            realm.cwrite('<green*>RUNE UP:  <blue*:green>%s'%rune)
            realm.cwrite('<green*>RUNE UP:  <blue*:green>%s'%rune)
        self.outputToGui(realm.root)
        
    def outputToGui(self, realm):
        active_channels = realm.active_channels
        realm.active_channels=['class']
        realm.cwrite(self.getString(realm.state['target']))
        realm.active_channels=active_channels
        
        
    #Ground runes
    @binding_alias('^ing$')
    def inguz(self, match, realm):
        realm.send_to_mud=False
        realm.send('sketch inguz on ground')
        
    @binding_alias('^uruz$')
    def uruz(self, match,realm):
        realm.send_to_mud=False
        realm.send('sketch uruz on ground')
        self.announce('Dropping Uruz (heals allies)')
    @binding_alias('^hail$')
    def hugalaz(self, match, realm):
        realm.send_to_mud=False
        realm.send('sketch hugalaz on ground')
        self.announce('Dropping Hugalaz (hailstorm)')
    
    @binding_alias('^vortex$')
    def ansuz(self, match, realm):
        realm.send_to_mud=False
        target = realm.root.state['target']
        realm.send('sketch ansuz on ground at %s'%target)
        self.announce('Vortexing %s!!!!'%target)
    @binding_alias('^laguz$')    
    def laguz(self,match,realm):
        realm.send_to_mud=False
        realm.send('sketch laguz on ground')
        self.announce('Dropping Laguz (makes it hard to leave the room)')
    
    @binding_alias('^wall (\w+)$')
    def gular(self, match, realm):
        dir = match.group(1)
        realm.send_to_mud=False
        realm.send('sketch gular on ground %s'%dir)
        self.announce('Dropping a wall to %s'%dir)
        
    @binding_alias('^roof$')    
    def lagul(self,match,realm):
        realm.send_to_mud=False
        realm.send('sketch lagul on ground')
        self.announce('Dropping Lagul (makes the room indoor)')
        
    @binding_alias('^norites$')    
    def eihwaz(self,match,realm):
        realm.send_to_mud=False
        realm.send('sketch eihwaz on ground')
        self.announce('Dropping Eihwaz (kills rites)')
        
    
    @property
    def triggers(self):
        return [self.self_flare, self.rune_back]
    
    @property
    def aliases(self):
        return [self.shoot_flare,self.set_target, self.inguz, self.uruz,
                self.hugalaz, self.ansuz, self.laguz, self.gular, self.lagul,
                self.eihwaz]