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

def getInternalStateAsNumPy(internalState, sorted_components) :
    res = []
    for c in sorted_components:
        if c == 'test.source' or c == 'test.sink':
            continue
        res+= [b.id if b != None else 0 for b in internalState[c]]
    return np.asarray(res)

def stateAsNumPy(state, sorted_components):
    return np.asarray([state.componentsState[c] for c in sorted_components])

def itemStateAsNumPy(state, nitems, sorted_components_dict, step):
    itemsState = state.itemsState

    res = np.zeros((nitems, len(sorted_components_dict.keys())))
    for k in itemsState.keys():
        res[k-1, sorted_components_dict[itemsState[k]]] = step
    return res 

def appendNPState(state, sorted_components, npstate):
    tmp = stateAsNumPy(state, sorted_components)
    return np.vstack((npstate, tmp))

def saveItemTraceInFile(itemTrace, fileName):
    np.savetxt(fileName, itemTrace, fmt='%.0f', delimiter=',') 

def saveInternalStateInFile(fullInternalState, fileName):
    np.savetxt(fileName, fullInternalState, fmt='%3.0f', delimiter=',') 


def plot(title, npstate, sorted_components, max_plot_steps):
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
    #norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
    norm = colors.BoundaryNorm(bounds, cmap.N)
    fig, ax = plt.subplots(1,1)
    img = ax.imshow(npstate[:max_plot_steps,:-1], aspect= 'auto', cmap=cmap, norm=norm, interpolation='nearest')
    ax.set_xticks(range(len(sorted_components)-1))
    ax.set_xticklabels(sorted_components[:-1])
    plt.xticks(rotation=90)
    plt.ylabel('time step')
    plt.xlabel('component')
    plt.title(title)
    plt.colorbar(img, boundaries=bounds, ticks=bounds)
    plt.show()

def resetItems(items):
    for item in items:
        item.reset()

nitems = 100
items = [Box.random() for i in range(nitems)]

w = Warehouse('test', 'files/wh1.txt')
sorted_components = w.getSortedComponents()
sorted_components_dict = {sorted_components[i]: i for i in range(len(sorted_components))}
#w.printStructure()
bursts = [10, 15]
waits  = [40]
wb = 1

itemTrace = np.zeros((100, len(sorted_components_dict.keys())))
fullInternalState = np.zeros(54)
max_plot_steps = 500

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
                itemTrace= np.maximum(itemTrace, itemStateAsNumPy(state, nitems, sorted_components_dict, ctime))

                instate = getInternalStateAsNumPy(w.getInternalState(), sorted_components)
        
                fullInternalState = np.vstack((fullInternalState, instate))

                if terminated:
                    title = f'ok. burst size = {b} wait = {ww} finished after {ctime} steps, reward {reward}'
                    plot(title, npstate, sorted_components, max_plot_steps)  
                    #saveItemTraceInFile(itemTrace, f'files/itemstrace{b}_{ww}_{ctime}.txt')                             
                    
                    saveInternalStateInFile(fullInternalState, f'results/internalstate{b}_{ww}_{ctime}.txt')
                    #plt.imshow(fullInternalState, aspect= 'auto')
                    #plt.show()
                  
                    break
                elif truncated:
                    print(info)
                    title = f'failed. burst size = {b} wait = {ww} failed after {ctime} steps, reward {reward}'
                    plot(title, npstate, sorted_components, max_plot_steps)
                    saveInternalStateInFile(fullInternalState, f'results/internalstate{b}_{ww}_{ctime}.txt')
                    break 

            if not terminated and not truncated:
                title = f'failed. burst size = {b} wait = {ww} failed after {ctime} steps {info}'
                plot(title, npstate, sorted_components, max_plot_steps)
   