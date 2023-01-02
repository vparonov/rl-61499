import numpy as np

from utils import getInternalStateAsNumPy, appendNPState, plot
from warehouse import Warehouse
from dataloader import BoxListFromFile
from policies import HeuristicPolicy


datafolder = 'data'
datafile = 'b_154_958_1_1_1_10000_20000.txt'

items = BoxListFromFile(f'{datafolder}/{datafile}')
nitems = len(items)

w = Warehouse('test', 'files/wh1.txt')

sorted_components = w.getSortedComponents()
sorted_components_dict = {sorted_components[i]: i for i in range(len(sorted_components))}
capacities = np.asarray(w.getCapacities(sorted_components))

bursts = range(1, 10, 1)
waits  = range(1, 10, 1)
wb = 1

best_reward = -1000 
best_npstate = None 
best_title = ''

for ww in waits:
    for b in bursts:
        print(ww, b)
        state, info = w.reset(items)
        policy = HeuristicPolicy(burstSize=b, waitBetweenBoxes= wb, waitBetweenBursts=ww)
        #policy = RandomPolicy(minwait=1, maxwait=5)
        
        npstate = np.zeros(len(sorted_components))
        fullInternalState = np.zeros(54)

        #for ctime in range(100000):
        ctime = 0 
        while True:

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
                print(f'failed. burst size = {b} wait = {ww} failed after {ctime} steps, reward {reward}')
                # plot(title, npstate, sorted_components)
                # saveInternalStateInFile(fullInternalState, f'results/internalstate_{datafile}')
                break 

            ctime += 1

plot(best_title, best_npstate, sorted_components)  
