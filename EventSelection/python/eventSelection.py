
#
# list of functions to select events
#

from HNL.ObjectSelection.leptonSelector import isTightLightLepton

def getSortKey(item): return item[0]

def select3LightLeptons(chain, new_chain):

    chain.leptons = [(chain._lPt[l], l) for l in xrange(chain._nLight) if isTightLightLepton(chain, l)]
    if len(chain.leptons) != 3:  return False

    ptAndIndex = sorted(chain.leptons, reverse=True, key = getSortKey) 
    new_chain.l1 = ptAndIndex[0][1]
    new_chain.l2 = ptAndIndex[1][1]
    new_chain.l3 = ptAndIndex[2][1]
    new_chain.l1_pt = ptAndIndex[0][0]
    new_chain.l2_pt = ptAndIndex[1][0]
    new_chain.l3_pt = ptAndIndex[2][0]

    new_chain.isEEE = (chain._lFlavor[chain.l1] == 0 and chain._lFlavor[chain.l2] == 0 and chain._lFlavor[chain.l3] == 0)
    new_chain.isEEMu = ((chain._lFlavor[chain.l1] == 0 and chain._lFlavor[chain.l2] == 0 and chain._lFlavor[chain.l3] == 1)
                    or (chain._lFlavor[chain.l1] == 0 and chain._lFlavor[chain.l2] == 1 and chain._lFlavor[chain.l3] == 0)
                    or (chain._lFlavor[chain.l1] == 1 and chain._lFlavor[chain.l2] == 0 and chain._lFlavor[chain.l3] == 0))
    new_chain.isEMuMu = ((chain._lFlavor[chain.l1] == 0 and chain._lFlavor[chain.l2] == 1 and chain._lFlavor[chain.l3] == 1)
                    or (chain._lFlavor[chain.l1] == 1 and chain._lFlavor[chain.l2] == 1 and chain._lFlavor[chain.l3] == 0)
                    or (chain._lFlavor[chain.l1] == 1 and chain._lFlavor[chain.l2] == 0 and chain._lFlavor[chain.l3] == 1))
    new_chain.isMuMuMu = (chain._lFlavor[chain.l1] == 1 and chain._lFlavor[chain.l2] == 1 and chain._lFlavor[chain.l3] == 1)
    
    if bVeto(chain, 'AN2017-014'):      return False

    #if not passesPtCuts(chain):         return False
    return True   

from HNL.ObjectSelection.leptonSelector import isTightLepton

def select3Leptons(chain, new_chain):

    chain.leptons = [(chain._lPt[l], l) for l in xrange(chain._nL) if isTightLepton(chain, l)]
    if len(chain.leptons) != 3:  return False

    ptAndIndex = sorted(chain.leptons, reverse=True, key = getSortKey) 
    new_chain.l1 = ptAndIndex[0][1]
    new_chain.l2 = ptAndIndex[1][1]
    new_chain.l3 = ptAndIndex[2][1]
    new_chain.l1_pt = ptAndIndex[0][0]
    new_chain.l2_pt = ptAndIndex[1][0]
    new_chain.l3_pt = ptAndIndex[2][0]
    
    if bVeto(chain, 'Deep'):      return False

    return True   

from HNL.ObjectSelection.jetSelector import isGoodJet, isBJet
def bVeto(chain, algo):
    for jet in xrange(chain._nJets):
        if not isGoodJet(chain, jet): continue
        if isBJet(chain, jet, algo, 'loose'): return True    
    return False


def passesPtCuts(chain):
    
    if chain.l1_pt < 15: return False
    if chain.l2_pt < 10: return False
    if chain._lFlavor[chain.l3] == 1 and chain.l3_pt < 5:      return False    
    if chain._lFlavor[chain.l3] == 0 and chain.l3_pt < 10:      return False    
 
    if chain.isEEE:
        if (chain.l1_pt > 19 and chain.l2_pt > 15) or chain.l1_pt > 30:  return True

    if chain.isEEMu:
        if chain._lFlavor[chain.l3] == 0 and chain.l3_pt < 15:  return (chain.l1_pt > 23)
        if chain._lFlavor[chain.l3] == 1 and chain.l3_pt < 8:   return (chain.l1_pt > 25 and chain.l2_pt > 15)
        if chain._lFlavor[chain.l3] == 1 and chain.l3_pt > 8:   return (chain.l1_pt > 23 or chain.l2_pt > 15)

    if chain.isEMuMu:
        if chain._lFlavor[chain.l3] == 1 and chain.l3_pt < 9:  return (chain.l1_pt > 23)

    return True
    
def passedCategory(chain, cat_name):
    
    if cat_name == 'eee' and not chain.isEEE: return False
    if cat_name == 'eemu' and not chain.isEEMu: return False
    if cat_name == 'emumu' and not chain.isEMuMu: return False
    if cat_name == 'mumumu' and not chain.isMuMuMu: return False
    return True
    
from HNL.Tools.helpers import getFourVec
def calculateKinematicVariables(chain, new_chain):
    l1Vec = getFourVec(chain._lPt[new_chain.l1], chain._lEta[new_chain.l1], chain._lPhi[new_chain.l1], chain._lE[new_chain.l1])
    l2Vec = getFourVec(chain._lPt[new_chain.l2], chain._lEta[new_chain.l2], chain._lPhi[new_chain.l2], chain._lE[new_chain.l2])
    l3Vec = getFourVec(chain._lPt[new_chain.l3], chain._lEta[new_chain.l3], chain._lPhi[new_chain.l3], chain._lE[new_chain.l3])
    lVec = [l1Vec, l2Vec, l3Vec]

    new_chain.M3l = (l1Vec + l2Vec + l3Vec).M()
    print new_chain.M3l
    
    #min(M_OS)
    min_mos = 9999999.
    for i1, l in enumerate([new_chain.l1, new_chain.l2, new_chain.l3]):
        for i2, sl in enumerate([new_chain.l1, new_chain.l2, new_chain.l3]):
            if i2 <= i1:        continue
            if chain._lFlavor[l] == chain._lFlavor[sl]: continue
            tmp_mos = (lVec[i1]+lVec[i2]).M()
            if tmp_mos < min_mos:       min_mos = tmp_mos
    new_chain.minMos = min_mos        

    for l in xrange(chain._nLight):
        new_chain.pt_cone[l] = chain._lPt[l]*(1+max(0., chain._miniIso[l]-0.4)) #TODO: is this the correct definition?
    print len(new_chain.pt_cone)

    return

def lowMassCuts(chain, new_chain):
    calculateKinematicVariables(chain, new_chain)
    if new_chain._met > 75:         return False
    if new_chain.m3l > 80:          return False
    if new_chain.l1_pt > 55:        return False
    return True 
     
    
