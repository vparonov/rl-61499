from component import Component

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
