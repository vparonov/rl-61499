from component import Component

class Probe(Component):  
    def __init__(self, name, description, checkerPredicate=None):          
        super().__init__(name, description)
        self.checkerPredicate = checkerPredicate

    def connect(self, next):
        self.add_child(next)
        return next 

    def receive(self, msg):
        if self.checkerPredicate(msg) == False :
            raise Exception("Probe %s failed with workload = %s" % (self.name, msg))

        return self.children[0].receive(msg)
 
    def changeState(self, ctime):
        return True 

    def printState(self):
        pass

    def resetState(self):
        pass