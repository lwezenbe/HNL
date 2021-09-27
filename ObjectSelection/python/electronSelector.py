from HNL.Tools.helpers import deltaR
import math
from HNL.ObjectSelection.bTagWP import getBTagWP

#
# Simple gen level selection
#
def isGoodGenElectron(chain, index):
    if not chain._gen_lIsPrompt[index]:         return False
    if chain._gen_lEta[index] > 2.5:            return False
    return True

#
# Basic kinematic cuts
#
def isBaseElectron(chain, index):
    if chain._lPtCorr[index] <= 5.:                  return False
    if abs(chain._lEta[index]) >= 2.5:          return False
    return True 

#
# We dont use electrons that fall within dr 0.05 of a loose muon
#
from HNL.ObjectSelection.muonSelector import isGoodMuon
def isCleanFromMuons(chain, index):
    
    for mu in xrange(chain._nMu):
        if not isGoodMuon(chain, mu, workingpoint='loose'):  continue
        if deltaR(chain._lEta[mu], chain._lEta[index], chain._lPhi[mu], chain._lPhi[index]) < 0.05: return False
    return True


def slidingCutElectron(chain, index, lowpt, lowptwp, highpt, highptwp):
    
    if chain._lPtCorr[index] < lowpt:
        return lowptwp
    elif chain._lPtCorr[index] > highpt:
        return highptwp
    else:
        slope = (highptwp - lowptwp)/(highpt-lowpt)
        return lowptwp + slope*(chain._lPtCorr[index]-lowpt)

#
# WP as defined in AN 2017/014
#
        
def cutBasedMVA(chain, index, wp, pt):
    
    if pt < 15:
        if wp == 'FO':
            if abs(chain._lEta[index]) < 0.8: return -0.02
            elif abs(chain._lEta[index]) < 1.479: return -0.52
            else:       return -0.52
        else:
            if abs(chain._lEta[index]) < 0.8: return 0.77
            elif abs(chain._lEta[index]) < 1.479: return 0.56
            else:       return 0.48

    elif pt > 25:
        if wp == 'FO':
            if abs(chain._lEta[index]) < 0.8: return -0.02
            elif abs(chain._lEta[index]) < 1.479: return -0.52
            else:       return -0.52
        else:
            if abs(chain._lEta[index]) < 0.8: return 0.52
            elif abs(chain._lEta[index]) < 1.479: return 0.11
            else:       return -0.01
    else:
        return slidingCutElectron(chain, index, 15., cutBasedMVA(chain, index, wp, 14), 25., cutBasedMVA(chain, index, wp, 26))

def isLooseElectronCutBased(chain, index):
   
    if not isBaseElectron(chain, index):        return False 
    if not isCleanFromMuons(chain, index):      return False
    if chain._lPtCorr[index] <= 10.:            return False
    if abs(chain._dxy[index]) >= 0.05:          return False
    if abs(chain._dz[index]) >= 0.1:            return False
    if chain._relIso[index] >= 0.6:             return False
    if not chain._lElectronPassConvVeto[index]: return False
    if chain._lElectronMissingHits[index] > 1:  return False
    return True

def isFOElectronCutBased(chain, index):
    if getattr(chain, 'is_loose_lepton', None) is not None and chain.is_loose_lepton[index] is not None and chain.is_loose_lepton[index][1] == 'cutbased':
        if not chain.is_loose_lepton[index][0]: return False
    else:
        if not isLooseElectronCutBased(chain, index):       return False
    if chain._3dIPSig[index] >= 4.:              return False
    if cutBasedMVA(chain, index, 'FO', chain._lPtCorr[index]) >= chain._lElectronSummer16MvaGP[index]: return False
    # if not chain._lElectronPassEmu[index]:      return False   #sigma_ietaieta, H/E, deltaEta_in, deltaPhi_in, 1/E-1/p
    if abs(chain._lEta[index]) < 1.479 and chain._lElectronSigmaIetaIeta[index] > 0.011: return False
    if 1.479 < abs(chain._lEta[index]) and chain._lElectronSigmaIetaIeta[index] > 0.033: return False
    if abs(chain._lEta[index]) < 1.479 and chain._lElectronHOverE[index] > 0.1: return False
    if 1.479 < abs(chain._lEta[index]) and chain._lElectronHOverE[index] > 0.07: return False
    if abs(chain._lEta[index]) < 1.479 and chain._lElectronDeltaEtaSuperClusterTrack[index] > 0.01: return False
    if 1.479 < abs(chain._lEta[index]) and chain._lElectronDeltaEtaSuperClusterTrack[index] > 0.008: return False
    if abs(chain._lEta[index]) < 1.479 and chain._lElectronDeltaPhiSuperClusterTrack[index] > 0.04: return False
    if 1.479 < abs(chain._lEta[index]) and chain._lElectronDeltaPhiSuperClusterTrack[index] > 0.07: return False
    if abs(chain._lEta[index]) < 1.479 and (chain._lElectronEInvMinusPInv[index] > 0.01 or chain._lElectronEInvMinusPInv[index] < -0.05): return False
    if 1.479 < abs(chain._lEta[index]) and (chain._lElectronEInvMinusPInv[index] > 0.005 or chain._lElectronEInvMinusPInv[index] < -0.05): return False
    if chain._lElectronMissingHits[index] != 0: return False
    return True

def isTightElectronCutBased(chain, index):
    if getattr(chain, 'is_FO_lepton', None) is not None and chain.is_FO_lepton[index] is not None and chain.is_FO_lepton[index][1] == 'cutbased':
        if not chain.is_FO_lepton[index][0]: return False
    else:
        if not isFOElectronCutBased(chain, index):          return False
    if chain._relIso[index] >= 0.1:                    return False
    if cutBasedMVA(chain, index, 'tight', chain._lPtCorr[index]) >= chain._lElectronSummer16MvaGP[index]: return False
    return True

#
# Ewkino Working Points
#
def isLooseElectronEwkino(chain, index):
    if chain._lFlavor[index] != 0: return False
    if(abs(chain._dxy[index])>= 0.05 or abs(chain._dz[index])>= 0.1 or chain._3dIPSig[index] >= 8): return False    
    if chain._miniIso[index] >= 0.4:    return False
    if chain._lPtCorr[index] <= 7 or abs(chain._lEta[index]) >= 2.5:       return False
    if chain._lElectronMissingHits[index] > 1: return False
    if not isCleanFromMuons(chain, index, 'ewkino'):      return False
    return True #isLooseMuon From heavyNeutrino already included in basic muon cuts

def isFOElectronEwkino(chain, index):
    if getattr(chain, 'is_loose_lepton', None) is not None and chain.is_loose_lepton[index] is not None and chain.is_loose_lepton[index][1] == 'ewkino':
        if not chain.is_loose_lepton[index][0]: return False
    else:
        if not isLooseElectronEwkino(chain, index):       return False
    if chain._lPtCorr[index] <= 10:       return False
    if chain._lElectronMissingHits[index] != 0: return False
    if abs(chain._lEta[index]) < 1.479 and chain._lElectronSigmaIetaIeta[index] > 0.011: return False
    if 1.479 < abs(chain._lEta[index]) and chain._lElectronSigmaIetaIeta[index] > 0.033: return False
    if chain._lElectronEInvMinusPInv[index] < -0.04: return False
    if not chain._lElectronPassConvVeto[index]:       return False
    if chain._lElectronHOverE[index] > 0.1: return False
    if (chain._closestJetDeepFlavor_b[index] + chain._closestJetDeepFlavor_bb[index] + chain._closestJetDeepFlavor_lepb[index]) >=   getBTagWP(chain.year, 'tight', 'Deep'): return False       
    if chain._leptonMvaTTH[index] <= 0.4:
        if not passMVAWP90(chain, index): return False
        if chain.year == 2018:
            if chain._ptRatio[index] < 0.6:        return False
        else:
            if chain._ptRatio[index] < 0.7:        return False
    else:
        if not passMVAloose(chain, index): return False
    return True

def isTightElectronEwkino(chain, index):
    if getattr(chain, 'is_FO_lepton', None) is not None and chain.is_loose_lepton[index] is not None and chain.is_loose_lepton[index][1] == 'ewkino':
        if not chain.is_loose_lepton[index][0]: return False
    else:
        if not isLooseElectronEwkino(chain, index):       return False
    if chain._lPtCorr[index] <= 10:       return False
    if chain._lElectronMissingHits[index] != 0: return False
    if abs(chain._lEta[index]) < 1.479 and chain._lElectronSigmaIetaIeta[index] > 0.011: return False
    if 1.479 < abs(chain._lEta[index]) and chain._lElectronSigmaIetaIeta[index] > 0.033: return False
    if chain._lElectronEInvMinusPInv[index] < -0.04: return False
    if chain._lElectronHOverE[index] > 0.1: return False
    if (chain._closestJetDeepFlavor_b[index] + chain._closestJetDeepFlavor_bb[index] + chain._closestJetDeepFlavor_lepb[index]) >= getBTagWP(chain.year, 'tight', 'Deep'): return False  
    if not chain._lElectronPassConvVeto[index]:       return False
    if chain._leptonMvaTTH[index] <= 0.4:   return False
    return True

#
# WP as defined in ttH analysis
#
def rawElectronMVA(mva):
    if mva == 1: mva = 0.9999 #temporary fix to the value being 1 in the tree, fix this
    if mva == -1: mva = -0.9999 #temporary fix to the value being 1 in the tree, fix this
    return -0.5 * ( math.log( ( 1. - mva ) / ( 1. + mva ) ) )

def electronMVAcategory(chain, index):
    abs_etaSC = abs(chain._lEtaSC[index])
    if chain._lPtCorr[index] < 10:
        if(abs_etaSC < .8):             return 0
        elif(abs_etaSC < 1.479):        return 1
        else:                           return 2
    else:
        if(abs_etaSC < .8):             return 3
        elif(abs_etaSC < 1.479):        return 4
        else:                           return 5

def looseMVAcut(chain, index):
    category = electronMVAcategory(chain, index)
    if category == 0:  return 0.700642584415
    elif category == 1:  return 0.739335420875
    elif category == 2:  return 1.45390456109
    elif category == 3:  return -0.146270871164
    elif category == 4:  return -0.0315850882679
    else: return -0.0321841194737 


def wp80MVACut(chain, index):
    category = electronMVAcategory(chain, index)
    if category == 0:  return 3.53495358797 - math.exp( -chain._lPtCorr[index] / 3.07272325141 ) * 9.94262764352
    elif category == 1:  return 3.06015605623 - math.exp( -chain._lPtCorr[index] / 1.95572234114 ) * 14.3091184421
    elif category == 2:  return 3.02052519639 - math.exp( -chain._lPtCorr[index] / 1.59784164742 ) * 28.719380105
    elif category == 3:  return 7.35752275071 - math.exp( -chain._lPtCorr[index] / 15.87907864 ) * 7.61288809226
    elif category == 4:  return 6.41811074032 - math.exp( -chain._lPtCorr[index] / 14.730562874 ) * 6.96387331587
    else: return 5.64936312428 - math.exp( -chain._lPtCorr[index] / 16.3664949747 ) * 7.19607610311

def wp90MVACut(chain, index):
    category = electronMVAcategory(chain, index)
    if category == 0: return 2.84704783417 - math.exp( -chain._lPtCorr[index] / 3.32529515837 ) * 9.38050947827
    elif category == 1: return 2.03833922005 - math.exp( -chain._lPtCorr[index] / 1.93288758682 ) * 15.364588247
    elif category == 2: return 1.82704158461 - math.exp( -chain._lPtCorr[index] / 1.89796754399 ) * 19.1236071158
    elif category == 3: return 6.12931925263 - math.exp( -chain._lPtCorr[index] / 13.281753835 ) * 8.71138432196
    elif category == 4: return 5.26289004857 - math.exp( -chain._lPtCorr[index] / 13.2154971491 ) * 8.0997882835
    else: return 4.37338792902 - math.exp( -chain._lPtCorr[index] / 14.0776094696 ) * 8.48513324496

def passMVAloose(chain, index):
    rawMVA = rawElectronMVA(chain._lElectronMvaFall17NoIso[index])
    return rawMVA > looseMVAcut(chain, index)

def passMVAWP80(chain, index):
    rawMVA = rawElectronMVA(chain._lElectronMvaFall17NoIso[index])
    return rawMVA > wp80MVACut(chain, index)
    
def passMVAWP90(chain, index):
    rawMVA = rawElectronMVA(chain._lElectronMvaFall17NoIso[index])
    return rawMVA > wp90MVACut(chain, index)

def isLooseElectronttH(chain, index):
    
    if abs(chain._lEta[index]) >= 2.5:          return False
    if chain._lPtCorr[index] < 7:                  return False
    if not isCleanFromMuons(chain, index):      return False
    if abs(chain._dxy[index]) >= 0.05:          return False
    if abs(chain._dz[index]) >= 0.1:            return False
    if chain._miniIso[index] >= 0.4:                    return False
    if chain._3dIPSig[index] >= 8:              return False
    if chain._lElectronMissingHits[index] > 1:  return False
    # if not passMVAloose(chain, index):  return False
    return True

def isFOElectronttH(chain, index):
    if getattr(chain, 'is_loose_lepton', None) is not None and chain.is_loose_lepton[index] is not None and chain.is_loose_lepton[index][1] == 'leptonMVAttH':
        if not chain.is_loose_lepton[index][0]: return False
    else:
        if not isLooseElectronttH(chain, index):    return False
    if chain._lPtCorr[index] < 10:                  return False
    # if chain._lElectronMissingHits[index] != 0: return False
    # if not chain._lElectronPassEmu[index]:      return False
    # if chain._closestJetDeepFlavor[index] >= getBTagWP(chain.year, 'medium', 'Deep'): return False
    # if chain._leptonMvaTTH[index] <= 0.8:
    #     if not passMVAWP80(chain, index):       return False
    #     if chain._ptRatio[index] <= .7:           return False
    # else:
    #    if not passMVAloose(chain, index):      return False
    # if not chain._lElectronPassConvVeto[index]:          return False
    return True

def isTightElectronttH(chain, index):
    if getattr(chain, 'is_FO_lepton', None) is not None and chain.is_FO_lepton[index] is not None and chain.is_FO_lepton[index][1] == 'leptonMVAttH':
        if not chain.is_FO_lepton[index][0]: return False
    else:
        if not isFOElectronttH(chain, index):       return False
    if chain._leptonMvaTTH[index] <= 0.8:       return False
    return True

#    
# tZq MVA selection
#
def isLooseElectrontZq(chain, index):
    
    if abs(chain._lEta[index]) >= 2.5:          return False
    if chain._lPtCorr[index] < 7:                  return False
    if not isCleanFromMuons(chain, index):      return False
    if abs(chain._dxy[index]) >= 0.05:          return False
    if abs(chain._dz[index]) >= 0.1:            return False
    if chain._miniIso[index] >= 0.4:                    return False
    if chain._3dIPSig[index] >= 8:              return False
    if chain._lElectronMissingHits[index] > 1:  return False
    # if not passMVAloose(chain, index):  return False
    return True

def isFOElectrontZq(chain, index):
    if getattr(chain, 'is_loose_lepton', None) is not None and chain.is_loose_lepton[index] is not None and chain.is_loose_lepton[index][1] == 'leptonMVAtZq':
        if not chain.is_loose_lepton[index][0]: return False
    else:
        if not isLooseElectrontZq(chain, index):    return False
    if chain._lPtCorr[index] < 10:                  return False
    # if chain._lElectronMissingHits[index] != 0: return False
    # if not chain._lElectronPassEmu[index]:      return False
    # if chain._closestJetDeepFlavor[index] >= getBTagWP(chain.year, 'medium', 'Deep'): return False
    # if chain._leptonMvatZq[index] <= 0.4:
    #     if not passMVAWP80(chain, index):       return False
    #     if chain._ptRatio[index] <= .4:           return False
    # else:
    #     if not passMVAloose(chain, index):      return False
    # if not chain._lElectronPassConvVeto[index]:          return False
    return True

def isTightElectrontZq(chain, index):
    if getattr(chain, 'is_FO_lepton', None) is not None and chain.is_FO_lepton[index] is not None and chain.is_FO_lepton[index][1] == 'leptonMVAtZq':
        if not chain.is_FO_lepton[index][0]: return False
    else:
        if not isFOElectrontZq(chain, index):       return False
    if chain._leptonMvatZq[index] <= 0.4:       return False
    return True

#
# top lepton MVA selection
#
def topPreselection(chain, index):
    if not isBaseElectron(chain, index):        return False
    if chain._lPtCorr[index] <= 10.:            return False
    if not isCleanFromMuons(chain, index):      return False
    if abs(chain._dxy[index]) >= 0.05:          return False
    if abs(chain._dz[index]) >= 0.1:            return False
    if chain._miniIso[index] >= 0.4:            return False
    if chain._3dIPSig[index] >= 8:              return False
    if chain._lElectronMissingHits[index] > 1:  return False
    return True

def isLooseElectronTop(chain, index):
    if not topPreselection(chain, index):       return False
    if chain._leptonMvaTOP[index] <= 0.0:       return False
    return True

#
# Taken from Luka
# https://github.com/wverbeke/ewkino/blob/tZq_new/objectSelection/ElectronSelector.cc
#
def isFOElectronTop(chain, index):
    if getattr(chain, 'is_loose_lepton', None) is not None and chain.is_loose_lepton[index] is not None and chain.is_loose_lepton[index][1] == 'leptonMVAtop':
        if not chain.is_loose_lepton[index][0]: return False
    else:
        if not isLooseElectronTop(chain, index):       return False
    if not chain._lElectronPassConvVeto[index]: return False
    if chain._leptonMvaTOP[index] <= 0.6:       return False




    # if chain._lElectronHOverE[index] > 0.10:    return False
    # if chain._lElectronEInvMinusPInv[index] < -0.04:    return False
    # #Barrel
    # if abs(chain._lEta[index]) < 1.479:
    #     if chain._lElectronSigmaIetaIeta[index] > 0.011:    return False
    # #endcap
    # else:
    #     if chain._lElectronSigmaIetaIeta[index] < 0.03:    return False
    # if chain._leptonMvaTOP[index] <= 0.6:
    #     if not passMVAloose(chain, index):  return False
    #     if chain._ptRatio[index] < 0.5:     return False
    #     if (chain._closestJetDeepFlavor_b[index] + chain._closestJetDeepFlavor_bb[index] + chain._closestJetDeepFlavor_lepb[index]) >= slidingCutElectron(chain, index, 25., 0.1, 50., 0.05): 
    #         return False        

    return True

def isTightElectronTop(chain, index):
    if getattr(chain, 'is_FO_lepton', None) is not None and chain.is_FO_lepton[index] is not None and chain.is_FO_lepton[index][1] == 'leptonMVAtop':
        if not chain.is_FO_lepton[index][0]: return False
    else:
        if not isFOElectronTop(chain, index):       return False
    if chain._leptonMvaTOP[index] <= 0.9:       return False  #Tight leptonMVA wp  
    # if chain._leptonMvaTOP[index] <= 0.6:       return False    #Medium leptonMVA wp
    return True

#
# Tu Thong's selection
#
def isLooseElectronTTT(chain, index):
    if chain._lFlavor[index] != 0:              return False
    if not isCleanFromMuons(chain, index):      return False
    if chain._lPtCorr[index] < 5: return False
    if abs(chain._lEta[index]) > 2.5: return False
    if abs(chain._dxy[index]) >= 0.05:          return False
    if abs(chain._dz[index]) >= 0.1:            return False
    if chain._miniIso[index] >= 0.4:            return False
    if chain._3dIPSig[index] >= 8:              return False
    if chain._lElectronMissingHits[index] > 2:  return False
    return True

