import glob
import random 
import numpy as np

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
from policies import SELECT_1, SELECT_2, SELECT_3 


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
            random.shuffle(self.datafiles)
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
  
    def getAgentsWaitingRatio(self):
        ttlCountAll = 0
        ttlCountWaiting = 0

        for k in self.components:
            c = self.components[k]

            countAll, _, _, countWaiting, _ = c.getAgentsStatistics()
            if countAll > 0:
                ttlCountAll += countAll
                ttlCountWaiting += countWaiting
        if ttlCountAll > 0:
            return float(ttlCountWaiting) / float(ttlCountAll)
        else:
            return 0.0
        

    # def reward(self, state):
    #     countReceived = self.components['__sink__'].countReceived 
    #     return countReceived / self.nitems

    # def reward(self, state):
    #     if self.t > 0:
    #         alpha = 0.50
    #         countReceived = self.components['__sink__'].countReceived 
    #         #return alpha * (countReceived / self.t) + (1.0-alpha) * (countReceived / self.nitems)
    #         return alpha * (countReceived / self.t) + (1.0-alpha) * (1.0 - self.getAgentsWaitingRatio())
    #     else:
    #         return 0 

    # def reward(self, state, terminated, truncated):
    #     if terminated:
    #         countReceived = self.components['__sink__'].countReceived 
    #         return 1.0 + (countReceived / self.t)
    #     elif truncated:
    #         return -10.0
    #     elif self.t > 0:
    #          alpha = 0.80
    #          countReceived = self.components['__sink__'].countReceived 
    #          return alpha * (countReceived / self.t) + (1.0-alpha) * (countReceived / self.nitems)
    #     else:
    #         return 0 

    #reward for best - robust - min processing time per item
    def reward(self, state, terminated, truncated):
        if terminated:
            avgPickTime =  self.components['__sink__'].avgPickTime 
            if avgPickTime > 0:
                return 100.0/avgPickTime
            else:
                return 0.0
        elif truncated:
            return 0.0
        elif self.t > 0:
            return -0.1 * self.getAgentsWaitingRatio()
        else:
            return 0.0

    

    # def reward(self, state, terminated, truncated):
    #     if terminated:
    #         countReceived = self.components['__sink__'].countReceived 
    #         return (countReceived / self.t)
    #     elif truncated:
    #         return 0
    #     elif self.t > 0:
    #         countReceived = self.components['__sink__'].countReceived 
    #         #the average speed is weighted with the percentage of blocked pickers
    #         # (i.e. the effective speed is lower, when there is a blocked picker)
    #         return (countReceived / self.t) * (1.0 - self.getAgentsWaitingRatio())
    #     else:
    #         return 0 
   
    def reset(self,itemsToPick = None):

        if itemsToPick == None:
            fileName = self.sampleDataFiles()
            print(fileName)
            itemsToPick = BoxListFromFile(fileName)
            if random.random() > 0.8:
                sort = random.randint(0, 2)
                if sort == 0 :
                    print('1,2,3')
                    itemsToPick.sort(reverse=False, key=lambda b: b.route)
                elif sort == 1: 
                    print('2,3,1')
                    itemsToPick.sort(reverse=True, key=lambda b: 1 if b.route == 2 else 0 )
                else:
                    print('3,2,1')
                    itemsToPick.sort(reverse=True, key=lambda b: b.route)
            else:
                print('iid')
        self.source.reset()
        self.state.reset()
        for item in itemsToPick:
            item.reset()

        self.t = 0
        self.maxT = 10000#self.calcMaxT(itemsToPick)
        self.nitems= len(itemsToPick)
        self.strategy.setItems(itemsToPick) 
        return self.state, self.nitems, self.strategy.getActionsMask() 

    def step(self, action):
        self.strategy.setAction(action)
        terminated = False 
        truncated = False 
        info = ''
        actionsMask = self.strategy.getEmptyActionsMask()
        avgPickTime = -1 
        try:
            if self.t > self.maxT:
                raise Exception(f'the maximum simulation time of {self.maxT} steps reached')
            self.source.tick(self.t)

            actionsMask = self.strategy.getActionsMask() 
            state = self.state 
            reward = self.reward(state, False, False)
            avgPickTime = self.components['__sink__'].avgPickTime 
            #self.source.print()
            if self.components['__sink__'].countReceived == self.nitems:
                terminated = True
                reward = self.reward(state, True, False)
        except Exception as e:
            info = e 
            state = self.state 
            reward = self.reward(state, False, True)
            truncated = True 
        nitems = self.strategy.remaining_items
        self.t += 1 
        return state, reward, terminated, truncated, (info, nitems, actionsMask, avgPickTime)
  

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
        id, count, markStation, delay, maxBlockedTime, stationName, returnConvName, isStochastic = \
            [_s.strip() for _s in s.split(',')]

        def markAsPicked(stations):
            def g(w, ctime):
                for station in stations:
                    w.pickAtS(station) 
            return g 

        station = self.components[stationName]
        returnTo = self.components[returnConvName]
        isStochasticVal = False
        if int(isStochastic) == 1:
            isStochasticVal = True

        for i in range(int(count)):
            name = id + str(i+1)
            agent = PickingAgent(
                name,
                destination = returnTo, 
                delay = int(delay),
                markWorkload = markAsPicked([markStation]), 
                stopConveyor = False, 
                maxBlockedTime = int(maxBlockedTime), 
                state = self.state, 
                isStochastic= isStochasticVal)
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
        self.remaining_items = 0
  
    def setItems(self, items):
        self.ix = 0 
        self.items= items
        self.remaining_items = len(self.items)

    def setAction(self, action):
        self.action = action 

    def getActionsMask(self):    
        # no masked actions 
        return [True, True]

    def getEmptyActionsMask(self):
        return [False, False]

    def __call__(self, ctime):
        if self.action == FIFO:
            if self.ix < len(self.items):
                item = self.items[self.ix]
                self.ix += 1 
                self.remaining_items -= 1 
                return item
        elif self.action == SKIP:
            return None 
        return None 

class AdvancedActionStrategy:
    def __init__(self):
        self.ix = 0 
        self.remaining_items = 0
  
    def setItems(self, items):
        self.ix = 0 
        self.route_slots = [[],[],[]]
        self.route_ixes = [0, 0, 0]

        self.items= items
        self.remaining_items = len(self.items)
        for ix in range(len(items)):
            self.route_slots[items[ix].route-1].append(ix)

    def getActionsMask(self):
        # 'SKIP' action is always available
        mask = [True, False, False, False]
        for ix in range(3):
            if self.route_ixes[ix] < len(self.route_slots[ix]):
                mask[ix + 1] = True  

        return mask

    def getEmptyActionsMask(self):
        return [False, False, False, False]

    def setAction(self, action):
        self.action = action 

    def __call__(self, ctime):
        if self.action == SKIP:
            return None 

        action_ix = self.action - 1
        ix = self.route_ixes[action_ix]

        if ix < len(self.route_slots[action_ix]):
            item = self.self.route_slots[action_ix][ix]
            ix += 1 
            self.route_ixes[action_ix] = ix 
            self.remaining_items -= 1 
            return item

        return None 

