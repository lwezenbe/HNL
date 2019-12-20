#
# Loose WP for light leptons
#
from HNL.ObjectSelection.electronSelector import isLooseElectron
from HNL.ObjectSelection.muonSelector import isLooseMuon

def isLooseLightLepton(chain, index, algo = 'cutbased'):
    
    if chain._lFlavor[index] == 0:
        return isLooseElectron(chain, index, algo)
 
    if chain._lFlavor[index] == 1:
        return isLooseMuon(chain, index, algo)

    return False #If tau
#
# FO WP for light leptons
#
from HNL.ObjectSelection.electronSelector import isFOElectron
from HNL.ObjectSelection.muonSelector import isFOMuon

def isFOLightLepton(chain, index, algo = 'cutbased'):
    
    if chain._lFlavor[index] == 0:
        return isFOElectron(chain, index, algo)
    if chain._lFlavor[index] == 1:   
        return isFOMuon(chain, index, algo)
    return False

#
# Tight WP for light leptons
#
from HNL.ObjectSelection.electronSelector import isTightElectron
from HNL.ObjectSelection.muonSelector import isTightMuon

def isTightLightLepton(chain, index, algo ='cutbased'):
    
    if chain._lFlavor[index] == 0:    
        return isTightElectron(chain, index, algo)
    if chain._lFlavor[index] == 1:   
        return isTightMuon(chain, index, algo)
    return False

#
# Loose WP for leptons
#
from HNL.ObjectSelection.tauSelector import isLooseTau, isFOTau, isTightTau

def isLooseLepton(chain, index, algo = 'cutbased'):
   
    if isLooseLightLepton(chain, index, algo):          return True 
    if chain._lFlavor[index] == 2 and isLooseTau(chain, index):    return True
    return False

#
# FO WP for leptons
#
def isFOLepton(chain, index, algo = 'cutbased'):
    
    if isFOLightLepton(chain, index, algo):          return True 
    if chain._lFlavor[index] == 2 and isFOTau(chain, index):    return True
    return False

#
# Tight WP for leptons
#
def isTightLepton(chain, index, algo ='cutbased'):
    
    if isTightLightLepton(chain, index, algo):          return True 
    if chain._lFlavor[index] == 2 and isTightTau(chain, index):    return True
    return False

#
# Is a lepton in signal sample l1 in MC truth?
#
from HNL.Tools.helpers import deltaR
def whichHNLlepton(chain, lepton):
    hnl_daughters = []
    match_index = None
    min_dr = 0.4
    for i in xrange(chain._nLheParticles):
        if chain._lheMother1[i] != -1 and abs(chain._lhePdgId[chain._lheMother1[i]]) == 9900012: hnl_daughters.append(abs(chain._lhePdgId[i]))
        if abs(chain._lhePdgId[i]) != abs(chain._lMatchPdgId[lepton]): continue
        if deltaR(chain._lEta[lepton], chain._lheEta[i], chain._lPhi[lepton], chain._lhePhi[i]) < min_dr:
            match_index = i
            min_dr = deltaR(chain._lEta[lepton], chain._lheEta[i], chain._lPhi[lepton], chain._lhePhi[i])

    if match_index is None: return None 

    if abs(chain._lhePdgId[chain._lheMother1[match_index]]) == 24 and match_index not in hnl_daughters:       return 1
   
    #if N->Wl 
    elif 24 in hnl_daughters:
        if abs(chain._lhePdgId[chain._lheMother1[match_index]]) != 24 and chain._lheMother1[match_index] in hnl_daughters:      return 2
        if abs(chain._lhePdgId[chain._lheMother1[match_index]]) == 24 and chain._lheMother1[match_index] in hnl_daughters:      return 3
    
    #if N->Znu
    elif 23 in hnl_daughters:
        if abs(chain._lhePdgId[chain._lheMother1[match_index]]) == 23: return 4
    return None
    
