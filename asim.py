import matplotlib.pyplot as plt
import matplotlib as mpl
import random 
import numpy as np

from matplotlib import colors
from warehouse import Warehouse
from dataloader import BoxListFromFile

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

def printstate(state, sorted_components):
    print([(c, state.componentsState[c]) for c in sorted_components])

def getInternalStateAsNumPy(internalState, sorted_components) :
    res = []
    for c in sorted_components:
        if c == 'test.source' or c == 'test.sink':
            continue
        res+= [b.id if b != None else 0 for b in internalState[c]]
    return np.asarray(res)

def stateAsNumPy(state, sorted_components, capacities):
    return np.asarray([state.componentsState[c] for c in sorted_components]) / capacities

def itemStateAsNumPy(state, nitems, sorted_components_dict, step):
    itemsState = state.itemsState

    res = np.zeros((nitems, len(sorted_components_dict.keys())))
    for k in itemsState.keys():
        res[k-1, sorted_components_dict[itemsState[k]]] = step
    return res 

def appendNPState(state, sorted_components, capacities, npstate):
    tmp = stateAsNumPy(state, sorted_components, capacities)
    return np.vstack((npstate, tmp))

def saveItemTraceInFile(itemTrace, fileName):
    np.savetxt(fileName, itemTrace, fmt='%.0f', delimiter=',') 

def saveInternalStateInFile(fullInternalState, fileName):
    np.savetxt(fileName, fullInternalState, fmt='%3.0f', delimiter=',') 


def plot(title, npstate, sorted_components):
    cmap = plt.cm.inferno 
    _, ax = plt.subplots(1,1)
    img = ax.imshow(npstate[:,:-1].T, aspect= 'auto', cmap=cmap, interpolation='nearest')
    ax.set_yticks(range(len(sorted_components)-1))
    ax.set_yticklabels(sorted_components[:-1])
    plt.xlabel('time step')
    plt.ylabel('component')
    plt.title(title)
    plt.colorbar(img)
    plt.show()

def resetItems(items):
    for item in items:
        item.reset()

datafolder = 'data'
datafile = 'b_108_686_1_1_1_1000_5000.txt'#'b_2_172_1_1_1_1000_5000.txt'

items = BoxListFromFile(f'{datafolder}/{datafile}')
nitems = len(items)

w = Warehouse('test', 'files/wh1.txt')
sorted_components = w.getSortedComponents()
sorted_components_dict = {sorted_components[i]: i for i in range(len(sorted_components))}
capacities = np.asarray(w.getCapacities(sorted_components))
#w.printStructure()
bursts = range(1, 50, 1)
waits  = range(1, 50, 1)
wb = 1


best_reward = -1000 
best_npstate = None 
best_title = ''

for xx in range(1):
    for ww in waits:
        for b in bursts:
            print(ww, b)
            resetItems(items)
            state, info = w.reset(items)
            policy = HeuristicPolicy(burstSize=b, waitBetweenBoxes= wb, waitBetweenBursts=ww)
            #policy = RandomPolicy(minwait=1, maxwait=5)
            
            npstate = np.zeros(len(sorted_components))
            fullInternalState = np.zeros(54)

            for ctime in range(100000):
                action = policy(ctime, state)
                state, reward, terminated, truncated, info = w.step(action)

                npstate = appendNPState(state, sorted_components, capacities, npstate)
         
                instate = getInternalStateAsNumPy(w.getInternalState(), sorted_components)
        
                fullInternalState = np.vstack((fullInternalState, instate))

                if terminated:
                    if reward > best_reward:
                        best_reward = reward
                        best_title = f'ok. burst size = {b} wait = {ww} finished after {ctime} steps, reward {reward}'
                        best_npstate = npstate.copy()
                    #saveInternalStateInFile(fullInternalState, f'results/internalstate_{datafile}')
                    #plt.imshow(fullInternalState, aspect= 'auto')
                    #plt.show()
                  
                    break
                elif truncated:
                    # print(info)
                    # title = f'failed. burst size = {b} wait = {ww} failed after {ctime} steps, reward {reward}'
                    # plot(title, npstate, sorted_components)
                    # saveInternalStateInFile(fullInternalState, f'results/internalstate_{datafile}')
                    break 

            if not terminated and not truncated:
                title = f'failed. burst size = {b} wait = {ww} failed after {ctime} steps {info}'
                plot(title, npstate, sorted_components)
 

plot(best_title, best_npstate, sorted_components)  
