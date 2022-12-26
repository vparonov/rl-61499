from probe import Probe
from state import State

def genUpdateStateFunc(state, componentID):
    def updateState(msg):
        state.update(msg.id, componentID)
        return True 
    return updateState

class StateProbe(Probe):
    def __init__(self, name, description, state, componentID):
        Probe.__init__(self, name, description, checkerPredicate=genUpdateStateFunc(state, componentID))


#tests 
if __name__ == '__main__':
    from source import Source
    from sink import Sink
    from state import State
    from box import Box

    source = Source('test', '', 1, lambda ctime : Box.random()) 
    sink = Sink('test') 
    state = State()

    stateProbe = StateProbe('p1', '', state, 'sink')

    source.connect(stateProbe).connect(sink)

    for i in range(10):
        source.tick(i)
        print(state.get())