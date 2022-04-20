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

luka_year_dict = {
    '2016pre' : '2016PreVFP',
    '2016post' : '2016PostVFP',
    '2017' : '2017',
    '2018' : '2018',
}


def lightLepFileName(year, data_string, flavor):
    if data_string == 'data':
        return 'fakeRateMap_'+data_string+'_'+flavor+'_'+year+'_mT.root'
    else:
        return 'fakeRateMap_'+data_string+'_'+flavor+'_'+year+'.root'

default_tau_path = lambda proc, year, selection, data_string : os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Weights', 'data', 'FakeRates', year, 'Tau', 'TauFakes'+proc+'ttl-'+selection, data_string, 'fakerate.root')
default_ele_path = lambda era, year, data_string : os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'BackgroundEstimation', 'data', 'FakeRates', era+'-'+year, lightLepFileName(luka_year_dict[year], data_string, 'electron'))
default_mu_path = lambda era, year, data_string : os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'BackgroundEstimation', 'data', 'FakeRates', era+'-'+year, lightLepFileName(luka_year_dict[year], data_string, 'muon'))

ele = 0
mu = 1
tau = 2

TAU_METHOD = 'WeightedMix'
#TAU_METHOD = 'TauFakesDY'

def returnTauFR(tau_method, chain, region = None):
    if region == None: region = chain.region

    if tau_method == 'TauFakesDY':
        return FakeRate('ttl', lambda c, i: [c.l_pt[i], abs(c.l_eta[i])], ('pt', 'eta'), default_tau_path('DY', chain.era+'-'+chain.year, chain.selection, data_dict[(chain.is_data, 'tau')]))
    elif tau_method == 'TauFakesTT':
        return FakeRate('ttl', lambda c, i: [c.l_pt[i], abs(c.l_eta[i])], ('pt', 'eta'), default_tau_path('TT', chain.era+'-'+chain.year, chain.selection, data_dict[(chain.is_data, 'tau')]))
    elif tau_method == 'WeightedMix':
        from HNL.BackgroundEstimation.getTauFakeContributions import getWeights
        return SingleFlavorFakeRateCollection([default_tau_path('DY', chain.era+'-'+chain.year, chain.selection, data_dict[(chain.is_data, 'tau')]), default_tau_path('TT', chain.era+'-'+chain.year, chain.selection, data_dict[(chain.is_data, 'tau')])], ['ttl', 'ttl'], ['DY', 'TT'], 
                                            frac_weights = getWeights(chain.era, chain.year, chain.selection, region), frac_names = ['DY', 'TT'])   
    elif tau_method == 'OSSFsplitMix':
        return SingleFlavorFakeRateCollection([default_tau_path('DY', chain.era+'-'+chain.year, chain.selection, data_dict[(chain.is_data, 'tau')]), default_tau_path('TT', chain.era+'-'+chain.year, chain.selection, data_dict[(chain.is_data, 'tau')])], ['ttl', 'ttl'], ['DY', 'TT'], method = 'OSSFsplitMix',
                                            ossf_map = {True : 'DY', False : 'TT'})  
    else:
        raise RuntimeError('Unknown method "{}"in fakeRateWeights.py'.format(tau_method))


def returnFakeRateCollection(chain, tau_method = None, region = None):
    fakerates = {}
    fakerates[ele] = FakeRateEmulator('fakeRate_electron_'+luka_year_dict[str(chain.year)], lambda c, i: [c.l_pt[i], c.l_eta[i]], ('pt', 'eta'), default_ele_path(chain.era, str(chain.year), data_dict[(chain.is_data, 'light')]))
    fakerates[mu] = FakeRateEmulator('fakeRate_muon_'+luka_year_dict[str(chain.year)], lambda c, i: [c.l_pt[i], c.l_eta[i]], ('pt', 'eta'), default_mu_path(chain.era, str(chain.year), data_dict[(chain.is_data, 'light')]))
    if tau_method is None: tau_method = TAU_METHOD
    fakerates[tau] = returnTauFR(tau_method, chain, region)

    fakerate_collection = FakeRateCollection(chain, fakerates)

    return fakerate_collection
