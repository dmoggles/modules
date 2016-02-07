'''
Created on Sep 18, 2015

@author: Dmitry
'''
from pymudclient.modules import BaseModule
from pymudclient.triggers import binding_trigger
from pymudclient.aliases import binding_alias
import os
from pandas import DataFrame

class MainModule(BaseModule):
    '''
    classdocs
    '''
    def __init__(self, realm):
        BaseModule.__init__(self,realm)
        self.state='off'
        self.affliction_list=[]
        self.aff_index=0
        self.affs={}
        
        self.curr_aff=''

    @property
    def aliases(self):
        return [self.scan]
    
    @property
    def triggers(self):
        return [self.text_line, self.scan_more, self.scan_done,
                self.new_affliction,self.cure_message,self.diag_message,
                self.cure,self.cure2,self.physical,self.mental,self.purged]
    
    @binding_alias('^scan affs$')
    def scan(self, match, realm):
        realm.send_to_mud=False
        self.state='scanning'
        self.affliction_list=[]
        realm.send('affliction list all')
        
    @binding_trigger('^([a-zA-Z]+(?:(?:\s|\.|,)+[a-zA-Z]+)*\.?)$')
    def text_line(self,match,realm):
        if self.state=='scanning':
            aff=match.group(1)
            print('got aff %s'%aff)
            self.affliction_list.append(aff)
        elif self.state=='parsing_desc':
            print('description: %s'%match.group(1))
            self.affs[self.curr_aff]['description']=match.group(1)
            self.aff_index+=1
            if self.aff_index < len(self.affliction_list):
                self.state='parsing'
                realm.send('affliction show %s'%self.affliction_list[self.aff_index])
            else:
                self.state='off'
            
     
    @binding_trigger('^Type MORE to continue reading\. \((\d+)% shown\)$')
    def scan_more(self, match,realm):
        if self.state=='scanning':
            realm.send('more')   
            
    @binding_trigger('^Use AFFLICTION SHOW <name> to display information about an affliction\.$')
    def scan_done(self,match,realm):
        if self.state=='scanning':
            self.state='parsing'
            self.aff_index = 0
            print(self.affliction_list)
            realm.send('affliction show %s'%self.affliction_list[self.aff_index])
    
    @binding_trigger('^Affliction:\s+ ([a-z]+(?:\s+[a-z]+)*)$')
    def new_affliction(self,match,realm):
        if self.state=='parsing':
            print('affliction: %s'%match.group(1))
            self.curr_aff=match.group(1)
            self.affs[self.curr_aff]={}
            
    @binding_trigger('^Cure message:\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)*)\.$')
    def cure_message(self,match,realm):
        if self.state=='parsing':
            print('cm: %s'%match.group(1))
            self.affs[self.curr_aff]['cure_msg']=match.group(1)
            
    @binding_trigger('^Diagnose:\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)*)\.$')
    def diag_message(self,match,realm):
        if self.state=='parsing':
            print('diag: %s'%match.group(1))
            self.affs[self.curr_aff]['diagnose_msg']=match.group(1)
    
    @binding_trigger('^Cure:\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)*)$')
    def cure(self,match,realm):
        if self.state=='parsing':
            print('cure: %s'%match.group(1))
            self.affs[self.curr_aff]['cure']=match.group(1)        
    
    @binding_trigger('^Cure 2:\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)*)$')
    def cure2(self,match,realm):
        if self.state=='parsing':
            print('cure2: %s'%match.group(1))
            self.affs[self.curr_aff]['cure2']=match.group(1)
            
    @binding_trigger('^Physical:\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)*)$')
    def physical(self,match,realm):
        if self.state=='parsing':
            print('physicla: %s'%match.group(1))
            self.affs[self.curr_aff]['physical']=match.group(1)=='Yes'  
    @binding_trigger('^Mental:\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)*)$')
    def mental(self,match,realm):
        if self.state=='parsing':
            print('mental: %s'%match.group(1))
            self.affs[self.curr_aff]['mental']=match.group(1)=='Yes'
            
    @binding_trigger('^Can be purged:\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)*)$')
    def purged(self,match,realm):
        if self.state=='parsing':
            print('purged: %s'%match.group(1))
            self.affs[self.curr_aff]['purged']=match.group(1)=='Yes'
            #self.state='parsing_desc'
            self.aff_index+=1
            if self.aff_index < len(self.affliction_list):
                self.state='parsing'
                realm.send('affliction show %s'%self.affliction_list[self.aff_index])
            else:
                self.state='off'   
                df=DataFrame.from_dict(self.affs, orient='index')
                pth=os.path.join(os.path.expanduser('~'),'affs.csv')
                df.to_csv(pth)
     
                        