def isFOElectronTTT(chain, index):
    if getattr(chain, 'is_loose_lepton', None) is not None and chain.is_loose_lepton[index] is not None and chain.is_loose_lepton[index][1] == 'TTT':
        if not chain.is_loose_lepton[index][0]: return False
    else:
        if not isLooseElectronTTT(chain, index):      return False
    if chain._lPtCorr[index] < 10: return False
    if chain._lElectronHOverE[index] >= 0.10:    return False
    if chain._lElectronEInvMinusPInv[index] <= -0.04:    return False
    if not chain._lElectronPassConvVeto[index]: return False
    # if chain._lElectronMissingHits[index] > 1:  return False
    #Barrel
    if abs(chain._lEta[index]) <= 1.479:
        if chain._lElectronSigmaIetaIeta[index] >= 0.011:    return False
    #endcap
    else:
        if chain._lElectronSigmaIetaIeta[index] >= 0.03:    return False
    if chain._leptonMvaTOP[index] <= 0.4:
        if not passMVAloose(chain, index):  return False
        if chain._ptRatio[index] < 0.5:     return False
        if chain.year == 2016:
            if (chain._closestJetDeepFlavor_b[index] + chain._closestJetDeepFlavor_bb[index] + chain._closestJetDeepFlavor_lepb[index]) >= slidingCutElectron(chain, index, 25., 0.5, 50., 0.05): 
                return False        
        elif chain.year == 2017:
            if (chain._closestJetDeepFlavor_b[index] + chain._closestJetDeepFlavor_bb[index] + chain._closestJetDeepFlavor_lepb[index]) >= slidingCutElectron(chain, index, 25., 0.5, 50., 0.08): 
                return False        
        elif chain.year == 2018:
            if (chain._closestJetDeepFlavor_b[index] + chain._closestJetDeepFlavor_bb[index] + chain._closestJetDeepFlavor_lepb[index]) >= slidingCutElectron(chain, index, 25., 0.4, 50., 0.05): 
                return False        
        # print 'deepflavor'
    return True

def isTightElectronTTT(chain, index):
    if getattr(chain, 'is_FO_lepton', None) is not None and chain.is_FO_lepton[index] is not None and chain.is_FO_lepton[index][1] == 'TTT':
        if not chain.is_FO_lepton[index][0]: return False
    else:
        if not isFOElectronTTT(chain, index):      return False
    if chain._leptonMvaTOP[index] <= 0.4: return False        
    return True

#
# Luka's selection
#
def isLooseElectronLuka(chain, index):
    if chain._lFlavor[index] != 0:              return False
    if not isCleanFromMuons(chain, index):      return False
    if chain._lPtCorr[index] < 5: return False
    if abs(chain._lEta[index]) > 2.5: return False
    if abs(chain._dxy[index]) >= 0.05:          return False
    if abs(chain._dz[index]) >= 0.1:            return False
    if chain._miniIso[index] >= 0.4:            return False
    if chain._3dIPSig[index] >= 8:              return False
    if chain._lElectronMissingHits[index] >= 2:  return False
    return True

def isFOElectronLuka(chain, index):
    if getattr(chain, 'is_loose_lepton', None) is not None and chain.is_loose_lepton[index] is not None and chain.is_loose_lepton[index][1] == 'Luka':
        if not chain.is_loose_lepton[index][0]: return False
    else:
        if not isLooseElectronLuka(chain, index):      return False
    if chain._lPtCorr[index] <= 10: return False
    if chain._lElectronHOverE[index] >= 0.10:    return False
    if chain._lElectronEInvMinusPInv[index] <= -0.04:    return False
    if not chain._lElectronPassConvVeto[index]: return False
    if not chain._lElectronChargeConst[index]: return False
    #Barrel
    if abs(chain._lEtaSC[index]) <= 1.479:
        if chain._lElectronSigmaIetaIeta[index] >= 0.011:    return False
    #endcap
    else:
        if chain._lElectronSigmaIetaIeta[index] >= 0.03:    return False
    if chain._leptonMvaTOP[index] <= 0.4:
        if not chain._lElectronPassMVAFall17NoIsoWPLoose[index]: return False
        if chain._ptRatio[index] < 0.5:     return False
        if (chain._closestJetDeepFlavor_b[index] + chain._closestJetDeepFlavor_bb[index] + chain._closestJetDeepFlavor_lepb[index]) > 0.5: return False
    return True

