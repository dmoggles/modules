'''
Created on Aug 12, 2015

@author: Dmitry
'''
from pymudclient.modules import BaseModule, EarlyInitialisingModule
from pymudclient.aliases import binding_alias
from pymudclient.triggers import binding_trigger
from afflictiontracking.afflictionpriority import AfflictionPriority

class Demons(EarlyInitialisingModule):
    def __init__(self, realm):
        self.active_demon=None

    @property
    def aliases(self):
        return [self.carve_pentagram,
                self.summon_daemonite,
                self.summon_fiend,
                self.summon_nightmare]

    @property
    def triggers(self):
        return [self.set_daemonite,
                self.set_fiend,
                self.set_nightmare]
        
            
    @binding_alias('^cp$')
    def carve_pentagram(self, match, realm):
        realm.send_to_mud=False
        realm.send('carve pentagram')
        
    @binding_trigger('^You summon forth a daemonite to harrass your enemies\.$')
    def set_daemonite(self, match,realm):
        realm.cwrite('<green*:blue> Demon: Daemonite')
        self.active_demon='daemonite'
        
    @binding_alias('^daem$')
    def summon_daemonite(self,match,realm):
        realm.send_to_mud=False
        realm.send('summon daemonite')
        
    @binding_trigger('^The blood that forms the pentagram begins to boil and churn as a razor-clawed fiend explodes into view\.$')
    def set_fiend(self, match,realm):
        realm.cwrite('<green*:blue> Demon: Fiend')
        self.active_demon='fiend'
        
    @binding_alias('^fien$')
    def summon_fiend(self,match,realm):
        realm.send_to_mud=False
        realm.send('summon fiend')
        
    @binding_trigger('^You conjure up images of unspeakable acts and force them to take semi-corporeal form\.$')
    def set_nightmare(self, match,realm):
        realm.cwrite('<green*:blue> Demon: Nightmare')
        self.active_demon='nightmare'
        
    @binding_alias('^nigh$')
    def summon_nightmare(self,match,realm):
        realm.send_to_mud=False
        realm.send('summon nightmare')
        
class Ouroboros(BaseModule):
    def __init__(self, realm):
        BaseModule.__init__(self, realm)
        self.do_catharsis=False
        self.infirmity=False
        
    @property
    def triggers(self):
        return [self.mana_check]
    @property
    def aliases(self):
        return [self.perform_catharsis,
                self.summon_ouroboros,
                self.mount_ouroboros,
                self.demon_sear,
                self.stain,
                self.demon_blast,
                self.demon_presences,
                self.demon_trace,
                self.demon_sap,
                self.demon_beckon,
                self.demon_strip]
    
    @binding_alias('^ouro$')
    def summon_ouroboros(self,match,realm):
        realm.send('queue eqbal summon ouroboros|demon mount')
        realm.send_to_mud=False
    
    @binding_alias('^dse$')
    def demon_sear(self,match,realm):
        target=realm.root.get_state('target')
        realm.send_to_mud=False
        realm.send('queue eqbal demon sear %s'%target)
        
    @binding_alias('^mnt$')
    def mount_ouroboros(self,match,realm):
        realm.send('demon mount')
        realm.send_to_mud=False
        
    @binding_alias('^cath$')
    def perform_catharsis(self,match,realm):
        self.do_catharsis=True
        self.send_to_mud=False
        target = realm.root.get_state('target')
        realm.send('contemplate %s'%target)
        
    @binding_alias('^sta$')
    def stain(self,match,realm):
        target=realm.root.get_state('target')
        realm.send_to_mud=False
        realm.send('demon stain %s'%target)
        
    @binding_alias('^trac$')
    def demon_trace(self,match,realm):
        target=realm.root.get_state('target')
        realm.send_to_mud=False
        realm.send('demon trace %s'%target)
    
    @binding_alias('^dstr$')
    def demon_strip(self,match,realm):
        target=realm.root.get_state('target')
        realm.send_to_mud=False
        realm.send('demon strip %s'%target)
        
    @binding_alias('^bec$')
    def demon_beckon(self,match,realm):
        target=realm.root.get_state('target')
        realm.send_to_mud=False
        realm.send('demon beckon %s'%target)
        
    @binding_alias('^dsap')
    def demon_sap(self,match,realm):
        target=realm.root.get_state('target')
        realm.send_to_mud=False
        realm.send('demon sap %s'%target)
        
    @binding_alias('^blas$')
    def demon_blast(self,match,realm):
        realm.send_to_mud=False
        realm.send('demon blast')
        
    @binding_alias('^scan$')
    def demon_presences(self,match,realm):
        realm.send_to_mud=False
        realm.send('demon presences')
        
    @binding_trigger("^(\w+)'s mana stands at (\d+)/(\d+)\.$")
    def mana_check(self, match, realm):
        person = match.group(1).lower()
        target = realm.root.state['target'].lower()
        if person == target and self.do_catharsis:
            self.do_catharsis=False
            pct = float(match.group(2))/float(match.group(3))
            if self.infirmity:
                threshold=.6
            else:
                threshold=.5
                
            if pct < threshold:
                realm.cwrite('<red:white>CATHARSIS NOW!')
                realm.send('demon catharsis %s'%target)
            else:
                realm.cwrite('<yellow:white>Catharsis not ready')
    

