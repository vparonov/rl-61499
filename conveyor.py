from component import Component
class Conveyor(Component):
    def __init__(self, name, description=None, delay = 1, capacity = 10):
        super().__init__(name, description)
        self.delay = delay
        self.capacity = capacity
        self.on = True 
        self.buffer = [None] * self.capacity

    def receive(self, msg):
        if self.on == False:
            return False  

        if self.buffer[0] is not None:
            return False 

        self.buffer[0] = msg
        return True 

    def start(self):
        self.on = True
    
    def stop(self):
        self.on = False
        
    def add_child(self, child):
        if len(self.children) > 0:
            raise Exception('%s. The conveyeror can have only one child.' % self.name)
        return super().add_child(child) 

    # gets an item from the conveyeror and returns the item
    def getItem(self):
        for ix in range(self.capacity-1, -1, -1):
            if self.buffer[ix] is not None:
                item = self.buffer[ix]
                self.buffer[ix] = None
                return item

    # puts an item to the conveyeror at the first empty position from the beginning
    def putItem(self, item):
        for ix in range(self.capacity):
            if self.buffer[ix] is None:
                self.buffer[ix] = item
                return 
        raise Exception('%s is full ' % self.name)
           
    def changeState(self, ctime):
        if self.on == False:
            return False  

        if ctime % self.delay == 0:
            outputMsg = self.buffer[self.capacity-1]
            if outputMsg is not None:

                if len(self.children) == 0:
                    self.stop()
                    return False 

                next = self.children[0] # the conveyeror must have only one child
                if next.receive(outputMsg) == False:
                    return False    

            self.buffer.insert(0,self.buffer.pop())
            self.buffer[0] = None 
        return True 

    def printState(self):
        print('%s -> [' % (self.name), end = '')
        for ix in range(0, self.capacity): 
            delim = ','
            if ix == self.capacity - 1:
                delim = ']'    
            if self.buffer[ix] is not None:
                print(self.buffer[ix], end = delim)
            else:
                print('()', end = delim)
        print('')
