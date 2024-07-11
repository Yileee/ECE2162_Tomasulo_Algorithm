import copy
from CopyState import CopyState

isIntAdderOperating = False

def fetch(instructionBuffer, pc, program, BranchTargetBuffer):
    while instructionBuffer.isFull() is False and int(pc) < 4 * len(program) and pc != -1:  #
        for i in program:
            if i.address == pc:
                instructionBuffer.add(i)
                if (i.opname == 'Bne') or (i.opname == 'Beq'):
                    # save the current information
                    # TODO: save the information after creating the ROB entry?
                    # CopyState.addEntry(copyState, pc, ReoderBuffer, RegisterFile, FunctionalUnit, instructionBuffer)  # TODO:MEM?-no BTB?-no
                    btb = BranchTargetBuffer.findBTB(i.address)
                    if btb is None:
                        btb = BranchTargetBuffer.creatBtbEntry(i)
                        pc = pc + 4     # first predict not taken
                        # pc = int(btb.targetPC)           # first predict taken(remember also change in BTB)
                        break
                    else:
                        if btb.prediction is True:
                            pc = int(btb.targetPC)
                            break
                        else:
                            pc = pc + 4
                                                # TODO: check the  preditor first,
                else:                           # TODO: if predict taken, fetch the target instruction
                    pc = pc + 4                 # TODO: if not taken, then pc = pc + 4
                break                           # TODO: also need a copy of all statements
    return instructionBuffer, pc, BranchTargetBuffer


