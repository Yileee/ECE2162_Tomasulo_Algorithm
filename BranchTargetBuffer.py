class BranchTargetBuffer(object):
    def __init__(self):
        self.size = 8
        self.tail = -1
        self.list = [BranchTargetBufferEntry(i) for i in range(self.size)]
        self.numelements = 0

    def creatBtbEntry(self, instruction):
        index = self.tail + 1
        index %= self.size
        self.tail += 1
        self.tail %= self.size
        self.numelements += 1
        self.list[index].currentPC = instruction.address
        offset = instruction.source1
        self.list[index].targetPC = int(instruction.address) + 4 + int(offset) * 4
        self.list[index].prediction = False          # False means not taken
        return self.list[index]

    def findBTB(self, pc):
        for entry in self.list:
            if entry.currentPC == pc:
                return entry
        return None

    def keepFirstEntry(self):    # maybe useless
        # only keep the first entry and initialize the rest entry
        for i in range(1, self.size):
            self.list[i].currentPC = None
            self.list[i].targetPC = None
            self.list[i].prediction = None


class BranchTargetBufferEntry(object):
    def __init__(self, i):
        self.currentPC = None
        self.targetPC = None
        self.prediction = None


if __name__ == '__main__':
    BTB = BranchTargetBuffer()
    print(BTB.creatBtbEntry(1).targetPC)
