from HNL.Tools.helpers import deltaR
import math
from bTagWP import getBTagWP

#
# Simple gen level selection
#
def isGoodGenElectron(chain, index):
    if not chain._gen_lIsPrompt[index]:         return False
    if chain._gen_lEta[index] > 2.5:            return False
    return True

#
# We dont use electrons that fall within dr 0.05 of a loose muon
#
from HNL.ObjectSelection.muonSelector import isLooseMuon
def isCleanFromMuons(chain, index, mu_algo = 'cut_based'):
    
    for mu in xrange(chain._nMu):
        if not isLooseMuon(chain, mu, mu_algo):  continue
        if deltaR(chain._lEta[mu], chain._lEta[index], chain._lPhi[mu], chain._lPhi[index]) < 0.05: return False
    return True

#
# WP as defined in AN 2017/014
#
def slidingCut(chain, index, high, low):
    
    slope = (high - low)/10.
    return min(low, max(high, low + slope*(chain._lPt[index]-15)))
        
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
        return slidingCut(chain, index, cutBasedMVA(chain, index, wp, 14), cutBasedMVA(chain, index, wp, 26))

def isLooseElectronCutBased(chain, index):
    
    if abs(chain._lEta[index]) >= 2.5:          return False
    if chain._lPt[index] <= 10:                  return False
    if not isCleanFromMuons(chain, index):      return False
    if abs(chain._dxy[index]) >= 0.05:          return False
    if abs(chain._dz[index]) >= 0.1:            return False
    if chain._relIso[index] >= 0.6:                    return False
    if not chain._lElectronPassConvVeto[index]: return False
    if chain._lElectronMissingHits[index] > 1:  return False
    return True

def isFOElectronCutBased(chain, index):
    
    if not isLooseElectronCutBased(chain, index):       return False
    if chain._3dIPSig[index] >= 4:              return False
    if cutBasedMVA(chain, index, 'FO', chain._lPt[index]) >= chain._lElectronSummer16MvaGP[index]: return False
    if not chain._lElectronPassEmu[index]:      return False   #sigma_ietaieta, H/E, deltaEta_in, deltaPhi_in, 1/E-1/p
    if chain._lElectronMissingHits[index] != 0: return False
    return True

def isTightElectronCutBased(chain, index):

    if not isFOElectronCutBased(chain, index):          return False
    if chain._relIso[index] >= 0.1:                    return False
    if cutBasedMVA(chain, index, 'tight', chain._lPt[index]) >= chain._lElectronSummer16MvaGP[index]: return False
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
    if chain._lPt[index] < 10:
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
    if category == 0:  return 3.53495358797 - math.exp( -chain._lPt[index] / 3.07272325141 ) * 9.94262764352
    elif category == 1:  return 3.06015605623 - math.exp( -chain._lPt[index] / 1.95572234114 ) * 14.3091184421
    elif category == 2:  return 3.02052519639 - math.exp( -chain._lPt[index] / 1.59784164742 ) * 28.719380105
    elif category == 3:  return 7.35752275071 - math.exp( -chain._lPt[index] / 15.87907864 ) * 7.61288809226
    elif category == 4:  return 6.41811074032 - math.exp( -chain._lPt[index] / 14.730562874 ) * 6.96387331587
    else: return 5.64936312428 - math.exp( -chain._lPt[index] / 16.3664949747 ) * 7.19607610311

def wp90MVACut(chain, index):
    category = electronMVAcategory(chain, index)
    if category == 0: return 2.84704783417 - math.exp( -chain._lPt[index] / 3.32529515837 ) * 9.38050947827
    elif category == 1: return 2.03833922005 - math.exp( -chain._lPt[index] / 1.93288758682 ) * 15.364588247
    elif category == 2: return 1.82704158461 - math.exp( -chain._lPt[index] / 1.89796754399 ) * 19.1236071158
    elif category == 3: return 6.12931925263 - math.exp( -chain._lPt[index] / 13.281753835 ) * 8.71138432196
    elif category == 4: return 5.26289004857 - math.exp( -chain._lPt[index] / 13.2154971491 ) * 8.0997882835
    else: return 4.37338792902 - math.exp( -chain._lPt[index] / 14.0776094696 ) * 8.48513324496

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
    if chain._lPt[index] < 7:                  return False
    if not isCleanFromMuons(chain, index):      return False
    if abs(chain._dxy[index]) >= 0.05:          return False
    if abs(chain._dz[index]) >= 0.1:            return False
    if chain._miniIso[index] >= 0.4:                    return False
    if chain._3dIPSig[index] >= 8:              return False
    if chain._lElectronMissingHits[index] > 1:  return False
    if not passMVAloose(chain, index):  return False
    return True

def isFOElectronttH(chain, index):
    
    if not isLooseElectronttH(chain, index):    return False
    if chain._lPt[index] < 10:                  return False
    if chain._lElectronMissingHits[index] != 0: return False
    if not chain._lElectronPassEmu[index]:      return False
    if chain._closestJetDeepFlavor[index] >= getBTagWP(chain.year, 'medium', 'Deep'): return False
    if chain._leptonMvaTTH[index] <= 0.8:
        if not passMVAWP80(chain, index):       return False
        if not chain._ptRatio[index] <= 7:           return False
    else:
        if not passMVAloose(chain, index):      return False
    if not chain._lElectronPassConvVeto[index]:          return False
    return True

def isTightElectronttH(chain, index):
    
    if not isFOElectronttH(chain, index):       return False
    if chain._leptonMvaTTH[index] <= 0.8:       return False
    return True


def isLooseElectron(chain, index, algo = 'cutbased'):
    return isLooseElectronCutBased(chain, index) if algo == 'cutbased' else isLooseElectronttH(chain, index)

def isFOElectron(chain, index, algo = 'cutbased'):
    return isFOElectronCutBased(chain, index) if algo == 'cutbased' else isFOElectronttH(chain, index)

def isTightElectron(chain, index, algo = 'cutbased'):
    return isTightElectronCutBased(chain, index) if algo == 'cutbased' else isTightElectronttH(chain, index)
