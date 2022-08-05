class Component(object):
    def __init__(self, name, description=None):
        self.name = name
        self.description = description
        self.children = []
        self.agents = []

    def add_child(self, child):
        self.children.append(child)

    def connect(self, next):
        self.add_child(next)

    def add_agent(self, agent):
        self.agents.append(agent)

    def print(self):
        self.printState()
        for child in self.children:
            child.print()

    def receive(self, msg):
        raise NotImplementedError

    def start(self):
        raise NotImplementedError
    
    def stop(self):
        raise NotImplementedError

    def changeState(self, ctime):
        raise NotImplementedError

    def printState(self):
        raise NotImplementedError

    def getItem(self):
        raise NotImplementedError

    def putItem(self, item):
        raise NotImplementedError

    def tick(self, ctime):
        for child in self.children:
            child.tick(ctime)

        for agent in self.agents:  
            agent.act(self, ctime)
        self.changeState(ctime)
