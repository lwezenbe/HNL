import numpy as np
from HNL.ObjectSelection.electronSelector import isLooseElectron
from HNL.ObjectSelection.muonSelector import isLooseMuon
from HNL.Tools.helpers import deltaR

#
# List of all tau ID algorithms so we can easily switch algorithm whenever we want
# After you select one particular algorithm to use, put correct string in default_algo var
#
#            algo, WP
tau_id_WP = {('MVA2017v2', 'none') : lambda c : np.ones(c._nL, dtype=bool),  
            ('MVA2017v2', 'vloose') : lambda c : c._lPOGVeto,
            ('MVA2017v2', 'loose') : lambda c : c._lPOGLoose,
            ('MVA2017v2', 'medium') : lambda c : c._lPOGMedium,
            ('MVA2017v2', 'tight') : lambda c : c._lPOGTight,
            ('MVA2017v2', 'vtight') : lambda c : c._tauPOGVTight2017v2,

            ('MVA2017v2New', 'none') : lambda c : np.ones(c._nL, dtype=bool),
            ('MVA2017v2New', 'vloose') : lambda c : c._tauVLooseMvaNew2017v2,
            ('MVA2017v2New', 'loose') : lambda c : c._tauLooseMvaNew2017v2,
            ('MVA2017v2New', 'medium') : lambda c : c._tauMediumMvaNew2017v2,
            ('MVA2017v2New', 'tight') : lambda c : c._tauTightMvaNew2017v2,
            ('MVA2017v2New', 'vtight') : lambda c : c._tauVTightMvaNew2017v2,

            ('deeptauVSjets', 'none') : lambda c : np.ones(c._nL, dtype=bool),
            ('deeptauVSjets', 'vvvloose') : lambda c : c._tauVVVLooseDeepTauVsJets,
            ('deeptauVSjets', 'vvloose') : lambda c : c._tauVVLooseDeepTauVsJets,
            ('deeptauVSjets', 'vloose') : lambda c : c._tauVLooseDeepTauVsJets,
            ('deeptauVSjets', 'loose') : lambda c : c._tauLooseDeepTauVsJets,
            ('deeptauVSjets', 'medium') : lambda c : c._tauMediumDeepTauVsJets,
            ('deeptauVSjets', 'tight') : lambda c : c._tauTightDeepTauVsJets,
            ('deeptauVSjets', 'vtight') : lambda c : c._tauVTightDeepTauVsJets,
            ('deeptauVSjets', 'vvtight') : lambda c : c._tauVVTightDeepTauVsJets,

            #From here on very outdated WP, purely there for showing that the new ones are much better
            ('MVA2015', 'none') : lambda c : np.ones(c._nL, dtype=bool),
            ('MVA2015', 'vloose') : lambda c : c._tauPOGVLoose2015,
            ('MVA2015', 'loose') : lambda c : c._tauPOGLoose2015,
            ('MVA2015', 'medium') : lambda c : c._tauPOGMedium2015,
            ('MVA2015', 'tight') : lambda c : c._tauPOGTight2015,
            ('MVA2015', 'vtight') : lambda c : c._tauPOGVTight2015,
            
            ('MVA2015New', 'none') : lambda c : np.ones(c._nL, dtype=bool),
            ('MVA2015New', 'vloose') : lambda c : c._tauVLooseMvaNew2015,
            ('MVA2015New', 'loose') : lambda c : c._tauLooseMvaNew2015,
            ('MVA2015New', 'medium') : lambda c : c._tauMediumMvaNew2015,
            ('MVA2015New', 'tight') : lambda c : c._tauTightMvaNew2015,
            ('MVA2015New', 'vtight') : lambda c : c._tauVTightMvaNew2015,
            
            
            }

tau_eleDiscr_WP = {('againstElectron', 'none') : lambda c : np.ones(c._nL, dtype=bool),
                ('againstElectron', 'loose') : lambda c : c._tauEleVetoLoose,
                ('againstElectron', 'tight') : lambda c : c._tauEleVetoTight,
            
            ('deeptauVSe', 'none') : lambda c : np.ones(c._nL, dtype=bool),
            ('deeptauVSe', 'vvvloose') : lambda c : c._tauVVVLooseDeepTauVsEle,
            ('deeptauVSe', 'vvloose') : lambda c : c._tauVVLooseDeepTauVsEle,
            ('deeptauVSe', 'vloose') : lambda c : c._tauVLooseDeepTauVsEle,
            ('deeptauVSe', 'loose') : lambda c : c._tauLooseDeepTauVsEle,
            ('deeptauVSe', 'medium') : lambda c : c._tauMediumDeepTauVsEle,
            ('deeptauVSe', 'tight') : lambda c : c._tauTightDeepTauVsEle,
            ('deeptauVSe', 'vtight') : lambda c : c._tauVTightDeepTauVsEle,
            ('deeptauVSe', 'vvtight') : lambda c : c._tauVVTightDeepTauVsEle,
                }
            
