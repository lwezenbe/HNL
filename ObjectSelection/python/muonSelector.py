def getMuonPt(chain, index, syst = None):
    from HNL.Systematics.systematics import checkSyst
    syst = checkSyst(chain, syst)
    if syst == 'muonScaleUp':
        return chain._lPtScaleUp[index]
    elif syst == 'muonScaleDown':
        return chain._lPtScaleDown[index]
    elif syst == 'muonResUp':
        return chain._lPtResUp[index]
    elif syst == 'muonResDown':
        return chain._lPtResDown[index]
    else:
        return chain._lPtCorr[index]

def getMuonE(chain, index, syst = None):
    from HNL.Systematics.systematics import checkSyst
    syst = checkSyst(chain, syst)
    if syst == 'muonScaleUp':
        return chain._lEScaleUp[index]
    elif syst == 'muonScaleDown':
        return chain._lEScaleDown[index]
    elif syst == 'muonResUp':
        return chain._lEResUp[index]
    elif syst == 'muonResDown':
        return chain._lEResDown[index]
    else:
        return chain._lECorr[index]


def isGoodGenMuon(chain, index):
    if not chain._gen_lIsPrompt[index]:         return False
    if chain._gen_lEta[index] > 2.4:            return False
    return True

def isPromptMuon(chain, index):
    if chain._lFlavor[index] != 1: return False
    if not chain._lIsPrompt[index]: return False
    return True


def isBaseMuon(chain, index, syst = None):
    if abs(chain._lEta[index]) >= 2.4:          return False
    if getMuonPt(chain, index, syst) <= 5:                   return False
    return True

def slidingCutMuon(chain, index, lowpt, lowptwp, highpt, highptwp, syst=None):
    
    slope = (highptwp - lowptwp)/(highpt-lowpt)
    if getMuonPt(chain, index, syst) < lowpt:
        return lowptwp
    elif getMuonPt(chain, index, syst) > highpt:
        return highptwp
    else:
        return lowptwp + slope*(getMuonPt(chain, index, syst)-lowpt)

#
# Cut-based selection
#
def isLooseMuonCutBased(chain, index, syst=None):
    if not isBaseMuon(chain, index, syst):            return False
    if abs(chain._dxy[index]) >= 0.05:          return False
    if abs(chain._dz[index]) >= 0.1:            return False
    if chain._relIso[index] >= 0.6:                    return False
    #PF Muon and (tracker or global) Muon requirements already in ntuplizer
    return True

def isFOMuonCutBased(chain, index, syst=None):
    if getattr(chain, 'is_loose_lepton', None) is not None and chain.is_loose_lepton[index] is not None and chain.is_loose_lepton[index][1] == 'cutbased':
        if not chain.is_loose_lepton[index][0]: return False
    else:
        if not isLooseMuonCutBased(chain, index, syst):           return False
    if chain._3dIPSig[index] >= 4:              return False 
    if not chain._lPOGMedium[index]:            return False
    return True

def isTightMuonCutBased(chain, index, syst=None):
    if getattr(chain, 'is_FO_lepton', None) is not None and chain.is_FO_lepton[index] is not None and chain.is_FO_lepton[index][1] == 'cutbased':
        if not chain.is_FO_lepton[index][0]: return False
    else:
        if not isFOMuonCutBased(chain, index, syst):              return False
    if chain._relIso[index] >= 0.1:                    return False
    return True

from HNL.ObjectSelection.bTagWP import getBTagWP

#
# ewkino selection
#
def isLooseMuonEwkino(chain, index, syst=None):
    if chain._lFlavor[index] != 1: return False
    if(abs(chain._dxy[index])>= 0.05 or abs(chain._dz[index])>= 0.1 or chain._3dIPSig[index] >= 8): return False    
    if chain._miniIso[index] >= 0.4:    return False
    if getMuonPt(chain, index, syst) <= 5 or abs(chain._lEta[index]) >= 2.4:       return False
    if not chain._lPOGLoose[index]: return False
    return True #isLooseMuon From heavyNeutrino already included in basic muon cuts

