'''
Created on Dec 16, 2015

@author: Dmitry
'''
from pymudclient.modules import BaseModule
from aetolia.warhounds import WarhoundParser, WarhoundPicker


class Carnifex(BaseModule):
    
    def __init__(self, manager):
        BaseModule.__init__(self, manager)
        self.warhound_parser = WarhoundParser()
        
    @property
    def modules(self):
        return [self.warhound_parser, WarhoundPicker]