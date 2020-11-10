default_muon_selection = 'leptonMVAtop'

def isGoodGenMuon(chain, index):
    if not chain._gen_lIsPrompt[index]:         return False
    if chain._gen_lEta[index] > 2.4:            return False
    return True

def isBaseMuon(chain, index):
    if abs(chain._lEta[index]) >= 2.4:          return False
    if chain._lPt[index] <= 5:                   return False
    return True

#
# Cut-based selection
#
def isLooseMuonCutBased(chain, index):
    if not isBaseMuon(chain, index):            return False
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

from HNL.ObjectSelection.bTagWP import slidingDeepFlavorThreshold

#
# Updated selection with ttH MVA
#
def isLooseMuonttH(chain, index):
    if not isBaseMuon(chain, index):            return False
    if abs(chain._dxy[index]) >= 0.05:          return False
    if abs(chain._dz[index]) >= 0.1:            return False
    if chain._3dIPSig[index] >= 8:              return False
    if chain._miniIso[index] >= 0.4:            return False
    if not chain._lPOGLoose[index]:             return False
    return True
   
def isFOMuonttH(chain, index):
    if not isLooseMuonttH(chain, index):        return False
    if chain._lPt[index] < 10:                  return False
    # if chain._leptonMvaTTH[index] <= 0.85:      
    #     if chain._ptRatio[index] <= 0.65: return False
    # if chain._closestJetDeepFlavor[index] >= slidingDeepFlavorThreshold(chain.year, chain._lPt[index]):
    #     return False
    return True

def isTightMuonttH(chain, index):
    if not isFOMuonttH(chain, index):   return False
    if not chain._lPOGMedium[index]:    return False
    if chain._leptonMvaTTH[index] <= 0.85:     return False
    return True
    
#
# Updated selection with tZq MVA
#
def isLooseMuontZq(chain, index):
    if not isBaseMuon(chain, index):            return False
    if abs(chain._dxy[index]) >= 0.05:          return False
    if abs(chain._dz[index]) >= 0.1:            return False
    if chain._3dIPSig[index] >= 8:              return False
    if chain._miniIso[index] >= 0.4:            return False
    if not chain._lPOGLoose[index]:             return False
    return True
   
def isFOMuontZq(chain, index):
    if not isLooseMuontZq(chain, index):        return False
    # if chain._leptonMvaTTH[index] <= 0.4:      
    #     if chain._ptRatio[index] <= 0.4: return False
    # if chain._closestJetDeepFlavor[index] >= slidingDeepFlavorThreshold(chain.year, chain._lPt[index]):
    #     return False
    return True

def isTightMuontZq(chain, index):
    if not isFOMuontZq(chain, index):   return False
    if not chain._lPOGMedium[index]:    return False
    if chain._leptonMvatZq[index] <= 0.4:     return False
    return True

#
# Updated selection with top MVA
#
def topPreselection(chain, index):
    if not isBaseMuon(chain, index):            return False
    if chain._lPt[index] < 10:                  return False
    if abs(chain._dxy[index]) >= 0.05:          return False
    if abs(chain._dz[index]) >= 0.1:            return False
    if chain._3dIPSig[index] >= 8:              return False
    if chain._miniIso[index] >= 0.4:            return False
    if not chain._lPOGMedium[index]:            return False
    return True

def isLooseMuonTop(chain, index):
    if not topPreselection(chain, index):       return False
    if chain._leptonMvaTOP[index] <= 0.05:       return False
    return True
   
def isFOMuonTop(chain, index):
    if not isLooseMuonTop(chain, index):        return False
    if chain._leptonMvaTOP[index] <= 0.65:       return False
    return True

def isTightMuonTop(chain, index):
    if not isFOMuonTop(chain, index):           return False
    if chain._leptonMvaTOP[index] <= 0.9:       return False
    return True

#
# Tu Thong's selection
#
def slidingCutTTT(chain, index, high, low):
    
    slope = (high - low)/20.
    return min(low, max(high, low + slope*(chain._lPt[index]-20.)))

def isLooseMuonTTT(chain, index):
    if chain._lFlavor[index] != 1:              return False
    if chain._lPt[index]*(1+max(0., chain._miniIso[index]-0.4)) < 5: return False
    if abs(chain._lEta[index]) > 2.4:           return False
    if abs(chain._dxy[index]) >= 0.05:          return False
    if abs(chain._dz[index]) >= 0.1:            return False
    if chain._miniIso[index] >= 0.4:            return False
    if chain._3dIPSig[index] >= 8:              return False
    if not chain._lPOGMedium[index]:            return False
    return True
   
def isFOMuonTTT(chain, index):
    if not isLooseMuonTTT(chain, index):        return False
    if chain._lPt[index]*(1+max(0., chain._miniIso[index]-0.4)) < 10: return False
    if chain._leptonMvaTOP[index] <= 0.4:
        if chain._ptRatio[index] < 0.45:        return False
        # if chain._closestJetDeepFlavor[index] >= slidingCutTTT(chain, index, 0.025, 0.015): return False        
        if (chain._closestJetDeepFlavor_b[index] + chain._closestJetDeepFlavor_bb[index] + chain._closestJetDeepFlavor_lepb[index]) >= slidingCutTTT(chain, index, 0.025, 0.015): return False        
    return True

def isTightMuonTTT(chain, index):
    if not isLooseMuonTTT(chain, index):        return False
    if chain._lPt[index]*(1+max(0., chain._miniIso[index]-0.4)) < 10: return False
    if chain._leptonMvaTOP[index] <= 0.4:   return False 
    return True

#
# General function for selecting muons
#
def isLooseMuon(chain, index, algo = default_muon_selection):
    if algo == 'cutbased':       return isLooseMuonCutBased(chain, index)
    elif algo == 'leptonMVAttH':        return isLooseMuonttH(chain, index)
    elif algo == 'leptonMVAtZq':        return isLooseMuontZq(chain, index)
    elif algo == 'leptonMVAtop':        return isLooseMuonTop(chain, index)
    elif algo == 'TTT':        return isLooseMuonTTT(chain, index)
    else:
        print 'Wrong input for "algo" in isLooseMuon'
        return False

def isFOMuon(chain, index, algo = default_muon_selection):
    if algo == 'cutbased':              return isFOMuonCutBased(chain, index)
    elif algo == 'leptonMVAttH':        return isFOMuonttH(chain, index)
    elif algo == 'leptonMVAtZq':        return isFOMuontZq(chain, index)
    elif algo == 'leptonMVAtop':        return isFOMuonTop(chain, index)
    elif algo == 'TTT':        return isFOMuonTTT(chain, index)
    else:
        print 'Wrong input for "algo" in isFOMuon'
        return False

def isTightMuon(chain, index, algo = default_muon_selection):
    if algo == 'cutbased':       return isTightMuonCutBased(chain, index)
    elif algo == 'leptonMVAttH':        return isTightMuonttH(chain, index)
    elif algo == 'leptonMVAtZq':        return isTightMuontZq(chain, index)
    elif algo == 'leptonMVAtop':        return isFOMuonTop(chain, index)
    elif algo == 'TTT':        return isTightMuonTTT(chain, index)
    else:
        print 'Wrong input for "algo" in isTightMuon'
        return False

#
# Check for fakes
#
def isFakeMuon(chain, index):
    return not chain._lIsPrompt[index]