import glob
import random 

from collections import defaultdict
from source import Source 
from sink import Sink 
from stateprobe import StateProbe
from state import State 
from pickingagent import PickingAgent
from conveyor import Conveyor
from diverter import Diverter
from dataloader import BoxListFromFile

from policies import FIFO, SKIP 


class ActionSpace():
    def __init__(self, actions):
        self.actions = actions 
        self.n = len(self.actions)
    
    def sample(self):
        return random.sample(self.actions, k=1)[0]
    
class Warehouse:
    def __init__(self, name, fileName, datadir, randomFileSelect = False):
        self.name = name
        self.source = Source(name + '.source', '', 1, lambda ctime : self.strategy(ctime)) 
        self.state = State()
        
        self.randomFileSelect = randomFileSelect

        if datadir != None:
            self.datafiles = self.enumerateDataFiles(datadir)
            self.datafiles.sort()
            self.fileIx = 0
        else:
            self.datafiles = []

        self.action_space = ActionSpace([SKIP, FIFO])

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
  
    # def reward(self, state):
    #     countReceived = self.components['__sink__'].countReceived 
    #     return countReceived / self.nitems
    
    def reward(self, state):
        if self.t > 0:
            alpha = 0.80
            countReceived = self.components['__sink__'].countReceived 
            return alpha * (countReceived / self.t) + (1.0-alpha) * (countReceived / self.nitems)
        else:
            return 0 

    def reset(self,itemsToPick = None):

        if itemsToPick == None:
            fileName = self.sampleDataFiles()
            print(fileName)
            itemsToPick = BoxListFromFile(fileName)
            if random.random() > 0.8:
                itemsToPick.sort(reverse=False, key=lambda b: b.route)

        self.source.reset()
        self.state.reset()
        for item in itemsToPick:
            item.reset()

        self.t = 0
        self.maxT = self.calcMaxT(itemsToPick)
        self.nitems= len(itemsToPick)
        self.strategy.setItems(itemsToPick) 
        return self.state, '' 

    def step(self, action):
        self.strategy.setAction(action)
        terminated = False 
        truncated = False 
        info = ''
        reward = -10.0
        try:
            if self.t > self.maxT:
                raise Exception(f'the maximum simulation time of {self.maxT} steps reached')
            self.source.tick(self.t)
            state = self.state 
            reward = self.reward(state)
            #self.source.print()
            if self.components['__sink__'].countReceived == self.nitems:
                terminated = True
 #               reward = 1.0 * (1.0 + self.nitems / self.t)  
 #           else:
 #               reward = self.reward(state)
        except Exception as e:
            info = e 
            #reward = -1.0
            state = self.state 
            truncated = True 

        self.t += 1 
        return state, reward, terminated, truncated, info
  

    def calcMaxT(self, itemsToPick):
        maxt = 1e6
        # max simulation time
        # is minimal deadline time of itemsToPick
        for item in itemsToPick:
            if maxt > item.deadline:
                maxt = item.deadline
        return maxt 
    def getCapacities(self, componentIds):
        return [ self.components[id].capacity if id in self.components.keys() else 1 for id in componentIds]
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

    def getInternalState(self):
        internalState = {}
        
        def __traverse(c):
            if c.name[-6:-1] != '_prob': 
                internalState[c.name] = c.getInternalState()
                for a in c.agents:
                    internalState[a.name] = a.getInternalState()
            for id in range(len(c.children)-1, -1, -1):
                __traverse(c.children[id])

        __traverse(self.source.children[0])    
 
        return internalState

    def enumerateDataFiles(self, dataDir):
        return glob.glob(f'{dataDir}/*.txt')

    def sampleDataFiles(self):
        if self.randomFileSelect:
            return random.sample(self.datafiles, k=1)[0]
        else:
            f = self.datafiles[self.fileIx]
            self.fileIx = (self.fileIx + 1) % len(self.datafiles)
            return f

class ActionStrategy:
    def __init__(self):
        self.ix = 0 
  
    def setItems(self, items):
        self.ix = 0 
        self.items= items

    def setAction(self, action):
        self.action = action 

    def __call__(self, ctime):
        if self.action == FIFO:
            if self.ix < len(self.items):
                item = self.items[self.ix]
                self.ix += 1 
                return item
        elif self.action == SKIP:
            return None 
        return None 

