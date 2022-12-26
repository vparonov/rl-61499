from collections import defaultdict

class State:
    def __init__(self) -> None:
        self.itemsState = defaultdict(lambda : '__buffer__')
        self.componentsState= defaultdict(lambda : 0)

    def update(self, itemID, componentID):
        prevComponentID = self.itemsState[itemID]
        self.componentsState[prevComponentID] -= 1

        self.itemsState[itemID] = componentID
        self.componentsState[componentID] += 1

    def get(self):
        return self.itemsState, self.componentsState


#tests 
if __name__ == '__main__':
    s = State()
    print(s.get())
    s.update(0, 'C1')
    print(s.get())
    s.update(0, 'C2')
    print(s.get())
    s.update(1, 'C1')
    print(s.get())
    s.update(1, 'C2')
    print(s.get())

    itemsDict, componentsState = s.get()
    print(itemsDict[0], itemsDict[3])

