
class Agent(object):   
    def __init__(self, name, description=None) :
        self.name = name
        self.description = description
        self.status = -1 # not defined 
    def act(self, component, ctime):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError