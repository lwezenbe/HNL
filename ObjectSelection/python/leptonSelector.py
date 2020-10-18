#
# Is good lepton on generator level
#
from HNL.ObjectSelection.electronSelector import isGoodGenElectron
from HNL.ObjectSelection.muonSelector import isGoodGenMuon
from HNL.ObjectSelection.tauSelector import isGoodGenTau

def isGoodGenLepton(chain, index):
    if chain._gen_lFlavor[index] == 0:       return isGoodGenElectron(chain, index)
    if chain._gen_lFlavor[index] == 1:       return isGoodGenMuon(chain, index)
    if chain._gen_lFlavor[index] == 2:       return isGoodGenTau(chain, index)
    else:
        return False

#
# Loose WP for light leptons
#
from HNL.ObjectSelection.electronSelector import isLooseElectron
from HNL.ObjectSelection.muonSelector import isLooseMuon

def isLooseLightLepton(chain, index, algo = None):
    
    if chain._lFlavor[index] == 0:
        if algo is None: return isLooseElectron(chain, index)
        else: return isLooseElectron(chain, index, algo)
 
    if chain._lFlavor[index] == 1:
        if algo is None: return isLooseMuon(chain, index)
        return isLooseMuon(chain, index, algo)

    return False

#
# FO WP for light leptons
#
from HNL.ObjectSelection.electronSelector import isFOElectron
from HNL.ObjectSelection.muonSelector import isFOMuon

def isFOLightLepton(chain, index, algo = None):

    if chain._lFlavor[index] == 0:
        if algo is None: return isFOElectron(chain, index)
        else: return isFOElectron(chain, index, algo)
 
    if chain._lFlavor[index] == 1:
        if algo is None: return isFOMuon(chain, index)
        return isFOMuon(chain, index, algo)

    return False

#
# Tight WP for light leptons
#
from HNL.ObjectSelection.electronSelector import isTightElectron
from HNL.ObjectSelection.muonSelector import isTightMuon

def isTightLightLepton(chain, index, algo = None):
    
    if chain._lFlavor[index] == 0:
        if algo is None: return isTightElectron(chain, index)
        else: return isTightElectron(chain, index, algo)
 
    if chain._lFlavor[index] == 1:
        if algo is None: return isTightMuon(chain, index)
        return isTightMuon(chain, index, algo)

    return False

#
# Loose WP for leptons
#
from HNL.ObjectSelection.tauSelector import isLooseTau, isFOTau, isTightTau

def isLooseLepton(chain, index, algo = None, tau_algo = None):
   
    if chain._lFlavor[index] != 2: return isLooseLightLepton(chain, index, algo) 
    if chain._lFlavor[index] == 2: 
        if tau_algo:    return isLooseTau(chain, index, tau_algo)
        else:           return isLooseTau(chain, index)
    return False

#
# FO WP for leptons
#
def isFOLepton(chain, index, algo = None, tau_algo = None):
    
    if chain._lFlavor[index] != 2: return isFOLightLepton(chain, index, algo)
    if chain._lFlavor[index] == 2: 
        if tau_algo:    return isFOTau(chain, index, tau_algo)
        else:           return isFOTau(chain, index)
    return False

#
# Tight WP for leptons
#
def isTightLepton(chain, index, algo = None, tau_algo = None):
    
    if chain._lFlavor[index] != 2: return isTightLightLepton(chain, index, algo)
    if chain._lFlavor[index] == 2: 
        if tau_algo:    return isTightTau(chain, index, tau_algo)
        else:           return isTightTau(chain, index)
    return False

def isGoodLepton(chain, index, algo = None, tau_algo = None, workingpoint = 'tight'):

    if workingpoint == 'loose':
        return isLooseLepton(chain, index, algo = algo, tau_algo = tau_algo)
    elif workingpoint == 'FO':
        return isFOLepton(chain, index, algo = algo, tau_algo = tau_algo)
    elif workingpoint == 'tight':
        return isTightLepton(chain, index, algo = algo, tau_algo = tau_algo)
    else:
        raise RuntimeError('Defined working point does not exist: ' +str(workingpoint))

def isGoodLeptonTycho(chain, index, algo = None, tau_algo = None):
    if chain._lFlavor[index] != 2: return isTightLightLepton(chain, index, algo)
    if chain._lFlavor[index] == 2: 
        if tau_algo:    return isLooseTau(chain, index, tau_algo)
        else:           return isLooseTau(chain, index)
    return False

from HNL.ObjectSelection.tauSelector import isJetFakingTau
from HNL.ObjectSelection.electronSelector import isFakeElectron
from HNL.ObjectSelection.muonSelector import isFakeMuon
def isFakeLepton(chain, index):
    if chain._lFlavor[index] == 0: return isFakeElectron(chain, index)
    if chain._lFlavor[index] == 1: return isFakeMuon(chain, index)
    if chain._lFlavor[index] == 2: return isJetFakingTau(chain, index)
    return False