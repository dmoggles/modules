'''
Created on Aug 28, 2015

@author: Dmitry
'''


from twisted.internet import stdio
from twisted.internet import reactor
from pymudclient.modules import BaseModule
from pymudclient.processor import MudProcessor

class MainModule(BaseModule):
    def __init__(self, manager):
        BaseModule.__init__(self, manager)


def main():
    rr = MudProcessor()
    MainModule(rr)
    
    stdio.StandardIO(rr)
    reactor.run()

if __name__=='__main__':
    main()