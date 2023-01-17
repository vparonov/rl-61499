class Component(object):
    def __init__(self, name, description=None):
        self.name = name
        self.description = description
        self.children = []
        self.agents = []

    def tick(self, ctime):
        for child in self.children:
            child.tick(ctime)

        for agent in self.agents:  
            agent.act(self, ctime)
        self.changeState(ctime)

    def add_child(self, child):
        self.children.append(child)

    def connect(self, next):
        self.add_child(next)
        return next 

    def add_agent(self, agent):
        self.agents.append(agent)

    def print(self):
        self.printState()
        for child in self.children:
            child.print()

    def getInternalState(self):
        raise NotImplementedError

    def getAgentsStatistics(self):
        countAll = 0 
        countIdle = 0
        countPicking = 0
        countWaiting = 0 
        countOthers = 0

        for a in self.agents:
            a_status = a.status
            countAll += 1
            if a_status == 0:
                countIdle += 1
            elif a_status == 1:
                countPicking += 1
            elif a_status == 2:
                countWaiting += 1
            else:
                countOthers += 1
        return countAll, countIdle, countPicking, countWaiting, countOthers

    def reset(self):
        self.resetState()
        for child in self.children:
            child.reset()

        for agent in self.agents:  
            agent.reset()    

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

    def resetState(self):
        raise NotImplementedError

    def getItem(self):
        raise NotImplementedError

    def putItem(self, item):
        raise NotImplementedError

    