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
    if chain._lFlavor[index] == 2 and isLooseTau:    return True
    return False

#
# FO WP for leptons
#
def isFOLepton(chain, index, algo = 'cutbased'):
    
    if isFOLightLepton(chain, index, algo):          return True 
    if chain._lFlavor[index] == 2 and isFOTau:    return True
    return False

#
# Tight WP for leptons
#
def isTightLepton(chain, index, algo ='cutbased'):
    
    if isTightLightLepton(chain, index, algo):          return True 
    if chain._lFlavor[index] == 2 and isTightTau:    return True
    return False
