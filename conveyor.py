from component import Component
class Conveyor(Component):
    def __init__(self, name, description=None, delay = 1, capacity = 10):
        super().__init__(name, description)
        self.delay = delay
        self.capacity = capacity
        self.resetState()

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
                return True 
        return False 
           
    def changeState(self, ctime):
        if self.on == False:
            return False  

        if ctime % self.delay != 0:
            return False 

        if len(self.children) > 0:
            outputMsg = self.buffer[self.capacity-1]
            if outputMsg is not None:
                next = self.children[self.activeChildID] 
                if next.receive(outputMsg):
                    self.buffer[self.capacity-1] = None 

        for i in range(self.capacity-1, 0, -1):
            if self.buffer[i] == None:
                self.buffer[i] = self.buffer[i-1]
                self.buffer[i-1] = None

        return True 

    def getInternalState(self):
        return self.buffer.copy()
        
    def printState(self):
        countBoxes = 0 
        for ix in range(0, self.capacity):
            if self.buffer[ix] is not None:
                countBoxes += 1
       
        print('%s(%s, %d) -> [' % (self.name, 'on' if self.on else 'off', countBoxes), end = '')
        for ix in range(0, self.capacity): 
            delim = ','
            if ix == self.capacity - 1:
                delim = ']'    
            if self.buffer[ix] is not None:
                print(self.buffer[ix], end = delim)
            else:
                print('()', end = delim)
        print('')
        for agent in self.agents:
            agent.printState()
    
    def resetState(self):
        self.on = True 
        self.buffer = [None] * self.capacity
        self.activeChildID = 0  

    def setActiveChildID(self, id):
        self.activeChildID = id 


if __name__ == '__main__':
    from source import Source 
    from sink import Sink
    from box import Box

    def genNitems(n):
        def g(ctime):
            if ctime <= n:
                return Box.random()
            else:
                return None 

        return g 

    def test1():
        nitems = 2
        source = Source('source','warehouse', delay=1, generator = genNitems(nitems))

        c1 = Conveyor("c1", capacity=30) 

        source.connect(c1) 

        for i in range(40):
            source.tick(i)
            source.print()

    def test2():
        nitems = 2
        source = Source('source','warehouse', delay=1, generator = genNitems(nitems))
        sink = Sink('sink') 
        c1 = Conveyor('c1', capacity=30) 

        source.\
            connect(c1).\
            connect(sink)

        for i in range(40):
            source.tick(i)
            source.print()

    # test1()
    test2()
    