def issue(currentCycle, reorderBuffer, instructionBuffer, pc, functionalUnit, architectureRegisterFile, copyState):
    if reorderBuffer.isFull() is False and pc != -1:
        # Ld & Sd
        if (instructionBuffer.head().opname == 'Ld'):
            lsq = functionalUnit.findAvailableLSQ()  # TODO: does it need cycles?
            if lsq is not False:
                inst = instructionBuffer.pop()
                lsq.opName = inst.opname
                lsq.Vj = int(inst.source1)
                for register in architectureRegisterFile.intRegisterList:  # TODO: source is int and destination is fp
                    if register.name == inst.source2:
                        if register.busy:
                            h = reorderBuffer.findLastEntry(register)
                            if h is not None and h.ready:
                                lsq.Vk = h.value
                            else:
                                lsq.Qk = h.name
                        else:
                            lsq.Vk = register.value
                        break

                b = reorderBuffer.createRobEntry(inst)
                reorderBuffer.getROBEntry(b).issueCycle = currentCycle
                lsq.robId=b
                for register in architectureRegisterFile.intRegisterList:  # TODO: optimize
                    if register.name == inst.destination:
                        if inst.opname != 'Sd':
                            # if not register.busy:
                            register.robId = b
                            register.busy = True
                            break
                for register in architectureRegisterFile.fpRegisterList:
                    if register.name == inst.destination:
                        if inst.opname != 'Sd':
                            # if not register.busy:
                            register.robId = b
                            register.busy = True
                            break

                lsq.destination = b
                lsq.busy = True
                lsq.occupied = True
                lsq.opName = inst.opname
                lsq.cyclesRemained = 1
                lsq.cyclesMemRemained = 5

        elif instructionBuffer.head().opname == 'Sd':
            # TODO issue stage for Sd, correct the destination problem
            lsq = functionalUnit.findAvailableLSQ()
            if lsq is not False:
                inst = instructionBuffer.pop()
                lsq.opName = inst.opname
                lsq.isStore = True # set the store value
                lsq.Vj = int(inst.source1) # offset

                # Rn
                for register in architectureRegisterFile.intRegisterList:
                    if register.name == inst.source2:
                        if register.busy:
                            h = reorderBuffer.findLastEntry(register)
                            if h is not None and h.ready:
                                lsq.Vk = h.value
                            else:
                                lsq.Qk = h.name
                        else:
                            lsq.Vk = register.value
                        break
                # Fn
                for register in architectureRegisterFile.fpRegisterList:
                    if register.name == inst.destination:
                        if register.busy:
                            h = reorderBuffer.findLastEntry(register)
                            if h is not None and h.ready:
                                lsq.Vl = h.value
                            else:
                                lsq.Ql = h.name
                        else:
                            lsq.Vl = register.value
                        break

                b = reorderBuffer.createRobEntry(inst)
                reorderBuffer.getROBEntry(b).issueCycle = currentCycle
                lsq.robId = b
                # Sd does not need to rename destination
                # for register in architectureRegisterFile.intRegisterList:  # TODO: optimize
                #     if register.name == inst.destination:
                #         if inst.opname != 'Sd':
                #             if not register.busy:
                #                 register.robId = b
                #                 register.busy = True
                #                 break
                # for register in architectureRegisterFile.fpRegisterList:
                #     if register.name == inst.destination:
                #         if inst.opname != 'Sd':
                #             if not register.busy:
                #                 register.robId = b
                #                 register.busy = True
                #                 break

                lsq.destination = b
                lsq.busy = True
                lsq.occupied = True
                lsq.opName = inst.opname
                lsq.cyclesRemained = 1
                lsq.cyclesMemRemained = 5

        # Branch Instructions
        elif instructionBuffer.head().opname == 'Beq' or instructionBuffer.head().opname == 'Bne':
            inst = instructionBuffer.pop()
            # TODO: cannot directly copy current statements
            CopyState.addEntry(copyState, inst.address, architectureRegisterFile)
            rs, fu_cycle = functionalUnit.findAvailableRS(inst.opname)
            for register in architectureRegisterFile.intRegisterList:
                if register.name == inst.Rs:
                    if register.busy:
                        h = reorderBuffer.findLastEntry(register)
                        if h is not None and h.ready:
                            rs.Vj = h.value
                        else:
                            rs.Qj = h.name
                    else:
                        rs.Vj = register.value
                if register.name == inst.Rt:
                    if register.busy:
                        h = reorderBuffer.findLastEntry(register)
                        if h is not None and h.ready:
                            rs.Vk = h.value
                        else:
                            rs.Qk = h.name
                    else:
                        rs.Vk = register.value
            b = reorderBuffer.createRobEntry(inst)
            reorderBuffer.getROBEntry(b).issueCycle = currentCycle
            rs.destination = b
            rs.busy = True
            rs.opName = inst.opname
            rs.cyclesRemained = fu_cycle   # cycles in execute stage

        # Other ALU instructions
        elif functionalUnit.isAvailable(instructionBuffer.head().opname):  # TODO: LD also goes into this part
            inst = instructionBuffer.pop()
            # fu = functionalUnit.findAvailable(inst.opname)   # if inst is a non ld/Sd instruction
            rs, fu_cycle = functionalUnit.findAvailableRS(inst.opname)
            find = False
            # source1
            for register in architectureRegisterFile.intRegisterList:  # TODO: also need to check fp registers
                if register.name == inst.source1:
                    if register.busy:
                        h = reorderBuffer.findLastEntry(register)
                        # for robEntry in ROB.list:
                        #     if robEntry.name == h:
                        #         if robEntry.ready:
                        if h is not None and h.ready:
                            # fu.reservationStation.Vj = h.value
                            rs.Vj = h.value
                        else:
                            # fu.reservationStation.Qj = h.name
                            rs.Qj = h.name
                    else:
                        # fu.reservationStation.Vj = register.value     # TODO: check
                        rs.Vj = register.value  # TODO: check
                    find = True
                    break
            if not find:
                for register in architectureRegisterFile.fpRegisterList:
                    if register.name == inst.source1:
                        if register.busy:
                            h = reorderBuffer.findLastEntry(register)
                            # for robEntry in ROB.list:
                            #     if robEntry.name == h:
                            #         if robEntry.ready:
                            if h is not None and h.ready:
                                # fu.reservationStation.Vj = h.value
                                rs.Vj = h.value
                            else:
                                # fu.reservationStation.Qj = h.name
                                rs.Qj = h.name
                        else:
                            # fu.reservationStation.Vj = register.value
                            rs.Vj = register.value
                        find = True
                        break
            if not find:
                rs.Vj = int(inst.source1)
                # for register in architectureRegisterFile.fpRegisterList:
                #     if register.name == inst.source1

            # rename source2
            find = False
            for register in architectureRegisterFile.intRegisterList:
                if register.name == inst.source2:
                    if register.busy:
                        h = reorderBuffer.findLastEntry(register)
                        # for robEntry in ROB.list:
                        #     if robEntry.name == h:
                        #         if robEntry.ready:
                        if h is not None and h.ready:
                            rs.Vk = h.value
                        else:
                            rs.Qk = h.name
                    else:
                        rs.Vk = register.value
                    find = True
                    break
            if not find:
                for register in architectureRegisterFile.fpRegisterList:
                    if register.name == inst.source2:
                        if register.busy:
                            h = reorderBuffer.findLastEntry(register)
                            # for robEntry in ROB.list:
                            #     if robEntry.name == h:
                            #         if robEntry.ready:
                            if h is not None and h.ready:
                                rs.Vk = h.value
                            else:
                                rs.Qk = h.name
                        else:
                            rs.Vk = register.value
                        find = True
                        break
            if not find:
                rs.Vk = int(inst.source2)


            b = reorderBuffer.createRobEntry(inst)  # TODO: LD and SD also go into ROB(unless it can solve immediately?)
            reorderBuffer.getROBEntry(b).issueCycle = currentCycle
            # TODO: Also check the condition for creating ROB entry
            if inst.opname != 'Bne' and inst.opname != 'Beq':   # rename RF(branch instruction does need to rename)
                for register in architectureRegisterFile.intRegisterList:  # TODO: optimize
                    if register.name == inst.destination:
                        # if not register.busy:
                        register.robId = b
                        register.busy = True
                        break
                for register in architectureRegisterFile.fpRegisterList:
                    if register.name == inst.destination:
                        # if not register.busy:
                        register.robId = b
                        register.busy = True
                        break

            rs.destination = b
            rs.busy = True
            rs.opName = inst.opname
            rs.cyclesRemained = fu_cycle
    return reorderBuffer, instructionBuffer, functionalUnit, architectureRegisterFile


