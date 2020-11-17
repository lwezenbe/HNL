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
        return isLooseElectron(chain, index, algo)
 
    if chain._lFlavor[index] == 1:
        return isLooseMuon(chain, index, algo)

    return False

#
# FO WP for light leptons
#
from HNL.ObjectSelection.electronSelector import isFOElectron
from HNL.ObjectSelection.muonSelector import isFOMuon

def isFOLightLepton(chain, index, algo = None):

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

def isTightLightLepton(chain, index, algo = None):
    
    if chain._lFlavor[index] == 0:
        return isTightElectron(chain, index, algo)
 
    if chain._lFlavor[index] == 1:
        return isTightMuon(chain, index, algo)

    return False

#
# Loose WP for leptons
#
from HNL.ObjectSelection.tauSelector import isLooseTau, isFOTau, isTightTau

def isLooseLepton(chain, index, algo = None, tau_algo = None, analysis = 'HNL'):
   
    if chain._lFlavor[index] != 2: return isLooseLightLepton(chain, index, algo) 
    if chain._lFlavor[index] == 2: 
        return isLooseTau(chain, index, algo = tau_algo, analysis = analysis)
    return False

#
# FO WP for leptons
#
def isFOLepton(chain, index, algo = None, tau_algo = None, analysis = 'HNL'):
    
    if chain._lFlavor[index] != 2: return isFOLightLepton(chain, index, algo)
    if chain._lFlavor[index] == 2: 
        return isFOTau(chain, index, algo = tau_algo, analysis = analysis)
    return False

#
# Tight WP for leptons
#
def isTightLepton(chain, index, algo = None, tau_algo = None, analysis = 'HNL'):
    
    if chain._lFlavor[index] != 2: return isTightLightLepton(chain, index, algo)
    if chain._lFlavor[index] == 2: 
        return isTightTau(chain, index, algo = tau_algo, analysis = analysis)
    return False

def isGoodLepton(chain, index, algo = None, tau_algo = None, workingpoint = 'tight', analysis = 'HNL'):

    if workingpoint == 'loose':
        return isLooseLepton(chain, index, algo = algo, tau_algo = tau_algo, analysis = analysis)
    elif workingpoint == 'FO':
        return isFOLepton(chain, index, algo = algo, tau_algo = tau_algo, analysis = analysis)
    elif workingpoint == 'tight':
        return isTightLepton(chain, index, algo = algo, tau_algo = tau_algo, analysis = analysis)
    else:
        raise RuntimeError('Defined working point does not exist: ' +str(workingpoint))

def isGoodLeptonTycho(chain, index, algo = None, tau_algo = None):
    if chain._lFlavor[index] != 2: return isTightLightLepton(chain, index, algo)
    if chain._lFlavor[index] == 2: 
        return isLooseTau(chain, index, algo = tau_algo)
    return False

from HNL.ObjectSelection.tauSelector import isJetFakingTau
from HNL.ObjectSelection.electronSelector import isFakeElectron
from HNL.ObjectSelection.muonSelector import isFakeMuon
def isFakeLepton(chain, index):
    if chain._lFlavor[index] == 0: return isFakeElectron(chain, index)
    if chain._lFlavor[index] == 1: return isFakeMuon(chain, index)
    if chain._lFlavor[index] == 2: return isJetFakingTau(chain, index)
    return False