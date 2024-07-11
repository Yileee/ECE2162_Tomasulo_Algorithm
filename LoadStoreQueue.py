class LoadStoreQueue(object):  # TODO: add cyclesRemained = 4
    def __init__(self):
        self.opName = ''
        self.pc = None
        self.occupied = False
        self.busy = False
        self.ready = False  # Ld and Sd have
        self.address = None  # offset+Rn
        self.value = None  # value of the register to be stored
        self.destination = None  # the register name to be stored
        self.Vj = None  # offset
        self.Vk = None  # Rn
        self.Qj = None  # no Qj in this situation
        self.Qk = None  # ROB for Rn

        # For store, add fields:
        self.Vl = None
        self.Ql = None
        self.isStore = False
        # end of store fields

        self.cyclesRemained = None
        self.cyclesMemRemained = None  # TODO modify with values from config file
        self.isDone = False
        self.isInHistory = False
        self.writeback = False
        self.cdbcycle = 2
        self.robId = None
        self.isDoneCycle = 1

    def readFromMemory(self, memory):  # in execute stage, calculate the address
        # self.address = self.Vj + self.Vk
        # print("address: " + str(self.address))
        self.value = memory.getValue(self.address)

    # def setValue(self,memory):
    #     self.value = memory
    def clear(self):
        self.opName = ''
        self.pc = None
        self.occupied = False
        self.busy = False
        self.ready = False  # Ld and Sd have
        self.address = None  # offset+Rn
        self.value = None  # value of the register to be stored
        self.destination = None  # the register name to be stored
        self.Vj = None  # offset
        self.Vk = None  # Rn
        self.Qj = None  # no Qj in this situation
        self.Qk = None  # ROB for Rn

        # For store, add fields:
        self.Vl = None
        self.Ql = None
        self.isStore = False
        # end of store fields

        self.cyclesRemained = None
        self.cyclesMemRemained = None  # TODO modify with values from config file
        self.isDone = False
        self.isInHistory = False
        self.writeback = False
        self.cdbcycle = 2
        self.robId = None
        self.isDoneCycle = 1