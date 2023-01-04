import numpy as np

from utils import getInternalStateAsNumPy, stateAsNumPy, plot
from warehouse import Warehouse
from dataloader import BoxListFromFile
from policies import StateFullHeuristicPolicy


#datafolder = 'data/train'
#datafile = 'b_4_808_1_1_1_10000_20000.txt'#'b_979_116_1_1_1_10000_20000.txt'

#items = BoxListFromFile(f'{datafolder}/{datafile}')
#items.sort(reverse=True, key=lambda b: b.route)

w = Warehouse('test', 'files/wh1.txt', 'data/train')

sorted_components = w.getSortedComponents()
sorted_components_dict = {sorted_components[i]: i for i in range(len(sorted_components))}
capacities = np.asarray(w.getCapacities(sorted_components))

best_reward = -1000 
best_npstate = None 
best_title = ''

for fillFactor in [0.1, 0.2, 0.3, 0.40, 0.5, 0.6]:
    state, info = w.reset()
    policy = StateFullHeuristicPolicy(coefC1 = 10, coefC2 = 10, fillMargin = fillFactor)
    
    npstate = np.zeros(len(sorted_components))
    normalizedState =  np.zeros(len(sorted_components))
    fullInternalState = np.zeros(54)

    ctime = 0 
    while True:

        action = policy(ctime, normalizedState)
        state, reward, terminated, truncated, info = w.step(action)

        normalizedState = stateAsNumPy(state, sorted_components, capacities)
        npstate = np.vstack((npstate, normalizedState))
    
        instate = getInternalStateAsNumPy(w.getInternalState(), sorted_components)

        fullInternalState = np.vstack((fullInternalState, instate))

        if terminated:
            title = f'ok. fillFactor = {fillFactor} finished after {ctime} steps, reward {reward}'
            print(title)
            if reward > best_reward:
                best_reward = reward
                best_title = title
                best_npstate = npstate.copy()  
            break
        elif truncated:
            title = f'failed.{info}, fillFactor = {fillFactor} failed after {ctime} steps, reward {reward}'
            print(title)
            plot(title, npstate, sorted_components)
            break 

        ctime += 1

plot(best_title, best_npstate, sorted_components)       