def isTightElectronLuka(chain, index):
    if getattr(chain, 'is_FO_lepton', None) is not None and chain.is_FO_lepton[index] is not None and chain.is_FO_lepton[index][1] == 'Luka':
        if not chain.is_FO_lepton[index][0]: return False
    else:
        if not isFOElectronLuka(chain, index):      return False
    if chain._leptonMvaTOP[index] <= 0.4: return False        
    return True

#
# HNL selection
#
def isLooseElectronHNL(chain, index):
    if chain._lFlavor[index] != 0:              return False
    if not isCleanFromMuons(chain, index):      return False
    if chain._lPtCorr[index] < 5: return False
    if abs(chain._lEta[index]) > 2.5: return False
    if abs(chain._dxy[index]) >= 0.05:          return False
    if abs(chain._dz[index]) >= 0.1:            return False
    if chain._miniIso[index] >= 0.4:            return False
    if chain._3dIPSig[index] >= 8:              return False
    if chain._lElectronMissingHits[index] >= 2:  return False
    return True

def isFOElectronHNL(chain, index):
    if getattr(chain, 'is_loose_lepton', None) is not None and chain.is_loose_lepton[index] is not None and chain.is_loose_lepton[index][1] == 'HNL':
        if not chain.is_loose_lepton[index][0]: return False
    else:
        if not isLooseElectronHNL(chain, index):      return False
    if chain._lPtCorr[index] <= 10: return False
    if chain._lElectronHOverE[index] >= 0.10:    return False
    if chain._lElectronEInvMinusPInv[index] <= -0.04:    return False
    if not chain._lElectronPassConvVeto[index]: return False
    #Barrel
    if abs(chain._lEtaSC[index]) <= 1.479:
        if chain._lElectronSigmaIetaIeta[index] >= 0.011:    return False
    #endcap
    else:
        if chain._lElectronSigmaIetaIeta[index] >= 0.03:    return False
    if chain._leptonMvaTOP[index] <= 0.4:
        if not chain._lElectronPassMVAFall17NoIsoWPLoose[index]: return False
        if chain._ptRatio[index] < 0.5:     return False
        if (chain._closestJetDeepFlavor_b[index] + chain._closestJetDeepFlavor_bb[index] + chain._closestJetDeepFlavor_lepb[index]) > 0.5: return False
    return True

def isTightElectronHNL(chain, index):
    if getattr(chain, 'is_FO_lepton', None) is not None and chain.is_FO_lepton[index] is not None and chain.is_FO_lepton[index][1] == 'HNL':
        if not chain.is_FO_lepton[index][0]: return False
    else:
        if not isFOElectronHNL(chain, index):      return False
    if chain._leptonMvaTOP[index] <= 0.4: return False        
    return True


#
# General functions for selection
#
def isLooseElectron(chain, index, algo):
    if algo == 'cutbased':              return isLooseElectronCutBased(chain, index)
    elif algo == 'leptonMVAttH':        return isLooseElectronttH(chain, index)
    elif algo == 'leptonMVAtZq':        return isLooseElectrontZq(chain, index)
    elif algo == 'leptonMVAtop':        return isLooseElectronTop(chain, index)
    elif algo == 'TTT':                 return isLooseElectronTTT(chain, index)
    elif algo == 'Luka':                 return isLooseElectronLuka(chain, index)
    elif algo == 'HNL':                 return isLooseElectronHNL(chain, index)
    elif algo == 'ewkino':              return isLooseElectronEwkino(chain, index)
    else:
        print 'Wrong input for "algo" in isLooseElectron'
        return False

