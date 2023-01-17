from xml.etree.ElementPath import prepare_predicate
from agent import Agent

IDLE = 0
PICKING = 1
WAITING = 2

class PickingAgent(Agent):
    def __init__(self, name, description=None, predicate = None, delay=1, 
            destination=None, stopConveyor= False, 
            markWorkload = None, verbose = False, 
            maxBlockedTime = 0, 
            state = None) :
        super().__init__(name, description)
        self.delay = delay  
        self.destination = destination
        self.predicate = predicate
        self.stopConveyor = stopConveyor
        self.markWorkload = markWorkload
        self.verbose = verbose
        self.maxBlockedTime = maxBlockedTime
        self.state = state

        self.status = IDLE

        self.reset()

    def act(self, component, ctime):
        if self.workload is not None :
            self.counter -= 1
            if self.counter > 0 :
                self.status = PICKING
                if self.verbose: 
                    print('%d agent %s is waiting %d' % (ctime, self.name, self.counter))
                return 
            else:
                if self.destination.putItem(self.workload) == True:
                    self.status = IDLE 
                    if self.verbose:
                        print('%d agent %s is ready with workload = %s' % (ctime, self.name, self.workload))
                    self.markWorkload(self.workload, ctime)
                    self.state.update(self.workload.id, self.destination.name)
                    self.workload = None
                    self.currentBlockedTime = 0 
                    if self.stopConveyor == True:
                        component.start() 
                else:
                    self.status = WAITING
                    if self.verbose:
                        print('%d agent %s the destination %s is full! the agent will wait' % (ctime, self.name, self.destination.name))
                    self.currentBlockedTime += 1
                    if self.maxBlockedTime > 0 and self.currentBlockedTime > self.maxBlockedTime:
                        raise Exception('(%d) Agent %s is blocked for more than %s time steps' % (ctime, self.name, self.maxBlockedTime))
                    return 
        else:
            self.status = IDLE 

        self.workload = component.getItem()
     
        if self.workload is None:
            return
        # if the agent's predicate returns False the item is returned to the source component
        # i.e. it should not be processed from the agent
        if self.predicate != None and self.predicate(self.workload) == False :
            component.putItem(self.workload)
            self.workload = None
            return 

        if self.stopConveyor == True:
            component.stop() 
        else:
            # start the component in case if was full and stopped before the agent picked the item
            component.start()

        self.state.update(self.workload.id, self.name)
   
        self.status = PICKING

        if self.verbose:
            print('%d agent: %s got workload: %s' % (ctime, self.name, self.workload))
        self.counter = self.delay

    def getInternalState(self):
        return [self.workload]
              
    def printState(self):
        print('agent: %s is %s current blocked time = %d max blocked time = %d' % 
            (self.name, 
            'free' if self.workload is None else 'picking', 
            self.currentBlockedTime, 
            self.maxBlockedTime))    
    
    def reset(self):
        self.workload = None
        self.counter = 0 
        self.currentBlockedTime = 0