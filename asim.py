from cmath import sin
from os import pread
from tracemalloc import stop
import random
from diverter import Diverter
from source import Source
from sink import Sink
from conveyor import Conveyor
from pickingagent import PickingAgent
from probe import Probe
from box import Box


def genNitems(n):
    def g(ctime):
        if ctime <= n:
            return Box.random()
        else:
            return None 

    return g 

def markAsPicked(station):
    def g(w, ctime):
        w.pickAtS(station) 
    return g 

def main():
    print('------------------')
    test()

def test():
    nitems = 50

    source = Source('source','warehouse', rate=1, generator = genNitems(nitems))
    c1 = Conveyor('c1','c1', delay = 1, capacity =1)
    c2 = Conveyor('c2','c2', delay = 1, capacity =5)
    c3 = Conveyor('c3','c3', delay = 1, capacity =5)
    s01 = Conveyor('s01','s01', delay = 1, capacity = 5)
    ds01 = Diverter('ds01','ds01')
    sink = Sink('sink','sink')
    probe = Probe('all picked probe','', 
        checkerPredicate = lambda workload: workload['AFP01'] != 1 and workload['S01'] != 1)

    aframe = PickingAgent('aframe', 'aframe',  destination=c2, delay=4, 
        stopConveyor=True, 
        markWorkload= markAsPicked('AFP01'), 
        predicate = lambda load: load['AFP01'] == 1)

    s01Picker = PickingAgent(
        's01Picker',
        's01Picker', 
        destination=c2, 
        delay=4,
        markWorkload= markAsPicked('S01'), 
        stopConveyor=False)

    source.connect(c1)
    
    c1.connect(c2)
    c1.add_agent(aframe)

    c2.connect(ds01)
    ds01.connect(
        straightConnection= c3, 
        divertConnection= s01, 
        divertPredicate= lambda load: load['S01'] == 1)
    
    s01.add_agent(s01Picker)

    c3.connect(probe)

    probe.connect(sink)
    #for t in range(1,50):
    t = 1 
    while True:
        source.tick(t)
        source.print()
        t += 1
        if sink.countReceived == nitems:
            break 

    print('Done after %s ticks' % t)
    sink.printAll()

if __name__ == '__main__':
    main()