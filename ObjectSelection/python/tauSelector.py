import numpy as np
from HNL.ObjectSelection.electronSelector import isGoodElectron
from HNL.ObjectSelection.muonSelector import isGoodMuon
from HNL.Tools.helpers import deltaR

#
# List of all tau ID algorithms so we can easily switch algorithm whenever we want
# After you select one particular algorithm to use, put correct string in default_algo var
#
#            algo, WP
tau_id_WP = {('MVA2017v2', None) : lambda c : np.ones(c._nL, dtype=bool),  
            ('MVA2017v2', 'vloose') : lambda c : c._lPOGVeto,
            ('MVA2017v2', 'loose') : lambda c : c._lPOGLoose,
            ('MVA2017v2', 'medium') : lambda c : c._lPOGMedium,
            ('MVA2017v2', 'tight') : lambda c : c._lPOGTight,
            ('MVA2017v2', 'vtight') : lambda c : c._tauPOGVTight2017v2,

            ('MVA2017v2New', None) : lambda c : np.ones(c._nL, dtype=bool),
            ('MVA2017v2New', 'vloose') : lambda c : c._tauVLooseMvaNew2017v2,
            ('MVA2017v2New', 'loose') : lambda c : c._tauLooseMvaNew2017v2,
            ('MVA2017v2New', 'medium') : lambda c : c._tauMediumMvaNew2017v2,
            ('MVA2017v2New', 'tight') : lambda c : c._tauTightMvaNew2017v2,
            ('MVA2017v2New', 'vtight') : lambda c : c._tauVTightMvaNew2017v2,

            ('deeptauVSjets', None) : lambda c : np.ones(c._nL, dtype=bool),
            ('deeptauVSjets', 'vvvloose') : lambda c : c._tauVVVLooseDeepTauVsJets,
            ('deeptauVSjets', 'vvloose') : lambda c : c._tauVVLooseDeepTauVsJets,
            ('deeptauVSjets', 'vloose') : lambda c : c._tauVLooseDeepTauVsJets,
            ('deeptauVSjets', 'loose') : lambda c : c._tauLooseDeepTauVsJets,
            ('deeptauVSjets', 'medium') : lambda c : c._tauMediumDeepTauVsJets,
            ('deeptauVSjets', 'tight') : lambda c : c._tauTightDeepTauVsJets,
            ('deeptauVSjets', 'vtight') : lambda c : c._tauVTightDeepTauVsJets,
            ('deeptauVSjets', 'vvtight') : lambda c : c._tauVVTightDeepTauVsJets,

            #From here on very outdated WP, purely there for showing that the new ones are much better
            ('MVA2015', None) : lambda c : np.ones(c._nL, dtype=bool),
            ('MVA2015', 'vloose') : lambda c : c._tauPOGVLoose2015,
            ('MVA2015', 'loose') : lambda c : c._tauPOGLoose2015,
            ('MVA2015', 'medium') : lambda c : c._tauPOGMedium2015,
            ('MVA2015', 'tight') : lambda c : c._tauPOGTight2015,
            ('MVA2015', 'vtight') : lambda c : c._tauPOGVTight2015,
            
            ('MVA2015New', None) : lambda c : np.ones(c._nL, dtype=bool),
            ('MVA2015New', 'vloose') : lambda c : c._tauVLooseMvaNew2015,
            ('MVA2015New', 'loose') : lambda c : c._tauLooseMvaNew2015,
            ('MVA2015New', 'medium') : lambda c : c._tauMediumMvaNew2015,
            ('MVA2015New', 'tight') : lambda c : c._tauTightMvaNew2015,
            ('MVA2015New', 'vtight') : lambda c : c._tauVTightMvaNew2015,
            }

tau_eleDiscr_WP = {('againstElectron', None) : lambda c : np.ones(c._nL, dtype=bool),
                ('againstElectron', 'loose') : lambda c : c._tauEleVetoLoose,
                ('againstElectron', 'tight') : lambda c : c._tauEleVetoTight,
            
            ('deeptauVSe', None) : lambda c : np.ones(c._nL, dtype=bool),
            ('deeptauVSe', 'vvvloose') : lambda c : c._tauVVVLooseDeepTauVsEle,
            ('deeptauVSe', 'vvloose') : lambda c : c._tauVVLooseDeepTauVsEle,
            ('deeptauVSe', 'vloose') : lambda c : c._tauVLooseDeepTauVsEle,
            ('deeptauVSe', 'loose') : lambda c : c._tauLooseDeepTauVsEle,
            ('deeptauVSe', 'medium') : lambda c : c._tauMediumDeepTauVsEle,
            ('deeptauVSe', 'tight') : lambda c : c._tauTightDeepTauVsEle,
            ('deeptauVSe', 'vtight') : lambda c : c._tauVTightDeepTauVsEle,
            ('deeptauVSe', 'vvtight') : lambda c : c._tauVVTightDeepTauVsEle,
                }
            
