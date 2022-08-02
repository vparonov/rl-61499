
from curses import tigetflag
from this import s


class Component(object):
    def __init__(self, name, description=None):
        self.name = name
        self.description = description
        self.children = []
        self.agents = []

    def add_child(self, child):
        self.children.append(child)

    def add_agent(self, agent):
        self.agents.append(agent)

    def print(self):
        self.printState()
        for child in self.children:
            child.print()

    def receive(self, msg):
        raise NotImplementedError

    def changeState(self, ctime):
        raise NotImplementedError

    def printState(self):
        raise NotImplementedError

    def getItem(self):
        raise NotImplementedError

    def putItem(self, item):
        raise NotImplementedError

    def tick(self, ctime):
        for child in self.children:
            child.tick(ctime)

        for agent in self.agents:  
            print('Agent %s has tick time' % agent.name)
            agent.act(self, ctime)
        self.changeState(ctime)

class Source(Component):
    def __init__(self, name, description=None, rate = 1, generator = None) :
        super().__init__(name, description)
        self.rate = rate
        self.generator = generator
        self.idx = 0

    def changeState(self, ctime):
        if ctime % self.rate == 0 :
            for child in self.children:
                if child.receive(self.generator(self.idx+1)) == True:
                    self.idx = self.idx + 1
       
    def printState(self):
        print('%s -> %d' % (self.name, self.idx))

class Agent(object):   
    def __init__(self, name, description=None) :
        self.name = name
        self.description = description

    def act(self, component, ctime):
        raise NotImplementedError

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

    
class Sink(Component):
    def __init__(self, name, description=None):
        super().__init__(name, description)
        self.countReceived = 0

    def receive(self, msg):
        self.countReceived += 1

    def changeState(self, ctime):
        pass 

    def printState(self):
        print('%s -> count=%d' % (self.name, self.countReceived))

class Conveyer(Component):
    def __init__(self, name, description=None, delay = 1, capacity = 10):
        super().__init__(name, description)
        self.delay = delay
        self.capacity = capacity
        self.on = True 
        self.buffer = [None] * self.capacity

    def receive(self, msg):
        if self.on == False:
            return False  

        if self.buffer[0] is not None:
            return False 

        self.buffer[0] = msg
        return True 

    def start(self):
        self.on = True
    
    def stop(self):
        self.on = False

    def add_child(self, child):
        if len(self.children) > 0:
            raise Exception('%s. The conveyeror can have only one child.' % self.name)
        return super().add_child(child) 

    # gets an item from the conveyeror and returns the item
    def getItem(self):
        for ix in range(self.capacity-1, -1, -1):
            if self.buffer[ix] is not None:
                item = self.buffer[ix]
                self.buffer[ix] = None
                return item

    # puts an item to the conveyeror at the first empty position from the beginning
    def putItem(self, item):
        for ix in range(self.capacity):
            if self.buffer[ix] is None:
                self.buffer[ix] = item
                return 
        raise Exception('%s is full ' % self.name)
           
    def changeState(self, ctime):
        if self.on == False:
            return False  

        if ctime % self.delay == 0:
            outputMsg = self.buffer[self.capacity-1]
            if outputMsg is not None:
                next = self.children[0] # the conveyeror must have only one child
                if next.receive(outputMsg) == False:
                    return False    

            self.buffer.insert(0,self.buffer.pop())
            self.buffer[0] = None 
        return True 

    def printState(self):
        print('%s -> [' % (self.name), end = '')
        for ix in range(0, self.capacity): 
            delim = ','
            if ix == self.capacity - 1:
                delim = ']'    
            if self.buffer[ix] is not None:
                print(self.buffer[ix], end = delim)
            else:
                print("()", end = delim)
        print("")

class Diverter(Component):  
    def __init__(self, name, description):          
        super().__init__(name, description)
        self.straight = None
        self.divert = None
        self.predicate = None

    def connect(self, straightConnection, divertConnection, divertPredicate):
        self.straight = straightConnection
        self.divert = divertConnection 
        self.predicate = divertPredicate    

    def receive(self, msg):
        if self.predicate(msg):
            return self.divert.receive(msg)
        else:
            return self.straight.receive(msg)

def genNitems(n):
    def g(ctime):
        if ctime <= n:
            return {"idx": ctime}
        else:
            return None 

    return g 
def main():
    print("Starting")
    #test1()
    #test2()
    testAFrame()

def test1():
    source = Source("source","warehouse", rate=1, generator = genNitems(10))#lambda t: {"idx": t})
    c1 = Conveyer("c1","c1", delay = 1, capacity = 20)
    c2 = Conveyer("c2","c2", delay = 1, capacity = 5)
    sink = Sink("sink","final sink")
    a1 = PickingAgent("a1","a1", delay = 5, destination=c2)
    a2 = PickingAgent("a2","a2", delay = 5, destination=c2)
    a3 = PickingAgent("a3","a3", delay = 5, destination=c2)

    source.add_child(c1)
    c1.add_agent(a1)
    c1.add_agent(a2)
    c1.add_agent(a3)
    c2.add_child(sink)
    
    for t in range(1,20):
        source.tick(t)
        c2.tick(t) 
        source.print()
        c2.print()

def test2():
    source = Source("source","warehouse", rate=1, generator = genNitems(10))#lambda t: {"idx": t})
    c1 = Conveyer("c1","c1", delay = 1, capacity = 20)
    c2 = Conveyer("c2","c2", delay = 1, capacity = 5)
    sink = Sink("sink","final sink")
    c2.add_child(sink)

    source.add_child(c1)


def testAFrame():
    source = Source("source","warehouse", rate=1, generator = genNitems(10))
    c1 = Conveyer("c1","c1", delay = 1, capacity =1)
    sink = Sink("sink","sink")

    source.add_child(c1)
    c1.add_child(sink)

    for t in range(1,20):
        source.tick(t)
        source.print()

if __name__ == '__main__':
    main()