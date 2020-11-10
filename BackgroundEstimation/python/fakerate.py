from HNL.Tools.efficiency import Efficiency

class FakeRate(Efficiency):
    
    def __init__(self, name, var, var_tex, path, bins=None, subdirs=None):
        super(FakeRate, self).__init__(name, var, var_tex, path, bins, subdirs)

    def returnFakeFactor(self, chain, l_index = None, manual_var_entry = None):
        ttl = self.evaluateEfficiency(chain, l_index, manual_var_entry)
        return ttl/(1-ttl)

    def returnFakeWeight(self, chain, flavor):
        weight = -1.
        nleptons = 0
        for i in xrange(len(chain.l_indices)):
            if not chain.l_flavor[i] == flavor: continue
            if not chain.l_istight[i]:
                weight *= -1*self.returnFakeFactor(chain, l_index = i)
                nleptons += 1

        if nleptons == 0:
            return -999.
        else:
            return weight

        