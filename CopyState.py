import copy

class CopyState:
    def __init__(self):
        self.tail = -1
        self.list = []

    def addEntry(self, currentPC, currentRF):
        self.tail += 1
        PC = copy.deepcopy(currentPC)
        RF = copy.deepcopy(currentRF)
        self.list.append(CopyStateEntry(PC, RF))

    def clearFirstEntry(self):
        self.list.pop(0)
        self.tail -= 1

    def clear(self):
        self.list = []
        self.tail = -1

    def updateRF(self, currentRF):
        # first clear the resetRF(a class type) of the first entry
        # self.list[0].resetRF.clear()
        # self.list[0].resetRF = []
        # print(self.list)
        # self.list[0].resetRF = None
        self.list[0].resetRF = copy.deepcopy(currentRF)


class CopyStateEntry:
    def __init__(self, currentPC, currentRF):
        self.resetPC = currentPC  # the PC when current branch is fetched
        self.resetRF = currentRF



if __name__ == '__main__':
    copy = CopyState()
    CopyState.addEntry(copy, 1, 2)
    CopyState.addEntry(copy, 2, 3)
    CopyState.addEntry(copy, 3, 4)
    CopyState.clearFirstEntry(copy)
    print(copy.list[0].resetPC)