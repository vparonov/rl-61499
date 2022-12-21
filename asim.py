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

def markAsPicked(stations):
    def g(w, ctime):
        for station in stations:
            w.pickAtS(station) 
    return g 

def main():
    print('------------------')
    simple_test()
    #test()


def simple_test():
    nitems = 30
    source = Source('source',delay=1, generator = genNitems(nitems))
    c11 = Conveyor('c1.1',delay = 1, capacity =20)
    s01 = Conveyor('s01',delay = 1, capacity = 10)
    ds01 = Diverter('ds01',divertPredicate= lambda load: load.isForStationS('A'))
 
    sink = Sink('sink','sink')
     
    source.\
        connect(c11).\
        connect(ds01).\
        connect(
            straightConnection= sink, 
            divertConnection= s01)
    t = 1 
    gotError = False
    while True:
        try:
            source.tick(t)
        except Exception as e:
            gotError = True  
            print(e)
            source.print()
            break
        #if t % 1000 == 0:
        source.print()
        t += 1
        #if t == 40:
        #    break  
        if sink.countReceived == nitems:
           break 
    if not gotError:
        print('Done after %d ticks' % t)
        sink.printAll()
    else:
        print('Failed at tick %d ' % t)      


def test():
    nitems = 2

    source = Source('source','warehouse', delay=100, generator = genNitems(nitems))
    c11 = Conveyor('c1.1','c1.1', delay = 1, capacity =2)
    c12 = Conveyor('c1.2','c1.2', delay = 1, capacity =3)
    c13 = Conveyor('c1.3','c1.3', delay = 1, capacity =5)
    c2 = Conveyor('c2','c2', delay = 1, capacity =10)
    c3 = Conveyor('c3','c3', delay = 1, capacity =2)
    s01 = Conveyor('s01','s01', delay = 1, capacity = 10)
    s02 = Conveyor('s02','s02', delay = 1, capacity = 10)
    ds01 = Diverter('ds01','ds01')
    ds02 = Diverter('ds02','ds02')

    sink = Sink('sink','sink')
    probe = Probe('all picked probe','', 
        checkerPredicate = lambda workload: workload.pickingFinished())

    ns01Pickers = 1
    for i in range(ns01Pickers):
        s01.add_agent(PickingAgent(
            's01-%2.2dPicker'%(i+1),
            's01-%2.2dPicker'%(i+1), 
            destination=c2, 
            delay=10,
            markWorkload= markAsPicked(['1']), 
            stopConveyor=False, 
            maxBlockedTime= 200))

    ns02Pickers = 1
    for i in range(ns02Pickers):
        s02.add_agent(PickingAgent(
            's02-%2.2dPicker'%(i+1),
            's02-%2.2dPicker'%(i+1), 
            destination=c2, 
            delay=10,
            markWorkload= markAsPicked(['2']), 
            stopConveyor=False, 
            maxBlockedTime= 200))
   
    source.\
        connect(c11).\
        connect(c12).\
        connect(c13).\
        connect(c2).\
        connect(ds01).\
        connect(
            straightConnection= ds02, 
            divertConnection= s01, 
            divertPredicate= lambda load: load.isForStationS('A')).\
        connect(
            straightConnection=c3,
            divertConnection=s02,
            divertPredicate= lambda load: load.isForStationS('C')).\
        connect(probe).\
        connect(sink)
 
    t = 1 
    gotError = False
    while True:
        try:
            source.tick(t)
        except Exception as e:
            gotError = True  
            print(e)
            source.print()
            break
        if t % 1000 == 0:
            source.print()
        #source.print()
        t += 1
        if sink.countReceived == nitems:
            break 
    if not gotError:
        print('Done after %d ticks' % t)
        sink.printAll()
    else:
        print('Failed at tick %d ' % t)
if __name__ == '__main__':
    main()