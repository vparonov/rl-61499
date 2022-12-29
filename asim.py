import matplotlib.pyplot as plt
import matplotlib as mpl
import random 
import numpy as np

from matplotlib import colors
from warehouse import Warehouse
from box import Box 



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

def stateAsNumPy(state, sorted_components):
    return np.asarray([state.componentsState[c] for c in sorted_components])

def appendNPState(state, sorted_components, npstate):
    tmp = stateAsNumPy(state, sorted_components)
    return np.vstack((npstate, tmp))


def plot(title, npstate, sorted_components):
    cmap = plt.cm.jet  # define the colormap
    # extract all colors from the .jet map
    cmaplist = [cmap(i) for i in range(cmap.N)]
    # force the first color entry to be grey
    cmaplist[0] = (.5, .5, .5, 1.0)

    # create the new map
    cmap = mpl.colors.LinearSegmentedColormap.from_list(
        'Custom cmap', cmaplist, cmap.N)

    # define the bins and normalize
    bounds = np.linspace(0, 10, 11)
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
    norm = colors.BoundaryNorm(bounds, cmap.N)
    fig, ax = plt.subplots(1,1)
    img = ax.imshow(npstate[:,:-1], aspect= 'auto', cmap=cmap, norm=norm, interpolation='nearest')
    ax.set_xticks(range(len(sorted_components)-1))
    ax.set_xticklabels(sorted_components[:-1])
    plt.xticks(rotation=90)
    plt.ylabel('time step')
    plt.xlabel('component')
    plt.title(title)
    plt.colorbar(img, cmap=cmap, norm=norm, boundaries=bounds, ticks=bounds)
    plt.show()

def resetItems(items):
    for item in items:
        item.reset()

nitems = 100
items = [Box.random() for i in range(nitems)]

w = Warehouse('test', 'files/wh1.txt')
sorted_components = w.getSortedComponents()

#w.printStructure()
bursts = [10, 11]
waits  = [140]
wb = 10

for xx in range(1):
    for ww in waits:
        for b in bursts:
            resetItems(items)
            state, info = w.reset(items)
            policy = HeuristicPolicy(burstSize=b, waitBetweenBoxes= wb, waitBetweenBursts=ww)
            npstate = np.empty(len(sorted_components))

            for ctime in range(10000):
                action = policy(ctime, state)
                state, reward, terminated, truncated, info = w.step(action)

                npstate = appendNPState(state, sorted_components, npstate)
                #if ctime % 100 == 0:
                #    print(reward, ctime, state.componentsState)

                if terminated:
                    title = f'ok. burst size = {b} wait = {ww} finished after {ctime} steps, reward {reward}'
                    plot(title, npstate, sorted_components)                    
                    break
                elif truncated:
                    title = f'failed. burst size = {b} wait = {ww} failed after {ctime} steps, reward {reward}'
                    plot(title, npstate, sorted_components)
                    break 

            if not terminated and not truncated:
                title = f'failed. burst size = {b} wait = {ww} failed after {ctime} steps {info}'
                plot(title, npstate, sorted_components)
            

