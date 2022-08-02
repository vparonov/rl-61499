class Agent(object):   
    def __init__(self, name, description=None) :
        self.name = name
        self.description = description
 
    def act(self, component, ctime):
        raise NotImplementedError
