

class ReservationStation(object):
    def __init__(self):
        self.opName = ''
        self.busy = False
        self.Vj = None
        self.Vk = None
        self.Qj = None
        self.Qk = None
        self.destination = None
        self.cyclesRemained = None
        self.cdbcycle=2

    def clear(self):
        self.opName = ''
        self.busy = False
        self.Vj = None
        self.Vk = None
        self.Qj = None
        self.Qk = None
        self.destination = None
        self.cyclesRemained = None

    def execute(self):
        if (self.opName == 'Add') or (self.opName =='Addi') or (self.opName =='Add.d'):
            return self.Vj + self.Vk
        elif (self.opName == 'Sub') or (self.opName == 'Sub.d'):
            return self.Vj - self.Vk
        elif self.opName == 'Mult.d':
            return self.Vj * self.Vk
        elif self.opName == 'Div':
            # print('Div')
            # print(self.destination + " " + str(self.Vj) + "/" + str(self.Vk) + "=" + str(self.Vj / self.Vk))
            return self.Vj / self.Vk
        elif self.opName == 'Bne':    #True means branch taken
            return self.Vj != self.Vk
        elif self.opName == 'Beq':
            return self.Vj == self.Vk

        # elif self.opName == 'Ld':    # TODO: check Load Store Queue
        #     return self.Vj


    def toString(self):
        st = ' '
        if self.busy:
            st = self.opName + ' '
            if self.opName == 'Ld':
                st += ' '
            if self.Vj is None:
                st += self.Qj + ' '
            else:
                st += str(self.Vj) + '  '
            if self.Vk is None:
                if self.Qk is None:
                    st += '-  '
                else:
                    st += self.Qk + ' '
            else:
                st += str(self.Vk) + '  '
            st += self.destination
        return st