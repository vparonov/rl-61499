import matplotlib.pyplot as plt
import numpy as np 

def getInternalStateAsNumPy(internalState, sorted_components) :
    res = []
    for c in sorted_components:
        if c == 'test.source' or c == 'test.sink':
            continue
        res+= [b.id if b != None else 0 for b in internalState[c]]
    return np.asarray(res)

def appendNPState(state, sorted_components, capacities, npstate):
    tmp = stateAsNumPy(state, sorted_components, capacities)
    return np.vstack((npstate, tmp))

def plot(title, npstate, sorted_components):
    cmap = plt.cm.inferno 
    _, ax = plt.subplots(1,1)
    img = ax.imshow(npstate.T, aspect= 'auto', cmap=cmap, interpolation='nearest')
    ax.set_yticks(range(len(sorted_components)))
    ax.set_yticklabels(sorted_components)
    plt.xlabel('time step')
    plt.ylabel('component')
    plt.title(title)
    plt.colorbar(img)
    plt.show()

#internal functions 

def stateAsNumPy(state, sorted_components, capacities):
    return np.asarray([state.componentsState[c] for c in sorted_components]) / capacities
