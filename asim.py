from source import Source
from sink import Sink
from conveyor import Conveyor
from pickingagent import PickingAgent

def genNitems(n):
    def g(ctime):
        if ctime <= n:
            return {"idx": ctime}
        else:
            return None 

    return g 
def main():
    print("Starting")
    #test1()
    #test2()
    testAFrame()

def test1():
    source = Source("source","warehouse", rate=1, generator = genNitems(10))#lambda t: {"idx": t})
    c1 = Conveyor("c1","c1", delay = 1, capacity = 20)
    c2 = Conveyor("c2","c2", delay = 1, capacity = 5)
    sink = Sink("sink","final sink")
    a1 = PickingAgent("a1","a1", delay = 5, destination=c2)
    a2 = PickingAgent("a2","a2", delay = 5, destination=c2)
    a3 = PickingAgent("a3","a3", delay = 5, destination=c2)

    source.add_child(c1)
    c1.add_agent(a1)
    c1.add_agent(a2)
    c1.add_agent(a3)
    c2.add_child(sink)
    
    for t in range(1,20):
        source.tick(t)
        c2.tick(t) 
        source.print()
        c2.print()

def test2():
    source = Source("source","warehouse", rate=1, generator = genNitems(10))#lambda t: {"idx": t})
    c1 = Conveyor("c1","c1", delay = 1, capacity = 20)
    c2 = Conveyor("c2","c2", delay = 1, capacity = 5)
    sink = Sink("sink","final sink")
    c2.add_child(sink)

    source.add_child(c1)


def testAFrame():
    source = Source("source","warehouse", rate=1, generator = genNitems(10))
    c1 = Conveyor("c1","c1", delay = 1, capacity =1)
    sink = Sink("sink","sink")

    source.add_child(c1)
    c1.add_child(sink)

    for t in range(1,20):
        source.tick(t)
        source.print()

if __name__ == '__main__':
    main()