def execute(currentCycle, functionalUnit, memory, reorderBuffer, commonDataBus):
    global isIntAdderOperating
    for fu in functionalUnit.fuList:
        currentInstructionTypeCycles = fu.cycles
        # for the instructions that need to go through reservation station(ALU instructions and branch instructions)
        for rs in fu.reservationStation:
            if rs.busy and rs.Vj is not None:
                if rs.Vk is not None:
                    if rs.cdbcycle!=1:
                        # Now, the instruction is ready to execute
                        # for Add,Addi,Sub and branch instruction, check whether currently has the same type of instruction in RS that is executing
                        # integer adder is unpipielined and branch is send to integer ALU
                        if rs.opName == 'Add' or rs.opName == 'Addi' or rs.opName == 'Sub' or rs.opName == 'Bne' or rs.opName == 'Beq':
                            if rs.cyclesRemained == currentInstructionTypeCycles:
                                if isIntAdderOperating:
                                    continue
                                else:
                                    isIntAdderOperating = True
                                    reorderBuffer.getROBEntry(rs.destination).executeCycleStart = currentCycle
                                    rs.cyclesRemained -= 1
                                    if rs.cyclesRemained == 0:
                                        isIntAdderOperating = False
                                        reorderBuffer.getROBEntry(rs.destination).executeCycleEnd = currentCycle

                        if rs.cyclesRemained == currentInstructionTypeCycles:
                            reorderBuffer.getROBEntry(rs.destination).executeCycleStart = currentCycle
                        rs.cyclesRemained -= 1
                        if rs.cyclesRemained == 0:
                            reorderBuffer.getROBEntry(rs.destination).executeCycleEnd = currentCycle
                    elif rs.cdbcycle == 1:
                        # if rs.cyclesRemained > 0:       # TODO
                        #     rs.cyclesRemained -= 1
                        #     if rs.cyclesRemained == 0:
                        #         reorderBuffer.getROBEntry(rs.destination).executeCycleEnd = currentCycle
                        #         if currentInstructionTypeCycles == 1:
                        #             reorderBuffer.getROBEntry(rs.destination).executeCycleStart = currentCycle
                        #     elif rs.cyclesRemained + 1 == currentInstructionTypeCycles:
                        #         reorderBuffer.getROBEntry(rs.destination).executeCycleStart = currentCycle
                        rs.cdbcycle -= 1

        # Load and Store Instructions
        for currentIndex, lsq in enumerate(fu.loadstorequeue):
            if lsq.busy and lsq.Vj is not None and lsq.Vk is not None and lsq.cyclesRemained > 0:
                if lsq.cdbcycle !=1:
                    lsq.address = lsq.Vj + lsq.Vk
                    # TODO last changed here 1
                    # reorderBuffer.getROBEntry(lsq.destination).value = lsq.address
                    if lsq.cyclesRemained == 1: # TODO add a cycle field to config file
                        reorderBuffer.getROBEntry(lsq.destination).executeCycleStart = currentCycle
                    lsq.cyclesRemained -= 1
                    if lsq.cyclesRemained == 0:
                        # print("lsq target:" + lsq.destination + " address: " + str(lsq.address))
                        reorderBuffer.getROBEntry(lsq.destination).executeCycleEnd = currentCycle

                elif lsq.cdbcycle == 1:
                    lsq.cdbcycle -= 1

    return functionalUnit, reorderBuffer

