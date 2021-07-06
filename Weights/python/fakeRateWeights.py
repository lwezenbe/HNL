from HNL.BackgroundEstimation.fakerateEmulator import FakeRateEmulator
from HNL.BackgroundEstimation.fakerateArray import SingleFlavorFakeRateCollection, FakeRateCollection
import os

default_tau_path = lambda proc, year, selection : os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'BackgroundEstimation', 'data', 'tightToLoose', year, 'DATA', 'tau', 'TauFakes'+proc+'ttl-'+selection, 'events.root')
default_ele_path = lambda year : os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'BackgroundEstimation', 'data', 'FakeRates', year, 'Lukav2', 'fakeRateMap_data_electron_'+year+'_mT.root')
default_mu_path = lambda year : os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'BackgroundEstimation', 'data', 'FakeRates', year, 'Lukav2', 'fakeRateMap_data_muon_'+year+'_mT.root')

ele = 0
mu = 1
tau = 2

TAU_METHOD = 'WeightedMix'

def returnTauFR(tau_method, chain):
    if tau_method == 'TauFakesDY':
        return FakeRate('tauttl', lambda c, i: [c.l_pt[i], c.l_eta[i]], ('pt', 'eta'), default_tau_path('DY', str(chain.year), chain.selection), subdirs = ['total'])
    elif tau_method == 'TauFakesTT':
        return FakeRate('tauttl', lambda c, i: [c.l_pt[i], c.l_eta[i]], ('pt', 'eta'), default_tau_path('TT', str(chain.year), chain.selection), subdirs = ['total'])
    elif tau_method == 'WeightedMix':
        from HNL.BackgroundEstimation.getTauFakeContributions import getWeights
        return SingleFlavorFakeRateCollection([default_tau_path('DY', str(chain.year), chain.selection), default_tau_path('TT', str(chain.year), chain.selection)], ['total/tauttl', 'total/tauttl'], ['DY', 'TT'], 
                                            frac_weights = getWeights(str(chain.year), chain.selection, chain.region), frac_names = ['DY', 'TT'])   
    elif tau_method == 'OSSFsplitMix':
        return SingleFlavorFakeRateCollection([default_tau_path('DY', str(chain.year), chain.selection), default_tau_path('TT', str(chain.year), chain.selection)], ['total/tauttl', 'total/tauttl'], ['DY', 'TT'], method = 'OSSFsplitMix',
                                            ossf_map = {True : 'DY', False : 'TT'})  
    else:
        raise RuntimeError('Unknown method "{}"in fakeRateWeights.py'.format(tau_method))


def returnFakeRateCollection(chain):
    fakerates = {}
    fakerates[ele] = FakeRateEmulator('fakeRate_electron_'+str(chain.year), lambda c, i: [c.l_pt[i], c.l_eta[i]], ('pt', 'eta'), default_ele_path(str(chain.year)))
    fakerates[mu] = FakeRateEmulator('fakeRate_muon_'+str(chain.year), lambda c, i: [c.l_pt[i], c.l_eta[i]], ('pt', 'eta'), default_mu_path(str(chain.year)))
    fakerates[tau] = returnTauFR(TAU_METHOD, chain)

    fakerate_collection = FakeRateCollection(chain, fakerates)

    return fakerate_collection