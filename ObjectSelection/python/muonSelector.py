
def isGoodGenMuon(chain, index):
    if not chain._gen_lIsPrompt[index]:         return False
    if chain._gen_lEta[index] > 2.4:            return False
    return True

def isLooseMuonCutBased(chain, index):
    if abs(chain._lEta[index]) >= 2.4:          return False
    if chain._lPt[index] < 5:                   return False
    if abs(chain._dxy[index]) >= 0.05:          return False
    if abs(chain._dz[index]) >= 0.1:            return False
    if chain._relIso[index] >= 0.6:                    return False
    #PF Muon and (tracker or global) Muon requirements already in ntuplizer
    return True

def isFOMuonCutBased(chain, index):
    if not isLooseMuonCutBased(chain, index):           return False
    if chain._3dIPSig[index] >= 4:              return False 
    if not chain._lPOGMedium[index]:            return False
    return True

def isTightMuonCutBased(chain, index):
    if not isFOMuonCutBased(chain, index):              return False
    if chain._relIso[index] >= 0.1:                    return False
    return True

from bTagWP import slidingDeepFlavorThreshold
#
# Updated selection with ttH MVA
#
def isLooseMuonttH(chain, index):
    if abs(chain._lEta[index]) >= 2.4:          return False
    if chain._lPt[index] < 5:                   return False
    if abs(chain._dxy[index]) >= 0.05:          return False
    if abs(chain._dz[index]) >= 0.1:            return False
    if chain._3dIPSig[index] >= 8:              return False
    if chain._miniIso[index] >= 0.4:            return False
    if not chain._lPOGLoose[index]:             return False
    return True
   
def isFOMuonttH(chain, index):
    if not isLooseMuonttH(chain, index):        return False
    if chain._lPt[index] < 10:                  return False
    if chain._leptonMvaTTH[index] <= 0.85:      
        if chain._ptRatio[index] <= 0.65: return False
    if chain._closestJetDeepFlavor[index] >= slidingDeepFlavorThreshold(chain.year, chain._lPt[index]):
        return False
    return True

def isTightMuonttH(chain, index):
    if not isFOMuonttH(chain, index):   return False
    if not chain._lPOGMedium[index]:    return False
    if chain._leptonMvaTTH[index] <= 0.85:     return False
    return True
    

def isLooseMuon(chain, index, algo = 'cutbased'):
    return isLooseMuonCutBased(chain, index) if algo == 'cutbased' else isLooseMuonttH(chain, index)

def isFOMuon(chain, index, algo = 'cutbased'):
    return isFOMuonCutBased(chain, index) if algo == 'cutbased' else isFOMuonttH(chain, index)

def isTightMuon(chain, index, algo = 'cutbased'):
    return isTightMuonCutBased(chain, index) if algo == 'cutbased' else isTightMuonttH(chain, index)
