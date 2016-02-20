'''
Created on Aug 5, 2015

@author: dmitry
'''
from pymudclient.modules import BaseModule
from pymudclient.gmcp_events import binding_gmcp_event

def update_display(f):
    def func_with_updated_display(self, matched_data, realm):
        f(self, matched_data, realm)
        self.output_to_gui(realm.root)
    return func_with_updated_display
                    
                    
                    

class SelfAfflictions(BaseModule):
    '''
    classdocs
    '''


    def __init__(self, realm):
        '''
        Constructor
        '''
        BaseModule.__init__(self, realm)
        self.by_cure_table={}
        self.full_list=[]
        self.unknown_afflictions=0
        self.all_herb_cures=['wormwood','mandrake','kelp','orphine','nightshade','galingale','maidenhair']
        self.all_smoke_cures=['lovage','laurel']
        self.all_salve_cures=['restoration','epidermal','mending','caloric']
        self.combined_cures = self.all_herb_cures+self.all_smoke_cures+self.all_salve_cures
        
    
    @property
    def gmcp_events(self):
        return[self.on_char_afflictions_add, self.on_char_afflictions_remove]    
    #Helper functions
    
    
            
    def output_to_gui(self, realm):
        #cur_channels = realm.active_channels
        #realm.active_channels=['afflictions']
        realm.cwrite(self.output(), channels=['afflictions'])
        #realm.active_channels=cur_channels
     
    def output(self):
        s = '||'.join(["%s: %s"%(k[:3],','.join(v)) for k,v in self.by_cure_table.items() if len(v)> 0])
        print s
        return s
       
    @binding_gmcp_event('Char.Afflictions.Add')
    @update_display
    def on_char_afflictions_add(self, gmcp_data, realm):
        
        aff=gmcp_data['name']
        aff_cure = gmcp_data['cure']
        realm.cwrite('<red*:grey>++++%s++++\n++++%s++++'%(aff.upper(),aff.upper()))
        short_cure=''
        for c in self.combined_cures:
            if c in aff_cure:
                short_cure=c
                break
        if short_cure == '':
            short_cure = 'unk'
            
        if not short_cure in self.by_cure_table:
            self.by_cure_table[short_cure]=[]
        if not aff in self.by_cure_table[short_cure]:
            self.by_cure_table[short_cure].append(aff)
            
    @binding_gmcp_event('Char.Afflictions.Remove')
    @update_display
    def on_char_afflictions_remove(self, gmcp_data, realm):
        for d in gmcp_data:
            realm.cwrite('<green*:grey>----%s----\n----%s----'%(d.upper(),d.upper()))
            for cure in self.by_cure_table:
                if d in self.by_cure_table[cure]:
                    self.by_cure_table[cure].remove(d)
                    

class MainModule(SelfAfflictions):
    pass
            