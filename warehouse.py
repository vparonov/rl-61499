from source import Source 
from sink import Sink 
from pickingagent import PickingAgent
from conveyor import Conveyor
from diverter import Diverter

class Warehouse:
    def __init__(self, name, fileName, generator):
        self.name = name
        self.source = Source(name + '.source', '', 1, generator)
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
  
    def addStructure(self, s):
        if s[0] == 'c' or s[0] == 's':
            name, p1, p2 = s.split(',')
            item = Conveyor(name, '', delay=int(p1), capacity=int(p2))
        elif s[0] == 'd':
            name, p1 = s.split(',')
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
                print(f'conv {c_name}')
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



if __name__ == '__main__':
    from box import Box 

    nitems = 200
    def genNitems(n):
        def g(ctime):
            if ctime <= n:
                return Box.random()
            else:
                return None 

        return g 
    w = Warehouse('test', 'files/wh1.txt', generator = genNitems(nitems))
    