def isFOMuonEwkino(chain, index, syst=None):
    if getattr(chain, 'is_loose_lepton', None) is not None and chain.is_loose_lepton[index] is not None and chain.is_loose_lepton[index][1] == 'ewkino':
        if not chain.is_loose_lepton[index][0]: return False
    else:
        if not isLooseMuonEwkino(chain, index, syst):       return False
    if getMuonPt(chain, index, syst)[index] <= 10:       return False
    if not chain._lPOGMedium[index]: return False
    if chain._leptonMvaTTH[index] <= 0.4:
        if chain._ptRatio[index] < 0.35:        return False
        looseWP = getBTagWP(chain.year, 'loose', 'Deep')
        mediumWP = getBTagWP(chain.year, 'medium', 'Deep')
        if '2016' in chain.year:
            if (chain._closestJetDeepFlavor_b[index] + chain._closestJetDeepFlavor_bb[index] + chain._closestJetDeepFlavor_lepb[index]) >= slidingCutMuon(chain, index, 10., looseWP/1.5, 50., looseWP/5., syst): return False       
        else:
            if (chain._closestJetDeepFlavor_b[index] + chain._closestJetDeepFlavor_bb[index] + chain._closestJetDeepFlavor_lepb[index]) >= slidingCutMuon(chain, index, 10., mediumWP/2., 50., looseWP/5., syst): return False
    return True

def isTightMuonEwkino(chain, index, syst=None):
    if getattr(chain, 'is_loose_lepton', None) is not None and chain.is_loose_lepton[index] is not None and chain.is_loose_lepton[index][1] == 'ewkino':
        if not chain.is_loose_lepton[index][0]: return False
    else:
        if not isLooseMuonEwkino(chain, index, syst):       return False
    if getMuonPt(chain, index, syst) <= 10:       return False
    if not chain._lPOGMedium[index]: return False
    if chain._leptonMvaTTH[index] <= 0.4: return False
    return True

#
# Updated selection with ttH MVA
#
def isLooseMuonttH(chain, index, syst=None):
    if not isBaseMuon(chain, index, syst):            return False
    if abs(chain._dxy[index]) >= 0.05:          return False
    if abs(chain._dz[index]) >= 0.1:            return False
    if chain._3dIPSig[index] >= 8:              return False
    if chain._miniIso[index] >= 0.4:            return False
    if not chain._lPOGLoose[index]:             return False
    return True
   
def isFOMuonttH(chain, index, syst=None):
    if getattr(chain, 'is_loose_lepton', None) is not None and chain.is_loose_lepton[index] is not None and chain.is_loose_lepton[index][1] == 'leptonMVAttH':
        if not chain.is_loose_lepton[index][0]: return False
    else:
        if not isLooseMuonttH(chain, index, syst):        return False
    if getMuonPt(chain, index, syst) < 10:                  return False
    # if chain._leptonMvaTTH[index] <= 0.85:      
    #     if chain._ptRatio[index] <= 0.65: return False
    # if chain._closestJetDeepFlavor[index] >= slidingDeepFlavorThreshold(chain.year, chain._lPt[index]):
    #     return False
    return True

def isTightMuonttH(chain, index, syst=None):
    if getattr(chain, 'is_FO_lepton', None) is not None and chain.is_FO_lepton[index] is not None and chain.is_FO_lepton[index][1] == 'leptonMVAttH':
        if not chain.is_FO_lepton[index][0]: return False
    else:
        if not isFOMuonttH(chain, index, syst):   return False
    if not chain._lPOGMedium[index]:    return False
    if chain._leptonMvaTTH[index] <= 0.85:     return False
    return True
    
#
# Updated selection with tZq MVA
#
def isLooseMuontZq(chain, index, syst=None):
    if not isBaseMuon(chain, index, syst):            return False
    if abs(chain._dxy[index]) >= 0.05:          return False
    if abs(chain._dz[index]) >= 0.1:            return False
    if chain._3dIPSig[index] >= 8:              return False
    if chain._miniIso[index] >= 0.4:            return False
    if not chain._lPOGLoose[index]:             return False
    return True
   
def isFOMuontZq(chain, index, syst=None):
    if getattr(chain, 'is_loose_lepton', None) is not None and chain.is_loose_lepton[index] is not None and chain.is_loose_lepton[index][1] == 'leptonMVAtZq':
        if not chain.is_loose_lepton[index][0]: return False
    else:
        if not isLooseMuontZq(chain, index, syst):        return False
    # if chain._leptonMvaTTH[index] <= 0.4:      
    #     if chain._ptRatio[index] <= 0.4: return False
    # if chain._closestJetDeepFlavor[index] >= slidingDeepFlavorThreshold(chain.year, chain._lPt[index]):
    #     return False
    return True

