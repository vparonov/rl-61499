import numpy as np

from utils import getInternalStateAsNumPy, stateAsNumPy, plot
from warehouse import Warehouse
from dataloader import BoxListFromFile
from policies import StateFullHeuristicPolicy, RLPolicy


datafolder = 'data/test'
#datafile = 'b_801_816_1_1_1_10000_20000.txt'
datafile = 'b_979_116_1_1_1_10000_20000.txt'

items = BoxListFromFile(f'{datafolder}/{datafile}')
items.sort(reverse=False, key=lambda b: b.route)

#w = Warehouse('test', 'files/wh1_slower_agents.txt', None)
w = Warehouse('test', 'files/wh1.txt', None)

sorted_components = w.getSortedComponents()
sorted_components_dict = {sorted_components[i]: i for i in range(len(sorted_components))}
capacities = np.asarray(w.getCapacities(sorted_components))

policies = [
    StateFullHeuristicPolicy(coefC1 = 10, coefC2 = 10, fillMargin = 0.4), 
    RLPolicy('models/best.onnx'), 
    RLPolicy('models/trained_policy_network.onnx'),
    ]

for policy in policies:
    state, info = w.reset(items)
    capacities[-1] = w.nitems
    
    npstate = np.zeros(len(sorted_components))
    normalizedState =  np.zeros(len(sorted_components))
    fullInternalState = np.zeros(54)

    ctime = 0 
    while True:

        action = policy(ctime, normalizedState)
        state, reward, terminated, truncated, info = w.step(action)

        normalizedState = stateAsNumPy(state, sorted_components, capacities)
        normalizedState[0] = action 
        npstate = np.vstack((npstate, normalizedState))
    
        instate = getInternalStateAsNumPy(w.getInternalState(), sorted_components)

        fullInternalState = np.vstack((fullInternalState, instate))

        if terminated:
            title = f'ok. finished after {ctime} steps, reward {reward}'
            print(title)
            plot(title, npstate, sorted_components)       
            break
        elif truncated:
            title = f'failed.{info},  failed after {ctime} steps, reward {reward}'
            print(title)
            plot(title, npstate, sorted_components)
            break 

        ctime += 1

    