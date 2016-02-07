'''
Created on Dec 16, 2015

@author: Dmitry
'''
from pymudclient.modules import EarlyInitialisingModule, BaseModule
from pymudclient.aliases import binding_alias
from pymudclient.triggers import binding_trigger
import json
import os

class WarhoundParser(EarlyInitialisingModule):
    
    def __init__(self):
        self.hound={}
        self.state='off'
        
        
    
    @property
    def triggers(self):
        return [self.name_line, self.get_stat, self.major_traits_start, self.minor_traits_start,
                self.get_trait]
    
    @property
    def aliases(self):
        return [self.print_hound, self.hound_info]
    
    @binding_trigger('(?:(\w+), )?a vicious warhound \(#(\d+)\)')
    def name_line(self, matches, realm):
        if self.state=='start_parse':
            self.hound={}
            self.hound['Name']=str(matches.group(1)) if not matches.group(1)== None else 'None'
            self.hound['Id']=int(matches.group(2))
            self.state='stats_parse'
            
    @binding_trigger('(\w+): (Male|Female|\d+)')
    def get_stat(self, matches, realm):
        if self.state=='stats_parse':
            if matches.group(1)==u'Sex':
                self.hound[str(matches.group(1))]=str(matches.group(2))
            else:
                self.hound[str(matches.group(1))]=int(matches.group(2))
            
    @binding_trigger('==\[ Major Traits \]==')
    def major_traits_start(self,matches, realm):
        if self.state=='stats_parse':
            self.state = 'major_parse'
            self.hound['Major']=[]
    @binding_trigger('==\[ Minor Traits \]==')
    def minor_traits_start(self, matches, realm):
        if self.state=='major_parse':
            self.state='minor_parse'
            self.hound['Minor']=[]
            
    @binding_trigger('- (?:P: )?([A-Z][a-z\-]+) ')
    def get_trait(self, matches, realm):
        if self.state=='major_parse':
            self.hound['Major'].append(str(matches.group(1)))
        if self.state=='minor_parse':
            self.hound['Minor'].append(str(matches.group(1)))
            if len(self.hound['Minor'])==6:
                if 'Lazy' in self.hound['Minor'][0:3]:
                    self.hound['Speed']+=30
                if 'Weak' in self.hound['Minor'][0:3]:
                    self.hound['Ferocity']+=30
                if 'Fragile' in self.hound['Minor'][0:3]:
                    self.hound['Resilience']+=30
                
                self.state='done'
                realm.root.fireEvent('houndDoneEvent', json.dumps(self.hound))
            
    @binding_alias('^print_hound$')
    def print_hound(self, match, realm):
        realm.send_to_mud=False
        realm.write(self.hound)
        
    @binding_alias('^hound info$')
    def hound_info(self, match, realm):
        self.state='start_parse'
        
        