def isTightMuontZq(chain, index, syst=None):
    if getattr(chain, 'is_FO_lepton', None) is not None and chain.is_FO_lepton[index] is not None and chain.is_FO_lepton[index][1] == 'leptonMVAtZq':
        if not chain.is_FO_lepton[index][0]: return False
    else:
        if not isFOMuontZq(chain, index, syst):   return False
    if not chain._lPOGMedium[index]:    return False
    if chain._leptonMvatZq[index] <= 0.4:     return False
    return True

#
# Updated selection with top MVA
#
def topPreselection(chain, index, syst=None):
    if not isBaseMuon(chain, index, syst):            return False
    if getMuonPt(chain, index, syst) < 10:                  return False
    if abs(chain._dxy[index]) >= 0.05:          return False
    if abs(chain._dz[index]) >= 0.1:            return False
    if chain._3dIPSig[index] >= 8:              return False
    if chain._miniIso[index] >= 0.4:            return False
    if not chain._lPOGMedium[index]:            return False
    return True

def isLooseMuonTop(chain, index, syst=None):
    if not topPreselection(chain, index, syst):       return False
    if chain._leptonMvaTOP[index] <= -0.45:       return False

    return True

# Taken from Luka
# https://github.com/wverbeke/ewkino/blob/tZq_new/objectSelection/MuonSelector.cc
muon_top_FO_dfdict = { '2016' : 0.015, '2016pre' : 0.015, '2016post' : 0.015, '2017' : 0.02, '2018' : 0.02}
muon_top_FO_ptratiodict = { '2016' : 0.5, '2016pre' : 0.5, '2016post' : 0.5, '2017' : 0.6, '2018' : 0.6}

def isFOMuonTop(chain, index, syst=None):
    if getattr(chain, 'is_loose_lepton', None) is not None and chain.is_loose_lepton[index] is not None and chain.is_loose_lepton[index][1] == 'leptonMVAtop':
        if not chain.is_loose_lepton[index][0]: return False
    else:
        if not isLooseMuonTop(chain, index, syst):        return False
    # if chain._ptRatio[index] < muon_top_FO_ptratiodict[chain.year]: return False
    # if (chain._closestJetDeepFlavor_b[index] + chain._closestJetDeepFlavor_bb[index] + chain._closestJetDeepFlavor_lepb[index]) > muon_top_FO_dfdict[chain.year]: return False
    if chain._leptonMvaTOP[index] <= 0.05:       return False          #Tight leptonMVA
    return True

def isTightMuonTop(chain, index, syst=None):
    if getattr(chain, 'is_FO_lepton', None) is not None and chain.is_FO_lepton[index] is not None and chain.is_FO_lepton[index][1] == 'leptonMVAtop':
        if not chain.is_FO_lepton[index][0]: return False
    else:
        if not isFOMuonTop(chain, index, syst):           return False
    # if chain._leptonMvaTOP[index] <= 0.9:       return False          #Tight leptonMVA
    if chain._leptonMvaTOP[index] <= 0.65:       return False           #Medium leptonMVA
    return True

#
# Tu Thong's selection
#
def isLooseMuonTTT(chain, index, syst=None):
    if chain._lFlavor[index] != 1:              return False
    if getMuonPt(chain, index, syst) < 5: return False
    if abs(chain._lEta[index]) > 2.4:           return False
    if abs(chain._dxy[index]) >= 0.05:          return False
    if abs(chain._dz[index]) >= 0.1:            return False
    if chain._miniIso[index] >= 0.4:            return False
    if chain._3dIPSig[index] >= 8:              return False
    if not chain._lPOGMedium[index]:            return False
    return True
   
def isFOMuonTTT(chain, index, syst=None):
    if getattr(chain, 'is_loose_lepton', None) is not None and chain.is_loose_lepton[index] is not None and chain.is_loose_lepton[index][1] == 'TTT':
        if not chain.is_loose_lepton[index][0]: return False
    else:
        if not isLooseMuonTTT(chain, index, syst):        return False
    if getMuonPt(chain, index, syst) < 10: return False
    if chain._leptonMvaTOP[index] <= 0.4:
        if chain._ptRatio[index] < 0.45:        return False
        if '2016' in chain.year:
            if (chain._closestJetDeepFlavor_b[index] + chain._closestJetDeepFlavor_bb[index] + chain._closestJetDeepFlavor_lepb[index]) >= slidingCutMuon(chain, index, 20., 0.02, 40., 0.015, syst): return False 
        else:
            if (chain._closestJetDeepFlavor_b[index] + chain._closestJetDeepFlavor_bb[index] + chain._closestJetDeepFlavor_lepb[index]) >= slidingCutMuon(chain, index, 20., 0.025, 40., 0.015, syst): return False 
    return True