def memoryAccess(currentCycle, functionalUnit, memory, reorderBuffer):
    checkHistory = False
    for fu in functionalUnit.fuList:
        for index, lsq in enumerate(fu.loadstorequeue):
            if lsq.opName == 'Ld':   # TODO: should check if the previous Sd has the same address?
                if lsq.busy and lsq.address is not None:
                    index2= copy.deepcopy(index)
                    while index2 > 0:        # TODO: Look back to find the latest store instruction
                        lsq2 = fu.loadstorequeue[index2-1]
                        index2 -= 1

                        if lsq2.address is not None:
                            # if lsq2.opName == 'Sd':
                                if lsq2.address == lsq.address:
                                    lsq.isInHistory = True
                                    if lsq2.opName == 'Sd':
                                        if lsq2.Vl is not None and lsq2.cdbcycle != 1:
                                            lsq.value = lsq2.Vl
                                            checkHistory = True
                                            lsq.cyclesMemRemained = 0
                                            reorderBuffer.getROBEntry(lsq.destination).memoryCycleStart = currentCycle
                                            reorderBuffer.getROBEntry(lsq.destination).memoryCycleEnd = currentCycle
                                            lsq.busy = False
                                        break
                                    elif lsq2.opName == 'Ld':
                                        if lsq2.value is not None and lsq2.cdbcycle!= 1:
                                            lsq.value = lsq2.value
                                            checkHistory = True
                                            lsq.cyclesMemRemained = 0
                                            reorderBuffer.getROBEntry(lsq.destination).memoryCycleStart = currentCycle
                                            reorderBuffer.getROBEntry(lsq.destination).memoryCycleEnd = currentCycle
                                            lsq.busy = False


                                        # reorderBuffer.getROBEntry(lsq.destination).memoryCycleStart = currentCycle
                    if lsq.cyclesRemained==0:
                        if lsq.isInHistory is False:
                            index2 = copy.deepcopy(index)
                            while index2 > 0:  # TODO: Look back to find the latest store instruction
                                lsq2 = fu.loadstorequeue[index2 - 1]
                                index2 -= 1
                                if lsq2.opName == 'Sd' and lsq2.isDone is False:
                                    return functionalUnit, memory, reorderBuffer
                                elif lsq2.opName == 'Sd' and lsq2.isDone is True and lsq2.isDoneCycle == 1:
                                    lsq2.isDoneCycle -= 1
                                    return functionalUnit, memory, reorderBuffer
                            if functionalUnit.memoryAccess is False or functionalUnit.instrMemRunning ==index:

                                # if lsq.busy and lsq.Vj is not None and lsq.Vk is not None:
                                if lsq.cyclesMemRemained == 5 and checkHistory is False:
                                    reorderBuffer.getROBEntry(lsq.destination).memoryCycleStart = currentCycle
                                    functionalUnit.memoryAccess = True
                                    functionalUnit.instrMemRunning = index
                                # if lsq.cyclesMemRemained == 1 and checkHistory is True:
                                #     reorderBuffer.getROBEntry(lsq.destination).memoryCycleStart = currentCycle
                                lsq.cyclesMemRemained -= 1
                                if lsq.cyclesMemRemained == 0:
                                    reorderBuffer.getROBEntry(lsq.destination).memoryCycleEnd = currentCycle
                                    lsq.readFromMemory(memory)
                                    lsq.busy = False
                                    functionalUnit.memoryAccess = False
                                    functionalUnit.instrMemRunning = None
                                    # lsq.clear()
                                break
    return functionalUnit, memory, reorderBuffer