tau_muonDiscr_WP = {('againstMuon', 'none') : lambda c : np.ones(c._nL, dtype=bool),
                ('againstMuon', 'loose') : lambda c : c._tauMuonVetoLoose,
                ('againstMuon', 'tight') : lambda c : c._tauMuonVetoTight,
           
            ('deeptauVSmu', 'vloose') : lambda c : c._tauVLooseDeepTauVsMu,
            ('deeptauVSmu', 'loose') : lambda c : c._tauLooseDeepTauVsMu,
            ('deeptauVSmu', 'medium') : lambda c : c._tauMediumDeepTauVsMu,
            ('deeptauVSmu', 'tight') : lambda c : c._tauTightDeepTauVsMu,
                }

tau_DMfinding = {'MVA2017v2' : lambda c : c._decayModeFinding,
          'MVA2017v2New' : lambda c : c._decayModeFindingNew,
          'MVA2015' : lambda c : c._decayModeFinding,
          'MVA2015New' : lambda c : c._decayModeFindingNew,
          'deeptauVSjets' : lambda c : c._decayModeFindingDeepTau,
}

default_id_algo = 'MVA2017v2'
default_eleDiscr_algo = 'againstElectron'
default_muonDiscr_algo = 'againstMuon'

def isCleanFromLightLeptons(chain, index):
    
    for l in xrange(chain._nLight):
        if chain._lFlavor == 1 and not isLooseMuon(chain, l):    continue
        if chain._lFlavor == 0 and not isLooseElectron(chain, l):    continue
        if deltaR(chain._lEta[l], chain._lEta[index], chain._lPhi[l], chain._lPhi[index]) < 0.4: return False
    return True
        

def isLooseTau(chain, index, algo_iso = default_id_algo, algo_ele = default_eleDiscr_algo, algo_mu = default_muonDiscr_algo):
    
    if chain._lFlavor[index] != 2:              return False
    if not tau_DMfinding[algo_iso](chain)[index]:   return False
    if not tau_id_WP[(algo_iso, 'vloose')](chain)[index]:   return False
    if not isCleanFromLightLeptons(chain, index):       return False
    if not tau_eleDiscr_WP[(algo_ele, 'loose')](chain)[index]:    return False
    if not tau_muonDiscr_WP[(algo_mu, 'loose')](chain)[index]:    return False
    return True

def isFOTau(chain, index, algo = default_id_algo, algo_ele = default_eleDiscr_algo, algo_mu = default_muonDiscr_algo):
    
    if not isLooseTau(chain, index, algo, algo_ele, algo_mu):              return False
    if not tau_id_WP[(algo, 'medium')](chain)[index]:   return False
    return True


def isTightTau(chain, index, algo = default_id_algo, algo_ele = default_eleDiscr_algo, algo_mu = default_muonDiscr_algo): 
    
    if not isFOTau(chain, index, algo, algo_ele, algo_mu):              return False
    if not tau_id_WP[(algo, 'tight')](chain)[index]:   return False
    return True


# Test function only used in compareTauID
def isGeneralTau(chain, index, algo_iso, iso_WP, algo_ele, ele_WP, algo_mu, mu_WP, needDMfinding = True):
    
    if chain._lFlavor[index] != 2:              return False
    if algo_iso != 'none' and not tau_id_WP[(algo_iso, iso_WP)](chain)[index]:   return False
    if needDMfinding:
        if algo_iso == 'none': algo_iso = default_id_algo
        if not tau_DMfinding[algo_iso](chain)[index]:   return False
    if not isCleanFromLightLeptons(chain, index):       return False
    if algo_mu != 'none' and not tau_eleDiscr_WP[(algo_ele, ele_WP)](chain)[index]:    return False
    if algo_mu != 'none' and not tau_muonDiscr_WP[(algo_mu, mu_WP)](chain)[index]:    return False
    return True
