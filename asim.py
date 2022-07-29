
class Component(object):
    def __init__(self, name, description=None):
        self.name = name
        self.description = description
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def print(self):
        self.printState()
        for child in self.children:
            child.print()

    def receive(self, msg):
        pass

    def changeState(self, ctime):
        pass

    def printState(self):
        pass

    def tick(self, ctime):
        for child in self.children:
            child.tick(ctime)
        self.changeState(ctime)

class Source(Component):
    def __init__(self, name, description=None, rate = 1, generator = None) :
        super().__init__(name, description)
        self.rate = rate
        self.generator = generator
        self.idx = 0

    def changeState(self, ctime):
        if ctime % self.rate == 0 :
            self.idx = self.idx + 1
            for child in self.children:
                child.receive(self.generator(self.idx))
    def printState(self):
        print('%s -> %d' % (self.name, self.idx))

class Sink(Component):
    def __init__(self, name, description=None):
        super().__init__(name, description)
        self.countReceived = 0

    def receive(self, msg):
        self.countReceived += 1
        #print('sink received: %s' % msg)

    def printState(self):
        print('%s -> %d' % (self.name, self.countReceived))

class Conveyer(Component):
    def __init__(self, name, description=None, speed = 1, capacity = 10):
        super().__init__(name, description)
        self.speed = speed
        self.capacity = capacity
        self.buffer = [None] * self.capacity

    def receive(self, msg):
        if self.buffer[0] is not None:
            raise Exception('%s is full ' % self.name)
        self.buffer[0] = msg

    def changeState(self, ctime):
        if ctime % self.speed == 0:
            outputMsg = self.buffer[self.capacity-1]
            self.buffer.insert(0,self.buffer.pop())
            self.buffer[0] = None 

            if outputMsg is not None:
                for child in self.children:
                    child.receive(outputMsg)   

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

def main():
    print("Starting")
    source = Source("source","warehouse", rate=1, generator = lambda t: {"idx": t})
    c1 = Conveyer("c1","c1", speed = 1, capacity = 2)
    sink = Sink("sink","final sink")


    source.add_child(c1)
    c1.add_child(sink)
    
    for t in range(1,10):
        source.tick(t)
        source.print()


if __name__ == '__main__':
    main()