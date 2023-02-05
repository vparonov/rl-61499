from component import Component

class Sink(Component):
    def __init__(self, name, description=None):
        super().__init__(name, description)
        self.resetState()

    def receive(self, workload):
        self.countReceived += 1
        workload.setFinishTime(self.ctime) 
        self.received.append(workload)  
        if self.ctime > 0:
            pickTime = workload.getPickTime()
            totalProcessingTime = workload.getTotalProcessingTime()
            self.avgPickTime += (pickTime - self.avgPickTime) / (self.countReceived) 
            self.avgTotalProcessingTime += (totalProcessingTime - self.avgTotalProcessingTime) / (self.countReceived) 
        return True 

    def putItem(self, item):
        self.receive(item)

    def changeState(self, ctime):
        self.ctime = ctime  

    def printState(self):
        print('%s -> count=%d' % (self.name, self.countReceived))

    def resetState(self):
        self.countReceived = 0
        self.ctime = 0 
        self.received = []
        self.avgPickTime = 0
        self.avgTotalProcessingTime =0 

    def printAll(self):
        self.printState()
        print('%s -> [' % (self.name), end = '')
        for ix in range(0, len(self.received)): 
            delim = ','
            if ix == len(self.received) - 1:
                delim = ']'    
            if self.received[ix] is not None:
                print(self.received[ix], end = delim)
            else:
                print('()', end = delim)
        print('')

    def getInternalState(self):
        return self.received.copy()