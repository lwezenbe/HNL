def isGoodGenMuon(chain, index):
    if not chain._gen_lIsPrompt[index]:         return False
    if chain._gen_lEta[index] > 2.4:            return False
    return True

def isBaseMuon(chain, index):
    if abs(chain._lEta[index]) >= 2.4:          return False
    if chain._lPt[index] <= 5:                   return False
    return True

def slidingCutMuon(chain, index, lowpt, lowptwp, highpt, highptwp):
    
    slope = (highptwp - lowptwp)/(highpt-lowpt)
    if chain._lPt[index] < lowpt:
        return lowptwp
    elif chain._lPt[index] > highpt:
        return highptwp
    else:
        return lowptwp + slope*(chain._lPt[index]-lowpt)

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

from HNL.ObjectSelection.bTagWP import slidingDeepFlavorThreshold, getBTagWP

#
# ewkino selection
#
def isLooseMuonEwkino(chain, index):
    if chain._lFlavor[index] != 1: return False
    if(abs(chain._dxy[index])>= 0.05 or abs(chain._dz[index])>= 0.1 or chain._3dIPSig[index] >= 8): return False    
    if chain._miniIso[index] >= 0.4:    return False
    if chain._lPt[index] <= 5 or abs(chain._lEta[index]) >= 2.4:       return False
    if not chain._lPOGLoose[index]: return False
    return True #isLooseMuon From heavyNeutrino already included in basic muon cuts

def isFOMuonEwkino(chain, index):
    if not isLooseMuonEwkino(chain, index):       return False
    if chain._lPt[index] <= 10:       return False
    if not chain._lPOGMedium[index]: return False
    if chain._leptonMvaTTH[index] <= 0.4:
        if chain._ptRatio[index] < 0.35:        return False
        looseWP = getBTagWP(chain.year, 'loose', 'Deep')
        mediumWP = getBTagWP(chain.year, 'medium', 'Deep')
        if chain.year == 2016:
            if (chain._closestJetDeepFlavor_b[index] + chain._closestJetDeepFlavor_bb[index] + chain._closestJetDeepFlavor_lepb[index]) >= slidingCutMuon(chain, index, 10., looseWP/1.5, 50., looseWP/5.): return False       
        else:
            if (chain._closestJetDeepFlavor_b[index] + chain._closestJetDeepFlavor_bb[index] + chain._closestJetDeepFlavor_lepb[index]) >= slidingCutMuon(chain, index, 10., mediumWP/2., 50., looseWP/5.): return False
    return True

def isTightMuonEwkino(chain, index):
    if not isLooseMuonEwkino(chain, index):       return False
    if chain._lPt[index] <= 10:       return False
    if not chain._lPOGMedium[index]: return False
    if chain._leptonMvaTTH[index] <= 0.4: return False
    return True

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

# Taken from Luka
# https://github.com/wverbeke/ewkino/blob/tZq_new/objectSelection/MuonSelector.cc
muon_top_FO_dfdict = { 2016 : 0.015, 2017 : 0.02, 2018 : 0.02}
muon_top_FO_ptratiodict = { 2016 : 0.5, 2017 : 0.6, 2018 : 0.6}

def isFOMuonTop(chain, index):
    if not isLooseMuonTop(chain, index):        return False
    if chain._ptRatio[index] < muon_top_FO_ptratiodict[chain.year]: return False
    if (chain._closestJetDeepFlavor_b[index] + chain._closestJetDeepFlavor_bb[index] + chain._closestJetDeepFlavor_lepb[index]) > muon_top_FO_dfdict[chain.year]: return False
    return True

def isTightMuonTop(chain, index):
    if not isFOMuonTop(chain, index):           return False
    # if chain._leptonMvaTOP[index] <= 0.9:       return False          #Tight leptonMVA
    if chain._leptonMvaTOP[index] <= 0.65:       return False           #Medium leptonMVA
    return True

#
# Tu Thong's selection
#
def isLooseMuonTTT(chain, index):
    if chain._lFlavor[index] != 1:              return False
    if chain._lPt[index] < 5: return False
    if abs(chain._lEta[index]) > 2.4:           return False
    if abs(chain._dxy[index]) >= 0.05:          return False
    if abs(chain._dz[index]) >= 0.1:            return False
    if chain._miniIso[index] >= 0.4:            return False
    if chain._3dIPSig[index] >= 8:              return False
    if not chain._lPOGMedium[index]:            return False
    return True
   
def isFOMuonTTT(chain, index):
    if not isLooseMuonTTT(chain, index):        return False
    if chain._lPt[index] < 10: return False
    if chain._leptonMvaTOP[index] <= 0.4:
        if chain._ptRatio[index] < 0.45:        return False
        if chain.year == 2016:
            if (chain._closestJetDeepFlavor_b[index] + chain._closestJetDeepFlavor_bb[index] + chain._closestJetDeepFlavor_lepb[index]) >= slidingCutMuon(chain, index, 20., 0.02, 40., 0.015): return False 
        else:
            if (chain._closestJetDeepFlavor_b[index] + chain._closestJetDeepFlavor_bb[index] + chain._closestJetDeepFlavor_lepb[index]) >= slidingCutMuon(chain, index, 20., 0.025, 40., 0.015): return False 
    return True

def isTightMuonTTT(chain, index):
    if not isLooseMuonTTT(chain, index):        return False
    if chain._lPt[index] < 10: return False
    if chain._leptonMvaTOP[index] <= 0.4:   return False 
    return True

