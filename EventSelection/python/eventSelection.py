
#
# list of functions to select events
#

from HNL.ObjectSelection.leptonSelector import isTightLightLepton

def getSortKey(item): return item[0]

def select3LightLeptons(chain):

    chain.leptons = [(chain._lPt[l], l) for l in xrange(chain._nLight) if isTightLightLepton(chain, l)]
    if len(chain.leptons) != 3:  return False

    ptAndIndex = sorted(chain.leptons, reverse=True, key = getSortKey) 
    chain.l1 = ptAndIndex[0][1]
    chain.l2 = ptAndIndex[1][1]
    chain.l3 = ptAndIndex[2][1]
    chain.l1_pt = ptAndIndex[0][0]
    chain.l2_pt = ptAndIndex[1][0]
    chain.l3_pt = ptAndIndex[2][0]

    chain.isEEE = (chain._lFlavor[chain.l1] == 0 and chain._lFlavor[chain.l2] == 0 and chain._lFlavor[chain.l3] == 0)
    chain.isEEMu = ((chain._lFlavor[chain.l1] == 0 and chain._lFlavor[chain.l2] == 0 and chain._lFlavor[chain.l3] == 1)
                    or (chain._lFlavor[chain.l1] == 0 and chain._lFlavor[chain.l2] == 1 and chain._lFlavor[chain.l3] == 0)
                    or (chain._lFlavor[chain.l1] == 1 and chain._lFlavor[chain.l2] == 0 and chain._lFlavor[chain.l3] == 0))
    chain.isEMuMu = ((chain._lFlavor[chain.l1] == 0 and chain._lFlavor[chain.l2] == 1 and chain._lFlavor[chain.l3] == 1)
                    or (chain._lFlavor[chain.l1] == 1 and chain._lFlavor[chain.l2] == 1 and chain._lFlavor[chain.l3] == 0)
                    or (chain._lFlavor[chain.l1] == 1 and chain._lFlavor[chain.l2] == 0 and chain._lFlavor[chain.l3] == 1))
    chain.isMuMuMu = (chain._lFlavor[chain.l1] == 1 and chain._lFlavor[chain.l2] == 1 and chain._lFlavor[chain.l3] == 1)
    
    if bVeto(chain, 'AN2017-014'):      return False

    #if not passesPtCuts(chain):         return False
    return True   

from HNL.ObjectSelection.leptonSelector import isTightLepton

def select3Leptons(chain):

    chain.leptons = [(chain._lPt[l], l) for l in xrange(chain._nL) if isTightLepton(chain, l)]
    if len(chain.leptons) != 3:  return False

    ptAndIndex = sorted(chain.leptons, reverse=True, key = getSortKey) 
    chain.l1 = ptAndIndex[0][1]
    chain.l2 = ptAndIndex[1][1]
    chain.l3 = ptAndIndex[2][1]
    chain.l1_pt = ptAndIndex[0][0]
    chain.l2_pt = ptAndIndex[1][0]
    chain.l3_pt = ptAndIndex[2][0]
    
    if bVeto(chain, 'Deep'):      return False

    return True   

from HNL.ObjectSelection.jetSelector import *
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
    
     
    
