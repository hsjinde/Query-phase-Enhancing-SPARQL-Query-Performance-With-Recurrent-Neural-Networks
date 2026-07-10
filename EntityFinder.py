from CaculateEntityTag import combineEntity_Tag
class EntityFinder:
    def __init__(self, parsresult:list):
        self.V = []
        self.E = []
        self.R = []
        self.RR = []
        self.C = []

        for parsword in parsresult:
            if parsword.getERC() == 'RR':
                self.RR.append(parsword.getWord())
            else:
                for e in parsword.getERC():
                    if e == 'V':
                        self.V.append(parsword.getWord())
                    elif e == 'R':
                        self.R.append(parsword.getWord())
                    elif e == 'E':
                        self.E.append(parsword.getWord())
                    elif e == 'C':
                        self.C.append(parsword.getWord())
        print('所有陣列-> V:', self.V, ',', 'E:', self.E, ',', 'R:', self.R, ',', 'RR:', self.RR, ',', 'C:', self.C)

    def getV(self):
        return self.V

    def getE(self):
        return self.E

    def getR(self):
        return self.R

    def getC(self):
        return self.C

    def getRR(self):
        return self.RR
