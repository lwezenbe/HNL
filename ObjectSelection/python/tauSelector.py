import ROOT

from HNL.ObjectSelection.leptonSelector import isLooseLightLepton
from HNL.Tools.helpers import deltaR

#
# List of all tau ID algorithms so we can easily switch algorithm whenever we want
# After you select one particular algorithm to use, put correct string in default_algo var
#
#            algo, WP
tau_id_WP = {('MVA2017v2', 'vloose') : lambda c : c._lPOGVeto,
            ('MVA2017v2', 'loose') : lambda c : c._lPOGLoose,
            ('MVA2017v2', 'medium') : lambda c : c._lPOGMedium,
            ('MVA2017v2', 'tight') : lambda c : c._lPOGTight,
            ('MVA2017v2', 'vtight') : lambda c : c._tauPOGVTight2017v2,

            ('MVA2017v2_new', 'vloose') : lambda c : c._tauVLooseMvaNew2017v2,
            ('MVA2017v2_new', 'loose') : lambda c : c._tauLooseMvaNew2017v2,
            ('MVA2017v2_new', 'medium') : lambda c : c._tauMediumMvaNew2017v2,
            ('MVA2017v2_new', 'tight') : lambda c : c._tauTightMvaNew2017v2,
            ('MVA2017v2_new', 'vtight') : lambda c : c._tauVTightMvaNew2017v2
            }
            
tau_DMfinding = {'MVA2017v2' : lambda c : c._decayModeFinding,
          'MVA2017v2_new' : lambda c : c._decayModeFindingNew}

default_algo = 'MVA2017v2'

def isCleanFromLightLeptons(chain, index):
    
    for l in xrange(chain._nLight):
        if not isLooseLightLepton(chain, l):    continue
        if deltaR(chain._lEta[l], chain._lEta[index], chain._lPhi[l], chain._lPhi[index]) < 0.4: return False
    return True
        

def isLooseTau(chain, index, algo = default_algo):
    
    if chain._lFlavor[index] != 2:              return False
    if not tau_DMfinding[algo](chain)[index]:   return False
    if not tau_id_WP[(algo, 'vloose')](chain)[index]:   return False
    if not isCleanFromLightLeptons(chain, index):       return False
    if not chain._tauMuonVetoLoose[index]:    return False
    if not chain._tauEleVetoLoose[index]:     return False
    return True

def isFOTau(chain, index, algo = default_algo):
    
    if not isLooseTau(chain, index, algo):              return False
    if not tau_id_WP[(algo, 'medium')](chain)[index]:   return False
    return True


def isTightTau(chain, index, algo = default_algo): 
    
    if not isFOTau(chain, index, algo):              return False
    if not tau_id_WP[(algo, 'tight')](chain)[index]:   return False
    return True

