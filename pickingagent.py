from xml.etree.ElementPath import prepare_predicate
from agent import Agent


class PickingAgent(Agent):
    def __init__(self, name, description=None, predicate = None, delay=1, 
            destination=None, stopConveyor= False, 
            markWorkload = None) :
        super().__init__(name, description)
        self.delay = delay  
        self.destination = destination
        self.workload = None
        self.counter = 0 
        self.predicate = predicate
        self.stopConveyor = stopConveyor
        self.markWorkload = markWorkload

    def act(self, component, ctime):
        if self.workload is not None :
            self.counter -= 1
            if self.counter > 0 :
                print('%d agent %s is waiting %d' % (ctime, self.name, self.counter))
                return 
            else:
                if self.destination.putItem(self.workload) == True:
                    print('%d agent %s is ready with workload = %s' % (ctime, self.name, self.workload))
                    self.markWorkload(self.workload, ctime)
                    self.workload = None
                    if self.stopConveyor == True:
                        component.start() 
                else:
                    print('%d agent %s the destination %s is full! the agent will wait' % (ctime, self.name, self.destination.name))
                    return 
  
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

        print('%d agent: %s got workload: %s' % (ctime, self.name, self.workload))
        self.counter = self.delay

