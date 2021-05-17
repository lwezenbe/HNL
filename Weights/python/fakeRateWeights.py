from HNL.BackgroundEstimation.fakerateEmulator import FakeRateEmulator
from HNL.BackgroundEstimation.fakerateArray import loadFakeRatesWithJetBins, FakeRateCollection
import os

default_tau_path = lambda year : os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'BackgroundEstimation', 'data', 'tightToLoose', year, 'DATA', 'tau')
default_ele_path = lambda year : os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'BackgroundEstimation', 'data', 'FakeRates', year, 'Lukav2', 'fakeRateMap_data_electron_'+year+'_mT.root')
default_mu_path = lambda year : os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'BackgroundEstimation', 'data', 'FakeRates', year, 'Lukav2', 'fakeRateMap_data_muon_'+year+'_mT.root')

ele = 0
mu = 1
tau = 2

#TODO Change to proper FakeRate for taus
def returnFakeRateCollection(chain):
    fakerates = {}
    fakerates[ele] = FakeRateEmulator('fakeRate_electron_'+str(chain.year), lambda c, i: [c.l_pt[i], c.l_eta[i]], ('pt', 'eta'), default_ele_path(str(chain.year)))
    fakerates[mu] = FakeRateEmulator('fakeRate_muon_'+str(chain.year), lambda c, i: [c.l_pt[i], c.l_eta[i]], ('pt', 'eta'), default_mu_path(str(chain.year)))
    fakerates[tau] = loadFakeRatesWithJetBins('tauttl', lambda c, i: [c.l_pt[i], abs(c.l_eta[i])], ('pt', 'eta'), default_tau_path(str(chain.year)), 'tau', True)['TauFakesDY'].getFakeRate('total')

    fakerate_collection = FakeRateCollection(chain, fakerates)

    return fakerate_collection