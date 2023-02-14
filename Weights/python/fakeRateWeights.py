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
default_ele_path = lambda era, year, data_string : os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Weights', 'data', 'FakeRates', era+'-'+year, 'Electron', lightLepFileName(luka_year_dict[year], data_string, 'electron'))
default_mu_path = lambda era, year, data_string : os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Weights', 'data', 'FakeRates', era+'-'+year, 'Muon', lightLepFileName(luka_year_dict[year], data_string, 'muon'))

ele = 0
mu = 1
tau = 2

TAU_METHOD = 'WeightedMix'
#TAU_METHOD = 'TauFakesDY'


class FakeRateWeighter:
    
    def __init__(self, chain, region, tau_method = None):
        self.tau_method = tau_method if tau_method is not None else TAU_METHOD
        self.region = region
        self.fake_collection = self.returnFakeRateCollection(chain)

    def returnFakeRateCollection(self, chain):
        fakerates = {}
        fakerates[ele] = FakeRateEmulator('fakeRate_electron_'+luka_year_dict[str(chain.year)], lambda c, i: [c.l_pt[i], c.l_eta[i]], ('pt', 'eta'), default_ele_path(chain.era, str(chain.year), data_dict[(chain.is_data, 'light')]))
        fakerates[mu] = FakeRateEmulator('fakeRate_muon_'+luka_year_dict[str(chain.year)], lambda c, i: [c.l_pt[i], c.l_eta[i]], ('pt', 'eta'), default_mu_path(chain.era, str(chain.year), data_dict[(chain.is_data, 'light')]))
        if not chain.obj_sel['notau']:
            fakerates[tau] = self.returnTauFR(chain)
    
        fakerate_collection = FakeRateCollection(chain, fakerates)
    
        return fakerate_collection

    def returnTauFR(self, chain):
        if self.tau_method == 'TauFakesDY':
            return FakeRate('ttl', lambda c, i: [c.l_pt[i], abs(c.l_eta[i])], ('pt', 'eta'), default_tau_path('DY', chain.era+'-'+chain.year, chain.selection, data_dict[(chain.is_data, 'tau')]))
        elif self.tau_method == 'TauFakesTT':
            return FakeRate('ttl', lambda c, i: [c.l_pt[i], abs(c.l_eta[i])], ('pt', 'eta'), default_tau_path('TT', chain.era+'-'+chain.year, chain.selection, data_dict[(chain.is_data, 'tau')]))
        elif self.tau_method == 'WeightedMix':
            from HNL.BackgroundEstimation.getTauFakeContributions import getWeights
            return SingleFlavorFakeRateCollection([default_tau_path('DY', chain.era+'-'+chain.year, chain.selection, data_dict[(chain.is_data, 'tau')]), default_tau_path('TT', chain.era+'-'+chain.year, chain.selection, data_dict[(chain.is_data, 'tau')])], ['ttl', 'ttl'], ['DY', 'TT'], 
                                                frac_weights = getWeights(chain.era, chain.year, chain.selection, self.region), frac_names = ['DY', 'TT'])   
        elif self.tau_method == 'OSSFsplitMix':
            return SingleFlavorFakeRateCollection([default_tau_path('DY', chain.era+'-'+chain.year, chain.selection, data_dict[(chain.is_data, 'tau')]), default_tau_path('TT', chain.era+'-'+chain.year, chain.selection, data_dict[(chain.is_data, 'tau')])], ['ttl', 'ttl'], ['DY', 'TT'], method = 'OSSFsplitMix',
                                                ossf_map = {True : 'DY', False : 'TT'})  
        else:
            raise RuntimeError('Unknown method "{}"in fakeRateWeights.py'.format(tau_method))

    def returnFakeRateWeight(self, chain, syst = 'nominal'):
    #    print syst, self.fake_collection.getFakeWeight(), self.returnNonpromptSyst(chain, syst)
        return self.fake_collection.getFakeWeight() * self.returnNonpromptSyst(chain, syst)

    def returnNonpromptSyst(self, chain, syst_name = 'nominal'):
        if syst_name == 'nominal':
            return 1.
        elif 'tau' in syst_name:
            for i, f in enumerate(chain.l_flavor):
                if f == 2 and not chain.l_istight[i]:
                    return 1.3 if 'up' in syst_name else 0.7
            return 1.

        elif 'muon' or 'electron' in syst_name:
            leading_light_index = -1
            leading_light_nonprompt_index = -1
            for i, f in enumerate(chain.l_flavor):
                if f == 2: continue
                if leading_light_index == -1: leading_light_index = i
                if not chain.l_istight[i] and chain.l_isFO[i]:
                    if leading_light_nonprompt_index == -1: leading_light_nonprompt_index = i
            
            if leading_light_index == -1 or leading_light_nonprompt_index == -1:
                return 1.
            elif chain.l_flavor[leading_light_nonprompt_index] == 0:
                if 'electron' in syst_name:
                    if chain.l_pt[leading_light_index] < 35:
                        return 1.15 if 'up' in syst_name else 0.85
                    if chain.l_pt[leading_light_index] < 55:
                        return 1.3 if 'up' in syst_name else 0.7
                    else:
                        return 1.5 if 'up' in syst_name else 0.5
            
                else:
                    return 1. 
            elif chain.l_flavor[leading_light_nonprompt_index] == 1:
                if 'muon' in syst_name:
                    return 1.3 if 'up' in syst_name else 0.7
            
                else:
                    return 1. 
        else:
            raise RuntimeError("Unknown syst")
    
    
    
