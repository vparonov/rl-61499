import numpy as np
import matplotlib.pyplot as plt
import math 
from utils import plot, getInternalStateAsNumPy, stateAsNumPy
from warehouse import Warehouse
from dataloader import BoxListFromFile
from policies import HeuristicPolicy, StateFullHeuristicPolicy, RLPolicy

datafolder = 'data/test'
datafiles = [
    'demo1_3.txt',
    'demo3.txt',
    'demo_30.txt',
    'b_983_49_1_1_1_10000_20000.txt',
    'b_979_116_1_1_1_10000_20000.txt',
    'b_801_816_1_1_1_10000_20000.txt'
]

w = Warehouse('test', 'files/wh1.txt', None)
#w = Warehouse('test', 'files/wh1_deterministic_pickers.txt', None)
#w = Warehouse('test', 'files/wh1_slower_agents.txt', None)
#w = Warehouse('test', 'files/wh1_combined_agents_p5_q50.txt', None)
#w = Warehouse('test', 'files/wh1_combined_agents_p50_q5.txt', None)
#w = Warehouse('test', 'files/wh1_faster_agents.txt', None)
#w = Warehouse('test', 'files/wh1_even_slower_agents.txt', None)

sorted_components = w.getSortedComponents()
sorted_components_dict = {sorted_components[i]: i for i in range(len(sorted_components))}
capacities = np.asarray(w.getCapacities(sorted_components))

#uncomment to see the not normalized heatmap
#capacities = np.ones(capacities.shape)

policies = [
    HeuristicPolicy(burstSize=1, waitBetweenBoxes = 0, waitBetweenBursts=0), 
    HeuristicPolicy(burstSize=5, waitBetweenBoxes = 1, waitBetweenBursts=8), 
    StateFullHeuristicPolicy(coefC1 = 10, coefC2 = 10, fillMargin = 0.4), 
    RLPolicy('models/best-old-reward-function.onnx'), 
    RLPolicy('models/best.onnx'), 
    RLPolicy('models/trained_target_policy_network.onnx')
    ]

policy_names = [
    'heuristic_1_0_0',
    'heuristic_5_1_8',
    'C1C20.4', 
    'rl_old_RF',
    'rl_best',
    'latest'
]

sorts = ['iid', '1,2,3', '2,1,3', '3,2,1']

show_plots = False  


plt.rc('font', size=8) 
plt.rcParams["figure.figsize"] = [8, 8]
plt.rcParams["figure.autolayout"] = True

nxplots = int(math.sqrt(len(datafiles)))
nyplots = len(datafiles) - nxplots

fig, axes = plt.subplots(nxplots, nyplots, sharex=True, sharey=True, constrained_layout=True)
#fig.set_size_inches(5, 5)

for ax in axes.flat:
    ax.set_visible(False)

for ax, datafile in zip(axes.flat, datafiles):
    ax.set_visible(True)
    summary = np.zeros(shape=(len(policies), 4), dtype=int)
    for ix, (policy, policy_name) in enumerate(zip(policies, policy_names)):
        print('---s---------------------')
        items = BoxListFromFile(f'{datafolder}/{datafile}')
        for sorttype, sorttypestr in enumerate(sorts):
            if sorttype == 1:
                items.sort(reverse=False, key=lambda b: b.route)
            elif sorttype == 2:
                items.sort(reverse=True, key=lambda b: 1 if b.route == 2 else 0 )
            elif sorttype == 3:
                items.sort(reverse=True, key=lambda b: b.route)
                
            state, remaining_items = w.reset(items)
            capacities[-1] = w.nitems
            
            npstate = np.zeros(len(sorted_components))
            normalizedState =  np.zeros(len(sorted_components))
            fullInternalState = np.zeros(54)

            ctime = 0 
            while True:

                action = policy(ctime, normalizedState, remaining_items)
                state, reward, terminated, truncated, (info, remaining_items) = w.step(action)

                normalizedState = stateAsNumPy(state, sorted_components, capacities)
                normalizedState[0] = action 
                npstate = np.vstack((npstate, normalizedState))
            
                instate = getInternalStateAsNumPy(w.getInternalState(), sorted_components)

                fullInternalState = np.vstack((fullInternalState, instate))

                if terminated:
                    title = f'OK. T={ctime}, R={reward:.3f} P={policy_name} S={sorttypestr}'
                    print(title)
                    summary[ix, sorttype] = ctime
                    np.save(f'vis/full_state_{policy_name}_{sorttypestr}', fullInternalState)
                    if show_plots:
                        plot(title, npstate, sorted_components)       
                    break
                elif truncated:
                    title = f'Failed. {info} T={ctime}, R={reward:.3f} P={policy_name} S={sorttypestr}'
                    print(title)
                    if show_plots:
                        plot(title, npstate, sorted_components)
                    break 

                ctime += 1
            

    failed_value = int(1.5 * np.max(summary))

    summary[summary == 0] = failed_value

    #fig, ax = plt.subplots()
    im = ax.imshow(summary, cmap='inferno_r')

    # Show all ticks and label them with the respective list entries
    ax.set_yticks(np.arange(len(policy_names)))
    ax.set_yticklabels(policy_names)

    ax.set_xticks(np.arange(len(sorts)))
    ax.set_xticklabels(sorts)

    # Loop over data dimensions and create text annotations.
    avg = np.mean(summary)

    nitems = len(items)

    for i in range(len(policy_names)):
        for j in range(len(sorts)):
            v = summary[i, j]
            if v <= avg:
                c = 'k'
            else:
                c = 'w'

            if v == failed_value:
                v = 'F'
            else:
                v /= nitems
                v = f'{v:.3f}'
        
            text = ax.text(j, i, v,
                        ha='center', va='center', color=c)

    ax.set_title(f'{datafile}')


#fig.tight_layout()
#lt.show()
plt.tight_layout()
plt.show()
        