from os import pread
from tracemalloc import stop
from diverter import Diverter
from source import Source
from sink import Sink
from conveyor import Conveyor
from pickingagent import PickingAgent

def genNitems(n):
    def g(ctime):
        if ctime <= n:
            afp01Flag = 0
            if ctime % 2 == 0:
                afp01Flag = 1

            return {'idx': ctime, 'AFP01': afp01Flag, 'S01':1 } 
        else:
            return None 

    return g 

def markAsPicked(station):
    def g(w, ctime):
        w[station] = 2 
    return g 

def main():
    print('------------------')
    testAFrame()

def testAFrame():
    source = Source('source','warehouse', rate=1, generator = genNitems(1))
    c1 = Conveyor('c1','c1', delay = 1, capacity =1)
    c2 = Conveyor('c2','c2', delay = 1, capacity =5)
    c3 = Conveyor('c3','c3', delay = 1, capacity =5)
    s01 = Conveyor('s01','s01', delay = 1, capacity = 5)
    ds01 = Diverter('ds01','ds01')
    sink = Sink('sink','sink')
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

    c3.connect(sink)
    for t in range(1,20):
        source.tick(t)
        source.print()

if __name__ == '__main__':
    main()