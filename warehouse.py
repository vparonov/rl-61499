from collections import defaultdict
from source import Source 
from sink import Sink 
from stateprobe import StateProbe
from state import State 
from pickingagent import PickingAgent
from conveyor import Conveyor
from diverter import Diverter

class Warehouse:
    def __init__(self, name, fileName):
        self.name = name
        self.source = Source(name + '.source', '', 1, lambda ctime : self.strategy(ctime)) 
        self.state = State()

        sink = Sink(name + '.sink', '')
        sinkProbe = StateProbe(name + '.sink_probe', '', self.state, name + '.sink')
        sinkProbe.connect(sink)
        self.components = {
            '__sink__probe': sinkProbe, 
            '__sink__': sink
        }
        self.probes = defaultdict(lambda : None)
        self.firstComponent = None
        self.strategy = ActionStrategy() 
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
  
    def reward(self, state):
        countReceived = self.components['__sink__'].countReceived 
        return countReceived / self.nitems

    def reset(self,itemsToPick):
        self.source.reset()
        self.state.reset()
        self.t = 0
        self.nitems= len(itemsToPick)
        self.strategy.setItems(itemsToPick) 
        return self.state, '' 

    def step(self, action):
        self.strategy.setAction(action)
        terminated = False 
        truncated = False 
        info = ''
        try:
            self.source.tick(self.t)
            state = self.state 
            #self.source.print()
            if self.components['__sink__'].countReceived == self.nitems:
                terminated = True
                reward = 10  
            else:
                reward = self.reward(state)
        except Exception as e:
            info = e 
            reward = -10
            state = self.state 
            truncated = True 

        self.t += 1 
        return state, reward, terminated, truncated, info
  
    def addStructure(self, s):
        probe = None 

        if s[0] == 'c' or s[0] == 's':
            name, p1, p2, p3 = [_s.strip() for _s in s.split(',')]
            item = Conveyor(name, '', delay=int(p1), capacity=int(p2))
            # add probe 
            if int(p3) == 1:
                probe = StateProbe(name + '_state_probe', '', self.state, name)
                self.probes[name] = probe
        elif s[0] == 'd':
            name, p1, p2 = [_s.strip() for _s in s.split(',')]
            item = Diverter(name, divertPredicate=lambda load: load.isForStationS(p1))
            if int(p2) == 1:
                probe = StateProbe(name + '_state_probe', '', self.state, name)
                self.probes[name] = probe
        else:
            raise Exception('Unknow component type %s' % name)

        self.components[name] = item
    
    def addConnection(self, s):
        connections = s.split('->')

        next = self.components['__sink__probe']
        for ix in range(len(connections)-1, -1, -1):
            c_name = connections[ix]
            if c_name[0] == 'd':
                name, dname = c_name.split('!')
                c = self.components[name]
                
            
                d = self.components[dname]
                dprobe = self.probes[dname]
                if dprobe != None:
                    dprobe.connect(d)
                    d = dprobe 

                c.connect(straightConnection= next, 
                    divertConnection= d)
            
                sprobe = self.probes[name]
                if sprobe != None:
                    sprobe.connect(c)
                    c = sprobe
            else:
                c = self.components[c_name]
                c.connect(next)
            
            probe = self.probes[c_name] 
            if probe != None:
                probe.connect(c)
                next= probe 
            else:
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
                maxBlockedTime = int(maxBlockedTime), 
                state = self.state)
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
    
    def getSortedComponents(self):
        labels = []
        def __traverse(c):
            if c.name[-6:-1] != '_prob': 
                labels.append(c.name)
                for a in c.agents:
                    labels.append(a.name)
            for id in range(len(c.children)-1, -1, -1):
                __traverse(c.children[id])

        __traverse(self.source)    
        return labels
class ActionStrategy:
    def __init__(self):
        self.ix = 0 
  
    def setItems(self, items):
        self.ix = 0 
        self.items= items

    def setAction(self, action):
        self.action = action 

    def __call__(self, ctime):
        if self.action == 'FIFO':
            if self.ix < len(self.items):
                item = self.items[self.ix]
                self.ix += 1 
                return item
        elif self.action == 'SKIP':
            return None 
        return None 