import numpy as np
import matplotlib.pyplot as plt

from utils import plot, getInternalStateAsNumPy, stateAsNumPy
from warehouse import Warehouse
from dataloader import BoxListFromFile
from policies import RLPolicyWithGrad


datafolder = 'data/test'
datafile = 'demo_30.txt'
#datafile = 'b_801_816_1_1_1_10000_20000.txt'
#datafile = 'b_979_116_1_1_1_10000_20000.txt'
#datafile  = 'b_983_49_1_1_1_10000_20000.txt'

#w = Warehouse('test', 'files/wh1_slower_agents.txt', None)
w = Warehouse('test', 'files/wh1.txt', None)

sorted_components = w.getSortedComponents()
sorted_components_dict = {sorted_components[i]: i for i in range(len(sorted_components))}
capacities = np.asarray(w.getCapacities(sorted_components))

policy = RLPolicyWithGrad('models/trained_policy_network.pt')

items = BoxListFromFile(f'{datafolder}/{datafile}')

state, info = w.reset(items)
capacities[-1] = w.nitems

npstate = np.zeros(len(sorted_components))
saliency_map = np.zeros(len(sorted_components))

normalizedState =  np.zeros(len(sorted_components))
fullInternalState = np.zeros(54)

ctime = 0 
while True:

    action = policy(ctime, normalizedState)
    saliency = policy.saliency
    saliency_map = np.vstack((saliency_map, saliency))

    state, reward, terminated, truncated, info = w.step(action)

    normalizedState = stateAsNumPy(state, sorted_components, capacities)
    normalizedState[0] = action 
    npstate = np.vstack((npstate, normalizedState))

    instate = getInternalStateAsNumPy(w.getInternalState(), sorted_components)

    fullInternalState = np.vstack((fullInternalState, instate))

    if terminated:
        print(f'ok, {ctime}')
        break
    elif truncated:
        print(f'failed, {info} {ctime}')
        break 

    ctime += 1

_, ax = plt.subplots(1,1)
#img = ax.imshow(np.log(saliency_map[1:,:]).T, aspect= 'auto', cmap='gist_yarg', interpolation='nearest')
img = ax.imshow(saliency_map[1:,1:-1].T, aspect= 'auto', cmap='gist_yarg', interpolation='nearest')
ax.set_yticks(range(len(sorted_components)-2))
ax.set_yticklabels(sorted_components[1:-1])
plt.xlabel('time step')
plt.ylabel('component')
plt.title('Saliency map / time steps')
plt.colorbar(img)
plt.show()