import matplotlib.pyplot as plt
from warehouse import Warehouse
from box import Box 
import random 


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

def printstate(state, w):
    sorted_components = w.getSortedComponents()
    print([(c, state.componentsState[c]) for c in sorted_components])


nitems = 100
items = [Box.random() for i in range(nitems)]

w = Warehouse('test', 'files/wh1.txt')

#w.printStructure()
bursts = [8, 9, 10]
waits  = [28, 30, 32, 34, 35]
for xx in range(1):
    for b in bursts:
        for ww in waits:
            state, info = w.reset(items)
            policy = HeuristicPolicy(burstSize=b, waitBetweenBursts=ww)

            for ctime in range(10000):
                action = policy(ctime, state)
                state, reward, terminated, truncated, info = w.step(action)

                #if ctime % 100 == 0:
                #    print(reward, ctime, state.componentsState)

                if terminated:
                    print(f'burst size = {b} wait = {ww} finished in {ctime} steps')
                    print(reward)
                    printstate(state, w)
                    break
                elif truncated:
                    print(f'burst size = {b} wait = {ww} failed in {ctime} steps {info}')
                    print(reward)
                    printstate(state, w)
                    break 

            if not terminated and not truncated:
                print(f'burst size = {b} wait = {ww} failed in {ctime} steps {info}')
                print(reward)
                printstate(state, w)

