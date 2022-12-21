from conveyor import Conveyor


class Diverter(Conveyor):
    def __init__(self, name, divertPredicate, description=None, delay = 1):
        super().__init__(name = name, description= description, delay=delay, capacity=1)
        self.divertPredicate = divertPredicate

    def connect(self, straightConnection, divertConnection):
        super().connect(straightConnection)
        super().connect(divertConnection)
        return straightConnection

    def changeState(self, ctime):
        outputMsg = self.buffer[self.capacity-1]
        if outputMsg is not None:
            if self.divertPredicate(outputMsg):
                self.setActiveChildID(1) # divert
            else:
                self.setActiveChildID(0) # straight

        return super().changeState(ctime)

if __name__ == '__main__':
    from source import Source 
    from sink import Sink 
    from box import Box

    def genNitems(n):
        def g(ctime):
            if ctime <= n:
                return Box.random()
            else:
                return None 

        return g 

    nitems = 2
    source = Source('source','warehouse', delay=1, generator = genNitems(nitems))
    sink = Sink('sink','sink')
    sink2 = Sink('sink2','sink')
    diverter = Diverter('diverter', lambda load: load.isForStationS('A')) 

    source.connect(diverter).\
        connect(straightConnection=sink, divertConnection=sink2)

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
        if t == 40:
            break  
        #if sink.countReceived == nitems:
        #    break 
    if not gotError:
        print('Done after %d ticks' % t)
        sink.printAll()
    else:
        print('Failed at tick %d ' % t)      


