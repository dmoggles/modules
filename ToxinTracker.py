'''
Created on Aug 3, 2015

@author: dmitry
'''
from pymudclient.modules import EarlyInitialisingModule
from FlareTracker import FlareTracker, FlareObject


class SingleTargetToxins:
    def __init__(self):
        self.toxins={}
    
    def __get__(self, key):
        if not key in self.toxins:
            self.toxins[key]=0
        return self.toxins[key]
    
    def __set__(self,key, value):
        self.toxins[key]=value
            

class BaseToxinTracker(EarlyInitialisingModule):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.targets={}
    def __get__(self, key):
        if not key in self.targets:
            self.targets[key]=SingleTargetToxins()
        return self.targets[key]
            
        
    
    
class FlareKeyedToxinTracker(BaseToxinTracker):
    def __init__(self):
        BaseToxinTracker.__init__(self)
        pass
    def getNextToxinSet(self, flare):
        if flare == FlareObject.SOWULU:
            return ('strychnine','strychnine')
        if flare == FlareObject.PITHAKHAN:
            return ('metrazol','ciguatoxin')
        if flare==FlareObject.NAUTHIZ:
            return('metrazol','ciguatoxin')
        if flare==FlareObject.WUNJO:
            return('mazanor','luminal')
        return ('atropine','aconite')
    

