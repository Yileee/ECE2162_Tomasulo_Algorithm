import copy

class ReorderBuffer(object):
    def __init__(self, size=5):
        self.size = size
        self.head = 0
        self.tail = -1
        self.list = [ReorderBufferEntry(i) for i in range(self.size)]
        self.numelements = 0


    def isFull(self):
        if self.numelements == self.size:
            return True
        else:
            return False

    def getROBEntry(self, name): # name is ROBn format, not Fn nor Rn format
        for entry in self.list:
            if entry.name == name:
                return entry
        return None

    def createRobEntry(self, inst):
        index = self.tail + 1
        index %= self.size
        self.list[index].opname = inst.opname
        self.list[index].destination = inst.destination
        self.list[index].instruction = inst
        self.list[index].busy = True
        self.tail += 1
        self.tail %= self.size
        self.numelements += 1
        return self.list[index].name

    def getHead(self):
        return self.list[self.head]

    def pop(self):
        result = copy.copy(self.list[self.head])
        self.list[self.head].clear()
        self.head += 1
        self.head %= self.size
        self.numelements -= 1
        return result

    def flush(self, destination):
        index = 0
        for entry in self.list:
            if entry.name == destination:
                index = self.list.index(entry)
                break

        listtoremove = []
        while (self.tail - index) % self.size != 0:
            index += 1
            index %= self.size
            listtoremove.append(self.list[index].name)
            # self.list[index].clear()

        self.tail -= len(listtoremove)
        self.tail %= self.size
        self.numelements -= len(listtoremove)
        return listtoremove

    def toString(self):
        st = 'Reorder Buffer\n'
        i = 0
        for entry in self.list:
            st += entry.toString()
            if i == self.head:
                st += ' (H)'
            if i == self.tail:
                st += ' (T)'
            st += '\n'
            i += 1
        return st

    def findLastEntry(self, register):
        index = self.tail
        for i in range(self.numelements):  # ROB.numelements? public?
            if self.list[index].destination == register.name:
                return self.list[index]
            index -= 1
            index %= self.size
        return None


class ReorderBufferEntry(object):
    def __init__(self, i):
        self.name = 'ROB' + str(i)
        self.instructions = None
        self.opname = ''
        self.busy = False
        self.ready = False
        self.destination = ''
        self.value = None
        self.branchTaken = None     # TODO: another parameter and may not use this one
        self.branchPrediction = None
        # Cycle tags
        self.issueCycle = None
        self.executeCycleStart = None
        self.executeCycleEnd = None
        self.memoryCycleStart = None
        self.memoryCycleEnd = None
        self.writebackCycle = None
        self.commitCycle = None

    def clear(self):
        self.opname = ''
        self.busy = False
        self.ready = False
        self.destination = '' # Fn
        self.value = None # offset + Rn result
        # Clear cycle tags
        self.issueCycle = None
        self.executeCycleStart = None
        self.executeCycleEnd = None
        self.memoryCycleStart = None
        self.memoryCycleEnd = None
        self.writebackCycle = None
        self.commitCycle = None


    def toString(self):
        st = self.name + ': '
        if self.ready:
            st += self.opname + ' '
            if self.opname == 'Ld':
                st += ' '
            st += str(self.destination) + ' ' + str(self.value)
        elif self.busy:
            st += self.opname + ' '
            if self.opname == 'Ld':
                st += ' '
            st += str(self.destination) + ' -'

        # Cycle tags
        if self.issueCycle is not None:
            st += ' Issue: ' + str(self.issueCycle)
        if self.executeCycleStart is not None:
            st += ' Execute: ' + str(self.executeCycleStart) + '-' + str(self.executeCycleEnd)
        if self.memoryCycleStart is not None:
            st += ' Memory: ' + str(self.memoryCycleStart) + '-' + str(self.memoryCycleEnd)
        if self.writebackCycle is not None:
            st += ' Writeback: ' + str(self.writebackCycle)
        if self.commitCycle is not None:
            st += ' Commit: ' + str(self.commitCycle)

        return st
