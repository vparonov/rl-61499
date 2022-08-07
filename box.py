from ast import Str


class Box(object):
    def __init__(self, id, type, route, deadline):
        self.id = id
        self.type = type
        self.route = route
        self.pickedMask = 0  
        self.deadline = deadline

    def __str__(self):
        return "B(%s, %s, %s)" % (self.id, self.type, self.routeToString())
    
    def ixToStation(self, ix):
        if ix == 0:
            return 'A'
        elif ix == 1:
            return 'C'
        else:
            return str(ix- 1) 

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
    b = Box(1, "L", 0xAA, 1234)
    b.pickedMask = 0XA3
    print(b)

if __name__ == '__main__':
    testBox()