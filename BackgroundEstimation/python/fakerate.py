from HNL.Tools.histogram import Histogram
from HNL.Tools.efficiency import Efficiency
from HNL.Tools.outputTree import EfficiencyTree

class FakeRate(Efficiency):
    
    def __init__(self, name, var, var_tex, path, bins=None, subdirs=None):
        super(FakeRate, self).__init__(name, var, var_tex, path, bins, subdirs)

    def returnFakeFactor(self, chain, l_index = None, manual_var_entry = None):
        ttl = self.evaluateEfficiency(chain, l_index, manual_var_entry)
        return ttl/(1-ttl)

    #
    # Only to be used in case only one flavor contained in a single fake rate
    #
    def returnFakeWeight(self, chain, flavor):
        weight = -1.
        nleptons = 0
        for i in xrange(len(chain.l_indices)):
            if not chain.l_flavor[i] == flavor: continue
            if not chain.l_istight[i]:
                if chain.selection in ['Luka', 'default'] and flavor in [0, 1]:
                    man_var = [min(44.9, chain.l_pt[i]), abs(chain.l_eta[i])]
                else:
                    man_var = None
                weight *= -1*self.returnFakeFactor(chain, l_index = i, manual_var_entry = man_var)
                nleptons += 1

        if nleptons == 0:
            return 1.
        else:
            return weight

    @classmethod
    def getFakeRateFromTree(cls, name, path, vname, bins, var = None, condition = None):
        fakerate_tree = FakeRateTree(name, path)
        return fakerate_tree.getFakeRateObject(vname, bins, var, condition)


class FakeRateTree(EfficiencyTree):

    def __init__(self, name, path, branches = None):
        super(FakeRateTree, self).__init__(name, path, branches)

    def getFakeRateObject(self, vname, bins, var = None, condition = None):
        fakerate_object = FakeRate(self.name, var, None, self.path, bins)
        self.setBins(bins)
        fakerate_object.efficiency_num = Histogram(self.getNumerator(vname, self.name, condition))
        fakerate_object.efficiency_denom = Histogram(self.getDenominator(vname, self.name, condition))
        #fakerate_object.efficiency = Histogram(self.getEfficiency(vname, self.name, condition))
        return fakerate_object
