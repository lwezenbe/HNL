#
# Loose WP for leptons
#
from electronSelector import isLooseElectron
from muonSelector import isLooseMuon

def isLooseLepton(chain, index):
    
    if chain._lFlavor[index] == 0 and isLooseElectron(chain, index):    return True
    if chain._lFlavor[index] == 1 and isLooseMuon(chain, index):        return True
    return False

#
# FO WP for leptons
#
from electronSelector import isFOElectron
from muonSelector import isFOMuon

def isFOLepton(chain, index):
    
    if chain._lFlavor[index] == 0 and isFOElectron(chain, index):    return True
    if chain._lFlavor[index] == 1 and isFOMuon(chain, index):        return True
    return False

#
# Tight WP for leptons
#
from electronSelector import isTightElectron
from muonSelector import isTightMuon

def isTightLepton(chain, index):
    
    if chain._lFlavor[index] == 0:      return isTightElectron(chain, index)
    if chain._lFlavor[index] == 1:      return isTightMuon(chain, index)
    return False