def isTightMuonTTT(chain, index, syst=None):
    if getattr(chain, 'is_FO_lepton', None) is not None and chain.is_FO_lepton[index] is not None and chain.is_FO_lepton[index][1] == 'TTT':
        if not chain.is_FO_lepton[index][0]: return False
    else:
        if not isLooseMuonTTT(chain, index, syst):        return False
    if getMuonPt(chain, index, syst) < 10: return False
    if chain._leptonMvaTOP[index] <= 0.4:   return False 
    return True

#
# Updated selection with Luka's medium selection for tZq
#

def isLooseMuonLuka(chain, index, syst=None):
    if chain._lFlavor[index] != 1:              return False
    if getMuonPt(chain, index, syst) <= 5:                  return False
    if abs(chain._lEta[index]) >= 2.4:          return False
    if abs(chain._dxy[index]) >= 0.05:          return False
    if abs(chain._dz[index]) >= 0.1:            return False
    if chain._miniIso[index] >= 0.4:            return False
    if chain._3dIPSig[index] >= 8:              return False
    if not chain._lPOGMedium[index]:            return False
    return True

def isFOMuonLuka(chain, index, syst=None):
    if getattr(chain, 'is_loose_lepton', None) is not None and chain.is_loose_lepton[index] is not None and chain.is_loose_lepton[index][1] in ['Luka', 'HNL']:
        if not chain.is_loose_lepton[index][0]: return False
    else:
        if not isLooseMuonLuka(chain, index, syst):        return False
    if getMuonPt(chain, index, syst) <= 10: return False
    if chain._leptonMvaTOP[index] <= 0.4:
        if chain._ptRatio[index] < 0.45:        return False
        if '2016' in chain.year:
            if (chain._closestJetDeepFlavor_b[index] + chain._closestJetDeepFlavor_bb[index] + chain._closestJetDeepFlavor_lepb[index]) >= slidingCutMuon(chain, index, 20., 0.02, 40., 0.015, syst): return False 
        else:
            if (chain._closestJetDeepFlavor_b[index] + chain._closestJetDeepFlavor_bb[index] + chain._closestJetDeepFlavor_lepb[index]) >= slidingCutMuon(chain, index, 20., 0.025, 40., 0.015, syst): return False 
    return True

def isTightMuonLuka(chain, index, syst=None):
    if getattr(chain, 'is_FO_lepton', None) is not None and chain.is_FO_lepton[index] is not None and chain.is_FO_lepton[index][1] in ['Luka', 'HNL']:
        if not chain.is_FO_lepton[index][0]: return False
    else:
        if not isFOMuonLuka(chain, index, syst):        return False
    if getMuonPt(chain, index, syst) <= 10: return False
    if chain._leptonMvaTOP[index] <= 0.4:   return False 
    return True

def isLooseMuonHNL(chain, index, syst=None):
    if chain._lFlavor[index] != 1:              return False
    if getMuonPt(chain, index, syst) <= 10:                  return False
    if abs(chain._lEta[index]) >= 2.4:          return False
    if abs(chain._dxy[index]) >= 0.05:          return False
    if abs(chain._dz[index]) >= 0.1:            return False
    if chain._miniIso[index] >= 0.4:            return False
    if chain._3dIPSig[index] >= 8:              return False
    if not chain._lPOGMedium[index]:            return False
    return True

def isFOMuonHNL(chain, index, syst=None):
    if getattr(chain, 'is_loose_lepton', None) is not None and chain.is_loose_lepton[index] is not None and chain.is_loose_lepton[index][1] in ['Luka', 'HNL']:
        if not chain.is_loose_lepton[index][0]: return False
    else:
        if not isLooseMuonHNL(chain, index, syst):        return False
    if chain._leptonMvaTOPUL[index] <= 0.64:
        if chain._ptRatio[index] < 0.45:        return False
        if (chain._closestJetDeepFlavor_b[index] + chain._closestJetDeepFlavor_bb[index] + chain._closestJetDeepFlavor_lepb[index]) > 0.025: return False 
    return True

def isTightMuonHNL(chain, index, syst=None):
    if getattr(chain, 'is_FO_lepton', None) is not None and chain.is_FO_lepton[index] is not None and chain.is_FO_lepton[index][1] in ['Luka', 'HNL']:
        if not chain.is_FO_lepton[index][0]: return False
    else:
        if not isFOMuonHNL(chain, index, syst):        return False
    if chain._leptonMvaTOPUL[index] <= 0.64:   return False 
    return True

