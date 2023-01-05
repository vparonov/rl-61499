import numpy as np
import glob
import matplotlib.pyplot as plt

from utils import getInternalStateAsNumPy, stateAsNumPy, plot
from warehouse import Warehouse
from dataloader import BoxListFromFile
from policies import RLPolicy


datafolder = 'data/test'

w = Warehouse('test', 'files/wh1.txt', None)

sorted_components = w.getSortedComponents()
sorted_components_dict = {sorted_components[i]: i for i in range(len(sorted_components))}
capacities = np.asarray(w.getCapacities(sorted_components))

bursts = range(5, 6, 1)
waits  = range(8, 9, 1)
wb = 1

best_reward = -1000 
best_npstate = None 
best_title = ''

ww = 8
b = 5

cfiles = 0

x = []
y = []
fail_x = []
fail_y = []

#policy = HeuristicPolicy(burstSize=b, waitBetweenBoxes= wb, waitBetweenBursts=ww)
policy = RLPolicy('models/trained_policy_network.onnx')

for datafile in glob.glob(f'{datafolder}/*.txt'):

    items = BoxListFromFile(datafile)
    nitems = len(items)
    state, info = w.reset(items)
    #policy = RandomPolicy(minwait=1, maxwait=5)
    
    npstate = np.zeros(len(sorted_components))
    normalizedState =  np.zeros(len(sorted_components))

    fullInternalState = np.zeros(54)

    #for ctime in range(100000):
    ctime = 0 
    while True:

        action = policy(ctime, normalizedState)
        state, reward, terminated, truncated, info = w.step(action)

        normalizedState = stateAsNumPy(state, sorted_components, capacities)
        normalizedState[-1] = 0

        npstate = np.vstack((npstate, normalizedState))
     
        instate = getInternalStateAsNumPy(w.getInternalState(), sorted_components)

        fullInternalState = np.vstack((fullInternalState, instate))

        if terminated:
            title = f'ok.{datafile}, items = {len(items)}, burst size = {b} wait = {ww} finished after {ctime} steps, reward {reward}'
            print(title)
            x.append(len(items))
            y.append(ctime)
            #plot(title, npstate, sorted_components)         
            break
        elif truncated:
            print(f'failed. {datafile}, items = {len(items)},burst size = {b} wait = {ww} failed after {ctime} steps, reward {reward}')
            fail_x.append(len(items))
            fail_y.append(ctime)
            break 

        ctime += 1

    cfiles += 1 
    #if cfiles == 10:
    #    break
    

plt.scatter(x, y, label='ok')
plt.scatter(fail_x, fail_y, label = 'failed')
plt.xlabel('n items')
plt.ylabel('time steps')
plt.show()