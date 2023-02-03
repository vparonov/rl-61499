import random

class Box(object):
    max_box_id = 0 
    max_stations = 2 

    def __init__(self, id, type, route, deadline):
        self.id = int(id)
        self.type = type
        self.route = int(route)
        self.deadline = int(deadline)
        self.reset()

    def __str__(self):
        if self.finishTime >= 0:
            return "B(%s, %s, %s, %d, %d)" % (self.id, self.type, self.routeToString(), self.deadline, self.finishTime)
        else:
            return "B(%s, %s, %s, %d)" % (self.id, self.type, self.routeToString(), self.deadline)

    @staticmethod
    def random():
        b =  Box(Box.max_box_id, 
            random.choice(['S','L']), 
            random.randint(1, 2 ** Box.max_stations - 1), 
            random.randint(1000, 2000))
        Box.max_box_id += 1 
        return b 

    def isForStationIx(self, ix):
        mask = 1 << ix
        return bool(mask & self.route & (~self.pickedMask))

    def isForStationS(self, station):
        ix = self.stationToIx(station)
        return self.isForStationIx(ix)

    def pickAtIx(self, ix):
        self.pickedMask |= 1 << ix

    def reset(self):
        self.pickedMask = 0 
        self.finishTime = -1 
        self.startTime = -1

    def pickAtS(self, s):   
        return self.pickAtIx(self.stationToIx(s))

    def pickingFinished(self):
        return self.route & self.pickedMask == self.route
    def ixToStation(self, ix):
        if ix == 0:
            return 'A'
        elif ix == 1:
            return 'C'
        else:
            return str(ix- 1) 

    def setStartTime(self, ctime):
        self.startTime = ctime
    def setFinishTime(self, ctime):
        if ctime == 1:
            print('111')
        self.finishTime = ctime 

    def getPickTime(self):
        return self.finishTime - self.startTime

    def stationToIx(self, station):
        if station == 'A':
            return 0
        elif station == 'C':
            return 1
        else:
            return int(station) + 1


    def routeToString(self):
        res = '['
        tmp = self.route 
        tmp1 = self.pickedMask 
        for i in range(8):
            if tmp & 1 != 0 :
                if tmp1 & 1 != 0 :
                    res +=  colors.OKGREEN + colors.BOLD
                else:
                    res +=  colors.WARNING + colors.BOLD
                res += self.ixToStation(i) + colors.ENDC
            else:
                res +=  colors.HEADER
                res += '_' + colors.ENDC
            tmp >>= 1
            tmp1 >>=1

        res += ']' 
        return res



class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def testBox():
    b = Box.random()
    print(b)
    print('Is picking finished? ', b.pickingFinished())

    print(b.stationToIx('A'))
    print(b.stationToIx('C'))
    print(b.stationToIx('1'))
    print(b.stationToIx('6'))

    print(b.isForStationS('A'))
    print(b.isForStationS('C'))
    print(b.isForStationS('2'))

    for ix in range(8):
        b.pickAtIx(ix)
    b.setFinishTime(5555)
    print('Is picking finished? ', b.pickingFinished())
    print(b)

if __name__ == '__main__':
    testBox()