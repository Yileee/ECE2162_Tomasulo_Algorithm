from collections import deque
from ReadFile import *
from Tomasulo import *
from Instruction import Instruction, InstructionBuffer
from ReservationStation import ReservationStation
from RegisterFile import RegisterFile
from FunctionalUnit import FunctionalUnit, FunctionalUnits
from CommonDataBus import CommonDataBus
from ReorderBuffer import ReorderBuffer
from Memory import Memory
from BranchTargetBuffer import BranchTargetBuffer
from CopyState import CopyState
from LoadStoreQueue import LoadStoreQueue


# from Register import Register


def print_report():
    global cycles
    report_file = open("Report.txt", "a")
    report_file.write("------------------------\n")
    report_file.write("CYCLE " + str(cycles) + '\n')
    report_file.write(IB.toString() + '\n')
    report_file.write("CYCLE " + str(cycles) + '\n')
    report_file.write(RF.toString() + '\n')
    report_file.write("CYCLE " + str(cycles) + '\n')
    report_file.write(FU.toString() + '\n')
    report_file.write("CYCLE " + str(cycles) + '\n')
    report_file.write(ROB.toString() + '\n')
    report_file.write("CYCLE " + str(cycles) + '\n')
    report_file.write(CDB.toString() + '\n')
    report_file.write("CYCLE " + str(cycles) + '\n')
    report_file.write(MM.toString() + '\n')
    report_file.close()


if __name__ == '__main__':
    PC = 0
    number_of_registers = 0
    instruction_window_size = 0
    program = []
    LSQ = []
    wrongFetch = []
    finished = False

    number_of_registers, instruction_window_size, rs_size_dict = readParametersFile()
    MM = Memory()
    FU = FunctionalUnits()
    CDB = CommonDataBus()
    FU = readUnitsFile(FU, rs_size_dict)
    program = readProgramFile(program)
    BTB = BranchTargetBuffer()
    CS = CopyState()

    IB = InstructionBuffer(instruction_window_size)
    RF = RegisterFile(number_of_registers)
    ROB = ReorderBuffer(64)
    # ROB = ReorderBuffer(len(FU.fuList))
    cycles = 1
    misprediction = False
    recoverCycles = 1
    rf = open("Report.txt", "w")
    rf.close()

    ROB_POP_RESULTS = []

    while (not finished) and (PC != -1):  # before: WB Com fetch issue execute memory
        finished, PC, ROB, RF, ROB_POP_RESULTS = commit(cycles, finished, PC, ROB, RF, cycles, FU, MM, ROB_POP_RESULTS, misprediction, CS)
        CDB, FU, ROB, RF, IB, PC, BTB, misprediction, wrongFetch = writeBack(cycles, CDB, FU, ROB, RF, IB, CS, BTB, PC, misprediction, wrongFetch)
        # finished, PC, ROB, RF, ROB_POP_RESULTS = commit(cycles, finished, PC, ROB, RF, cycles, FU, MM, ROB_POP_RESULTS)
        if not misprediction:
            IB, PC, BTB = fetch(IB, PC, program, BTB)
        elif misprediction:
            if recoverCycles > 0:
                recoverCycles -= 1
            elif recoverCycles == 0:  # reset
                misprediction = False
                recoverCycles = 1
                IB, PC, BTB = fetch(IB, PC, program, BTB)
        FU, MM, ROB = memoryAccess(cycles, FU, MM, ROB)
        FU, ROB = execute(cycles, FU, MM, ROB, CDB)
        if not IB.isEmpty():
            ROB, IB, FU, RF = issue(cycles, ROB, IB, PC, FU, RF, CS)  # delete output PC
        # FU, ROB = execute(cycles, FU, MM, ROB)
        # FU,MM, ROB = memoryAccess(cycles, FU, MM, ROB)
        print_report()
        cycles += 1
        FU = resetCDBcycles(FU)
        # if cycles >= 100:
        #     print("cycles exceeded 100")
        #     finished = True
        #     break

    if finished:
        # print a table inside the ROB_POP_RESULTS
        print("finished")
        # Print the table header
        print(
            f"{'Name':7} {'Opname':10} {'Instruction':12} {'Value':5} {'Issue':6} {'Exec':10} {'Mem':10} {'Writeback':11} {'Commit':6}")

        # Print a horizontal line
        print("-" * 88)  # Adjust the number to match the length of your header

        for item in ROB_POP_RESULTS:
            item_name = item.name
            item_opname = item.opname
            item_destination = item.destination
            item_instruction = str(item.instruction.destination) + ' ' + str(item.instruction.source1) + ' ' + str(item.instruction.source2)
            item_value = str(item.value)
            item_issueCycle = str(item.issueCycle)
            item_executeCycle = str(item.executeCycleStart) if item.executeCycleEnd == item.executeCycleStart else str(
                item.executeCycleStart) + '-' + str(item.executeCycleEnd)
            item_memoryCycle = str(item.memoryCycleStart) if item.memoryCycleEnd == item.memoryCycleStart else str(
                item.memoryCycleStart) + '-' + str(item.memoryCycleEnd)
            item_writebackCycle = str(item.writebackCycle)
            item_commitCycle = str(item.commitCycle) if item_opname != 'Sd' else item_memoryCycle

            if item_opname == 'Bne' or item_opname == 'Beq':
                item_destination = ' '
                if item.branchTaken:
                    item_value = 'T'
                else:
                    item_value = 'NT'
                # item_value = ' '
                item_instruction = str(item.instruction.Rs) + ' ' + str(item.instruction.Rt) + ' ' + str(item.instruction.source1)
            print(
                f"{item_name:<7} "
                f"{item_opname:<10}"
                f"{item_instruction:<12} "
                f"{str(item_value):<5} "
                f"{str(item_issueCycle):<6} "
                f"{str(item_executeCycle):<10} "
                f"{str(item_memoryCycle):<10} "
                f"{str(item_writebackCycle):<11} "
                f"{str(item_commitCycle):<6}")

        print("--- Integer Registers ---")

        # Printing each register in the desired format
        for i, reg in enumerate(RF.intRegisterList):
            end_char = "\n" if (i + 1) % 8 == 0 else "\t"
            print(f"{reg.name}: {reg.value:<10}", end=end_char)

        print("--- Floating Point Registers ---")

        # Printing each register in the desired format
        for i, reg in enumerate(RF.fpRegisterList):
            end_char = "\n" if (i + 1) % 8 == 0 else "\t"
            print(f"{reg.name}: {reg.value:<10}", end=end_char)

        print("--- Memory ---")

        # Printing each register in the desired format
        for index, value in MM.memory.items():
            print(f"MEM[{index}]: {value}")

        print("--- Wrong Fetch ---")
        for item in wrongFetch:
            item_name = item.name
            item_opname = item.opname
            item_destination = item.destination
            item_instruction = str(item.instruction.destination) + ' ' + str(item.instruction.source1) + ' ' + str(item.instruction.source2)

            if item_opname == 'Bne' or item_opname == 'Beq':
                item_destination = ' '
                if item.branchTaken:
                    item_value = 'T'
                else:
                    item_value = 'NT'
                # item_value = ' '
                item_instruction = str(item.instruction.Rs) + ' ' + str(item.instruction.Rt) + ' ' + str(item.instruction.source1)
            print(
                f"{item_name:<7} "
                f"{item_opname:<10}"
                f"{item_instruction:<12} ")