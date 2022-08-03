from component import Component

class Diverter(Component):  
    def __init__(self, name, description):          
        super().__init__(name, description)
        self.straight = None
        self.divert = None
        self.predicate = None

    def connect(self, straightConnection, divertConnection, divertPredicate):
        self.straight = straightConnection
        self.divert = divertConnection 

        self.add_child(straightConnection)
        self.add_child(divertConnection)

        self.predicate = divertPredicate    

    def receive(self, msg):
        if self.predicate(msg):
            print('%s divert to %s' % (self.name, self.divert.name))
            return self.divert.receive(msg)
        else:
            return self.straight.receive(msg)

    def changeState(self, ctime):
        return True 

    def printState(self):
        pass
