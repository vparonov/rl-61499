import random 


class HeuristicPolicy():
    def __init__(self, burstSize=10, waitBetweenBoxes = 10, waitBetweenBursts = 100):
        self.waitBetweenBursts = waitBetweenBursts
        self.waitBetweenBoxes = waitBetweenBoxes
        self.burstSize = burstSize
        self.burstCounter = 0 
        self.waittime = 0
        self.waitbboxes =1 
        self.fifoCount = 0
        self.skipCount = 0 

    def __call__(self, ctime, state):
        if self.waittime == 0:
            if self.burstCounter < self.burstSize:
                if self.waitbboxes == self.waitBetweenBoxes:
                    self.burstCounter += 1
                    #print(ctime, 'fifo', self.burstCounter)
                    self.fifoCount +=1 
                    self.waitbboxes = 1 
                    return 'FIFO'
                else:
                    self.waitbboxes += 1 
            else:
                self.waittime = self.waitBetweenBursts
                self.burstCounter =0
                #print(ctime, 'skip', self.waittime)
        else:            
            self.waittime -= 1
            #print(ctime, 'skip', self.waittime)
        self.skipCount += 1
        return 'SKIP'


class RandomPolicy():
    def __init__(self, minwait, maxwait):
        self.waittime = 0 
        self.waittimes = []
        self.minwait = minwait
        self.maxwait = maxwait

    def __call__(self, ctime, state):
        if self.waittime == 0:
            self.waittime = random.randint(self.minwait, self.maxwait)
            self.waittimes.append(self.waittime) 
            return 'FIFO'
        else:
            self.waittime -= 1
        return 'SKIP'