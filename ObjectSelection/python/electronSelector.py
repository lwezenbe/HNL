from HNL.Tools.helpers import deltaR

#
# We dont use electrons that fall within dr 0.05 of a loose muon
#
from HNL.ObjectSelection.muonSelector import isLooseMuon
def isCleanFromMuons(chain, index):
    
    for mu in xrange(chain._nMu):
        if not isLooseMuon(chain, mu):  continue
        if deltaR(chain._lEta[mu], chain._lEta[index], chain._lPhi[mu], chain._lPhi[index]) < 0.05: return False
    return True

#
# WP as defined in AN 2017/014
#
def isLooseElectron(chain, index):
    
    if abs(chain._lEta[index]) >= 2.5:          return False
    if chain._lPt[index] < 10:                  return False
    if not isCleanFromMuons(chain, index):      return False
    if abs(chain._dxy[index]) >= 0.05:          return False
    if abs(chain._dz[index]) >= 0.1:            return False
    if chain._relIso[index] >= 0.6:                    return False
    if not chain._lElectronPassConvVeto[index]: return False
    if chain._lElectronMissingHits[index] > 1:  return False
    return True

def isFOElectron(chain, index):
    
    if not isLooseElectron(chain, index):       return False
    if chain._3dIPSig[index] >= 4:              return False
    if not chain._lElectronPassEmu[index]:      return False   #sigma_ietaieta, H/E, deltaEta_in, deltaPhi_in, 1/E-1/p
    if chain._lElectronMissingHits[index] != 0: return False
    #MVA
    return True

def isTightElectron(chain, index):

    if not isFOElectron(chain, index):          return False
    if chain._relIso[index] >= 0.1:                    return False
    #MVA
    return True