#
# General function for selecting muons
#
def isLooseMuon(chain, index, algo, syst=None):
    if algo == 'cutbased':       return isLooseMuonCutBased(chain, index, syst)
    elif algo == 'leptonMVAttH':        return isLooseMuonttH(chain, index, syst)
    elif algo == 'leptonMVAtZq':        return isLooseMuontZq(chain, index, syst)
    elif algo == 'leptonMVAtop':        return isLooseMuonTop(chain, index, syst)
    elif algo == 'TTT':                 return isLooseMuonTTT(chain, index, syst)
    elif algo == 'tZq' or algo == 'HNLprelegacy':                return isLooseMuonLuka(chain, index, syst)
    elif algo == 'HNL':                 return isLooseMuonHNL(chain, index, syst)
    elif algo == 'ewkino':              return isLooseMuonEwkino(chain, index, syst)
    elif algo == 'prompt':              return isPromptMuon(chain, index)
    else:
        print 'Wrong input for "algo" in isLooseMuon'
        return False

def isFOMuon(chain, index, algo, syst=None):
    if algo == 'cutbased':              return isFOMuonCutBased(chain, index, syst)
    elif algo == 'leptonMVAttH':        return isFOMuonttH(chain, index, syst)
    elif algo == 'leptonMVAtZq':        return isFOMuontZq(chain, index, syst)
    elif algo == 'leptonMVAtop':        return isFOMuonTop(chain, index, syst)
    elif algo == 'TTT':                 return isFOMuonTTT(chain, index, syst)
    elif algo == 'tZq' or algo == 'HNLprelegacy':                return isFOMuonLuka(chain, index, syst)
    elif algo == 'HNL':                return isFOMuonHNL(chain, index, syst)
    elif algo == 'ewkino':              return isFOMuonEwkino(chain, index, syst)
    elif algo == 'prompt':              return isPromptMuon(chain, index)
    else:
        print 'Wrong input for "algo" in isFOMuon'
        return False

def isTightMuon(chain, index, algo, syst=None):
    if algo == 'cutbased':       return isTightMuonCutBased(chain, index, syst)
    elif algo == 'leptonMVAttH':        return isTightMuonttH(chain, index, syst)
    elif algo == 'leptonMVAtZq':        return isTightMuontZq(chain, index, syst)
    elif algo == 'leptonMVAtop':        return isTightMuonTop(chain, index, syst)
    elif algo == 'TTT':                 return isTightMuonTTT(chain, index, syst)
    elif algo == 'tZq' or algo == 'HNLprelegacy':                return isTightMuonLuka(chain, index, syst)
    elif algo == 'HNL':                return isTightMuonHNL(chain, index, syst)
    elif algo == 'ewkino':              return isTightMuonEwkino(chain, index, syst)
    elif algo == 'prompt':              return isPromptMuon(chain, index)
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

def isGoodMuon(chain, index, workingpoint = None, algo = None, syst=None):
    workingpoint = checkMuonWP(chain, workingpoint)
    checked_algo = checkMuonAlgorithm(chain, algo)
    from HNL.Systematics.systematics import checkSyst
    checked_syst = checkSyst(chain, syst)

    if workingpoint == 'loose':
        if getattr(chain, 'is_loose_lepton', None) is not None and chain.is_loose_lepton[index] is not None and algo is None:
            return chain.is_loose_lepton[index][0] and chain._lFlavor[index] == 1
        else: 
            return isLooseMuon(chain, index, checked_algo, checked_syst)
    elif workingpoint == 'FO':
        if getattr(chain, 'is_FO_lepton', None) is not None and chain.is_FO_lepton[index] is not None and algo is None:  
            return chain.is_FO_lepton[index][0] and chain._lFlavor[index] == 1
        else: 
            return isFOMuon(chain, index, checked_algo, checked_syst)
    elif workingpoint == 'tight':
        if getattr(chain, 'is_tight_lepton', None) is not None and chain.is_tight_lepton[index] is not None and algo is None:  
            return chain.is_tight_lepton[index][0] and chain._lFlavor[index] == 1
        else: 
            return isTightMuon(chain, index, checked_algo, checked_syst)

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
        return 1+max(0., chain._relIso[index]-0.1)
    elif algo == 'TTT':
        return 0.67/chain._ptRatio[index]
    else:
        # return 0.8/chain._ptRatio[index]
        #return 0.67/chain._ptRatio[index]
        return 0.72/chain._ptRatio[index]
