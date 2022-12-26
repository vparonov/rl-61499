import matplotlib.pyplot as plt
from warehouse import Warehouse
from box import Box 


def policy(ctime, state):
    if ctime % 40 == 0:
        #print(ctime, 'fifo')
        return 'FIFO'
    else:
        #print(ctime, 'skip')
        return 'SKIP'

nitems = 100
items = [Box.random() for i in range(nitems)]

w = Warehouse('test', 'files/wh1.txt')

w.printStructure()
state, info = w.reset(items)

for ctime in range(10000):
    action = policy(ctime, state)
    state, reward, terminated, truncated, info = w.step(action)

    if ctime % 100 == 0:
        print(reward, ctime, state.componentsState)

    if terminated:
        print(f'finished in {ctime} steps')
        print(reward, state.itemsState, state.componentsState)
        break
    elif truncated:
        print(f'failed in {ctime} steps {info}')
        print(reward, state.itemsState, state.componentsState)
        break 
