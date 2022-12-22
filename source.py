from component import Component

class Source(Component):
    def __init__(self, name, description=None, delay = 1, generator = None) :
        super().__init__(name, description)
        self.delay = delay
        self.generator = generator
        self.resetState()
        
    def changeState(self, ctime):
        if ctime % self.delay == 0 :
            for child in self.children:
                if child.receive(self.generator(self.idx+1)) == True:
                    self.idx = self.idx + 1
    def resetState(self):
        self.idx = 0
            
    def printState(self):
        print('%s -> %d' % (self.name, self.idx))
