

class Register(object):
    def __init__(self, n, v):
        # self.name = 'R' + str(i)
        self.name = n
        self.value = v
        self.robId = None
        self.busy = False
        # self.Predicting = False
        # self.OriginalValue = None
        # self.OriginalRobId = None

    def clear(self):
        self.robId = None
        self.busy = False

    def toString(self):
        st = self.name + ': '
        if self.value is None:
            st += '-   '
        else:
            st += str(self.value) + ' '
        if self.robId is None:
            st += '-'
        else:
            st += self.robId
        return st