tau_muonDiscr_WP = {('againstMuon', None) : lambda c : np.ones(c._nL, dtype=bool),
                ('againstMuon', 'loose') : lambda c : c._tauMuonVetoLoose,
                ('againstMuon', 'tight') : lambda c : c._tauMuonVetoTight,
           
            ('deeptauVSmu', None) : lambda c : np.ones(c._nL, dtype=bool),
            ('deeptauVSmu', 'vloose') : lambda c : c._tauVLooseDeepTauVsMu,
            ('deeptauVSmu', 'loose') : lambda c : c._tauLooseDeepTauVsMu,
            ('deeptauVSmu', 'medium') : lambda c : c._tauMediumDeepTauVsMu,
            ('deeptauVSmu', 'tight') : lambda c : c._tauTightDeepTauVsMu,
                }

tau_DMfinding = {'MVA2017v2' : lambda c : c._decayModeFinding,
          'MVA2017v2New' : lambda c : c._decayModeFindingNew,
          'MVA2015' : lambda c : c._decayModeFinding,
          'MVA2015New' : lambda c : c._decayModeFindingNew,
          'deeptauVSjets' : lambda c : c._decayModeFindingNew,
          #'deeptauVSjets' : lambda c : c._decayModeFindingDeepTau,
}

#Reference order since the working points are in a dictionary without order
order_of_workingpoints = { None: 0, 'vvvloose' : 1, 'vvloose' : 2, 'vloose':3, 'loose': 4, 'medium' : 5, 'tight':6, 'vtight': 7, 'vvtight':8, 'vvvtight': 9}

def getCorrespondingLightLepDiscr(algorithm):
    if 'deeptau' in algorithm:
        return 'deeptauVSe', 'deeptauVSmu'
    else:
        return 'againstElectron', 'againstMuon'

def getIsoWorkingPoints(algorithm):
    all_wp = []
    for key in tau_id_WP.keys():
        if key[0] == algorithm: all_wp.append(key[1])
    sorted_wp = sorted(all_wp, key = lambda k: order_of_workingpoints[k])
    return sorted_wp

def getMuWorkingPoints(algorithm):
    all_wp = []
    for key in tau_muonDiscr_WP.keys():
        if key[0] == algorithm: all_wp.append(key[1])
    sorted_wp = sorted(all_wp, key = lambda k: order_of_workingpoints[k])
    return sorted_wp

def getEleWorkingPoints(algorithm):
    all_wp = []
    for key in tau_eleDiscr_WP.keys():
        if key[0] == algorithm: all_wp.append(key[1])
    sorted_wp = sorted(all_wp, key = lambda k: order_of_workingpoints[k])
    return sorted_wp

def passedElectronDiscr(chain, index, iso_algorithm_name, wp):
    if 'deeptau' in iso_algorithm_name:
        ele_discr_name = 'deeptauVSe'
    elif 'MVA' in iso_algorithm_name:
        ele_discr_name = 'againstElectron'
    else:
        print 'Error: inconsistent iso_algorithm_name in tauSelector.applyElectronDiscr'
        exit(0)
    return tau_eleDiscr_WP[(ele_discr_name, wp)](chain)[index]

def passedMuonDiscr(chain, index, iso_algorithm_name, wp):
    if 'deeptau' in iso_algorithm_name:
        mu_discr_name = 'deeptauVSmu'
    elif 'MVA' in iso_algorithm_name:
        mu_discr_name = 'againstMuon'
    else:
        print 'Error: inconsistent iso_algorithm_name in tauSelector.applyMuonDiscr'
        exit(0)
    return tau_muonDiscr_WP[(mu_discr_name, wp)](chain)[index]

def isGoodGenTau(chain, index):
    if chain._gen_lFlavor[index] != 2:          return False
    if not chain._gen_lIsPrompt[index]:         return False
    if not chain._gen_lDecayedHadr[index]:      return False
    if abs(chain._gen_lEta[index]) > 2.3:            return False
    # if abs(chain._gen_lVisPt[index]) < 20:            return False
    if abs(chain._gen_lPt[index]) < 20:            return False
    return True             

def isCleanFromLightLeptons(chain, index):
    for l in xrange(chain._nLight):
        if chain._lFlavor[l] == 1 and not isGoodMuon(chain, l, workingpoint='loose'):    continue
        if chain._lFlavor[l] == 0 and not isGoodElectron(chain, l, workingpoint='loose'):    continue
        if deltaR(chain._lEta[l], chain._lEta[index], chain._lPhi[l], chain._lPhi[index]) < 0.4: return False
    return True

def isBaseTau(chain, index):
    if chain._lFlavor[index] != 2:              return False
    if chain._lPt[index] < 20:                  return False
    if chain._lEta[index] > 2.3:                return False
    if chain._tauDecayMode[index] == 5 or chain._tauDecayMode[index] == 6: return False
    if not isCleanFromLightLeptons(chain, index):       return False
    return True

