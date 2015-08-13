'''
Created on Aug 5, 2015

@author: dmitry
'''
from pymudclient.modules import BaseModule
from pymudclient.gmcp_events import binding_gmcp_event

class SelfAfflictionTracker(BaseModule):
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
        self.all_herb_cures=['wormwood','mandrake','kelp','orphine','nightshade','galingale','maindenhair']
        self.all_smoke_cures=['lovage','laurel']
        self.all_salve_cures=['restoration','epidermal','mending','caloric']
        self.combined_cures = self.all_herb_cures+self.all_smoke_cures+self.all_salve_cures
        
        
    #Helper functions
    
    def update_display(self, f):
        def func_with_updated_display(self, matched_data, realm):
            f(self, matched_data, realm)
            self.output_to_gui(realm.root)
        return func_with_updated_display
            
    def output_to_gui(self, realm):
        cur_channels = realm.active_channels
        realm.active_channels=['afflictions']
        realm.cwrite(self.output())
        realm.active_channels=cur_channels
        
    @binding_gmcp_event('Char.Afflictions.Add')
    @update_display
    def on_char_afflictions_add(self, gmcp_data, realm):
        aff=gmcp_data['name']
        aff_cure = gmcp_data['cure']
        short_cure=''
        for c in self.all_herb_cures:
            if c in aff_cure:
                short_cure=c
        if c == '':
            for c in self.all_smoke_cures:
                if c in aff_cure: