from HNL.BackgroundEstimation.fakerate import FakeRate
from HNL.BackgroundEstimation.fakerateEmulator import FakeRateEmulator
from HNL.BackgroundEstimation.fakerateArray import loadFakeRatesWithJetBins
import os

default_tau_path = lambda year : os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'BackgroundEstimation', 'data', 'tightToLoose', year, 'DATA', 'tau')
default_ele_path = lambda year : os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'BackgroundEstimation', 'data','FakeRates', year, 'Lukav2', 'fakeRateMap_data_electron_'+year+'_mT.root')
default_mu_path = lambda year : os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'BackgroundEstimation', 'data','FakeRates', year, 'Lukav2', 'fakeRateMap_data_muon_'+year+'_mT.root')

ele = 0
mu = 1
tau = 2

class FakeRateCollection:

    def __init__(self, chain):
        self.fake_rates = {}
        self.fake_rates[ele] = FakeRateEmulator('fakeRate_electron_'+str(chain.year), lambda c, i: [c.l_pt[i], c.l_eta[i]], ('pt', 'eta'), default_ele_path(str(chain.year)))
        self.fake_rates[mu] = FakeRateEmulator('fakeRate_muon_'+str(chain.year), lambda c, i: [c.l_pt[i], c.l_eta[i]], ('pt', 'eta'), default_mu_path(str(chain.year)))
        self.fake_rates[tau] = loadFakeRatesWithJetBins('tauttl', lambda c, i: [c.l_pt[i], abs(c.l_eta[i])], ('pt', 'eta'), default_tau_path(str(chain.year)), 'tau', True)['TauFakesDY']
        self.chain = chain

    def returnFakeFactor(self, flavor, l_index = None, manual_var_entry = None):
        if flavor < 2:
            return self.fake_rates[flavor].returnFakeFactor(chain, l_index = l_index, manual_var_entry =  manual_var_entry)
        else:
            return fake_rates[flavor]['TauFakesDY'].getFakeRate('total').returnFakeFactor(chain, l_index = i, manual_var_entry = man_var)

    def getFakeWeight(self):
        weight = -1.
        nleptons = 0
        for i in xrange(len(self.chain.l_indices)):
            if not self.chain.l_istight[i]:
                if self.chain.selection in ['Luka', 'default'] and flavor == 0:
                    man_var = [min(44.9, self.chain.l_pt[i]), abs(self.chain.l_eta[i])]
                else:
                    man_var = None
                
                weight *= -1*self.returnFakeFactor(self.chain, self.chain.l_flavor[i], l_index = i, manual_var_entry = man_var)
                nleptons += 1

        if nleptons == 0:
            return 1.
        else:
            return weight
