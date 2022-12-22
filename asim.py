import matplotlib.pyplot as plt
from warehouse import Warehouse
from box import Box 

nitems = 100
items = [Box.random() for i in range(nitems)]

class SimpleStrategy:
    def __init__(self, delay):
        self.delay = delay
        self.ix = 0 
    def __call__(self, ctime, items):
        if ctime % self.delay == 0:
            if self.ix < len(items):
                item = items[self.ix]
                self.ix += 1 
                return item
        return None 

w = Warehouse('test', 'files/wh1.txt')

succeeded_y = [] 
succeeded_x = [] 

failed_y = [] 
failed_x = [] 
#for i in range(20):
for delay in range(10, 31, 1):
    ok, steps = w.run(-1, items, strategy= SimpleStrategy(delay), printEvery=-1)
    if ok:
        succeeded_y.append(steps)
        succeeded_x.append(delay)
    else:
        failed_y.append(steps)
        failed_x.append(delay)

plt.scatter(succeeded_x, succeeded_y, label='ok', c='green')
plt.scatter(failed_x, failed_y, label='failed', c='red')
plt.show()
    
