import numpy as np
import glob
import matplotlib.pyplot as plt

from utils import getInternalStateAsNumPy, stateAsNumPy, plot
from warehouse import Warehouse
from dataloader import BoxListFromFile
from policies import RLPolicy


datafolder = 'data/test'

w = Warehouse('test', 'files/wh1.txt', None)
#w = Warehouse('test', 'files/wh1_combined_agents_p5_q50.txt', None)
#w = Warehouse('test', 'files/wh1_combined_agents_p50_q5.txt', None)
#w = Warehouse('test', 'files/wh1_combined_agents_p50_q15.txt', None)
#w = Warehouse('test', 'files/wh1_faster_agents.txt', None)
#w = Warehouse('test', 'files/wh1_slower_agents.txt', None)
#w = Warehouse('test', 'files/wh1_even_slower_agents.txt', None)

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
avg_y = {}
y = []
fail_x = []
fail_y = []

#policy = HeuristicPolicy(burstSize=b, waitBetweenBoxes= wb, waitBetweenBursts=ww)
policy = RLPolicy('models/trained_policy_network.onnx')

avg = np.zeros(1000)

for datafile in glob.glob(f'{datafolder}/*.txt'):

    items = BoxListFromFile(datafile)
    #items.sort(reverse=False, key=lambda b: b.route)
    #items.sort(reverse=True, key=lambda b: b.route)
    items.sort(reverse=False, key=lambda b: 1 if b.route == 2 else 0 )
    
    nitems = len(items)
    state, info, _ = w.reset(items)
    #policy = RandomPolicy(minwait=1, maxwait=5)
    npstate = np.zeros(len(sorted_components))
    normalizedState =  np.zeros(len(sorted_components))

    fullInternalState = np.zeros(54)

    #for ctime in range(100000):
    ctime = 0 
    remaining_items = nitems 
    while True:

        action = policy(ctime, normalizedState, remaining_items)
        state, reward, terminated, truncated, (info, remaining_items, actions_mask, avgPickTime)  = w.step(action)

        normalizedState = stateAsNumPy(state, sorted_components, capacities)
        normalizedState[-1] = 0

        npstate = np.vstack((npstate, normalizedState))
     
        instate = getInternalStateAsNumPy(w.getInternalState(), sorted_components)

        fullInternalState = np.vstack((fullInternalState, instate))

        if terminated:
            title = f'ok.{datafile}, items = {len(items)}, finished after {ctime} steps, avg {ctime/len(items)}steps per item reward {reward}'
            print(title)
            x.append(len(items))
            
            y.append(ctime)
            avg[nitems] = ctime/len(items)
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


plt.plot(range(1000), avg, label='ok')
plt.xlabel('n items')
plt.ylabel('steps per item')
plt.show()
