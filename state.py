from collections import defaultdict

class State:
    def __init__(self, nitems, ncomponents) -> None:
        self.itemsState = defaultdict(lambda : -1)
        self.componentsState = [0] * ncomponents

    def update(self, itemID, componentID):
        prevComponentID = self.itemsState[itemID]
        if prevComponentID >= 0:
            self.componentsState[prevComponentID] -= 1

        self.itemsState[itemID] = componentID
        self.componentsState[componentID] += 1

    def get(self):
        return self.itemsState, self.componentsState
if __name__ == '__main__':
    s = State(5, 5)
    print(s.get())
    s.update(0, 0)
    print(s.get())
    s.update(0, 1)
    print(s.get())
    s.update(1, 0)
    print(s.get())
    s.update(1, 1)
    print(s.get())

