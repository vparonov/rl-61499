from source import Source 
from sink import Sink 
from pickingagent import PickingAgent
from conveyor import Conveyor
from diverter import Diverter

class Warehouse:
    def __init__(self, name, fileName):
        self.name = name
        self.source = Source(name + '.source', '', 1, None) 
        self.components = {'__sink__': Sink(name + '.sink', '')}
        self.firstComponent = None
        self.build(fileName)
  
    def build(self, fileName):
        state = 0 
        with open(fileName) as f:
            while True:
                s = f.readline().strip()
                if s == "":
                    break 
                if s[0] == "#":
                    continue

                if s == "begin structure":
                    state = 1
                    continue
                elif s == "begin connections":
                    state = 2
                    continue
                elif s == "begin agents":
                    state = 3
                    continue
                if s[0:3] == "end":
                    state = 0
                    continue 

                if state == 1:
                    self.addStructure(s)
                elif state == 2:
                    self.addConnection(s)
                elif state == 3:
                    self.addAgent(s)
  
    def run(self, maxTicks, itemsToPick, strategy, printEvery=1):
        self.itemsToPick = itemsToPick 
        self.source.reset()
        self.source.generator = lambda ctime : strategy(ctime, self.itemsToPick)

        nitems = len(itemsToPick)
        t = 1 
        gotError = False
        while True:
            try:
                self.source.tick(t)
            except Exception as e:
                gotError = True
                if printEvery > 0:  
                    print(e)
                    self.source.print()
                break
            if printEvery > 0 and t % printEvery == 0:
                self.source.print()
            t += 1
            if self.components['__sink__'].countReceived == nitems:
                break 
            if maxTicks >= 0 and t == maxTicks:
                break 
        
        retVal = True 
        if not gotError:
            if printEvery > 0:
                print('Done after %d ticks' % t)
                self.components['__sink__'].printAll()
        else:
            retVal = False
            if printEvery > 0:
                print('Failed at tick %d ' % t)

        return retVal, t

    def addStructure(self, s):
        if s[0] == 'c' or s[0] == 's':
            name, p1, p2 = [_s.strip() for _s in s.split(',')]
            item = Conveyor(name, '', delay=int(p1), capacity=int(p2))
        elif s[0] == 'd':
            name, p1 = [_s.strip() for _s in s.split(',')]
            item = Diverter(name, divertPredicate=lambda load: load.isForStationS(p1))
        else:
            raise Exception('Unknow component type %s' % name)

        self.components[name] = item
    
    def addConnection(self, s):
        connections = s.split('->')

        next = self.components['__sink__']
        for ix in range(len(connections)-1, -1, -1):
            c_name = connections[ix]
            if c_name[0] == 'd':
                name, dname = c_name.split('!')
                c = self.components[name]
                d = self.components[dname]
                c.connect(straightConnection= next, 
                    divertConnection= d)
            else:
                c = self.components[c_name]
                c.connect(next)
            next = c

        self.source.connect(next) 
    
    def addAgent(self,s):
        id, count, markStation, delay, maxBlockedTime, stationName, returnConvName = \
            [_s.strip() for _s in s.split(',')]

        def markAsPicked(stations):
            def g(w, ctime):
                for station in stations:
                    w.pickAtS(station) 
            return g 

        station = self.components[stationName]
        returnTo = self.components[returnConvName]
        
        for i in range(int(count)):
            name = id + str(i+1)
            agent = PickingAgent(
                name,
                destination = returnTo, 
                delay = int(delay),
                markWorkload = markAsPicked([markStation]), 
                stopConveyor = False, 
                maxBlockedTime = int(maxBlockedTime))
            station.add_agent(agent)

    def printStructure(self):
        c = self.source
        while True:
            if len(c.children) == 1:
                print(c.name)
                c = c.children[0]
            elif len(c.children) == 2:
                print(c.name, c.children[1].name)
                c = c.children[0]
            else:
                print(c.name)
                break
            

