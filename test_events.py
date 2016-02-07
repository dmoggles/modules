
from twisted.internet import reactor, defer


# def registerEvent(eventName):
#     def registerEventDecorator(f):
#         def wrapped_f(self):
#             self.eh.registerEvent(eventName, f)
#         return wrapped_f
#             
#     return registerEventDecorator
def make_dec():
    def _fnc(eventName, eh):
        def wrapped_event_handler(func):
            eh.registerEvent(eventName, func)
        return wrapped_event_handler
    return _fnc

registerEvent=make_dec()


class TestClass:
    def __init__(self, num, eh):
        self.num = num
        self.eh=eh
        
    @registerEvent('testClassEvent', self.eh)    
    def f(self, a,b):
        print((self.num + a)*b)
        
        


class EventHandler:
    def __init__(self):
        self.events={}
        
    def registerEvent(self, eventName, handler):
        print('registering event %s'%eventName)
        if not eventName in self.events:
            self.events[eventName]=[]
        self.events[eventName].append(handler)
        
    def fireEvent(self, eventName, *args):
        if eventName in self.events:
            for eh in self.events[eventName]:
                #d = defer.Deferred()
                #d.addCallback(eh)
                reactor.callLater(0, eh, *args)
                #eh(*args)
                
    

def doIt(EH):
    EH.fireEvent('testClassEvent',40,2)
    print('Im done')
        
    

if __name__=='__main__':

    EH=EventHandler()
    TC=TestClass(5, EH)
    TC2=TestClass(30, EH)
    #EH.registerEvent('testClassEvent',TC.f)
    #EH.registerEvent('testClassEvent',TC2.f)
    reactor.callLater(1, doIt, EH)    
    reactor.run()
   