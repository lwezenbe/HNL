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

def isLooseLightLepton(chain, index, algo = 'leptonMVAtZq'):
    
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

def isFOLightLepton(chain, index, algo = 'leptonMVAtZq'):
    
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

def isTightLightLepton(chain, index, algo ='leptonMVAtZq'):
    
    if chain._lFlavor[index] == 0:    
        return isTightElectron(chain, index, algo)
    if chain._lFlavor[index] == 1:   
        return isTightMuon(chain, index, algo)
    return False

#
# Loose WP for leptons
#
from HNL.ObjectSelection.tauSelector import isLooseTau, isFOTau, isTightTau

def isLooseLepton(chain, index, algo = 'leptonMVAtZq'):
   
    if chain._lFlavor[index] != 2: return isLooseLightLepton(chain, index, algo) 
    if chain._lFlavor[index] == 2: return isLooseTau(chain, index)
    return False

#
# FO WP for leptons
#
def isFOLepton(chain, index, algo = 'leptonMVAtZq'):
    
    if chain._lFlavor[index] != 2: return isFOLightLepton(chain, index, algo)
    if chain._lFlavor[index] == 2: return isFOTau(chain, index)
    return False

#
# Tight WP for leptons
#
def isTightLepton(chain, index, algo ='leptonMVAtZq', tau_algo = None):
    
    if chain._lFlavor[index] != 2: return isTightLightLepton(chain, index, algo)
    if chain._lFlavor[index] == 2: 
        if tau_algo:    return isTightTau(chain, index, tau_algo)
        else:           return isTightTau(chain, index)
    return False
