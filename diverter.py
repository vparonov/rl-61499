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
        self.predicate = divertPredicate    

    def receive(self, msg):
        if self.predicate(msg):
            return self.divert.receive(msg)
        else:
            return self.straight.receive(msg)
