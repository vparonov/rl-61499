from component import Component

class Sink(Component):
    def __init__(self, name, description=None):
        super().__init__(name, description)
        self.countReceived = 0
        self.ctime = 0 
        self.received = []

    def receive(self, msg):
        self.countReceived += 1
        msg['ft'] = self.ctime 
        self.received.append(msg)   

    def putItem(self, item):
        self.receive(item)

    def changeState(self, ctime):
        self.ctime = ctime  

    def printState(self):
        print('%s -> count=%d' % (self.name, self.countReceived))

    def printAll(self):
        self.printState()
        print('%s -> %s' % (self.name, self.received))