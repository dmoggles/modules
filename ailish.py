'''
Created on Jul 15, 2015

@author: Dmitry
'''
from pymudclient.modules import BaseModule, load_file
from pymudclient.aliases import binding_alias
from pymudclient.triggers import binding_trigger
from pymudclient.net.gmcp import ImperianGmcpHandler

from BashModule import BashModule
from sys import modules
from pymudclient.metaline import Metaline, RunLengthList
from pymudclient.colours import fg_code, bg_code, BLACK, RED, CYAN
from pymudclient.tagged_ml_parser import taggedml
from pymudclient.library.html import HTMLLoggingModule
from runeguard import Runeguard



class MainModule(HTMLLoggingModule, ImperianGmcpHandler):
        name = 'Ailish'
        host = 'imperian.com'
        port = 23
        
        
        def is_main(self, realm):
            HTMLLoggingModule.is_main(self, realm)
            
        @binding_alias(r'^show_gmcp$')
        def show_gmcp(self,match,realm):
            realm.write(self.gmcpToString(realm.root.gmcp), soft_line_start=True)
            realm.send_to_mud=False
            
        @binding_alias(r"^add_module (\w+)$")
        def add_module(self,match,realm):
            modname=match.group(1)
            realm.write("Adding module %s" % modname)
            realm.send_to_mud=False
            cls=load_file(modname)
            realm.write(cls)
            if cls!=None:
                realm.write('Got a class')
                realm.root.load_module(cls)
        @binding_alias 
        def reload_modules(self,match,realm):
            for m in modules:
                reload(m)
                
        @binding_alias('^tar (\w+)$')    
        def set_target(self, match, realm):
            my_target=match.group(1).capitalize()
            
            #ml = Metaline('Target set: %s'%my_target, RunLengthList([(0, fg_code(CYAN, True)),
            #                                                         (12,fg_code(RED,True))]),
            #              RunLengthList([(0,bg_code(BLACK))]))
            ml = taggedml('<cyan*:black>Target set: <red*>%s'%my_target)                                                    
            realm.write(ml)
            realm.root.state['target']=my_target
            realm.send_to_mud=False    
        @binding_trigger(['abc','def'])
        def testtesttest(self, match, realm):
            realm.write("Success!")    
        @property
        def aliases(self):
            return [self.add_module, self.show_gmcp, self.set_target]
        @property
        def triggers(self):
            return[self.testtesttest]
        @property
        def macros(self):
            return{}
        @property
        def modules(self):
            return[Runeguard]
            
        