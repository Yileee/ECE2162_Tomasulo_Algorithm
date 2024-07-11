from Instruction import Instruction
from FunctionalUnit import FunctionalUnit

def readParametersFile():
    # global number_of_registers, instruction_window_size
    parameters_file = open("Parameters.txt", 'r')
    RS_size_dict = {
        'int_add': 0,
        'fp_add': 0,
        'fp_mul': 0,
    }
    for line in parameters_file.readlines():
        args = line.split()
        if args[0] == 'number_of_registers:':
            number_of_registers = int(args[1])
        elif args[0] == 'instruction_window_size:':
            instruction_window_size = int(args[1])
        elif 'int' or 'fp' in args[0]:
            data_type = args[0].split('_')[0]
            op_type = args[0].split('_')[1]
            rs_key = data_type + '_' + op_type
            RS_size_dict[rs_key] = int(args[1])
    return number_of_registers, instruction_window_size, RS_size_dict


def readUnitsFile(FU,rs_size_dict):
    units_file = open("Units.txt", 'r')
    for line in units_file.readlines():
        args = line.split()
        if args[0] == '#':
            pass
        elif len(args) == 0:
            pass
        else:
            supported_instructions = args[1].split(',')
            cycles = int(args[2])
            FU.add(FunctionalUnit(supported_instructions, cycles, rs_size_dict))
    return FU


def readProgramFile(program):
    program_file = open("Program_test.txt", 'r')
    address = 0
    for line in program_file.readlines():
        args = line.split()
        if args[0] == '#':
            pass
        elif len(args) == 0:
            pass
        else:
            # address = int(args[0].split(':')[0])
            opname = args[0]
            # destination = args[1].split(',')[0]
            # source1 = args[2].split(',')[0]
            if opname == 'Ld' or opname == 'Sd':   # Ld F2, 0(R1) - destination, offset/s1(operand/s2)
                destination = args[1].split(',')[0]
                offset = args[2].split('(')[0]
                operand = args[2].split('(')[1].split(')')[0]
                instruction = Instruction(address, opname, dest=destination, s1=offset, s2=operand)
            elif opname == 'Bne' or opname == 'Beq':  # Bne R1, R2, 10 - Rs, Rt, offset
                Rs = args[1].split(',')[0]
                Rt = args[2].split(',')[0]
                offset = args[3]
                instruction = Instruction(address, opname, Rs=Rs, Rt=Rt, s1=offset)
            else:                                      # Add F1, F2, F3 - destination, s1, s2
                destination = args[1].split(',')[0]
                operand1 = args[2].split(',')[0]
                operand2 = args[3]
                instruction = Instruction(address, opname, dest=destination, s1=operand1, s2=operand2)
            program.append(instruction)
            address += 4
    return program


if __name__ == '__main__':
    program = readProgramFile([])