def writeBack(currentCycle, commonDataBus, functionalUnit, reorderBuffer, architectureRegisterFile, instructionBuffer, copyState, branchTargetBuffer, pc, misprediction, wrongFetch):
    commonDataBus.busy = False
    for fu in functionalUnit.fuList:
        LoadStoreQueue = fu.loadstorequeue
        for lsq in LoadStoreQueue:
            if (lsq.cyclesRemained is not None) and (lsq.cyclesMemRemained is not None) and (lsq.busy is False) and (lsq.writeback is False):
                if (lsq.cyclesRemained <= 0) and (lsq.cyclesMemRemained <= 0) and (lsq.opName == 'Ld'):
                    # lsq.busy = False
                    # if commonDataBus.remainedCycle == 1:
                    reorderBuffer.getROBEntry(lsq.destination).writebackCycle = currentCycle
                    if lsq.opName == 'Ld':   # TODO: set the remaining cycle here?
                        commonDataBus.busy = True
                        commonDataBus.value = lsq.value
                        commonDataBus.address = lsq.destination
                        # commonDataBus.remainedCycle = 1
                        for robentry in reorderBuffer.list:
                            if robentry.name == lsq.destination:
                                robentry.value = lsq.value
                                robentry.ready = True
                        for fu2 in functionalUnit.fuList:
                            for lsq2 in fu2.loadstorequeue:
                                if lsq2.Qk == lsq.destination:
                                    lsq2.Vk = commonDataBus.value
                                    lsq2.Qk = None
                                    lsq2.cdbcycle = 1

                                if lsq2.opName == 'Sd' and lsq2.Ql == lsq.destination:
                                    lsq2.Vl = commonDataBus.value
                                    lsq2.Ql = None
                                    lsq2.cdbcycle = 1
                        for fu2 in functionalUnit.fuList:
                            for rs2 in fu2.reservationStation:
                                if rs2.Qj == lsq.destination:
                                    rs2.Vj = lsq.value
                                    rs2.Qj = None
                                    rs2.cdbcycle = 1
                                if rs2.Qk == lsq.destination:
                                    rs2.Vk = lsq.value
                                    rs2.Qk = None
                                    rs2.cdbcycle = 1
                        lsq.busy = False # TODO check if it is busy or ready
                        lsq.writeback = True
                        lsq.cdbcycle -= 1
                        # lsq.occupied = False
                    # elif lsq.opName == 'Ld' and commonDataBus.remainedCycle == 1:
                    #     commonDataBus.remainedCycle -= 1
                        return commonDataBus, functionalUnit, reorderBuffer, architectureRegisterFile, instructionBuffer, pc, branchTargetBuffer, misprediction, wrongFetch

        ReservationStation = fu.reservationStation
        for rs in ReservationStation:
            if rs.cyclesRemained is not None and rs.busy is True:
                if rs.cyclesRemained <= 0 and not commonDataBus.busy:
                    rs.busy = False
                    # if commonDataBus.remainedCycle == 1:
                    reorderBuffer.getROBEntry(rs.destination).writebackCycle = currentCycle
                    if rs.opName != 'Bne' and rs.opName != 'Beq':
                        result = rs.execute()
                        b = rs.destination
                        commonDataBus.busy = True       # enter CDB
                        commonDataBus.value = result
                        commonDataBus.address = b
                        for robentry in reorderBuffer.list:  # write the result back to ROB
                            if robentry.name == b:
                                robentry.value = result
                                robentry.ready = True
                                break
                        for fu2 in functionalUnit.fuList:         # update the result to RS
                            for rs2 in fu2.reservationStation:
                                # rs2 = fu2.reservationStation
                                if rs2.Qj == b:
                                    rs2.Vj = result
                                    rs2.Qj = None
                                    rs2.cdbcycle = 1
                                if rs2.Qk == b:
                                    rs2.Vk = result
                                    rs2.Qk = None
                                    rs2.cdbcycle = 1
                        for fu2 in functionalUnit.fuList:
                            for lsq2 in fu2.loadstorequeue:
                                if lsq2.Qk == rs.destination:
                                    lsq2.Vk = commonDataBus.value
                                    lsq2.Qk = None
                                    lsq2.cdbcycle = 1

                                if lsq2.opName == 'Sd' and lsq2.Ql == rs.destination:
                                    lsq2.Vl = commonDataBus.value
                                    lsq2.Ql = None
                                    lsq2.cdbcycle = 1

                        # rs.busy = False
                        rs.clear()
                        return commonDataBus, functionalUnit, reorderBuffer, architectureRegisterFile, instructionBuffer, pc, branchTargetBuffer, misprediction, wrongFetch
                    elif rs.opName == 'Bne' or rs.opName == 'Beq':     # point to the first BTB entry
                        # find the BTB entry for this instruction, check is the prediction is correct or not
                        inst = reorderBuffer.getROBEntry(rs.destination).instruction
                        predictedResult = branchTargetBuffer.findBTB(inst.address).prediction
                        # if the prediction is correct, then only need to set the corresponding ROB entry to ready and correct?
                        # do not need to update the new result to BTB
                        # clear the first copyState entry
                        if rs.execute() == predictedResult:
                            reorderBuffer.getROBEntry(rs.destination).ready = True
                            reorderBuffer.getROBEntry(rs.destination).branchPrediction = True
                            reorderBuffer.getROBEntry(rs.destination).branchTaken = predictedResult
                            CopyState.clearFirstEntry(copyState)

                        # if the prediction is not correct
                        #   1. set the corresponding ROB entry to ready and not taken
                        #   2. recover the RF from the copyState(finished)
                        #   3. flush the ROB, RS&LSQ, IB
                        #   4. recover the current pc and set the PC to the target address(finished)
                        #   5. change the prediction in BTB
                        elif rs.execute() != predictedResult:
                            misprediction = True
                            pc = copyState.list[0].resetPC
                            if rs.execute():
                                btb = branchTargetBuffer.findBTB(pc)
                                # if the original prediction is False, then change to True, otherwise change to False
                                if btb.prediction == False:
                                    btb.prediction = True
                                else:
                                    btb.prediction = False
                                pc = int(btb.targetPC)
                            elif not rs.execute():
                                btb = branchTargetBuffer.findBTB(pc)
                                # if the original prediction is False, then change to True, otherwise change to False
                                if btb.prediction == False:
                                    btb.prediction = True
                                else:
                                    btb.prediction = False
                                pc = pc + 4
                            architectureRegisterFile = copyState.list[0].resetRF
                            CopyState.clearFirstEntry(copyState)
                            reorderBuffer.getROBEntry(rs.destination).ready = True
                            reorderBuffer.getROBEntry(rs.destination).branchPrediction = False
                            reorderBuffer.getROBEntry(rs.destination).branchTaken = not predictedResult
                            removeList = reorderBuffer.flush(rs.destination)
                            # save the ROB entry that have the name in removeList
                            for i in removeList:
                                # reorderBufferPopResults = []
                                wrongFetch.append(copy.deepcopy(reorderBuffer.getROBEntry(i)))
                                reorderBuffer.getROBEntry(i).clear()
                            functionalUnit.flush(removeList)
                            instructionBuffer.clear()


                        rs.clear()
                        return commonDataBus, functionalUnit, reorderBuffer, architectureRegisterFile, instructionBuffer, pc, branchTargetBuffer, misprediction, wrongFetch

        # loadStoreQueue = fu.loadstorequeue
        # for lsq in loadStoreQueue:     # TODO: write back the value to ROB

    return commonDataBus, functionalUnit, reorderBuffer, architectureRegisterFile, instructionBuffer, pc, branchTargetBuffer, misprediction, wrongFetch


