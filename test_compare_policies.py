import numpy as np
import matplotlib.pyplot as plt

from utils import plot, getInternalStateAsNumPy, stateAsNumPy
from warehouse import Warehouse
from dataloader import BoxListFromFile
from policies import HeuristicPolicy, StateFullHeuristicPolicy, RLPolicy


# def plot(ax, title, npstate, sorted_components):
#     cmap = plt.cm.inferno
#     img = ax.imshow(npstate.T, aspect= 'auto', cmap=cmap, interpolation='nearest')
#     ax.set_yticks(range(len(sorted_components)))
#     ax.set_yticklabels(sorted_components)
#     ax.set_xlabel('time step')
#     ax.set_ylabel('component')
#     ax.set_title(title, fontsize=10)
#     #plt.colorbar(img)

datafolder = 'data/test'
#datafile = 'demo_30.txt'
#datafile = 'b_801_816_1_1_1_10000_20000.txt'
#datafile = 'b_979_116_1_1_1_10000_20000.txt'
datafile  = 'b_983_49_1_1_1_10000_20000.txt'

#w = Warehouse('test', 'files/wh1_slower_agents.txt', None)
w = Warehouse('test', 'files/wh1.txt', None)

sorted_components = w.getSortedComponents()
sorted_components_dict = {sorted_components[i]: i for i in range(len(sorted_components))}
capacities = np.asarray(w.getCapacities(sorted_components))

policies = [
    HeuristicPolicy(burstSize=1, waitBetweenBoxes = 0, waitBetweenBursts=0), 
    HeuristicPolicy(burstSize=5, waitBetweenBoxes = 1, waitBetweenBursts=8), 
    StateFullHeuristicPolicy(coefC1 = 10, coefC2 = 10, fillMargin = 0.4), 
    RLPolicy('models/best.onnx'), 
    RLPolicy('models/trained_policy_network.onnx')
    ]

policy_names = [
    'heuristic 1/0/0',
    'heuristic 5/1/8',
    'C1+C2<0.4', 
    'rl best',
    'latest'
]

sorts = ['iid', '1,2,3', '2,1,3', '3,2,1']
show_plots = False 

summary = np.zeros(shape=(len(policies), 4), dtype=int)

for ix, (policy, policy_name) in enumerate(zip(policies, policy_names)):
    print('------------------------')
    items = BoxListFromFile(f'{datafolder}/{datafile}')
    for sorttype, sorttypestr in enumerate(sorts):
        if sorttype == 1:
            items.sort(reverse=False, key=lambda b: b.route)
        elif sorttype == 2:
            items.sort(reverse=True, key=lambda b: 1 if b.route == 2 else 0 )
        elif sorttype == 3:
            items.sort(reverse=True, key=lambda b: b.route)
            
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
                title = f'OK. T={ctime}, R={reward:.3f} P={policy_name} S={sorttypestr}'
                print(title)
                summary[ix, sorttype] = ctime
                break
                if show_plots:
                    plot(title, npstate, sorted_components)       
                break
            elif truncated:
                title = f'Failed. T={ctime}, R={reward:.3f} P={policy_name} S={sorttypestr}'
                print(title)
                if show_plots:
                    plot(title, npstate, sorted_components)
                break 

            ctime += 1
        

failed_value = int(1.5 * np.max(summary))

summary[summary == 0] = failed_value

fig, ax = plt.subplots()
im = ax.imshow(summary, cmap='inferno_r')

# Show all ticks and label them with the respective list entries
ax.set_yticks(np.arange(len(policy_names)))
ax.set_yticklabels(policy_names)

ax.set_xticks(np.arange(len(sorts)))
ax.set_xticklabels(sorts)

# Loop over data dimensions and create text annotations.
avg = np.mean(summary)

for i in range(len(policy_names)):
    for j in range(len(sorts)):
        v = summary[i, j]
        if v <= avg:
            c = 'k'
        else:
            c = 'w'

        if v == failed_value:
            v = 'F'
    
        text = ax.text(j, i, v,
                       ha='center', va='center', color=c)

ax.set_title(f'Number of steps to solve {datafile}')
fig.tight_layout()
plt.show()
#plt.tight_layout()
#plt.subplots_adjust(top=0.8, wspace=0.3)
#plt.show()
        