from HNL.BackgroundEstimation.fakerate import FakeRate
from HNL.BackgroundEstimation.fakerateEmulator import FakeRateEmulator
from HNL.BackgroundEstimation.fakerateArray import SingleFlavorFakeRateCollection, FakeRateCollection
import os

data_dict = {
    (True, 'tau') : 'DATA',
    (False, 'tau') : 'MC',
    (True, 'light') : 'data',
    (False, 'light') : 'MC'
}

year_dict = {
    '2016': '2016',
    '2016pre': '2016',
    '2016post': '2016',
    '2017': '2017',
    '2018': '2018',
}

default_tau_path = lambda proc, year, selection, data_string : os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'BackgroundEstimation', 'data', 'tightToLoose', year, data_string, 'tau', 'TauFakes'+proc+'ttl-'+selection, proc, 'events.root')
default_ele_path = lambda era, year, data_string : os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'BackgroundEstimation', 'data', 'FakeRates', era+'-'+year, 'Lukav2', 'fakeRateMap_'+data_string+'_electron_'+year+'_'+'mT' if data_string=='data' else 'fakeRateMap_'+data_string+'_electron_'+year+'.root')
default_mu_path = lambda era, year, data_string : os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'BackgroundEstimation', 'data', 'FakeRates', era+'-'+year, 'Lukav2', 'fakeRateMap_'+data_string+'_muon_'+year+'_'+'mT' if data_string=='data' else 'fakeRateMap_'+data_string+'_muon_'+year+'.root')

ele = 0
mu = 1
tau = 2

# TAU_METHOD = 'WeightedMix'
TAU_METHOD = 'TauFakesDY'

def returnTauFR(tau_method, chain):
    #
    # Go back to first part once all fake rates have been estimated
    #
    # if tau_method == 'TauFakesDY':
    #     return FakeRate('tauttl', lambda c, i: [c.l_pt[i], c.l_eta[i]], ('pt', 'eta'), default_tau_path('DY', chain.era+'-'+chain.year, chain.selection), subdirs = ['total'])
    # elif tau_method == 'TauFakesTT':
    #     return FakeRate('tauttl', lambda c, i: [c.l_pt[i], c.l_eta[i]], ('pt', 'eta'), default_tau_path('TT', chain.era+'-'+chain.year, chain.selection), subdirs = ['total'])
    # elif tau_method == 'WeightedMix':
    #     from HNL.BackgroundEstimation.getTauFakeContributions import getWeights
    #     return SingleFlavorFakeRateCollection([default_tau_path('DY', chain.era+'-'+chain.year, chain.selection), default_tau_path('TT', chain.era+'-'+chain.year, chain.selection)], ['total/tauttl', 'total/tauttl'], ['DY', 'TT'], 
    #                                         frac_weights = getWeights(chain.era+'-'+chain.year, chain.selection, chain.region), frac_names = ['DY', 'TT'])   
    # elif tau_method == 'OSSFsplitMix':
    #     return SingleFlavorFakeRateCollection([default_tau_path('DY', chain.era+'-'+chain.year, chain.selection), default_tau_path('TT', chain.era+'-'+chain.year, chain.selection)], ['total/tauttl', 'total/tauttl'], ['DY', 'TT'], method = 'OSSFsplitMix',
    #                                         ossf_map = {True : 'DY', False : 'TT'})  
    # else:
    #     raise RuntimeError('Unknown method "{}"in fakeRateWeights.py'.format(tau_method))


    if tau_method == 'TauFakesDY':
        return FakeRate('tauttl', lambda c, i: [c.l_pt[i], c.l_eta[i]], ('pt', 'eta'), default_tau_path('DY', chain.era+'-'+chain.year, chain.selection, data_dict[(chain.is_data, 'tau')]), subdirs = ['total'])
    elif tau_method == 'TauFakesTT':
        return FakeRate('tauttl', lambda c, i: [c.l_pt[i], c.l_eta[i]], ('pt', 'eta'), default_tau_path('TT', chain.era+'-'+chain.year, chain.selection, data_dict[(chain.is_data, 'tau')]), subdirs = ['total'])
    elif tau_method == 'WeightedMix':
        from HNL.BackgroundEstimation.getTauFakeContributions import getWeights
        return SingleFlavorFakeRateCollection([default_tau_path('DY', 'prelegacy-'+chain.year, chain.selection, data_dict[(chain.is_data, 'tau')]), default_tau_path('TT', 'prelegacy-'+chain.year, chain.selection, data_dict[(chain.is_data, 'tau')])], ['total/tauttl', 'total/tauttl'], ['DY', 'TT'], 
                                            frac_weights = getWeights('prelegacy', chain.year, chain.selection, chain.region), frac_names = ['DY', 'TT'])   
    elif tau_method == 'OSSFsplitMix':
        return SingleFlavorFakeRateCollection([default_tau_path('DY', 'prelegacy-'+chain.year, chain.selection, data_dict[(chain.is_data, 'tau')]), default_tau_path('TT', 'prelegacy-'+chain.year, chain.selection, data_dict[(chain.is_data, 'tau')])], ['total/tauttl', 'total/tauttl'], ['DY', 'TT'], method = 'OSSFsplitMix',
                                            ossf_map = {True : 'DY', False : 'TT'})  
    else:
        raise RuntimeError('Unknown method "{}"in fakeRateWeights.py'.format(tau_method))


def returnFakeRateCollection(chain):
    fakerates = {}
    fakerates[ele] = FakeRateEmulator('fakeRate_electron_'+year_dict[str(chain.year)], lambda c, i: [c.l_pt[i], c.l_eta[i]], ('pt', 'eta'), default_ele_path(chain.era, str(chain.year), data_dict[(chain.is_data, 'light')]))
    fakerates[mu] = FakeRateEmulator('fakeRate_muon_'+year_dict[str(chain.year)], lambda c, i: [c.l_pt[i], c.l_eta[i]], ('pt', 'eta'), default_mu_path(chain.era, str(chain.year), data_dict[(chain.is_data, 'light')]))
    fakerates[tau] = returnTauFR(TAU_METHOD, chain)

    fakerate_collection = FakeRateCollection(chain, fakerates)

    return fakerate_collection