def commit(currentCycle, finished, pc, reorderBuffer, architectureRegisterFile, cycle, functionalUnit, memory, reorderBufferPopResults, misprediction, copyState):
    head = reorderBuffer.getHead()
    sd_set_flag = False
    if head.opname == '' and cycle > 1 and misprediction is False:
        finished = True
        return finished, pc, reorderBuffer, architectureRegisterFile, reorderBufferPopResults
    if head is None and cycle > 1 and misprediction is False:
        finished = True
        return finished, pc, reorderBuffer, architectureRegisterFile, reorderBufferPopResults

    if head.ready or (head.opname == 'Sd'):
        if head.opname == 'Bne' or head.opname == 'Beq':
            if pc == -1:
                finished = True     # TODO: branch prediction part?
            head.commitCycle = currentCycle
            reorderBufferPopResults.append(reorderBuffer.pop())
        else:
            for reg in architectureRegisterFile.intRegisterList:
                if reg.name == head.destination:
                    reg.value = head.value
                    if reg.robId == head.name:       # TODO: check the reset logic
                        reg.robId = None
                        reg.busy = False
                    index = reorderBuffer.head
                    for i in range(reorderBuffer.numelements - 1):
                        index += 1
                        index %= reorderBuffer.size
                        if reorderBuffer.list[index].destination == reg.name:
                            reg.robId = reorderBuffer.list[index].name
                            reg.busy = True
                            break

            for reg in architectureRegisterFile.fpRegisterList:
                if reg.name == head.destination:
                    if head.opname == 'Sd':
                        for fu in functionalUnit.fuList:
                            for index, lsq in enumerate(fu.loadstorequeue):
                                if lsq.cyclesMemRemained is not None and lsq.cyclesMemRemained >= 0 and lsq.busy and lsq.robId==head.name:
                                    if functionalUnit.memoryAccess is False or functionalUnit.instrMemRunning == index:
                                        if lsq.cyclesMemRemained == 5:
                                            reorderBuffer.getROBEntry(lsq.destination).memoryCycleStart = currentCycle  # TODO
                                            functionalUnit.memoryAccess = True
                                            functionalUnit.instrMemRunning = index
                                        lsq.cyclesMemRemained -= 1
                                        if lsq.cyclesMemRemained == 0:
                                            reorderBuffer.getROBEntry(lsq.destination).memoryCycleEnd = currentCycle
                                            functionalUnit.memoryAccess = False
                                            functionalUnit.instrMemRunning = None
                                            lsq.isDone=True
                                            # break

                                            lsq.busy = False
                                            # lsq.clear()
                                            memory.setValue(lsq.address, reg.value)
                                            reorderBuffer.getROBEntry(lsq.destination).value = lsq.address
                                            reorderBuffer.getROBEntry(lsq.destination).ready = True
                                            sd_set_flag = True
                                            if sd_set_flag:
                                                head.commitCycle = currentCycle  # str(head.memoryCycleStart) + '-' + str(head.memoryCycleEnd)
                                                head.busy = False
                                                head.ready = True
                                                popResult = reorderBuffer.pop()
                                                # print(popResult)
                                                reorderBufferPopResults.append(popResult)
                                            # break
                                            return finished, pc, reorderBuffer, architectureRegisterFile, reorderBufferPopResults
                    else:
                        reg.value = head.value
                        if head.opname == 'Ld':
                            for fu in functionalUnit.fuList:
                                for lsq in fu.loadstorequeue:
                                    if lsq.robId == head.name:
                                        lsq.isDone = True
                                        break
                        if reg.robId == head.name:       # TODO: check the reset logic
                            reg.robId = None
                            reg.busy = False
                        index = reorderBuffer.head
                        for i in range(reorderBuffer.numelements - 1):
                            index += 1
                            index %= reorderBuffer.size
                            if reorderBuffer.list[index].destination == reg.name:
                                reg.robId = reorderBuffer.list[index].name
                                reg.busy = True
                                break

            # copyState.list[0].resetRF = None
            # copyState.list[0].resetRF = architectureRegisterFile
            if len(copyState.list) != 0:
                CopyState.updateRF(copyState, architectureRegisterFile)

            if head.opname != 'Sd':
                # print(head.destination)
                head.commitCycle = currentCycle
                head.busy = False
                head.ready = True
                popResult = reorderBuffer.pop()
                # print(popResult)
                reorderBufferPopResults.append(popResult)

            # else: # head.opname == 'Sd':
            #     if sd_set_flag:
            #         head.commitCycle = currentCycle # str(head.memoryCycleStart) + '-' + str(head.memoryCycleEnd)
            #         head.busy = False
            #         head.ready = True
            #         popResult = reorderBuffer.pop()
            #         print(popResult)
            #         reorderBufferPopResults.append(popResult)
                    # sd_set_flag = False
                # or (head.opname == 'Sd' and sd_set_flag):

    return finished, pc, reorderBuffer, architectureRegisterFile, reorderBufferPopResults

def resetCDBcycles(functionalUnit):
    for fu in functionalUnit.fuList:
        for rs in fu.reservationStation:
            rs.cdbcycle = 2
        for lsq in fu.loadstorequeue:
            lsq.cdbcycle = 2
    return functionalUnit