#
# HNL selection
#
def isLooseTauHNL(chain, index):
    if not isBaseTau(chain, index): return False
    if not tau_DMfinding['deeptauVSjets'](chain)[index]:   return False
    if not tau_id_WP[('deeptauVSjets', 'vvvloose')](chain)[index]:   return False
    if not passedElectronDiscr(chain, index, 'deeptauVSjets', 'loose'): return False
    if not passedMuonDiscr(chain, index, 'deeptauVSjets', 'loose'): return False
    return True

def isFOTauHNL(chain, index):
    if not isLooseTauHNL(chain, index):              return False
    # if not tau_id_WP[('deeptauVSjets, 'medium')](chain)[index]:   return False
    return True

def isTightTauHNL(chain, index): 
    if not isFOTauHNL(chain, index):              return False
    if not tau_id_WP[('deeptauVSjets', 'medium')](chain)[index]:   return False
    return True

#
# Ewkino selection (mainly for synchronization)
#
def isLooseTauEwkino(chain, index):
    if not isBaseTau(chain, index): return False
    if not tau_DMfinding['MVA2017v2'](chain)[index]:   return False
    if not tau_id_WP[('MVA2017v2', 'loose')](chain)[index]:   return False
    if not passedElectronDiscr(chain, index, 'MVA2017v2', 'loose'): return False
    if not passedMuonDiscr(chain, index, 'MVA2017v2', 'loose'): return False
    return True

def isFOTauEwkino(chain, index):
    if not isLooseTauEwkino(chain, index):              return False
    return True

def isTightTauEwkino(chain, index): 
    if not isFOTauEwkino(chain, index):              return False
    if not tau_id_WP[('MVA2017v2', 'tight')](chain)[index]:   return False
    return True

#
# General functions
#
def isLooseTau(chain, index, algo):
    if algo == 'HNL':
        return isLooseTauHNL(chain, index)
    elif algo == 'ewkino':
        return isLooseTauEwkino(chain, index)
    else:
        raise RuntimeError('Wrong input for "algo" in isLooseTau')

def isFOTau(chain, index, algo):
    if algo == 'HNL':
        return isFOTauHNL(chain, index)
    elif algo == 'ewkino':
        return isFOTauEwkino(chain, index)
    else:
        raise RuntimeError('Wrong input for "algo" in isFOTau')

def isTightTau(chain, index, algo):
    if algo == 'HNL':
        return isTightTauHNL(chain, index)
    elif algo == 'ewkino':
        return isTightTauEwkino(chain, index)
    else:
        raise RuntimeError('Wrong input for "algo" in isTightTau')

from HNL.ObjectSelection.objectSelection import objectSelectionCollection
def checkTauAlgorithm(chain, algo):
    if algo is None:
        try:
            chain.obj_sel
        except:
            #Initiate default object selection
            chain.obj_sel = objectSelectionCollection()
        return chain.obj_sel['tau_algo']
    else:
        return algo

def checkTauWP(chain, wp):
    if wp is None:
        try:
            chain.obj_sel
        except:
            #Initiate default object selection
            chain.obj_sel = objectSelectionCollection()
        return chain.obj_sel['tau_wp']
    else:
        return wp

def isGoodTau(chain, index, workingpoint = None, algo = None):
    workingpoint = checkTauWP(chain, workingpoint)
    algo = checkTauAlgorithm(chain, algo)

    if workingpoint == 'loose':
        return isLooseTau(chain, index, algo)
    elif workingpoint == 'FO':
        return isFOTau(chain, index, algo)
    elif workingpoint == 'tight':
        return isTightTau(chain, index, algo)
    else:
        raise RuntimeError("Undefined working point for tau")

def isJetFakingTau(chain, index):
    if chain._tauGenStatus[index] == 6: return True
    else: return False

# Test function only used in compareTauID
def isGeneralTau(chain, index, algo_iso, iso_WP, ele_algo, ele_WP, mu_algo, mu_WP, needDMfinding = True):
    
    if chain._lFlavor[index] != 2:              return False
    if chain._lPt[index] < 20:                  return False
    if chain._lEta[index] > 2.3:                return False
    if chain._tauDecayMode[index] == 5 or chain._tauDecayMode[index] == 6: return False
    if algo_iso is not None and not tau_id_WP[(algo_iso, iso_WP)](chain)[index]:   return False
    if needDMfinding:
        if not tau_DMfinding[algo_iso](chain)[index]:   return False
    if not isCleanFromLightLeptons(chain, index):       return False
    if not tau_eleDiscr_WP[(ele_algo, ele_WP)](chain)[index]:    return False
    if not tau_muonDiscr_WP[(mu_algo, mu_WP)](chain)[index]:    return False
    return True

def matchGenToReco(chain, l):
   
    min_dr = 0.3
    matched_l = None
    for lepton in xrange(chain._nLight, chain._nL):
        if chain._tauGenStatus[lepton] != 5: continue
        dr = deltaR(chain._gen_lEta[l], chain._lEta[lepton], chain._gen_lPhi[l], chain._lPhi[lepton])
        if dr < min_dr:
            matched_l = lepton
            min_dr = dr
        
    return matched_l

#
# Cone correction
#
def tauConeCorrection(chain, index, algo = None):
    return 1.