def isFOElectron(chain, index, algo):
    if algo == 'cutbased':              return isFOElectronCutBased(chain, index)
    elif algo == 'leptonMVAttH':        return isFOElectronttH(chain, index)
    elif algo == 'leptonMVAtZq':        return isFOElectrontZq(chain, index)
    elif algo == 'leptonMVAtop':        return isFOElectronTop(chain, index)
    elif algo == 'TTT':                 return isFOElectronTTT(chain, index)
    elif algo == 'Luka':                return isFOElectronLuka(chain, index)
    elif algo == 'HNL':                return isFOElectronHNL(chain, index)
    elif algo == 'ewkino':              return isFOElectronEwkino(chain, index)
    else:
        print 'Wrong input for "algo" in isFOElectron'
        return False

def isTightElectron(chain, index, algo):
    if algo == 'cutbased':              return isTightElectronCutBased(chain, index)
    elif algo == 'leptonMVAttH':        return isTightElectronttH(chain, index)
    elif algo == 'leptonMVAtZq':        return isTightElectrontZq(chain, index)
    elif algo == 'leptonMVAtop':        return isTightElectronTop(chain, index)
    elif algo == 'TTT':                 return isTightElectronTTT(chain, index)
    elif algo == 'Luka':                 return isTightElectronLuka(chain, index)
    elif algo == 'HNL':                 return isTightElectronHNL(chain, index)
    elif algo == 'ewkino':              return isTightElectronEwkino(chain, index)
    else:
        print 'Wrong input for "algo" in isTightElectron'
        return False

from HNL.ObjectSelection.objectSelection import objectSelectionCollection
def checkElectronAlgorithm(chain, algo):
    if algo is None:
        try:
            chain.obj_sel
        except:
            #Initiate default object selection
            chain.obj_sel = objectSelectionCollection()
        return chain.obj_sel['light_algo']
    else:
        return algo

def checkElectronWP(chain, wp):
    if wp is None:
        try:
            chain.obj_sel
        except:
            #Initiate default object selection
            chain.obj_sel = objectSelectionCollection()
        return chain.obj_sel['ele_wp']
    else:
        return wp

#
# algo is only used in the isGoodLeptonCustom function, in most cases this is not used 
# except when you specifically use it. By doing this, we make sure algo is centrally defined
# and reduce the introduction of a bug due to inconsistent use of algo
#
def isGoodElectron(chain, index, workingpoint = None, algo = None):
    workingpoint = checkElectronWP(chain, workingpoint)
    checked_algo = checkElectronAlgorithm(chain, algo)

    if workingpoint == 'loose':
        if getattr(chain, 'is_loose_lepton', None) is not None and chain.is_loose_lepton[index] is not None and algo is None:
            return chain.is_loose_lepton[index][0] and chain._lFlavor[index] == 0
        else:
            return isLooseElectron(chain, index, checked_algo)
    elif workingpoint == 'FO':
        if getattr(chain, 'is_FO_lepton', None) is not None and chain.is_FO_lepton[index] is not None and algo is None:
            return chain.is_FO_lepton[index][0] and chain._lFlavor[index] == 0
        else:
            return isFOElectron(chain, index, checked_algo)
    elif workingpoint == 'tight':
        if getattr(chain, 'is_tight_lepton', None) is not None and chain.is_tight_lepton[index] is not None and algo is None:
            return chain.is_tight_lepton[index][0] and chain._lFlavor[index] == 0
        else:
            return isTightElectron(chain, index, checked_algo)

#
# Check for fakes
#
def isFakeElectron(chain, index):
    return not chain._lIsPrompt[index]

#
# Cone correction
#
def electronConeCorrection(chain, index, algo = None):
    algo = checkElectronAlgorithm(chain, algo)
    if algo == 'cutbased':
        return 1+max(0., chain._relIso[index]-0.1)
    else:
        return 0.67/chain._ptRatio[index]