class Daegger(EarlyInitialisingModule):
    
    def __init__(self, realm, afftracker):
        
        self.ready=True
        self.realm=realm
        self.afftracker=afftracker
        self.priority=AfflictionPriority('daegger',realm.name,realm)
        self.priority.load_priorities('default')
        self.toxin=''
        
    @property
    def triggers(self):
        return [self.daegger_hunt, self.daegger_ready,self.hunt_hit]
    @property
    def aliases(self):
        return [self.summon_daegger, self.hunt,
                self.shadow_strikes]
    
    @binding_trigger("^(\w+) winces as a toxin from the daegger seeps into (?:his|her) body\.$")
    def hunt_hit(self,match,realm):
        person=match.group(1).lower()
        target=realm.root.get_state('target').lower()
        if person==target:
            self.afftracker.tracker(target).add_aff(self.toxin)
            self.toxin=''
    
    def next_toxin_physical(self):
        self.toxin = ''
        target=self.realm.get_state('target')
        tracker=self.afftracker.tracker(target)
        if not tracker['hemotoxin'].on and tracker.time_to_next_purge() < 8:
            self.toxin='hemotoxin'
            return self.toxin
        if not tracker['slickness'].on and (tracker['asthma'].on and tracker['anorexia'].on and 
                                            (tracker['hemotoxin'].on or tracker.pboc)):
            self.toxin='iodine'
            return self.toxin
        if not tracker['metrazol'].on:
            self.toxin='metrazol'
            return self.toxin
        if not tracker['sunallergy'].on:
            self.toxin = 'xeroderma'
            return self.toxin
        if not (tracker['paralysis'].on or tracker['numbness'].on):
            self.toxin = 'ciguatoxin'
            return self.toxin 
        #if not tracker['recklessness'].on:
            
        if not tracker['weariness'].on:
            self.toxin='arsenic'
            return self.toxin
        if not tracker['clumsiness'].on:
            self.toxin='ether'
            return self.toxin
        
        if not tracker['vomiting'].on:
            self.toxin='botulinum'
            return self.toxin
        if not tracker['slow balance'].on:
            self.toxin='noctec'
            return self.toxin
        if not tracker['slow herbs'].on:
            self.toxin = 'maznor'
            return self.toxin
        if not tracker['calotropis'].on:
            self.toxin='calotropis'
            return self.toxin
        if not tracker['butisol'].on:
            self.toxin='butisol'
            return self.toxin
        if not tracker['slow elixirs'].on:
            self.toxin='luminal'
            return self.toxin
        if not tracker['sunallergy'].on:
            self.toxin='xeroderma'
            return self.toxin
        
        self.toxin='benzene'
        return self.toxin
            
    
    
    def next_toxin(self):
        self.toxin=''
        target=self.realm.get_state('target')
        tracker = self.afftracker.tracker(target)
        if not tracker['hemotoxin'].on and tracker.time_to_next_purge()<5:
            self.toxin= 'hemotoxin'
        else:
            toxins=self.priority.get_afflictions(tracker, 1)
            if len(toxins)==1:
                self.toxin=toxins[0]
        return self.toxin

    @binding_alias('^daeg$')
    def summon_daegger(self,match,realm):
        realm.send_to_mud=False
        realm.send('queue eqbal summon daegger|attach wriststrap to daegger')
    
    @binding_alias('^dh$')
    def hunt(self, match,realm):
        realm.send_to_mud=False
        target=realm.root.state['target']
        toxin=self.next_toxin()
        realm.send('daegger hunt %s %s'%(target,toxin))
     
    @binding_alias('^dss$')
    def shadow_strikes(self,match,realm):
        realm.send_to_mud=False
        target= realm.root.state['target']
        realm.send('daegger shadowstrike %s'%target)
         
        
    @binding_trigger('^"Hunt!" you order your daegger\.$')
    def daegger_hunt(self,match,realm):
        realm.display_line=False
        realm.cwrite('<black:cyan>---- DAEGGER HUNT ----')
        self.ready=False
        self.timed_ready=realm.root.set_timer(12, self._daegger_ready)
        
    @binding_trigger('^The daegger is again ready to hunt its prey\.$')
    def daegger_ready(self,match,realm):
        realm.display_group=False
        realm.cwrite('<white*:cyan>++++ DAEGGER READY ++++')
        self._daegger_ready(realm.root)
        
    def _daegger_ready(self, realm):
        if not self.ready:
            self.ready=True
            realm.cwrite('<white*:cyan>+++++ DAEGGER READY +++++')
        