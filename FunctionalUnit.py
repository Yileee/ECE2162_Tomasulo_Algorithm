from ReservationStation import ReservationStation
from LoadStoreQueue import LoadStoreQueue
import copy

class FunctionalUnit(object):
    def __init__(self, supportedIns, cyclenums, rs_size_dict):
        self.supportedInstructions = supportedIns
        self.cycles = cyclenums
        self.reservationStation = []
        self.loadstorequeue = []
        self.lsq_size = 10

        op_type = supportedIns[0]
        if ('Mult' in op_type) or ('Add' in op_type):
            if '.d' in op_type:
                data_type = 'fp'
            else:
                data_type = 'int'
            if 'Add' in op_type:
                op_type = 'add'
            elif 'Mul' in op_type:
                op_type = 'mul'
            rs_key = data_type + '_' + op_type
            for i in range(rs_size_dict[rs_key]):
                self.reservationStation.append(ReservationStation())  # TODO: using RS instead of LSQ?
        elif ('Ld' in op_type) or ('Sd' in op_type):
        # elif ('Ld' in op_type) or ('Store' in op_type):
            for i in range(self.lsq_size):     # set the size of LSQ
                self.loadstorequeue.append(LoadStoreQueue())    # TODO: check Load and Store
            pass

    def clear(self):
        self.reservationStation = ReservationStation()


class FunctionalUnits(object):
    def __init__(self):
        self.fuList = []
        self.memoryAccess = False
        self.instrMemRunning=None

    def add(self, fu):
        self.fuList.append(fu)

    def findAvailableRS(self, opname):    # TODO: return the first available RS
        for funtionalunit in self.fuList:
            if opname in funtionalunit.supportedInstructions:
                for rs in funtionalunit.reservationStation:
                    if not rs.busy:
                        # if opname in funtionalunit.supportedInstructions:
                        return rs, funtionalunit.cycles
        return False


    def isAvailable(self, opname):
        for fu in self.fuList:
            for rs in fu.reservationStation:
                if opname in fu.supportedInstructions:
                    if not rs.busy:
                        return True
        return False

    def findAvailableLSQ(self):
        found=False
        for fu in self.fuList:
           if fu.supportedInstructions == ['Ld', 'Sd']:
                for lsq in fu.loadstorequeue:
                    if not lsq.occupied:
                        return lsq    # TODO: does it need cycles?

                if fu.loadstorequeue[0].isDone is True:
                    if fu.loadstorequeue[0].isDoneCycle!=1:
                        for index, lsq in enumerate(fu.loadstorequeue):

                            # transfer the young to old, step is 1
                            if index==fu.lsq_size-1:

                                lsq.opName = ''
                                lsq.pc = None
                                lsq.occupied = False
                                lsq.busy = False
                                lsq.ready = False  # Ld and Sd have
                                lsq.address = None  # offset+Rn
                                lsq.value = None  # value of the register to be stored
                                lsq.destination = None  # the register name to be stored
                                lsq.Vj = None  # offset
                                lsq.Vk = None  # Rn
                                lsq.Qj = None  # no Qj in this situation
                                lsq.Qk = None  # ROB for Rn

                                # For store, add fields:
                                lsq.Vl = None
                                lsq.Ql = None
                                lsq.isStore = False
                                # end of store fields

                                lsq.cyclesRemained = None
                                lsq.cyclesMemRemained = None  # TODO modify with values from config file
                                lsq.isDone = False
                                lsq.isInHistory = False
                                lsq.writeback = False
                                lsq.cdbcycle = 2
                                lsq.robId = None
                                lsq.isDoneCycle = 1
                                return lsq
                            if self.memoryAccess is True and index == self.instrMemRunning:
                                self.instrMemRunning = index-1
                            self.fuList[3].loadstorequeue[index] = copy.deepcopy(fu.loadstorequeue[index + 1])
                    else:
                        fu.loadstorequeue[0].isDoneCycle-=1


        return False

    def flush(self,list):
        for fu in self.fuList:
            for robId in list:
                for rs in fu.reservationStation:
                    if rs.Qj == robId or rs.Qk == robId or rs.destination == robId:
                        rs.clear()
                for lsq in fu.loadstorequeue:
                    if lsq.Qk == robId or lsq.Qj == robId or lsq.Ql == robId or lsq.destination == robId:
                        lsq.clear()

    def toString(self):
        st = 'Reservation Stations\n'
        i = 0
        for fu in self.fuList:
            for rs in fu.reservationStation:
                st += 'RS' + str(i) + ': ' + rs.toString() + '\n'
                i += 1
        return st