#
# Updated selection with Luka's medium selection for tZq
#

def isLooseMuonLuka(chain, index):
    if chain._lFlavor[index] != 1:              return False
    if chain._lPt[index] <= 5:                  return False
    if abs(chain._lEta[index]) >= 2.4:          return False
    if abs(chain._dxy[index]) >= 0.05:          return False
    if abs(chain._dz[index]) >= 0.1:            return False
    if chain._miniIso[index] >= 0.4:            return False
    if chain._3dIPSig[index] >= 8:              return False
    if not chain._lPOGMedium[index]:            return False
    return True

def isFOMuonLuka(chain, index):
    if not isLooseMuonLuka(chain, index):        return False
    if chain._lPt[index] <= 10: return False
    if chain._leptonMvaTOP[index] <= 0.4:
        if chain._ptRatio[index] < 0.45:        return False
        if chain.year == 2016:
            if (chain._closestJetDeepFlavor_b[index] + chain._closestJetDeepFlavor_bb[index] + chain._closestJetDeepFlavor_lepb[index]) >= slidingCutMuon(chain, index, 20., 0.02, 40., 0.015): return False 
        else:
            if (chain._closestJetDeepFlavor_b[index] + chain._closestJetDeepFlavor_bb[index] + chain._closestJetDeepFlavor_lepb[index]) >= slidingCutMuon(chain, index, 20., 0.025, 40., 0.015): return False 
    return True

def isTightMuonLuka(chain, index):
    if not isFOMuonLuka(chain, index):        return False
    if chain._lPt[index] <= 10: return False
    if chain._leptonMvaTOP[index] <= 0.4:   return False 
    return True

#
# General function for selecting muons
#
def isLooseMuon(chain, index, algo):
    if algo == 'cutbased':       return isLooseMuonCutBased(chain, index)
    elif algo == 'leptonMVAttH':        return isLooseMuonttH(chain, index)
    elif algo == 'leptonMVAtZq':        return isLooseMuontZq(chain, index)
    elif algo == 'leptonMVAtop':        return isLooseMuonTop(chain, index)
    elif algo == 'TTT':                 return isLooseMuonTTT(chain, index)
    elif algo == 'Luka' or algo == 'HNL':                return isLooseMuonLuka(chain, index)
    elif algo == 'ewkino':              return isLooseMuonEwkino(chain, index)
    else:
        print 'Wrong input for "algo" in isLooseMuon'
        return False

def isFOMuon(chain, index, algo):
    if algo == 'cutbased':              return isFOMuonCutBased(chain, index)
    elif algo == 'leptonMVAttH':        return isFOMuonttH(chain, index)
    elif algo == 'leptonMVAtZq':        return isFOMuontZq(chain, index)
    elif algo == 'leptonMVAtop':        return isFOMuonTop(chain, index)
    elif algo == 'TTT':                 return isFOMuonTTT(chain, index)
    elif algo == 'Luka' or algo == 'HNL':                return isFOMuonLuka(chain, index)
    elif algo == 'ewkino':              return isFOMuonEwkino(chain, index)
    else:
        print 'Wrong input for "algo" in isFOMuon'
        return False

def isTightMuon(chain, index, algo):
    if algo == 'cutbased':       return isTightMuonCutBased(chain, index)
    elif algo == 'leptonMVAttH':        return isTightMuonttH(chain, index)
    elif algo == 'leptonMVAtZq':        return isTightMuontZq(chain, index)
    elif algo == 'leptonMVAtop':        return isTightMuonTop(chain, index)
    elif algo == 'TTT':                 return isTightMuonTTT(chain, index)
    elif algo == 'Luka' or algo == 'HNL':                return isTightMuonLuka(chain, index)
    elif algo == 'ewkino':              return isTightMuonEwkino(chain, index)
    else:
        print 'Wrong input for "algo" in isTightMuon'
        return False

from HNL.ObjectSelection.objectSelection import objectSelectionCollection
def checkMuonAlgorithm(chain, algo):
    if algo is None:
        try:
            chain.obj_sel
        except:
            #Initiate default object selection
            chain.obj_sel = objectSelectionCollection()
        return chain.obj_sel['light_algo']
    else:
        return algo

def checkMuonWP(chain, wp):
    if wp is None:
        try:
            chain.obj_sel
        except:
            #Initiate default object selection
            chain.obj_sel = objectSelectionCollection()
        return chain.obj_sel['mu_wp']
    else:
        return wp

def isGoodMuon(chain, index, workingpoint = None, algo = None):
    workingpoint = checkMuonWP(chain, workingpoint)
    algo = checkMuonAlgorithm(chain, algo)

    if workingpoint == 'loose':
        return isLooseMuon(chain, index, algo)
    elif workingpoint == 'FO':
        return isFOMuon(chain, index, algo)
    elif workingpoint == 'tight':
        return isTightMuon(chain, index, algo)

#
# Check for fakes
#
def isFakeMuon(chain, index):
    return not chain._lIsPrompt[index]

#
# Cone correction
#
def muonConeCorrection(chain, index, algo = None):
    algo = checkMuonAlgorithm(chain, algo)
    if algo == 'cutbased':
        return 1+max(0., chain._relIso[l]-0.1)
    elif algo == 'TTT':
        return 0.67/chain._ptRatio[index]
    else:
        # return 0.8/chain._ptRatio[index]
        return 0.67/chain._ptRatio[index]
