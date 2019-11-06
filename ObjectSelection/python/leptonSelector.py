#
# Loose WP for light leptons
#
from electronSelector import isLooseElectronCutBased, isLooseElectronttH
from muonSelector import isLooseMuonCutBased, isLooseMuonttH

def isLooseLightLepton(chain, index, algo = 'cutbased'):
    
    if chain._lFlavor[index] == 0:
        return isLooseElectronCutBased(chain, index) if algo == 'cutbased' else isLooseElectronttH(chain, index)
 
    if chain._lFlavor[index] == 1:
        return isLooseMuonCutBased(chain, index) if algo == 'cutbased' else isLooseMuonttH(chain, index)

    return False #If tau
#
# FO WP for light leptons
#
from electronSelector import isFOElectronCutBased, isFOElectronttH
from muonSelector import isFOMuonCutBased, isFOMuonttH

def isFOLightLepton(chain, index, algo = 'cutbased'):
    
    if chain._lFlavor[index] == 0:
        return isFOElectronCutBased(chain, index) if algo == 'cutbased' else isFOElectronttH(chain, index)
    if chain._lFlavor[index] == 1:   
        return isFOMuonCutBased(chain, index) if algo == 'cutbased' else isFOMuonttH(chain, index)
    return False

#
# Tight WP for light leptons
#
from electronSelector import isTightElectronCutBased, isTightElectronttH
from muonSelector import isTightMuonCutBased, isTightMuonttH

def isTightLightLepton(chain, index, algo ='cutbased'):
    
    if chain._lFlavor[index] == 0:    
        return isTightElectronCutBased(chain, index) if algo == 'cutbased' else isTightElectronttH(chain, index)
    if chain._lFlavor[index] == 1:   
        return isTightMuonCutBased(chain, index) if algo == 'cutbased' else isTightMuonttH(chain, index)
    return False

#
# Loose WP for leptons
#
from tauSelector import isLooseTau, isFOTau, isTightTau

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
