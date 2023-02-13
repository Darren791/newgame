class HSVector(object):

    def __init__(self, ii = 0.0, jj = 0.0, kk = 0.0):
        self.ci = ii
        self.cj = jj
        self.ck = kk
    
    def i(self):
        return self.ci
    
    def j(self):
        return self.cj
    
    def k(self):
        return self.ck
    
    def __add__(self, vec: 'HSVector'):
        tmp = HSVector()
        tmp.ci = self.ci + vec.ci
        tmp.cj = self.cj + vec.cj
        tmp.ck = self.ck + vec.ck
        
        return tmp
     
    def __eq__(self, vec) -> bool:
        if self.ci == vec.ci and self.ck == vec.ck and self.cj == vec.cj:
            return True
        
        return False
    
    def __iadd__(self, vec):
        self.ci += vec.ci
        self.cj += vec.cj
        self.ck += vec.ck
        
        return self
    
    def dot_product(self, vec):
        rval = (self.ci * vec.ci) + (self.cj * vec.cj) + (self.ck * vec.ck)
        if (rval > 1):
            rval = 1
        elif (rval < -1):
            rval = -1

        return rval    
