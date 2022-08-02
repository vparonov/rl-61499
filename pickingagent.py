from agent import Agent


class PickingAgent(Agent):
    def __init__(self, name, description=None, delay=1, destination=None) :
        super().__init__(name, description)
        self.delay = delay  
        self.destination = destination
        self.workload = None
        self.counter = 0 
    
    def act(self, component, ctime):
        if self.workload is not None :
            self.counter -= 1
            if self.counter != 0 :
                print("%d agent %s is waiting %d" % (ctime, self.name, self.counter))
                return 
            else:
                print("%d agent %s is ready with msg = %s" % (ctime, self.name, self.workload))
                msg = self.workload
                msg['p'] = True 
                msg['a'] = self.name
                self.destination.putItem(msg) 
        self.workload = component.getItem()
        if self.workload is None:
            return

        print('%d agent: %s got workload: %s' % (ctime, self.name, self.workload))
        self.counter = self.delay