class WarhoundPicker(BaseModule):
    def __init__(self, manager):
        BaseModule.__init__(self, manager)
        print('hello')
        self.reset()
        self.state = 'off'
        manager.registerEventHandler('houndDoneEvent', self.process_hound)
        self.stat_save=None
        
    def reset(self):
        self.min_speed = 0
        self.min_ferocity = 0
        self.min_resilience= 0
        self.majors=[]
        self.minors=[]
        self.n_majors = 0
        self.n_minors = 0
        self.excluded_minors=[]
        self.sex='male'

    @property
    def triggers(self):
        return [self.hound_killed, self.get_hound]
    
    @property
    def aliases(self):
        return [self.print_config, self.set_config, self.run, self.stop]
    
    
    @binding_trigger('returns, a few freshly wrapped steaks in hand and a grin on his face.')
    def hound_killed(self, matches, realm):
        realm.write('state: %s'%self.state)
        if self.state == 'continue':
            self.request(realm)
    
    @binding_trigger('Yaps and snarls fill the kennel as a worker wades through the pens, finally dragging out a vicious')
    def get_hound(self, matches, realm):
        if self.state=='request':
            realm.send('hound info')
    
    @binding_alias('^hound selector config$')
    def print_config(self, matches, realm):  
        realm.send_to_mud=False
        realm.cwrite('~'*50)
        realm.cwrite('<white>| Sex: <red*>%-43s<white>|'%self.sex)
        if self.min_speed > 0:
            realm.cwrite('<white>| Min Speed: <red*>%-37s<white>|'%str(self.min_speed))
        if self.min_ferocity > 0:
            realm.cwrite('<white>| Min Feroc: <red*>%-37s<white>|'%str(self.min_ferocity))
        if self.min_resilience > 0:
            realm.cwrite('<white>| Min Resil: <red*>%-37s<white>|'%str(self.min_resilience))
        if not self.majors == []:
            realm.cwrite('<white>| Majors(%d): <green*>%-37s<white>|'%(self.n_majors,','.join(self.majors)))
        if not self.minors == []:
            realm.cwrite('<white>| Minors(%d): <green*>%-37s<white>|'%(self.n_minors,','.join(self.minors)))
        if not self.excluded_minors==[]:
            realm.cwrite('<white>| Ex Minors: <red*>%-37s<white>|'%','.join(self.excluded_minors))
        realm.cwrite('~'*50)
    
    @binding_alias('^hound selector config ([a-z]+) ([a-z,0-9\-]+)$')
    def set_config(self, matches, realm):
        realm.send_to_mud=False
        option=matches.group(1).lower()
        if option=='sex':
            self.sex = str(matches.group(2))
            self.print_config(None, realm)
            return
        if option=='speed':
            self.min_speed=int(matches.group(2))
            self.print_config(None, realm)
            return
        if option=='ferocity':
            self.min_ferocity=int(matches.group(2))
            self.print_config(None, realm)
            return
        if option=='resilience':
            self.min_resilience=int(matches.group(2))
            self.print_config(None, realm)
            return
        if option=='majors':
            self.majors=[s.capitalize() for s in str(matches.group(2)).split(',')]
            if self.n_majors == 0:
                self.n_majors = len(self.majors)
            self.print_config(None, realm)
            return
        if option=='nummajors':
            self.n_majors = int(matches.group(2))
            self.print_config(None, realm)
            return
        if option=='minors':
            self.minors=[s.capitalize() for s in str(matches.group(2)).split(',')]
            if self.n_minors == 0:
                self.n_minors = len(self.minors)
            self.print_config(None, realm)
            return
        if option=='numminors':
            self.n_minors = int(matches.group(2))
            self.print_config(None, realm)
            return
        if option=='exminors':
            self.excluded_minors=[s.capitalize() for s in str(matches.group(2)).split(',')]
            self.print_config(None, realm)
            return
        
        realm.cwrite('<red>ERROR: Unknown config option %s'%option)
        
    @binding_alias('^hound selector run$')
    def run(self, match, realm):
        realm.send_to_mud=False
        self.request(realm)
        path = os.path.join(os.path.expanduser('~'),'muddata','hounds')
        if not os.path.isdir(path):
            os.makedirs(path)
        self.stat_save = open('%s/hounds.csv'%path, 'a')
        
    @binding_alias('^hound selector stop$')
    def stop(self, match, realm):
        realm.send_to_mud=False
        self.state='off'
        self.stat_save.close()
        
        
    def request(self, realm):
        self.state='request'
        realm.send('qeb hound request %s'%self.sex)    
        
    
    def process_hound(self, info_string):
        self.manager.write('Processing')
        if self.state=='request':
            info = json.loads(info_string)
            accept=True
            csv_string = "%d,%d,%d,%d,%s,%s\n"%(info['Id'],
                                                info['Speed'],
                                                info['Ferocity'],
                                                info['Resilience'],
                                                ','.join(info['Major']),
                                                ','.join(info['Minor'])
                                                )
            
            self.stat_save.write(csv_string)
            
            if self.min_speed > 0 and info['Speed'] < self.min_speed:
                accept=False
            if self.min_ferocity > 0 and info['Ferocity'] < self.min_ferocity:
                accept=False
            if self.min_resilience > 0 and info['Resilience'] < self.min_resilience:
                accept=False
            found_majors = 0
            if not self.majors == []:
                for m in self.majors: 
                    if m in info['Major']:
                        found_majors+=1
            if found_majors < self.n_majors:
                accept=False
            found_minors = 0
            if not self.minors == []:
                for m in self.minors:
                    if m in info['Minor']:
                        found_minors+=1
            if found_minors < self.n_minors:
                accept = False
            if not self.excluded_minors==[]:
                for m in self.excluded_minors:
                    if m in info['Minor']:
                        accept=False
            
            if accept:
                self.state='done'
                self.manager.cwrite('<green*>Found the right hound!')
                self.stat_save.close()
            else:
                self.state='continue'
                self.manager.send('qeb hound name warhound trash|hound dismiss trash|hound reject trash confirm')
        
                
         
    
        
        
    