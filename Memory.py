class Memory(object):
    def __init__(self):
        m_path = r'./memory.txt'
        self.memory = {}
        with open(m_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line[0] != 'M':
                    continue
                line = line.strip()
                m_address = int(line.split('[')[1].split(']')[0])
                m_value = int(line.split(']')[-1])
                self.memory[m_address] = m_value

    def getValue(self, address):
        return self.memory[address]

    def setValue(self, address, value):
        self.memory[address] = value

    def toString(self):
        st = 'Memory\n'
        for address in self.memory:
            st += str(address) + ': ' + str(self.memory[address]) + '\n'
        return st

