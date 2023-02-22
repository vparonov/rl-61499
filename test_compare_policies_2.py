import numpy as np
import matplotlib.pyplot as plt
import math 
from utils import plot, getInternalStateAsNumPy, stateAsNumPy
from warehouse import Warehouse
from dataloader import BoxListFromFile
from policies import HeuristicPolicy, StateFullHeuristicPolicy, RLPolicy


def save_items_statistics(items, file):
    nitems = len(items)
    stats1 = np.asarray([items[i].startTime for i in range(len(items))]).reshape(nitems, 1)
    stats2 = np.asarray([items[i].finishTime for i in range(len(items))]).reshape(nitems, 1)
    stats = np.hstack((stats1, stats2))
    np.save(file, stats)
    #print(f'min={np.min(processing_times)}, max={np.max(processing_times)}, mean={np.mean(processing_times)}, std={np.std(processing_times)}')

datafolder = 'data/eval'
datafiles = [
    '1_001box.txt',    
    '2_003boxes.txt',  
    '3_030boxes.txt',  
    '4_049boxes.txt',  
    '5_116boxes.txt',  
    '6_816boxes.txt'
]

#w = Warehouse('test', 'files/wh1.txt', None)
#w = Warehouse('test', 'files/wh1_deterministic_pickers.txt', None)
#w = Warehouse('test', 'files/wh1_slower_agents.txt', None)
w = Warehouse('test', 'files/wh1_combined_agents_p5_q50.txt', None)
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
#    HeuristicPolicy(burstSize=5, waitBetweenBoxes = 1, waitBetweenBursts=8), 
    StateFullHeuristicPolicy(coefC1 = 10, coefC2 = 10, fillMargin = 0.4), 
#    RLPolicy('models/best-old-reward-function.onnx'), 
#    RLPolicy('models/best.onnx'), 
    #RLPolicy('models/best_robust_target.onnx'),
    #RLPolicy('models/best_robust_min_processing_time.onnx'),
    #RLPolicy('models/trained_policy_network_400.onnx'),
    RLPolicy('models/trained_policy_network_500.onnx')
    ]

policy_names = [
    'heuristic_1_0_0',
#    'heuristic_5_1_8',
    'C1C2_0.4', 
#    'rl_old_RF',
#    'rl_best',
    #'latest_robust',
    #'min-per-item',
    #'latest 400 ep',
    'RL_Best'
]

sorts = ['iid', '1,2,3', '2,1,3', '3,2,1']

show_plots = True  


#fig.set_size_inches(5, 5)

for datafile in datafiles:

    summary = np.zeros(shape=(len(policies), 4), dtype=int)
    summary_avg_total = np.zeros(shape=(len(policies), 4), dtype=float)
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
                
            state, remaining_items, actions_mask = w.reset(items)
            capacities[-1] = w.nitems
            
            npstate = np.zeros(len(sorted_components))
            normalizedState =  np.zeros(len(sorted_components))
            fullInternalState = np.zeros(54)

            ctime = 0 
            while True:

                action = policy(ctime, normalizedState, remaining_items)
                state, reward, terminated, truncated, (info, remaining_items, actions_mask, avgPickTime) = w.step(action)
                #print(ctime, reward, terminated, truncated)
                normalizedState = stateAsNumPy(state, sorted_components, capacities)
                normalizedState[0] = action 
                npstate = np.vstack((npstate, normalizedState))
            
                instate = getInternalStateAsNumPy(w.getInternalState(), sorted_components)

                fullInternalState = np.vstack((fullInternalState, instate))

                if terminated:
                    title = f'OK. T={ctime}, R={reward:.3f} P={policy_name} S={sorttypestr}'
                    print(title)
                    summary[ix, sorttype] = avgPickTime
                    summary_avg_total[ix, sorttype] = (1.0 * ctime) /len(items)
                    np.save(f'vis/full_state_{policy_name}_{sorttypestr}', fullInternalState)
                    if show_plots:
                        plot_title = f'F={datafile}_S={sorttypestr}_P={policy_name}_OK_T={ctime}_R={reward:.3f}'
                        plot(plot_title, npstate, sorted_components)  
                    save_items_statistics(items, f'vis/item_stats_{datafile}_{policy_name}_{sorttypestr}')     
                    break
                    
                elif truncated:
                    title = f'Failed. {info} T={ctime}, R={reward:.3f} P={policy_name} S={sorttypestr}'
                    print(title)
                    if show_plots:
                        plot_title = f'F={datafile}_S={sorttypestr}_P={policy_name}_Failed_T={ctime}_R={reward:.3f}'
                        plot(plot_title, npstate, sorted_components)
                    break 

                ctime += 1
            

    

