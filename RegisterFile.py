from Register import Register


class RegisterFile(object):
    def __init__(self, num_of_registers):
        self.size = num_of_registers
        self.intRegPath = r'./int_register.txt'
        self.fpRegPath = r'./fp_register.txt'

        # Initialize all integer registers to zero
        self.intRegisterList = [Register(f"R{i}", 0) for i in range(self.size)]


        # Update integer registers with values from the config file
        with open(self.intRegPath, 'r') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip().split(':')
                reg_num = int(line[0][1:])  # Assuming register names are like R0, R1, etc.
                if 0 <= reg_num < self.size:
                    self.intRegisterList[reg_num] = Register(line[0], int(line[1]))

        # Initialize all floating-point registers to zero
        self.fpRegisterList = [Register(f"F{i}", 0.0) for i in range(self.size)]

        # Update floating-point registers with values from the config file
        with open(self.fpRegPath, 'r') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip().split(':')
                reg_num = int(line[0][1:])  # Assuming register names are like F0, F1, etc.
                if 0 <= reg_num < self.size:
                    self.fpRegisterList[reg_num] = Register(line[0], float(line[1]))


    def getROBID(self, name):
        # print("getROBID: Name is " + name)
        for register in self.intRegisterList:
            if register.name == name:
                # print("getROBID: Found " + register.robId + " in intRegisterList")
                return register.robId
        for register in self.fpRegisterList:
            if register.name == name:
                # print("getROBID: Found " + register.robId + " in fpRegisterList")
                return register.robId
        return None

    def flush(self,list):
        for register in self.intRegisterList:
            for name in list:
                if register.robId == name:
                    register.clear()

    def toString(self):
        st = 'Registers\n'
        for reg in self.intRegisterList:
            st += reg.toString() + '\n'
        for reg in self.fpRegisterList:
            st += reg.toString() + '\n'
        return st


if __name__ == '__main__':
    registerFile = RegisterFile(16)
    print(registerFile.toString())
