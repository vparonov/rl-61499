from tracemalloc import stop
from source import Source
from sink import Sink
from conveyor import Conveyor
from pickingagent import PickingAgent

def genNitems(n):
    def g(ctime):
        if ctime <= n:
            afp01Flag = False
            if ctime % 2 == 0:
                afp01Flag = True

            return {"idx": ctime, "AFP01": afp01Flag} 
        else:
            return None 

    return g 
def main():
    print("------------------")
    testAFrame()

def testAFrame():
    source = Source("source","warehouse", rate=1, generator = genNitems(10))
    c1 = Conveyor("c1","c1", delay = 1, capacity =1)
    sink = Sink("sink","sink")
    aframe = PickingAgent("aframe","aframe",  
        destination=sink, 
        delay=4, 
        stopConveyor=True, 
        predicate = lambda load: load['AFP01'] == True)
    source.add_child(c1)
    c1.add_child(sink)
    c1.add_agent(aframe)

    for t in range(1,20):
        source.tick(t)
        source.print()

if __name__ == '__main__':
    main()