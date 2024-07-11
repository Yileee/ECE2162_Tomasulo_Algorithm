

class CommonDataBus(object):
    def __init__(self):
        self.value = None
        self.address = None
        self.busy = False
       # self.remainedCycle = 1 # if the remainedCycle is 0, then can set the value to CDB

    def toString(self):
        st ='Common Data Bus\n'
        if self.busy:
            st += str(self.value) + ' ' + self.address
        return st