
#
# list of functions to select events
#

from HNL.ObjectSelection.leptonSelector import isTightLepton

def getSortKey(item): return item[0]

def select3Leptons(chain):

    chain.leptons = [(chain._lPt[l], l) for l in xrange(chain._nLight) if isTightLepton(chain, l)]
    if len(chain.leptons) < 3:  return False

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
    return passesPtCuts(chain)    

def passesPtCuts(chain):
    
    if chain.l1_pt < 55 and (chain.isEEE or chain.isMuMuMu):       return False
        
    if chain.l1_pt > 30:
        return passesHighLeadingPtCuts(chain)
    else:
        return passesLowLeadingPtCuts(chain)

    
def passesHighLeadingPtCuts(chain):
    
    if chain.l2_pt < 10:        return False
    if chain._lFlavor[chain.l3] == 1 and chain.l3_pt < 5: return False
    if chain._lFlavor[chain.l3] == 0 and chain.l3_pt < 10: return False
    return True

    
def passesLowLeadingPtCuts(chain):
    
    if not passesHighLeadingPtCuts(chain): return False
    #Case 1: eemu
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
    
     
    
