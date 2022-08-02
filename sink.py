from component import Component

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
